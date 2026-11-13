#!/usr/bin/env python3
"""Step 8: model vs market price on held-out (later-half) paired maps: Brier/log-loss of P(home wins map) at every 5-s sample, plus score-only DP.
z0 (team strength) is anchored on the first market mid seen for the map (state-adjusted), evaluation starts 90 s after the anchor."""
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
    return (B[tk][i][1] + B[tk][i][2]) / 2
byk = collections.defaultdict(list)
for r in S: byk[r['key']].append(r)
def evaluate(keys, label):
    rows = []
    for k in keys:
        if k not in P or k not in byk: continue
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
            pM = pmap_row(r, m['o'], z0, w); pS = pmap_row(r, m['o'], z0, w, use_state=False)
            rows.append((k, r['t'], pm, pM, pS, m['y_map']))
    if not rows: print(label, 'no rows'); return rows
    a = np.array([x[2:] for x in rows]); y = a[:, 3]
    def ll(p): p = np.clip(p, 1e-4, 1 - 1e-4); return -np.mean(y * np.log(p) + (1 - y) * np.log(1 - p))
    def br(p): return np.mean((p - y) ** 2)
    print('%s: %d maps, %d sample points' % (label, len(set(x[0] for x in rows)), len(rows)))
    print('   Brier    market %.4f | model(state) %.4f | score-only DP %.4f | coin 0.2500' % (br(a[:, 0]), br(a[:, 1]), br(a[:, 2])))
    print('   logloss  market %.4f | model(state) %.4f | score-only DP %.4f' % (ll(a[:, 0]), ll(a[:, 1]), ll(a[:, 2])))
    d = a[:, 1] - a[:, 0]
    print('   model minus market: mean %+.3f, sd %.3f, |gap|>=5c in %.0f%% of points, >=10c in %.0f%%' % (d.mean(), d.std(), 100 * np.mean(np.abs(d) >= .05), 100 * np.mean(np.abs(d) >= .10)))
    # when model-market gap >=5c: who is right? realized y vs market and model
    for th in (0.05, 0.10):
        sel = d >= th
        if sel.sum() > 20: print('   gap model>market by >=%.0fc: n=%d, mean market %.3f, mean model %.3f, actual win rate %.3f' % (th * 100, sel.sum(), a[sel, 0].mean(), a[sel, 1].mean(), y[sel].mean()))
        sel = d <= -th
        if sel.sum() > 20: print('   gap model<market by >=%.0fc: n=%d, mean market %.3f, mean model %.3f, actual win rate %.3f' % (th * 100, sel.sum(), a[sel, 0].mean(), a[sel, 1].mean(), y[sel].mean()))
    return rows
evaluate(sorted(test), 'TEST half (later 80 maps)')
evaluate(sorted(train), 'TRAIN half (in-sample for the round model)')
