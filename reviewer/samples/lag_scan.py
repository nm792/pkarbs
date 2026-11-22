#!/usr/bin/env python3
"""EXPLORATORY cross-lag of Goalserve implied prob (home) vs Polymarket own-token trade price (last trade, forward filled, home token only).
corr over a 10 s grid of 30 s changes: ΔG(t) vs ΔP(t+s). Peak at s>0 = PM moves AFTER the feed; s<0 = PM moves BEFORE. Trade timestamps are 1 s resolution,
feed times are our receive times (one host); NOT a lead estimate: smoothed, overlapping windows, one match. Usage: lag_scan.py --slug S --sample F --eid E"""
import argparse, bisect, sys, statistics, json
sys.argv_backup = list(sys.argv)
import os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import chart_match as cm

ap = argparse.ArgumentParser(); ap.add_argument("--slug", required=True); ap.add_argument("--sample", required=True); ap.add_argument("--eid", required=True)
a = ap.parse_args()
ev, m = cm.market_for(a.slug)
tr = cm.trades_for(m["conditionId"])
fs = [x for x in cm.feed_series(a.sample, a.eid) if x[1] is not None]
home = fs[-1][3]
tt = sorted((t["timestamp"], t["price"]) for t in tr if cm.same(t["outcome"], home))
ft = [x[0] for x in fs]
t0, t1 = max(fs[0][0], tt[0][0]) + 60, min(fs[-1][0], tt[-1][0]) - 60
def G(t):
    i = bisect.bisect_right(ft, t) - 1
    return fs[i][1] if i >= 0 else None
tts = [x[0] for x in tt]
def P(t):
    i = bisect.bisect_right(tts, t) - 1
    return tt[i][1] if i >= 0 else None
grid = [t0 + 10 * k for k in range(int((t1 - t0) // 10))]
def corr(x, y):
    n = len(x)
    if n < 20: return None
    mx, my = sum(x) / n, sum(y) / n
    sx = sum((v - mx) ** 2 for v in x) ** .5; sy = sum((v - my) ** 2 for v in y) ** .5
    return sum((a_ - mx) * (b_ - my) for a_, b_ in zip(x, y)) / (sx * sy) if sx and sy else None
res = {}
for s in range(-120, 121, 10):
    X, Y = [], []
    for t in grid:
        g0, g1, p0, p1 = G(t - 30), G(t), P(t + s - 30), P(t + s)
        if None in (g0, g1, p0, p1): continue
        X.append(g1 - g0); Y.append(p1 - p0)
    c = corr(X, Y)
    if c is not None: res[s] = c
best = max(res, key=res.get)
print(json.dumps(dict(slug=a.slug, n_grid=len(grid), peak_lag_s=best, peak_corr=round(res[best], 3), corr_at_0=round(res.get(0, float('nan')), 3), corr_by_lag={k: round(v, 2) for k, v in res.items() if k % 30 == 0})))
