#!/usr/bin/env python3
"""Step 12b: does team Elo (whole bo3 history) carry information the Polymarket map price lacks?  Per paired map: market anchor price (first clean mid), Elo-implied
map prob (Elo diff -> map win with slope fitted by logistic on the maps themselves, 2 params, leave-one-match-out), outcome y_map. Compare Brier; logistic of y on
[logit(market), elo_diff/400] with match-clustered SE."""
import sys, json, pickle, numpy as np, collections
from scipy.optimize import minimize
D = pickle.load(open(sys.argv[1], 'rb')); E = json.load(open(sys.argv[2])); rows = pickle.load(open(sys.argv[3], 'rb'))['rows']
first = {}
for x in sorted(rows, key=lambda x: x['t']):
    if x['key'] not in first and 0.1 <= x['mkt'] <= 0.9: first[x['key']] = x          # anchor row (market mid at the first clean sample)
keys = [k for k in first if k in E and D['maps'][k]['complete']]
mk = np.array([first[k]['mkt'] for k in keys]); y = np.array([D['maps'][k]['y_map'] for k in keys], float); ed = np.array([(E[k]['elo_h'] - E[k]['elo_a']) / 400 for k in keys])
grp = [k.split('|')[0] for k in keys]
lg = lambda p: np.log(p / (1 - p))
print('maps %d, matches %d; home win rate %.2f' % (len(keys), len(set(grp)), y.mean()))
def fit(X, y):
    def f(w):
        z = X @ w; p = 1 / (1 + np.exp(-z)); return -np.sum(y * np.log(p + 1e-12) + (1 - y) * np.log(1 - p + 1e-12)), X.T @ (p - y)
    return minimize(f, np.zeros(X.shape[1]), jac=True).x
X1 = np.column_stack([np.ones(len(y)), lg(mk), ed]); w = fit(X1, y)
# match-clustered bootstrap for coefficients
rng = np.random.default_rng(1); ug = sorted(set(grp)); bs = []
gi = {g: [i for i, gg in enumerate(grp) if gg == g] for g in ug}
for _ in range(400):
    pick = rng.choice(len(ug), len(ug)); ix = [i for p in pick for i in gi[ug[p]]]; bs.append(fit(X1[ix], y[ix]))
bs = np.array(bs)
print('logit(y) = %.2f + %.2f*logit(market) + %.2f*elo_diff/400   | bootstrap SE: %.2f / %.2f / %.2f' % (w[0], w[1], w[2], *bs.std(0)))
print('   (market slope 1 and Elo coef 0 = market already has it all)')
# leave-one-match-out Elo-only prob and Elo+market prob
def loo(cols):
    p = np.zeros(len(y))
    for g in ug:
        te = gi[g]; tr = [i for i in range(len(y)) if i not in set(te)]
        ww = fit(cols[tr], y[tr]); p[te] = 1 / (1 + np.exp(-(cols[te] @ ww)))
    return p
pe = loo(np.column_stack([np.ones(len(y)), ed])); pm = loo(np.column_stack([np.ones(len(y)), lg(mk)])); pb = loo(X1)
br = lambda p: np.mean((p - y) ** 2)
print('Brier (leave-one-match-out): market raw %.4f | market recalibrated %.4f | Elo only %.4f | market+Elo %.4f | coin 0.25' % (br(mk), br(pm), br(pe), br(pb)))
