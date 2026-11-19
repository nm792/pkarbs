"""Amendment 1 of LOCKED-RULE-open-contracts-2026-11-19.md: sensitivity and descriptive. usage: analyze_oc2.py RUNDIR"""
import sys, json, math, collections, numpy as np
from oclib import *
import oclib
R = sys.argv[1]
src = open(__file__.replace("analyze_oc2.py", "analyze_oc.py")).read().split("def ask_fn_factory")[0]   # same rows / split / s as the locked run
sys.argv = [sys.argv[0], R]; exec(src)
def af(W):
    def f(r, kk):
        t0 = r["T"] - kk * 60; tr = trd[r["slug"]]; return dict(up=window_ask(tr, r["up_token"], t0, W), dn=window_ask(tr, r["dn_token"], t0, W))
    return f
print("=== 1. SENSITIVITY: fill window 600 s, thr 0.03 (not a verdict)")
for label, rs in (("TEST", test), ("all", rows)):
    for k in KS:
        tr, ex = evaluate(rs, S, k, af(600), THR)
        if not tr: print(label, k, "n=0", dict(ex)); continue
        byd = collections.defaultdict(list)
        for t in tr: byd[t["date"]].append(t["pnl"])
        lo, hi = boot_mean(byd); ndays = len({r["date"] for r in rs}); usd = collections.defaultdict(float)
        for t in tr: usd[t["date"]] += SLICE * t["shares"] * t["pnl"]
        m_d, lo_d, hi_d = boot_perday(usd, ndays)
        trf, _ = evaluate(rs, S, k, af(600), THR, flip=True)
        print(f"{label:5s} k={k} n={len(tr)} dates={len(byd)} hit={np.mean([t['win'] for t in tr]):.2f} ask={np.mean([t['ask'] for t in tr]):.2f} edge={np.mean([t['edge'] for t in tr]):+.3f} pnl/sh={np.mean([t['pnl'] for t in tr]):+.3f} CI=({lo:+.3f},{hi:+.3f}) $/day@10% {m_d:+.2f} CI({lo_d:+.2f},{hi_d:+.2f}) flip n={len(trf)} pnl={np.mean([t['pnl'] for t in trf]) if trf else None} excl={dict(ex)}")
print("=== 2. DESCRIPTIVE: model vs last Up-token trade (<= T-k, within 60 min before)")
for label, rs in (("TEST", test), ("all", rows)):
    for k in KS:
        a = []
        for r in rs:
            x = r["x"].get(k)
            if x is None: continue
            t0 = r["T"] - k * 60; ut = [t for t in trd[r["slug"]] if t["token_id"] == r["up_token"] and t0 - 3600 <= t["timestamp"] <= t0]
            if not ut: continue
            last = max(ut, key=lambda t: t["timestamp"]); a.append((p_up(x, S[r["prod"]]), last["price"], 1.0 if r["up"] else 0.0))
        if not a: print(label, k, "no rows"); continue
        a = np.array(a); print(f"{label:5s} k={k} rows={len(a)} Brier model={np.mean((a[:,0]-a[:,2])**2):.4f} market(last Up trade)={np.mean((a[:,1]-a[:,2])**2):.4f} naive50={np.mean((0.5-a[:,2])**2):.4f} mean(model-market)={np.mean(a[:,0]-a[:,1]):+.3f} mean|model-market|={np.mean(np.abs(a[:,0]-a[:,1])):.3f}")
print("=== 3. MODEL-FREE SIZE: USD traded (all sides, both tokens, both products) in the 60 min before T, per trading day")
byday = collections.defaultdict(float)
for r in rows: byday[r["date"]] += sum(t["price"] * t["size"] for t in trd[r["slug"]] if r["T"] - 3600 <= t["timestamp"] <= r["T"])
for label, ds in (("TEST", [d for d in byday if d >= cut]), ("all", list(byday))):
    v = np.array([byday[d] for d in ds]); print(f"{label:5s} days={len(v)} mean ${v.mean():.1f} median ${np.median(v):.1f} max ${v.max():.0f} share of days > $200: {np.mean(v > 200):.2f}")
print("=== 4. ex-dividend rows (Yahoo vs Polymarket disagreement):", [(r["slug"], r["up"], r["yahoo_up"]) for r in rows if r["up"] != r["yahoo_up"]])
