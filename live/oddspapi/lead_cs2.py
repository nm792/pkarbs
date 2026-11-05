"""Does Pinnacle (via OddsPapi history) move before the Polymarket price? CS2, 4 Nov 2026.
PM: 1 s books (cs2-feeds/2026-11-04). Pinnacle: OddsPapi historical-odds (createdAt = OddsPapi ingest time).
Usage: python3 lead_cs2.py OP_DIR PM_DIR
"""
import gzip, json, glob, sys, bisect, collections, datetime as dt, statistics as stx, re

op, pm = sys.argv[1], sys.argv[2]
def ts(s): return dt.datetime.fromisoformat(s.replace('Z', '+00:00')).timestamp()
def norm(s): return re.sub(r'[^a-z0-9]', '', s.lower())

# PM markets: match winner token for outcome[0]
mk = {}
for l in gzip.open(f'{pm}/markets.jsonl.gz', 'rt'):
    m = json.loads(l)
    if m['kind'] == 'Match Winner': mk[m['tokens'][0]] = m
want = set(mk)
# PM mid per token, 1 s
mids = collections.defaultdict(list)
for l in gzip.open(f'{pm}/books.jsonl.gz', 'rt'):
    b = json.loads(l)
    if b['asset'] not in want or not b['bids'] or not b['asks']: continue
    bb = max(float(x['price']) for x in b['bids']); ba = min(float(x['price']) for x in b['asks'])
    if ba - bb > 0.1: continue
    mids[b['asset']].append((b['recv_ms'] / 1000, (bb + ba) / 2))

def series_at(ser, t):
    i = bisect.bisect_right([x[0] for x in ser], t) - 1
    return ser[i][1] if i >= 0 else None

out = []
for f in glob.glob(f'{op}/hist/*'):
    d = json.load(gzip.open(f)); fx = d['fixture']
    if fx['sportId'] != 17: continue
    pin = d['hist'].get('bookmakers', {}).get('pinnacle')
    if not pin or '171' not in pin['markets']: continue
    p1, p2 = norm(fx['participant1Name']), norm(fx['participant2Name'])
    tok = None
    for t, m in mk.items():
        o = [norm(x) for x in m['outcomes']]
        if (o[0][:5] in p1 or p1[:5] in o[0]) and (o[1][:5] in p2 or p2[:5] in o[1]): tok, flip = t, False
        elif (o[0][:5] in p2 or p2[:5] in o[0]) and (o[1][:5] in p1 or p1[:5] in o[1]): tok, flip = t, True
        if tok: break
    if not tok or len(mids[tok]) < 100: continue
    outs = pin['markets']['171']['outcomes']
    ev = []
    for oid, ov in outs.items():
        for x in ov['players']['0']:
            ev.append((ts(x['createdAt']), oid, x['price'], x['active']))
    ev.sort()
    cur = {}; pser = []; susp = []
    for t, oid, pr, act in ev:
        if not act: susp.append(t); continue
        cur[oid] = pr
        if len(cur) == 2:
            a, b = (cur.get('171'), cur.get('172'))
            if a and b:
                q = (1 / a) / (1 / a + 1 / b)
                pser.append((t, 1 - q if flip else q))
    ser = mids[tok]
    if len(pser) < 20: continue
    # PM jumps: |mid(t) - mid(t-10)| >= 0.04, de-dup 60 s
    jumps = []; last = -1e9
    times = [x[0] for x in ser]
    for t, m in ser:
        m0 = series_at(ser, t - 10)
        if m0 is None or t - last < 60: continue
        if abs(m - m0) >= 0.04:
            jumps.append((t, m0, m)); last = t
    ptimes = [x[0] for x in pser]
    for t0, a, b in jumps:
        base = series_at(pser, t0 - 60)
        if base is None: continue
        thr = 0.5 * (b - a); tp = None
        i = bisect.bisect_left(ptimes, t0 - 60)
        for tt, q in pser[i:]:
            if tt > t0 + 120: break
            if (q - base) * (1 if thr > 0 else -1) >= abs(thr): tp = tt; break
        sp = [s for s in susp if t0 - 60 <= s <= t0 + 60]
        out.append(dict(match=f"{fx['participant1Name']} v {fx['participant2Name']}", t_pm=t0, move=round(b - a, 3),
                        pin_lag=None if tp is None else round(tp - t0, 1),
                        susp_lag=round(sp[0] - t0, 1) if sp else None))
json.dump(out, open('/tmp/claude-0/lead_cs2.json', 'w'), indent=1)
lags = [o['pin_lag'] for o in out if o['pin_lag'] is not None]
sl = [o['susp_lag'] for o in out if o['susp_lag'] is not None]
print('matches', len({o['match'] for o in out}), 'PM jumps', len(out), 'Pinnacle matched', len(lags))
if lags:
    print('Pinnacle move lag vs PM (s, negative = Pinnacle first): median', stx.median(lags),
          'share Pinnacle >=5 s earlier', round(sum(l <= -5 for l in lags) / len(lags), 2),
          'quartiles', [round(x, 1) for x in stx.quantiles(lags, n=4)])
if sl: print('Pinnacle suspension lag: median', stx.median(sl), 'n', len(sl), 'share <= -5 s', round(sum(l <= -5 for l in sl) / len(sl), 2))
for m in sorted({o['match'] for o in out}):
    l = [o['pin_lag'] for o in out if o['match'] == m and o['pin_lag'] is not None]
    print(' ', m, 'jumps', sum(o['match'] == m for o in out), 'median lag', stx.median(l) if l else None)
