#!/usr/bin/env python3
"""Runs the rule locked in scan/LOCKED-gas-reverse-rule-2026-11-11.md (one test, no variants)."""
import sys, os, re, calendar, time
from collections import defaultdict
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import volume_first_scan as v, gas_leader as g
rng = np.random.default_rng(9)
STATES = ["IL", "NJ", "WA", "NC", "OH", "PA", "GA", "VA"]
def run(st, n_ev=30):
    ser = f"KXAAAGASD{st}"
    ms = g.list_markets(ser, hist_pages=3)
    ev = defaultdict(list)
    for m in ms: ev[m["event_ticker"]].append(m)
    day = {e: time.strftime("%Y-%m-%d", time.gmtime(g.ts(l[0]["close_time"]) + 3600)) for e, l in ev.items()}
    byday = {d: e for e, d in day.items()}
    expv = {e: float(l[0]["expiration_value"]) for e, l in ev.items() if l[0].get("expiration_value")}
    pd_ = lambda d, k: time.strftime("%Y-%m-%d", time.gmtime(calendar.timegm(time.strptime(d, "%Y-%m-%d")) - 86400 * k))
    rows = []
    for d in sorted(byday)[-n_ev:]:
        e = byday[d]; e1, e2 = byday.get(pd_(d, 1)), byday.get(pd_(d, 2))
        if e not in expv or e1 not in expv or e2 not in expv: continue
        prev, chg = expv[e1], expv[e1] - expv[e2]
        if abs(chg) < 0.0005: continue
        for m in ev[e]:
            if abs(float(m["floor_strike"]) - prev) > 0.03: continue
            r = g.candles(m, ser)
            if not r: continue
            ask, bid, vol, ot, ct = r
            if len(ask) < 4 or np.isnan(ask[1]) or np.isnan(bid[1]) or ask[1] <= bid[1]: continue
            mid = (ask[1] + bid[1]) / 2
            if not (0.25 <= mid <= 0.75): continue
            side = "N" if chg > 0 else "Y"                       # AGAINST the last change
            cost = ask[1] if side == "Y" else 1 - bid[1]
            if not (0.05 < cost < 0.95): continue
            y = int(m["result"] == "yes"); win = (y == 1) == (side == "Y"); fee = 0.07 * cost * (1 - cost)
            rows.append({"st": st, "ev": e, "cost": cost, "imp": mid if side == "Y" else 1 - mid, "win": float(win), "gap": win - cost - fee,
                         "size": float(vol[1:3].sum()) * 0.5 * cost * 0.10, "ret": (win - cost - fee) / cost, "close": ct})
    return rows
allr = []; L = []
def P(s=""): print(s, flush=True); L.append(s)
P("# Reverse rule, locked test (fresh states only)\n| state | strikes (events) | hit rate | market-implied | gap net of fee |\n|---|---:|---:|---:|---:|")
for st in STATES:
    r = run(st); allr += r
    if r: P(f"| {st} | {len(r)} ({len({x['ev'] for x in r})}) | {np.mean([x['win'] for x in r])*100:.1f}% | {np.mean([x['imp'] for x in r])*100:.1f}% | {np.mean([x['gap'] for x in r])*100:+.1f}c |")
if len(allr) >= 20:
    gp = defaultdict(list)
    for r in allr: gp[r["ev"]].append(r["gap"])
    ks = list(gp); sm = np.array([sum(gp[k]) for k in ks]); ct = np.array([len(gp[k]) for k in ks])
    bs = rng.integers(0, len(ks), (2000, len(ks))); gm = sm[bs].sum(1) / ct[bs].sum(1)
    evs = sorted({r["ev"] for r in allr}); idx = {e: [r for r in allr if r["ev"] == e] for e in evs}
    sims = np.zeros(2000)
    for i in range(2000):
        tot = 0.0
        for e in evs:
            fl = rng.random() < 0.5
            for r in idx[e]:
                if not fl: tot += r["gap"]
                else:
                    c2 = 1 - r["imp"] + (r["cost"] - r["imp"]); tot += (1 - r["win"]) - c2 - 0.07 * c2 * (1 - c2)
        sims[i] = tot / len(allr)
    real = np.mean([r["gap"] for r in allr]); z = (real - sims.mean()) / (sims.std() + 1e-9)
    lo, hi = np.percentile(gm, 2.5), np.percentile(gm, 97.5)
    hit, imp = np.mean([r["win"] for r in allr]), np.mean([r["imp"] for r in allr])
    days = max(1, (max(r["close"] for r in allr) - min(r["close"] for r in allr)) / 86400)
    perday = sum(r["size"] * r["ret"] for r in allr) / days
    ok = real > 0 and lo > 0 and hit > imp and z >= 2.0 and len(allr) >= 100 and len(evs) >= 40
    P(f"\nPOOLED: {len(allr)} strikes, {len(evs)} events: hit {hit*100:.1f}% vs implied {imp*100:.1f}%, gap {real*100:+.2f}c (95% CI {lo*100:+.2f}, {hi*100:+.2f}), placebo z {z:+.1f}, "
      f"size/strike ${np.mean([r['size'] for r in allr]):,.0f}, ${perday:,.0f}/day over {days:.0f} days. VERDICT: {'PASS' if ok else 'FAIL / unproven'}")
open("scan/OUT-gas-reverse-test-2026-11-11.md", "w").write("\n".join(L) + "\n")
