#!/usr/bin/env python3
"""Step 13: cross-validated (4 folds by MATCH, every map is held out exactly once) comparison of feature sets for the in-round model, then map-level Brier vs market and the
locked fill test on ALL paired maps' out-of-fold predictions.  Feature sets: BASE (alive, hp, bomb, clock, side, cash, adr, kill diff) ; +PLAYER (team mean of players' ADR from OTHER maps,
leave-one-map-out) ; +SERIES (maps already won in the match, map number, from earlier maps in our data) ; +ELO (bo3 whole-history Elo diff) ; ALL.
Round-level held-out log-loss and map-level Brier vs market are reported for each; the fill test is run for BASE and ALL."""
import sys, json, pickle, math, bisect, collections, random, numpy as np
sys.argv_backup = sys.argv
from scipy.optimize import minimize
from predict import *
import predict as PR
D = pickle.load(open(sys.argv[1], 'rb')); S = D['samples']; M = D['maps']
P = json.load(open(sys.argv[2]))['pairs']; B = pickle.load(open(sys.argv[3], 'rb'))['book']; TR = json.load(open(sys.argv[4]))
E = json.load(open(sys.argv[5])); PL = json.load(open(sys.argv[6]))['plines']; RD = json.load(open(sys.argv[7]))
T = {k: [x[0] for x in v] for k, v in B.items()}
def mid(tk, t, maxage=20):
    ts = T.get(tk)
    if not ts: return None
    i = bisect.bisect_right(ts, t) - 1
    if i < 0 or t - ts[i] > maxage: return None
    b = B[tk][i]
    if b[2] - b[1] > 0.06: return None
    return (b[1] + b[2]) / 2
# --- extra per-map features
# player prior rating: mean ADR of the five players over OTHER maps (leave-one-map-out), shrunk to 75
padr = collections.defaultdict(list)
for k, v in PL.items():
    for side in ('home', 'away'):
        for name, kl, dt_, adr in v[side]: padr[name].append((k, adr))
def prior_rating(key, side):
    vals = []
    for name, kl, dt_, adr in PL[key][side]:
        o = [a for kk, a in padr[name] if kk != key]
        vals.append((sum(o) + 75 * 3) / (len(o) + 3))
    return sum(vals) / len(vals) if vals else 75.0
bymatch = collections.defaultdict(list)
for k in M: bymatch[k.split('|')[0]].append(k)
box = {k: RD[k]['meta']['box'] for k in RD}
def series_diff(k):
    mt = k.split('|')[0]; b = box.get(k)
    d = 0
    for kk in bymatch[mt]:
        if kk != k and box.get(kk) is not None and b is not None and box[kk] < b and M[kk]['complete']: d += 1 if M[kk]['y_map'] else -1
    return d, (b or 1)
EX = {}
for k in M:
    if k in PL:
        sd, bn = series_diff(k)
        e = E.get(k)
        EX[k] = dict(rate=(prior_rating(k, 'home') - prior_rating(k, 'away')) / 20.0, sdiff=sd, bn=bn, elo=((e['elo_h'] - e['elo_a']) / 400.0) if e else 0.0)
BASE = ['al_diff', 'al_few', 'hp', 'planted_s', 'planted_s_t', 'clock', 'side_s', 'al_planted_s', 'cash', 'adr', 'kdiff']
def base_feats(r):
    s = 1.0 if r['homeT'] else -1.0; d = r['al_h'] - r['al_a']; tot = r['al_h'] + r['al_a']; pl = r['planted']
    return [d, d * (10 - tot) / 10.0, (r['hp_h'] - r['hp_a']) / 100.0, pl * s, pl * s * min(r['tplant'], 45) / 40.0, (1 - pl) * (-s) * max(r['el'], 0) / 100.0, s, d * pl * s,
            r['mdiff'] / 10000.0, (r['adr_h'] - r['adr_a']) / 50.0, (r['k_h'] - r['k_a']) / max(r['n'], 3) / 3.0]
def extra(r, sets):
    e = EX.get(r['key']); f = []
    if 'player' in sets: f.append(e['rate'] if e else 0.0)
    if 'series' in sets: f += [(e['sdiff'] if e else 0) * 1.0, ((e['sdiff'] if e else 0) * (1 if r['homeT'] else 1))]
    if 'elo' in sets: f.append(e['elo'] if e else 0.0)
    return f
SETS = {'BASE': (), '+PLAYER': ('player',), '+SERIES': ('series',), '+ELO': ('elo',), 'ALL': ('player', 'series', 'elo')}
def X_of(rows, sets): return np.array([base_feats(r) + extra(r, sets) for r in rows])
def fit(X, y, l2=1.0):
    def f(w):
        z = X @ w[1:] + w[0]; p = 1 / (1 + np.exp(-z))
        return -np.sum(y * np.log(p + 1e-12) + (1 - y) * np.log(1 - p + 1e-12)) + 0.5 * l2 * np.sum(w[1:] ** 2), np.concatenate([[np.sum(p - y)], X.T @ (p - y) + l2 * w[1:]])
    return minimize(f, np.zeros(X.shape[1] + 1), jac=True, method='L-BFGS-B').x
matches = sorted(bymatch); random.Random(11).shuffle(matches)
fold = {m: i % 4 for i, m in enumerate(matches)}
byk = collections.defaultdict(list)
for r in S: byk[r['key']].append(r)
ws = None
OUT = {}
for name, sets in SETS.items():
    rows_out = []; rll = []; 
    for f in range(4):
        tr = [r for r in S if fold[r['key'].split('|')[0]] != f]; te = [r for r in S if fold[r['key'].split('|')[0]] == f]
        w = fit(X_of(tr, sets), np.array([r['y_round'] for r in tr], float))
        Xte = X_of(te, sets); p = 1 / (1 + np.exp(-(Xte @ w[1:] + w[0]))); yy = np.array([r['y_round'] for r in te])
        rll.append(-np.sum(yy * np.log(np.clip(p, 1e-6, 1)) + (1 - yy) * np.log(np.clip(1 - p, 1e-6, 1))))
        # map-level predictions for paired maps in this fold
        wl = list(w); n_base = len(BASE)
        def g(r): return float(np.array(base_feats(r) + extra(r, sets)) @ w[1:])
        side_c = w[1 + 6]
        for k in sorted(byk):
            if fold[k.split('|')[0]] != f or k not in P or not M[k]['complete']: continue
            m = M[k]; L = sorted(byk[k], key=lambda r: r['t']); tk = P[k]['tok_home']; anchor = None
            for r in L:
                pm = mid(tk, r['t'])
                if pm is not None and 0.08 <= pm <= 0.92: anchor = r; break
            if not anchor: continue
            def pm_row(r, z0, state=True):
                V = dp_for(m['o'], round(z0 * 1000), round(side_c, 4))
                if not state: return V(r['h'], r['a'])
                pr = sig(z0 + g(r)); return pr * V(r['h'] + 1, r['a']) + (1 - pr) * V(r['h'], r['a'] + 1)
            lo, hi = -3.0, 3.0; target = mid(tk, anchor['t'])
            for _ in range(40):
                z = (lo + hi) / 2
                if pm_row(anchor, z) < target: lo = z
                else: hi = z
            z0 = (lo + hi) / 2
            for r in L:
                if r['t'] < anchor['t'] + 90: continue
                pm = mid(tk, r['t'])
                if pm is None: continue
                rows_out.append(dict(key=k, t=r['t'], mkt=pm, A=pm_row(r, z0), S=pm_row(r, z0, False), y=m['y_map'], tmr=r['tmr']))
    OUT[name] = rows_out
    y = np.array([x['y'] for x in rows_out]); br = lambda a: np.mean((np.array(a) - y) ** 2)
    print('%-8s round logloss (4-fold CV, all maps) %.4f | map Brier: market %.4f model %.4f score-only %.4f | %d maps %d points' % (name, sum(rll) / len(S), br([x['mkt'] for x in rows_out]), br([x['A'] for x in rows_out]), br([x['S'] for x in rows_out]), len(set(x['key'] for x in rows_out)), len(rows_out)))
pickle.dump(OUT, open(sys.argv[8], 'wb'))
