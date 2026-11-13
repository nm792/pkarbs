"""When does the Polymarket NBA moneyline price move, relative to the official play time (NBA timeActual), and how
much of the move is done when each feed's message reaches us?  Inputs: NBA liveData play-by-play files (ms
timeActual), Polymarket data-api trades (1 s), and feed receipt logs (PM sports WS frames; optional poll.py output).
Usage: python3 price_vs_play.py PBP_DIR WS_FILE [POLL_DIR] ; slugs found via gamma by tricodes and date."""
import sys, os, json, glob, gzip, datetime as dt, collections, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))
import common as C
def ts(s): return dt.datetime.fromisoformat(s.replace('Z', '+00:00')).timestamp()
PBP, WSF = sys.argv[1], sys.argv[2]; POLL = sys.argv[3] if len(sys.argv) > 3 else None
games = []
for f in sorted(glob.glob(f'{PBP}/playbyplay_*.json')):
    d = json.load(open(f))['game']; A = d['actions']
    gid = d['gameId']; games.append((gid, A))
# Polymarket market per game via gamma (home/away tricodes from scoreboard schedule cache)
SCHED = json.load(open(sys.argv[4])) if len(sys.argv) > 4 else None
sch = {}
for gd in SCHED['leagueSchedule']['gameDates']:
    for g in gd['games']: sch[g['gameId']] = g
ws = collections.defaultdict(list)
for l in open(WSF):
    r = json.loads(l); d = json.loads(r['data']) if 'data' in r else r
    if d.get('leagueAbbreviation') == 'nba' and d.get('score'): ws[frozenset((d['homeTeam'], d['awayTeam']))].append((r['recv_ms'] / 1000, d['score']))
s3 = {}
if POLL:
    for l in open(f'{POLL}/nba_actions.jsonl'):
        a = json.loads(l); k = (a['gid'], int(a['h']), int(a['a'])); s3.setdefault(k, a['recv_ms'] / 1000)
SL = np.arange(-30, 61, 1); acc = np.zeros(len(SL)); n = 0; frac_ws = []; frac_s3 = []; lag_ws = []; lag_s3 = []; per = {}
for gid, A in games:
    g = sch[gid]; a3, h3 = g['awayTeam']['teamTricode'], g['homeTeam']['teamTricode']
    day = g['gameDateEst'][:10]
    c, e = C.jget('https://gamma-api.polymarket.com/events', {'slug': f'nba-{a3.lower()}-{h3.lower()}-{day}'})
    if not e: print('no PM event', gid, a3, h3); continue
    ml = [m for m in e[0]['markets'] if m.get('sportsMarketType') == 'moneyline'][0]
    oc = json.loads(ml['outcomes']); home0 = h3.lower() in oc[0].lower() or g['homeTeam']['teamName'].lower() in oc[0].lower()
    t0 = ts(g['gameDateTimeUTC'])
    tr = C.pull_trades(ml['conditionId'], t0 - 1800, t0 + 4 * 3600, 'us_live/trades')
    M = C.Mid(C.prints(tr))
    W = ws.get(frozenset((a3, h3)), []); wfirst = {}
    for t, sc in W:
        try: x, y = [int(v) for v in sc.split('-')]
        except Exception: continue
        wfirst.setdefault((x, y), t); wfirst.setdefault(('r', y, x), t)
    last = (0, 0); cnt = 0
    for a in A:
        sc = (int(a['scoreHome']), int(a['scoreAway']))
        if sc == last: continue
        dh = (sc[0] - last[0]) - (sc[1] - last[1]); last = sc
        if dh == 0 or not a.get('timeActual'): continue
        t = ts(a['timeActual']); s = np.sign(dh) * (1 if home0 else -1)
        pts = [M.at(t + x) for x in SL]
        if any(p is None for p in pts) or not (0.1 < pts[0] < 0.9): continue
        mv = s * (np.array(pts) - pts[0]); acc += mv; n += 1; cnt += 1
        tot = mv[-1]
        tw = wfirst.get(sc) or wfirst.get(('r', sc[0], sc[1]))
        # score string may be away-home or home-away: accept either order
        if tw is None: tw = wfirst.get((sc[1], sc[0]))
        if tw is not None and -5 < tw - t < 60:
            lag_ws.append(tw - t)
            if abs(tot) >= 0.01: frac_ws.append(s * (M.at(tw) - pts[0]) / tot)
        k = (gid, sc[0], sc[1])
        if k in s3 and -5 < s3[k] - t < 60:
            lag_s3.append(s3[k] - t)
            if abs(tot) >= 0.01: frac_s3.append(s * (M.at(s3[k]) - pts[0]) / tot)
    per[gid] = cnt
cum = acc / n * 100
half = SL[np.argmax(cum >= cum[-1] / 2)]; q80 = SL[np.argmax(cum >= 0.8 * cum[-1])]; q20 = SL[np.argmax(cum >= 0.2 * cum[-1])]
print(f'score changes {n} in {len(per)} games; signed move by +60 s {cum[-1]:.2f}c; before play time {cum[SL.tolist().index(0)]:.2f}c')
print(f'price move vs play time: 20% done at {q20:+d} s, 50% at {half:+d} s, 80% at {q80:+d} s')
for x in (-5, 0, 2, 4, 6, 8, 10, 15, 20, 30): print(f'  {x:+3d} s: {cum[SL.tolist().index(x)] / cum[-1] * 100:5.1f}% of 60 s move')
out = dict(n=n, games=per, move60_c=float(cum[-1]), t20=int(q20), t50=int(half), t80=int(q80), curve=dict(zip([int(x) for x in SL], [float(v) for v in cum])))
for nm, lg, fr in (('pm_ws', lag_ws, frac_ws), ('nba_s3', lag_s3, frac_s3)):
    if lg:
        lg = np.array(lg); fr = np.array(fr)
        out[nm] = dict(n=len(lg), delay_vs_play_med=float(np.median(lg)), delay_vs_price_half_med=float(np.median(lg) - half), move_done_at_receipt_med=float(np.median(fr)) if len(fr) else None)
        print(f'{nm}: n {len(lg)}, delay vs play {np.median(lg):.1f} s, vs price half-move {np.median(lg) - half:+.1f} s, median share of move done when it reaches us {np.median(fr) * 100 if len(fr) else float("nan"):.0f}%')
json.dump(out, open(os.path.join(HERE, f'out_price_vs_play_{os.path.basename(PBP.rstrip("/"))}.json'), 'w'), indent=1)
