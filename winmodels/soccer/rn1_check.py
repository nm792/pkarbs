"""Reality check: rn1's actual in-play fills (22-29 Oct) in the same soccer markets, scored with the same mid and outcomes."""
import sys, os, json, gzip, collections
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
import common as C, backtest as B
EV, _ = B.load_events()
mk = {m['cond']: (E, m) for E in EV for m in E['markets']}
A = [a for a in json.load(gzip.open('/mnt/project-files/rn1/raw/act7d.json.gz')) if a['type'] == 'TRADE' and a['conditionId'] in mk]
print('rn1 fills in these markets', len(A))
agg = collections.defaultdict(lambda: np.zeros(5)); cache = {}
for a in A:
    E, m = mk[a['conditionId']]
    if not (E['k1'] <= a['timestamp'] <= E['e2']): continue
    if a['conditionId'] not in cache:
        fn = f"{C.RAW}/soccer/trades/{a['conditionId']}.json.gz"
        cache[a['conditionId']] = C.Mid(C.prints(json.load(gzip.open(fn)))) if os.path.exists(fn) else None
    M = cache[a['conditionId']]
    if M is None: continue
    T = a['timestamp']; m0, m60 = M.at(T - 1), M.at(T + 61)
    if m0 is None or m60 is None: continue
    if a['outcomeIndex'] == 1: m0, m60 = 1 - m0, 1 - m60
    if not (0.05 <= m0 <= 0.95): continue
    p, q = a['price'], a['size']; out = 1.0 if (m['win0'] == (a['outcomeIndex'] == 0)) else 0.0
    rel = (m0 - p) / m0
    k = 'below mid >5%' if rel > 0.05 else 'below mid 1-5%' if rel > 0.01 else 'within 1% / above mid'
    for kk in (k, 'all', m['type']):
        agg[kk] += [q * p, q * (m0 - p), q * (m60 - p), q * (out - p), 1]
for k, v in sorted(agg.items()): print(f'{k:24} fills {int(v[4]):>6} $ {v[0]:>9.0f} entry {100*v[1]/v[0]:>6.2f}% 1min {100*v[2]/v[0]:>6.2f}% result {100*v[3]/v[0]:>6.2f}%')
