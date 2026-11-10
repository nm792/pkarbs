#!/usr/bin/env python3
"""Step 5a: real trade prints (data-api /v2/trades) for every paired map-winner and match-winner condition. Output trades.json {cond: [(ts, side, price, size, token_id)]}
Read-only public API. Keeps prints inside [first snapshot - 1 h, last snapshot + 1 h] of the map."""
import json, sys, requests, time, concurrent.futures as cf
P = json.load(open(sys.argv[1]))['pairs']; R = json.load(open(sys.argv[2]))
jobs = {}
for key, p in P.items():
    m = R[key]['meta']
    for c in (p['cond'], p.get('mw_cond')):
        if c:
            lo, hi = m['t0'] - 3600, m['t1'] + 3600
            a, b = jobs.get(c, (lo, hi)); jobs[c] = (min(a, lo), max(b, hi))
S = requests.Session()
def fetch(item):
    c, (lo, hi) = item; out = []; cur = None
    for _ in range(300):
        p = dict(condition=c, limit=500)
        if cur: p['cursor'] = cur
        j = None
        for a in range(5):
            try: j = S.get('https://data-api.polymarket.com/v2/trades', params=p, timeout=40).json()
            except Exception: j = None
            if j and 'data' in j: break
            time.sleep(1 + a); j = None
        if j is None: return c, None, out
        d = j['data']; out += [(x['timestamp'], x['side'], x['price'], x['size'], x['token_id']) for x in d if lo <= x['timestamp'] <= hi]
        if not d or d[-1]['timestamp'] < lo or not j['pagination'].get('has_more'): break
        cur = j['pagination'].get('next_cursor')
    return c, True, out
res = {}; bad = 0
with cf.ThreadPoolExecutor(12) as ex:
    for i, (c, ok, out) in enumerate(ex.map(fetch, jobs.items())):
        res[c] = sorted(out)
        if not ok: bad += 1
        if i % 20 == 0: print(i, len(jobs), flush=True)
json.dump(res, open(sys.argv[3], 'w'))
print('conds', len(res), 'errors', bad, 'prints', sum(len(v) for v in res.values()))
