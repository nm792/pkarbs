"""HLTV scorebot kill timing vs Polymarket price (capture of 4 Nov 2026 from Nick's Mac).
Usage: python3 hltv_lag.py <raw dir>   (scorebot.jsonl.gz, books.jsonl.gz, markets.jsonl)
Kills: dedup by eventId, keep FIRST receipt; drop kills that arrive in a replay burst (first message after a (re)connect
that carries >3 kills not seen before, i.e. history, not live).
Price: mid of the token's book (written on change, 1 s polls). For each live kill, signed mid change toward the killer's
team; event-study curve vs time from HLTV receipt, and per-kill time of first >=1-tick move toward the killer."""
import gzip, json, sys, os, bisect, statistics as st, collections
D = sys.argv[1]
mk = [json.loads(l) for l in open(os.path.join(D, 'markets.jsonl'))]
tok = {m['token']: m for m in mk}
books = collections.defaultdict(list)          # token -> [(t, mid, spread)]
with gzip.open(os.path.join(D, 'books.jsonl.gz'), 'rt') as f:
    for l in f:
        b = json.loads(l)
        if not b['bids'] or not b['asks']: continue
        bb = max(p for p, s in b['bids']); ba = min(p for p, s in b['asks'])
        books[b['token']].append((b['recv_ms'] / 1000, (bb + ba) / 2, ba - bb))
norm = lambda s: ''.join(ch for ch in (s or '').lower() if ch.isalnum()).replace('team', '')
def same(a, b): a, b = norm(a), norm(b); return bool(a) and bool(b) and (a in b or b in a)
SLUG = {2400004: 'cs2-navi-fal2-2026-11-04', 2400005: 'cs2-mglz-furia-2026-11-04', 2400076: 'cs2-meiano-damaju-2026-11-04'}
def token_for(mid, mapname, mapno):
    s = SLUG[mid]; c = [m for m in mk if m['slug'] == s]
    want = 'map%d' % mapno
    for m in c:
        if m['kind'] == want: return m
    for m in c:
        if m['kind'] == 'match': return m          # decider map: match market = map market
    return None
seen = set(); kills = []; rounds = []; sbstate = {}; mapseq = collections.defaultdict(list); last_ev = {}
with gzip.open(os.path.join(D, 'scorebot.jsonl.gz'), 'rt') as f:
    for l in f:
        d = json.loads(l); m = d['hltv_id']; t = d['recv_ms'] / 1000
        if d['ev'] in ('connect', 'reconnect'): last_ev[m] = 'connect'; continue
        if d['ev'] == 'scoreboard':
            s = d['data']; sbstate[m] = s
            if s.get('mapName') and (not mapseq[m] or mapseq[m][-1] != s['mapName']): mapseq[m].append(s['mapName'])
            continue
        if d['ev'] != 'log': continue
        evs = d['data'].get('log', []) if isinstance(d['data'], dict) else []
        new = [e['Kill'] for e in evs if 'Kill' in e and (m, e['Kill']['eventId']) not in seen]
        for e in evs:
            if 'Kill' in e: seen.add((m, e['Kill']['eventId']))
        after_conn = last_ev.get(m) == 'connect'; last_ev[m] = 'log'
        s = sbstate.get(m) or {}
        if not s.get('live'): continue
        if after_conn and len(new) > 3: continue            # history replay
        tn = {'TERRORIST': s.get('terroristTeamName'), 'CT': s.get('ctTeamName')}
        for k in new:
            kills.append(dict(t=t, m=m, team=tn.get(k['killerSide']), map=s.get('mapName'), mapno=len(mapseq[m]),
                              rnd=s.get('currentRound'), alive=None))
        for e in evs:
            if 'RoundEnd' in e and after_conn is False:
                pass
def mid_at(series, t):
    i = bisect.bisect_right([x[0] for x in series], t) - 1
    return series[i][1] if i >= 0 else None
rows = []
for k in kills:
    mm = token_for(k['m'], k['map'], k['mapno'])
    if not mm: continue
    ser = books.get(mm['token'])
    if not ser: continue
    sign = 1 if same(k['team'], mm['outcomes'][0]) else (-1 if same(k['team'], mm['outcomes'][1]) else 0)
    if sign == 0: continue
    m0 = mid_at(ser, k['t'] - 60)
    if m0 is None or not (0.03 < m0 < 0.97): continue
    curve = {dt: sign * (mid_at(ser, k['t'] + dt) - m0) for dt in range(-60, 61, 1)}
    # first >=1 tick (0.01; mid half-ticks count) move toward killer, from -30 s, relative to price 30 s before
    ref = mid_at(ser, k['t'] - 30); first = None
    for dt in range(-30, 61):
        v = sign * (mid_at(ser, k['t'] + dt) - ref)
        if v >= 0.0099: first = dt; break
    rows.append(dict(m=k['m'], slug=mm['slug'], kind=mm['kind'], t=k['t'], team=k['team'], map=k['map'], curve=curve, first=first, m0=m0))
out = dict(n_kills_live=len(kills), n_with_price=len(rows), per_match=collections.Counter(r['slug'] + ':' + r['kind'] for r in rows))
for name, sub in [('all', rows)] + [(s, [r for r in rows if r['slug'] == s]) for s in sorted(set(r['slug'] for r in rows))]:
    if not sub: continue
    avg = {dt: st.mean(r['curve'][dt] for r in sub) for dt in range(-60, 61, 5)}
    tot = st.mean(r['curve'][60] - r['curve'][-60] for r in sub)
    fm = [r['first'] for r in sub if r['first'] is not None]
    out[name] = dict(n=len(sub), avg_signed_mid_change_cents={dt: round(100 * v, 2) for dt, v in avg.items()},
                     n_moved=len(fm), first_move_median_s=st.median(fm) if fm else None,
                     first_move_quartiles=(st.quantiles(fm, n=4) if len(fm) >= 4 else fm),
                     share_moved_before_hltv=round(sum(1 for x in fm if x < 0) / len(fm), 2) if fm else None)
json.dump(out, sys.stdout, indent=1, default=str)
