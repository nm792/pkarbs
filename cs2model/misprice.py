#!/usr/bin/env python3
"""Step 9: how did the OLD model (round score only, strength from price) misprice vs the market, and which in-round state explains the gap?
Regress (market logit - score-only logit) on the in-round state pieces. Slope 1 = market prices that piece as our fitted model does; 0 = market ignores it.
Map-clustered standard errors. Uses all paired maps (rows.pkl)."""
import sys, pickle, numpy as np, collections
from predict import *
D = pickle.load(open(sys.argv[1], 'rb')); R = D['rows']
lg = lambda p: np.log(np.clip(p, 1e-3, 1 - 1e-3) / (1 - np.clip(p, 1e-3, 1 - 1e-3)))
keys = sorted(set(x['key'] for x in R))
def design(R, cols):
    X = []
    for x in R:
        r = x['r']; s = 1.0 if r['homeT'] else -1.0; d = r['al_h'] - r['al_a']; pl = r['planted']; tot = r['al_h'] + r['al_a']
        f = dict(alive=d, alive_few=d * (10 - tot) / 10.0, hp=(r['hp_h'] - r['hp_a']) / 100.0, bomb=pl * s, bomb_time=pl * s * min(r['tplant'], 45) / 40.0, clock=(1 - pl) * (-s) * max(r['el'], 0) / 100.0, state_total=lg(x['A']) - lg(x['S']))
        X.append([f[c] for c in cols])
    return np.array(X)
def cluster_ols(X, y, g):
    X1 = np.column_stack([np.ones(len(y)), X]); b = np.linalg.lstsq(X1, y, rcond=None)[0]; e = y - X1 @ b
    XtXi = np.linalg.inv(X1.T @ X1); meat = np.zeros((X1.shape[1],) * 2)
    for k in set(g):
        i = np.array([gg == k for gg in g]); s = X1[i].T @ e[i]; meat += np.outer(s, s)
    V = XtXi @ meat @ XtXi; return b, np.sqrt(np.diag(V)), 1 - e.var() / y.var()
y = np.array([lg(x['mkt']) - lg(x['S']) for x in R]); g = [x['key'] for x in R]
print('points %d, maps %d. Old model (score only) vs market: mean logit gap %+.3f, sd %.3f' % (len(R), len(keys), y.mean(), y.std()))
for cols in (['state_total'], ['alive', 'alive_few', 'hp', 'bomb', 'bomb_time', 'clock']):
    X = design(R, cols); b, se, r2 = cluster_ols(X, y, g)
    print('mkt_logit - score_only_logit ~ ' + ' + '.join(cols) + '   (R2 %.3f)' % r2)
    print('   intercept %+.3f (se %.3f)' % (b[0], se[0]))
    for c, bb, ss in zip(cols, b[1:], se[1:]): print('   %-12s coef %+.3f  se %.3f' % (c, bb, ss))
# where the old model is off, by score situation (market vs score-only): mean gap by lead bucket and map-stage
st = collections.defaultdict(list)
for x in R:
    r = x['r']; lead = r['h'] - r['a']; stage = 'early(<8 rds)' if r['n'] < 8 else ('mid(8-17)' if r['n'] < 18 else 'late(18+)')
    st[(stage, 'home leads' if lead > 0 else ('level' if lead == 0 else 'home trails'))].append((x['mkt'] - x['S'], x['y'] - x['S'], x['y'] - x['mkt']))
print('by stage/lead: n | mean(market - old model) | mean(actual - old model) | mean(actual - market)')
for k in sorted(st):
    v = np.array(st[k]); print('  %-34s n=%4d  %+.3f  %+.3f  %+.3f' % (str(k), len(v), v[:, 0].mean(), v[:, 1].mean(), v[:, 2].mean()))
