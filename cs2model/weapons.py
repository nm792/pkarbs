#!/usr/bin/env python3
"""Step 11b: weapon-id price table by non-negative least squares: team spend (cash at first full row el<=6 minus cash at el 28-45)
= sum_w n_w * price_w + per-player armor/utility constant, over all team-rounds with 100 <= spend <= 26000 and spend/5 buy visible. Output wprice.json {wid: price}."""
import sys, json, gzip, collections, numpy as np
from scipy.optimize import nnls
msgs = collections.defaultdict(list)
for l in gzip.open(sys.argv[1], 'rt'):
    r = json.loads(l); msgs[(r['mid'], r['map'])].append(r)
cnt = collections.Counter(); X = []; y = []
for key, L in msgs.items():
    L.sort(key=lambda r: r['t']); first = {}; post = {}
    for r in L:
        tm = (r['tm'] or [0, 0, 0])[2]
        if not tm: continue
        full = len(r['h']['pl']) == 5 and len(r['a']['pl']) == 5 and all(len(q) >= 10 for q in r['h']['pl'] + r['a']['pl'])
        if not full: continue
        el = r['t'] - tm
        if el <= 6 and tm not in first: first[tm] = r
        if 28 <= el <= 45 and tm not in post: post[tm] = r
    for tm in first:
        if tm not in post: continue
        for team in ('h', 'a'):
            pre = sum(q[1] for q in first[tm][team]['pl']); aft = sum(q[1] for q in post[tm][team]['pl']); sp = pre - aft
            if 100 <= sp <= 26000:
                ws = [q[6] for q in post[tm][team]['pl'] if q[6]]
                for w in ws: cnt[w] += 1
                X.append(ws); y.append(sp)
W = [w for w, c in cnt.items() if c >= 40]
idx = {w: i for i, w in enumerate(W)}
A = np.zeros((len(y), len(W) + 1))
for i, ws in enumerate(X):
    for w in ws:
        if w in idx: A[i, idx[w]] += 1
    A[i, -1] = 1.0
coef, res = nnls(A, np.array(y, float))
pred = A @ coef; r2 = 1 - np.sum((np.array(y) - pred) ** 2) / np.sum((np.array(y) - np.mean(y)) ** 2)
print('team-rounds', len(y), 'weapon ids', len(W), 'R2 %.3f' % r2, 'const %.0f' % coef[-1])
wp = {w: float(coef[idx[w]]) for w in W}
for w, p in sorted(wp.items(), key=lambda kv: kv[1]): print('  %s n=%d price~%.0f' % (w[:8], cnt[w], p))
json.dump(wp, open(sys.argv[2], 'w'))
