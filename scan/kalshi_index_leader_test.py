#!/usr/bin/env python3
"""Runs the rule locked in scan/LOCKED-kalshi-index-leader-rule-2026-11-11.md (one test, no variants)."""
import sys, os, random
from collections import defaultdict
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import volume_first_scan as v, gas_leader as g
random.seed(11); rng = np.random.default_rng(11)
SER = ["KXINXU", "KXNASDAQ100U", "KXDJIAH", "KXINXZ", "KXNASDAQ100Z"]
L = []
def P(s=""): print(s, flush=True); L.append(s)
def obs(m, s):
    r = g.candles(m, s)
    if not r: return None
    ask, bid, vol, ot, ct = r
    if len(ask) < 4 or np.isnan(ask[1]) or np.isnan(bid[1]) or ask[1] <= bid[1]: return None
    if ct - (ot + 3600) < 1800: return None
    mid = (ask[1] + bid[1]) / 2; side = "Y" if mid >= .5 else "N"
    cost = ask[1] if side == "Y" else 1 - bid[1]
    if not (0.55 <= cost <= 0.95): return None
    y = int(m["result"] == "yes"); win = (y == 1) == (side == "Y"); fee = 0.07 * cost * (1 - cost)
    return {"ev": m["event_ticker"], "cost": cost, "win": float(win), "fee": fee, "gap": win - cost - fee,
            "size": float(vol[1:3].sum()) * 0.5 * cost * 0.10, "ret": (win - cost - fee) / cost, "close": ct}
def summ(rows, days):
    gp = defaultdict(list)
    for r in rows: gp[r["ev"]].append(r["gap"])
    ks = list(gp); sm = np.array([sum(gp[k]) for k in ks]); ct = np.array([len(gp[k]) for k in ks])
    bs = rng.integers(0, len(ks), (2000, len(ks))); gm = sm[bs].sum(1) / ct[bs].sum(1)
    real = np.mean([r["gap"] for r in rows]); lo = float(np.percentile(gm, 2.5))
    sims = np.zeros(2000); cs = np.array([r["cost"] for r in rows]); fs = 0.07 * cs * (1 - cs)
    for i in range(2000):
        w = rng.random(len(rows)) < cs; sims[i] = np.mean(w - cs - fs)
    z = (real - sims.mean()) / (sims.std() or 1)
    perday = sum(r["size"] * r["ret"] for r in rows) / max(days, 1)
    return real, lo, z, perday
P("# Kalshi index early-leader, locked test\n| series | half | markets (events) | ask | win | gap net (95% lo) | placebo z | $/day |\n|---|---|---|---:|---:|---|---:|---:|")
verd = {}
for s in SER:
    ms = g.list_markets(s, hist_pages=6)
    if not ms: P(f"| {s} | no markets | | | | | | |"); continue
    random.shuffle(ms); ms = ms[:300]
    rows = [r for r in (obs(m, s) for m in ms) if r]
    if len(rows) < 20: P(f"| {s} | only {len(rows)} usable | | | | | | |"); continue
    cl = sorted(r["close"] for r in rows); mid = cl[len(cl) // 2]
    for nm, rs in (("train", [r for r in rows if r["close"] < mid]), ("TEST", [r for r in rows if r["close"] >= mid])):
        if len(rs) < 10: continue
        days = (max(r["close"] for r in rs) - min(r["close"] for r in rs)) / 86400
        real, lo, z, pd_ = summ(rs, days); ne = len({r["ev"] for r in rs})
        P(f"| {s} | {nm} | {len(rs)} ({ne}) | {np.mean([r['cost'] for r in rs])*100:.1f}c | {np.mean([r['win'] for r in rs])*100:.1f}% | {real*100:+.2f}c ({lo*100:+.2f}) | {z:+.1f} | ${pd_:.2f} over {days:.0f}d |")
        if nm == "TEST": verd[s] = "PASS" if (real > 0 and lo > 0 and z >= 2 and len(rs) >= 100 and ne >= 40) else f"FAIL/UNPROVEN (n={len(rs)}, ev={ne})"
P("\n" + "\n".join(f"{k}: {x}" for k, x in verd.items()))
open("scan/OUT-kalshi-index-leader-2026-11-11.md", "w").write("\n".join(L))
