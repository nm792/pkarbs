#!/usr/bin/env python3
"""Step 8b: model variants vs market on paired maps.  Variants: A fixed team strength z0 (anchored on first market mid); B/C Bayesian team strength
(prior sd 0.15 / 0.30 per-round logit, updated by completed rounds after the anchor); S score-only DP (no in-round state).
Saves rows (for the trade test) to rows.pkl.  Eval starts 90 s after the anchor."""
import sys, json, pickle, bisect, math, collections, numpy as np
from predict import *
D = pickle.load(open(sys.argv[1], 'rb')); S = D['samples']; M = D['maps']
mdl = load_model(sys.argv[2]); w = mdl['w']; test = set(mdl['test_maps']); train = set(mdl['train_maps'])
P = json.load(open(sys.argv[3]))['pairs']; B = pickle.load(open(sys.argv[4], 'rb'))['book']
T = {k: [x[0] for x in v] for k, v in B.items()}
def mid(tk, t, maxage=20):
    ts = T.get(tk)
    if not ts: return None
    i = bisect.bisect_right(ts, t) - 1
    if i < 0 or t - ts[i] > maxage: return None
    if B[tk][i][2] - B[tk][i][1] > 0.06: return None
    return (B[tk][i][1] + B[tk][i][2]) / 2
byk = collections.defaultdict(list)
for r in S: byk[r['key']].append(r)
ws = side_coef(w)
SIG = {'B': 0.15, 'C': 0.30, 'D': 0.60, 'E': 1.00}
ALL = []
for k in sorted(byk):
    if k not in P: continue
    m = M[k]
    if not m['complete']: continue
    L = sorted(byk[k], key=lambda r: r['t']); tk = P[k]['tok_home']
    anchor = None
    for r in L:
        pm = mid(tk, r['t'])
        if pm is not None and 0.08 <= pm <= 0.92: anchor = r; break
    if not anchor: continue
    z0 = solve_z0_row(anchor, m['o'], mid(tk, anchor['t']), w)
    for r in L:
        if r['t'] < anchor['t'] + 90: continue
        pm = mid(tk, r['t'])
        if pm is None: continue
        done = [(hT, y) for (tm, te, n, hT, y) in m['rounds'] if te < r['t'] and te > anchor['t']]
        row = dict(key=k, t=r['t'], mkt=pm, A=pmap_row(r, m['o'], z0, w), S=pmap_row(r, m['o'], z0, w, use_state=False), y=m['y_map'], z0=z0, tmr=r['tmr'], n=r['n'], r=r)
        for name, sg in SIG.items():
            post = posterior_z(done, z0, ws, sg)
            row[name] = pmap_row_post(r, m['o'], post, w)
        ALL.append(row)
pickle.dump(dict(rows=ALL, test=sorted(test), train=sorted(train)), open(sys.argv[5], 'wb'))
def rep(sel, label):
    R = [x for x in ALL if sel(x['key'])]
    if not R: return
    y = np.array([x['y'] for x in R])
    def ll(p): p = np.clip(p, 1e-4, 1 - 1e-4); return -np.mean(y * np.log(p) + (1 - y) * np.log(1 - p))
    def br(p): return np.mean((p - y) ** 2)
    print('%s: %d maps, %d points' % (label, len(set(x['key'] for x in R)), len(R)))
    for nm, key in (('market', 'mkt'), ('A fixed strength + state', 'A'), ('B Bayes sd.15 + state', 'B'), ('C Bayes sd.30 + state', 'C'), ('D Bayes sd.60 + state', 'D'), ('E Bayes sd1.0 + state', 'E'), ('S score-only', 'S')):
        p = np.array([x[key] for x in R]); print('   %-26s Brier %.4f  logloss %.4f' % (nm, br(p), ll(p)))
rep(lambda k: k in test, 'TEST half')
rep(lambda k: k in train, 'TRAIN half')
rep(lambda k: True, 'ALL paired maps')
