#!/usr/bin/env python3
"""Step 9b: equal-information comparison.  Model(state at feed time t) vs market mid at t-L, L=0..60 s.  If the model only matches the market at a lagged L,
the model's quality equals the market's quality on older information (the gap at L=0 is information timing, not model quality)."""
import sys, pickle, json, bisect, numpy as np
D = pickle.load(open(sys.argv[1], 'rb')); R = D['rows']; test = set(D['test'])
P = json.load(open(sys.argv[2]))['pairs']; B = pickle.load(open(sys.argv[3], 'rb'))['book']
T = {k: [x[0] for x in v] for k, v in B.items()}
def mid(tk, t, maxage=20):
    ts = T.get(tk); i = bisect.bisect_right(ts, t) - 1
    if i < 0 or t - ts[i] > maxage: return None
    return (B[tk][i][1] + B[tk][i][2]) / 2
for label, sel in (('ALL 86 maps', lambda k: True), ('TEST half', lambda k: k in test)):
    print(label)
    for L in (0, 10, 20, 30, 45, 60, 90):
        v = []
        for x in R:
            if not sel(x['key']): continue
            m = mid(P[x['key']]['tok_home'], x['t'] - L)
            if m is not None: v.append((x['y'], m, x['A'], x['C'], x['S']))
        a = np.array(v); y = a[:, 0]
        br = lambda p: np.mean((p - y) ** 2)
        print('  market lagged %2d s: Brier market %.4f | model A %.4f | model C %.4f | score-only %.4f | n=%d' % (L, br(a[:, 1]), br(a[:, 2]), br(a[:, 3]), br(a[:, 4]), len(a)))
