#!/usr/bin/env python3
"""Can-fail tests for ocbooks_depth.summarize. Run from this directory without -I."""
import datetime
from ocbooks_depth import summarize, slug_date, open_ts

fails = []
def check(name, cond):
    print(("PASS " if cond else "FAIL ") + name)
    if not cond: fails.append(name)

d = datetime.date(2026, 11, 20)
T = open_ts(d)
slug = "spx-opens-up-or-down-on-november-20-2026"
check("slug date parse", slug_date(slug) == d)
def row(dt, side, asks, bids=(), err=None):
    r = dict(t=T + dt, slug=slug, side=side, asks=[list(x) for x in asks], bids=[list(x) for x in bids])
    if err: r["err"] = err
    return r
# Up token: asks listed DESCENDING (as the clob does); best ask is the LAST level
rows = [row(-1800, "Up", [(0.999, 500), (0.62, 50), (0.60, 100)], [(0.01, 5), (0.58, 30)]),
        row(-1790, "Up", [(0.70, 10)]),                       # 10 s later but farther from T-30 than the first row -> must not be picked
        row(-3600, "Up", [(0.55, 40)]),
        row(-600, "Up", [(0.65, 20)]),
        row(-1800, "Down", [(0.30, 10)]),
        row(-1800, "Down", [(0.20, 10)], err="boom")]
rec = summarize(rows)
g = {(r["side"], r["k"]): r for r in rec}
check("Up T-30 nearest row used (best ask 0.60, depth 0.60*100+0.62*50 = 91)", not g[("Up", 30)]["missing"] and g[("Up", 30)]["best_ask"] == 0.60 and abs(g[("Up", 30)]["depth_usd"] - 91.0) < 1e-9)
check("Up T-30 best bid is the highest bid 0.58", g[("Up", 30)]["best_bid"] == 0.58)
check("Up T-60 and T-10 rows found", g[("Up", 60)]["best_ask"] == 0.55 and g[("Up", 10)]["best_ask"] == 0.65)
check("error rows are ignored (Down T-30 uses the good row, ask 0.30)", g[("Down", 30)]["best_ask"] == 0.30)
check("Down has no row at T-60 / T-10 -> MISSING, never filled in", g[("Down", 60)]["missing"] and g[("Down", 10)]["missing"])
check("rows farther than 20 s from the checkpoint are not used", summarize([row(-1800 + 25, "Up", [(0.5, 10)])])[1]["missing"])
check("0.97 ask is not tradable (dead bucket)", not summarize([row(-1800, "Up", [(0.97, 10)])])[1]["tradable"])
print("ALL PASS" if not fails else "FAILED: %s" % fails)
raise SystemExit(1 if fails else 0)
