"""NHL: how late is Polymarket's sports-WS score vs the Polymarket PRICE, on past nights (5 Nov 2026).
Inputs: server sports-WS frames (rn1/scores/cs2/server-2026-11/cs2_frames.jsonl.gz, all leagues, 2-4 Nov),
Polymarket moneyline trades + ESPN goal wallclock (winmodels/raw/us_nhl_hist, us_hist/nhl; s1_hist_nhl.py).
Per goal (ESPN score change), price reference from trades (1 s): onset = first print with >= 20% of the
(t-120 -> t+120) move in the scoring team's direction; half = first print with >= 50%.
Reports WS score-change recv time minus onset / half / ESPN wallclock. Usage: python3 ws_lag_past.py"""
import os, sys, json, gzip, re, bisect, collections, datetime as dt
import numpy as np
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, f'{R}/winmodels'); import common as C
def ts(s): return dt.datetime.fromisoformat(s.replace('Z', '+00:00')).timestamp()
def nz(s): return re.sub(r'[^a-z0-9]', '', (s or '').lower())
H = f'{R}/winmodels/raw/us_nhl_hist'
G = {str(e.get('gameId')): e for e in json.load(gzip.open(f'{H}/gamma_events.json.gz'))}
MT = json.load(open(f'{H}/match.json'))
fr = collections.defaultdict(list)
for l in gzip.open(f'{R}/rn1/scores/cs2/server-2026-11/cs2_frames.jsonl.gz', 'rt'):
    if '"nhl"' not in l: continue
    d = json.loads(l); fr[str(d['gameId'])].append(d)
rows = []; skipped = collections.Counter(); gaps = []
for gid, F in fr.items():
    e = G.get(gid)
    if not e: skipped['no gamma event'] += 1; continue
    g = json.load(gzip.open(f"{R}/winmodels/raw/us_hist/nhl/{MT[e['slug']]['espn_id']}.json.gz"))
    tm = {x['ordering']: nz(x['name']) for x in e['teams']}
    m = [m for m in e['markets'] if m.get('sportsMarketType') == 'moneyline'][0]
    o0 = nz(json.loads(m['outcomes'])[0]); home0 = o0 in tm['home'] or tm['home'] in o0
    pr = C.prints(json.load(gzip.open(f"{H}/trades/{m['conditionId']}.json.gz"))); tt = [p[0] for p in pr]; M = C.Mid(pr)
    F.sort(key=lambda d: d['recv_ms']); gaps += [(b['recv_ms'] - a['recv_ms']) / 1000 for a, b in zip(F, F[1:]) if b['live'] and not b['ended']]
    # WS score changes: (recv_s, total goals after) ; order of numbers in the score string is irrelevant for totals
    ws = []
    for a, b in zip(F, F[1:]):
        if a['score'] != b['score']:
            ws.append((b['recv_ms'] / 1000, sum(int(x) for x in b['score'].split('-'))))
    tl = sorted((ts(r[0]), r[3], r[4]) for r in g['tl'])
    for (t, h, a), (tp, hp, ap) in zip(tl[1:], tl[:-1]):
        if (h, a) == (hp, ap): continue
        tot = h + a
        if tot < hp + ap: skipped['goal removed (review)'] += 1; continue
        w = [x for x in ws if x[1] == tot and -60 < x[0] - t < 400]
        if not w: skipped['no WS change'] += 1; continue
        home_scored = h > hp; up0 = home_scored == home0          # token0 should rise?
        pa, pb = M.at(t - 120), M.at(t + 120)
        if pa is None or pb is None: skipped['no price'] += 1; continue
        mv = (pb - pa) if up0 else (pa - pb)
        if mv < 0.02: skipped['price moved < 2c'] += 1; continue
        on = half = None
        for p in pr[bisect.bisect_left(tt, t - 120):bisect.bisect_right(tt, t + 120)]:
            x = ((p[2] - pa) if up0 else (pa - p[2])) / mv
            if on is None and x >= 0.2: on = p[0]
            if x >= 0.5: half = p[0]; break
        if on is None or half is None: skipped['no onset'] += 1; continue
        rows.append(dict(game=e['slug'], wall=t, onset=on, half=half, ws=w[0][0], move=round(mv, 3)))
A = lambda k: np.array([r[k] for r in rows])
def st(x): return dict(n=len(x), median=float(np.median(x)), p10=float(np.percentile(x, 10)), p25=float(np.percentile(x, 25)), p75=float(np.percentile(x, 75)), p90=float(np.percentile(x, 90)))
out = dict(games=len({r['game'] for r in rows}), goals=len(rows), skipped=dict(skipped),
           ws_frame_gap_s=st(np.array(gaps)),
           ws_minus_onset=st(A('ws') - A('onset')), ws_minus_half=st(A('ws') - A('half')),
           espn_wall_minus_onset=st(A('wall') - A('onset')), half_minus_onset=st(A('half') - A('onset')), rows=rows)
for k, v in out.items():
    if k != 'rows': print(k, v)
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out_ws_lag_past.json'), 'w'), indent=1)
