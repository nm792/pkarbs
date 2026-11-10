#!/usr/bin/env python3
"""Step 7: fit the in-round state model g(x): P(home wins round | alive, hp, bomb, time, side, cash). Train = earlier half of maps (by start time), test = later half.
Prints coefficients, test log-loss / Brier vs a side-only baseline, and calibration by bomb state / alive diff.  Saves model.json."""
import sys, json, pickle, math, numpy as np
from scipy.optimize import minimize
D = pickle.load(open(sys.argv[1], 'rb')); S = D['samples']; M = D['maps']
keys = sorted(M, key=lambda k: M[k]['t0']); half = len(keys) // 2
train_keys = set(keys[:half]); test_keys = set(keys[half:])
FEATS = ['al_diff', 'al_diff_x_few', 'hp_diff', 'planted_s', 'planted_s_tplant', 'time_pressure', 'side_s', 'al_diff_planted_s', 'cash', 'adr_diff', 'kill_diff_pr']
def feats(r):
    s = 1.0 if r['homeT'] else -1.0
    d = r['al_h'] - r['al_a']; tot = r['al_h'] + r['al_a']; pl = r['planted']
    return [d, d * (10 - tot) / 10.0, (r['hp_h'] - r['hp_a']) / 100.0, pl * s, pl * s * min(r['tplant'], 45) / 40.0, (1 - pl) * (-s) * max(r['el'], 0) / 100.0, s,
            d * pl * s, r['mdiff'] / 10000.0, (r['adr_h'] - r['adr_a']) / 50.0, (r['k_h'] - r['k_a']) / max(r['n'], 3) / 3.0]
def fit(X, y, l2=1.0, offset=None):
    X = np.asarray(X); y = np.asarray(y); off = np.zeros(len(y)) if offset is None else offset
    def f(w):
        z = X @ w[1:] + w[0] + off; p = 1 / (1 + np.exp(-z))
        ll = -np.sum(y * np.log(p + 1e-12) + (1 - y) * np.log(1 - p + 1e-12)) + 0.5 * l2 * np.sum(w[1:] ** 2)
        g = np.concatenate([[np.sum(p - y)], X.T @ (p - y) + l2 * w[1:]])
        return ll, g
    return minimize(f, np.zeros(X.shape[1] + 1), jac=True, method='L-BFGS-B').x
def pred(w, X, off=0.0): return 1 / (1 + np.exp(-(np.asarray(X) @ w[1:] + w[0] + off)))
tr = [r for r in S if r['key'] in train_keys]; te = [r for r in S if r['key'] in test_keys]
Xtr = [feats(r) for r in tr]; ytr = [r['y_round'] for r in tr]; Xte = [feats(r) for r in te]; yte = np.array([r['y_round'] for r in te])
w = fit(Xtr, ytr)
print('maps train %d test %d | samples train %d test %d' % (len(train_keys), len(test_keys), len(tr), len(te)))
print('coefficients (home-perspective logit):')
print('  intercept %+.3f' % w[0])
for n, c in zip(FEATS, w[1:]): print('  %-20s %+.3f' % (n, c))
p = pred(w, Xte)
def ll(p, y): return -np.mean(y * np.log(np.clip(p, 1e-6, 1)) + (1 - y) * np.log(np.clip(1 - p, 1e-6, 1)))
base_side = fit([[1.0 if r['homeT'] else -1.0] for r in tr], ytr, l2=0.0); pb = pred(base_side, [[1.0 if r['homeT'] else -1.0] for r in te])
print('TEST round logloss: model %.4f | side-only %.4f | coin 0.6931 ; Brier model %.4f side-only %.4f' % (ll(p, yte), ll(pb, yte), np.mean((p - yte) ** 2), np.mean((pb - yte) ** 2)))
print('T-side advantage (home on T -> logit) : %+.3f ; i.e. round win prob for T-side team at 5v5 start ~ %.3f' % (base_side[1], 1 / (1 + math.exp(-base_side[1]))))
# calibration by (planted, alive diff bucket) on test
import collections
cal = collections.defaultdict(list)
for r, pi, yi in zip(te, p, yte):
    s = 1 if r['homeT'] else -1
    # Tperspective
    pT = pi if s == 1 else 1 - pi; yT = yi if s == 1 else 1 - yi
    dT = (r['al_h'] - r['al_a']) * s
    cal[(r['planted'], max(-3, min(3, dT)))].append((pT, yT))
print('test calibration, T-side perspective: (planted, T alive minus CT alive) -> n, mean pred, actual')
for k in sorted(cal): 
    v = cal[k]
    if len(v) >= 30: print('  ', k, len(v), '%.3f %.3f' % (np.mean([a for a, _ in v]), np.mean([b for _, b in v])))
json.dump(dict(feats=FEATS, w=list(map(float, w)), train_maps=sorted(train_keys), test_maps=sorted(test_keys)), open(sys.argv[2], 'w'))
