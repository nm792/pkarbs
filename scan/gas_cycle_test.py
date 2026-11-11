#!/usr/bin/env python3
"""Runs the rule locked in scan/LOCKED-gas-cycle-rule-2026-11-11.md (one test, no variants)."""
import sys, os, calendar, time
from collections import defaultdict
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import volume_first_scan as v, gas_leader as g
rng = np.random.default_rng(13)
STATES = ["OH", "MI", "IN", "WI"]
def run(st):
    ser = f"KXAAAGASD{st}"
    ms = g.list_markets(ser, hist_pages=3)
    ev = defaultdict(list)
    for m in ms: ev[m["event_ticker"]].append(m)
    day = {e: time.strftime("%Y-%m-%d", time.gmtime(g.ts(l[0]["close_time"]) + 3600)) for e, l in ev.items()}
    byday = {d: e for e, d in day.items()}
    expv = {d: float(ev[e][0]["expiration_value"]) for d, e in byday.items() if ev[e][0].get("expiration_value")}
    pd_ = lambda d, k: time.strftime("%Y-%m-%d", time.gmtime(calendar.timegm(time.strptime(d, "%Y-%m-%d")) - 86400 * k))
    rows = []
    for d in sorted(byday):
        e = byday[d]
        if not all(pd_(d, k) in expv for k in (1, 2)): continue
        prev = expv[pd_(d, 1)]
        last = prev - expv[pd_(d, 2)]
        if last >= 0.05: continue                                   # D-1 itself was a jump
        jump = False
        for k in range(1, 11):
            a, b = pd_(d, k), pd_(d, k + 1)
            if a in expv and b in expv and expv[a] - expv[b] >= 0.05: jump = True
        if not jump: continue
        for m in ev[e]:
            s = float(m["floor_strike"])
            if s < prev or s - prev > 0.03: continue
            r = g.candles(m, ser)
            if not r: continue
            ask, bid, vol, ot, ct = r
            if len(ask) < 4 or np.isnan(ask[1]) or np.isnan(bid[1]) or ask[1] <= bid[1]: continue
            mid = (ask[1] + bid[1]) / 2
            if not (0.25 <= mid <= 0.75): continue
            cost = 1 - bid[1]
            if not (0.05 < cost < 0.95): continue
            y = int(m["result"] == "yes"); win = (y == 0); fee = 0.07 * cost * (1 - cost)
            rows.append({"st": st, "ev": e, "cost": cost, "imp": 1 - mid, "win": float(win), "gap": win - cost - fee,
                         "size": float(vol[1:3].sum()) * 0.5 * cost * 0.10, "ret": (win - cost - fee) / cost, "close": ct})
    return rows
allr = []; L = []
def P(s=""): print(s, flush=True); L.append(s)
P("# Price-cycle rule, locked test\n| state | strikes (events) | hit rate | market-implied | gap net of fee |\n|---|---:|---:|---:|---:|")
for st in STATES:
    r = run(st); allr += r
    if r: P(f"| {st} | {len(r)} ({len({x['ev'] for x in r})}) | {np.mean([x['win'] for x in r])*100:.1f}% | {np.mean([x['imp'] for x in r])*100:.1f}% | {np.mean([x['gap'] for x in r])*100:+.1f}c |")
    else: P(f"| {st} | 0 qualifying | | | |")
def stats(rows, label):
    if len(rows) < 10: P(f"{label}: {len(rows)} strikes, too few"); return None
    gp = defaultdict(list)
    for r in rows: gp[r["ev"]].append(r["gap"])
    ks = list(gp); sm = np.array([sum(gp[k]) for k in ks]); ct = np.array([len(gp[k]) for k in ks])
    bs = rng.integers(0, len(ks), (2000, len(ks))); gm = sm[bs].sum(1) / ct[bs].sum(1)
    evs = sorted({r["ev"] for r in rows}); idx = {e: [r for r in rows if r["ev"] == e] for e in evs}
    sims = np.zeros(2000)
    for i in range(2000):
        tot = 0.0
        for e in evs:
            fl = rng.random() < 0.5
            for r in idx[e]:
                if not fl: tot += r["gap"]
                else:
                    c2 = 1 - r["imp"] + (r["cost"] - r["imp"]); tot += (1 - r["win"]) - c2 - 0.07 * c2 * (1 - c2)
        sims[i] = tot / len(rows)
    real = np.mean([r["gap"] for r in rows]); z = (real - sims.mean()) / (sims.std() + 1e-9)
    lo, hi = np.percentile(gm, 2.5), np.percentile(gm, 97.5)
    hit, imp = np.mean([r["win"] for r in rows]), np.mean([r["imp"] for r in rows])
    days = max(1, (max(r["close"] for r in rows) - min(r["close"] for r in rows)) / 86400)
    perday = sum(r["size"] * r["ret"] for r in rows) / days
    P(f"{label}: {len(rows)} strikes, {len(evs)} events: hit {hit*100:.1f}% vs implied {imp*100:.1f}%, gap {real*100:+.2f}c (95% CI {lo*100:+.2f}, {hi*100:+.2f}), "
      f"placebo z {z:+.1f}, size/strike ${np.mean([r['size'] for r in rows]):,.0f}, ${perday:,.0f}/day over {days:.0f} days")
    return real > 0 and lo > 0 and hit > imp and z >= 2.0 and len(rows) >= 100 and len(evs) >= 40
P("")
if allr:
    allr.sort(key=lambda r: r["close"]); mt = np.median([r["close"] for r in allr])
    stats([r for r in allr if r["close"] <= mt], "train")
    ok = stats([r for r in allr if r["close"] > mt], "TEST")
    P(f"VERDICT: {'PASS' if ok else 'FAIL / UNPROVEN'}")
open("scan/OUT-gas-cycle-test-2026-11-11.md", "w").write("\n".join(L) + "\n")
