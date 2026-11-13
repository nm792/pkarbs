#!/usr/bin/env python3
"""Cheap test (Nick 11 Nov 05:46Z): near-strike gas strikes (YES mid 25-75c at hour 1 after open). One signal: sign of AAA's last daily change
(prev day minus the day before). Signal says price keeps moving in the same direction: buy YES ('above') if it rose, NO if it fell.
Compare hit rate with the market-implied rate, gap after fee at the ask, held-out half, sign-flip placebo. RBOB not used (host blocked)."""
import sys, os, re, calendar, time
from collections import defaultdict
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import volume_first_scan as v, gas_leader as g
rng = np.random.default_rng(3)
SERIES = [("national daily", "KXAAAGASD", None)] + [(f"state {st}", f"KXAAAGASD{st}", 40) for st in ("CA", "TX", "FL", "NY")]
L = []
def P(s=""): print(s, flush=True); L.append(s)

def run(name, ser, max_ev):
    ms = g.list_markets(ser)
    ev = defaultdict(list)
    for m in ms: ev[m["event_ticker"]].append(m)
    day = {e: time.strftime("%Y-%m-%d", time.gmtime(g.ts(l[0]["close_time"]) + 3600)) for e, l in ev.items()}
    byday = {d: e for e, d in day.items()}
    expv = {e: float(l[0]["expiration_value"]) for e, l in ev.items() if l[0].get("expiration_value")}
    def prevday(d, k): return time.strftime("%Y-%m-%d", time.gmtime(calendar.timegm(time.strptime(d, "%Y-%m-%d")) - 86400 * k))
    days = sorted(byday)
    if max_ev: days = days[-max_ev:]
    rows = []
    for d in days:
        e = byday[d]; e1, e2 = byday.get(prevday(d, 1)), byday.get(prevday(d, 2))
        if e not in expv or e1 not in expv or e2 not in expv: continue
        prev, prev2, act = expv[e1], expv[e2], expv[e]
        chg = prev - prev2
        if abs(chg) < 0.0005: continue
        for m in ev[e]:
            if abs(float(m["floor_strike"]) - prev) > 0.03: continue
            r = g.candles(m, ser)
            if not r: continue
            ask, bid, vol, ot, ct = r
            if len(ask) < 4 or np.isnan(ask[1]) or np.isnan(bid[1]) or ask[1] <= bid[1]: continue
            mid = (ask[1] + bid[1]) / 2
            if not (0.25 <= mid <= 0.75): continue
            y = int(m["result"] == "yes"); side = "Y" if chg > 0 else "N"
            cost = ask[1] if side == "Y" else 1 - bid[1]
            if not (0.05 < cost < 0.95): continue
            win = (y == 1) == (side == "Y")
            fee = 0.07 * cost * (1 - cost)
            rows.append({"ev": e, "d": d, "close": ct, "cost": cost, "imp": mid if side == "Y" else 1 - mid, "win": float(win), "gap": win - cost - fee,
                         "ret": (win - cost - fee) / cost, "size": float(vol[1:3].sum()) * 0.5 * cost * 0.10, "y": y, "sg": 1 if chg > 0 else -1, "fee": fee})
    return rows

P("# Cheap gas signal test: does AAA's last change predict near-strike outcomes better than the market?")
P("Near-strike = YES mid 25-75c at hour 1 after open, strikes within 3c of the prior-day AAA value. Signal = direction of AAA's last daily change (momentum). "
  "Gap = win rate - ask - fee. Placebo = random signal direction per event (2000 draws). Size = 10% of $ traded in the 2h after hour 1 (x0.5 taker-buy).\n")
P("| series | half | strikes (events) | hit rate | market-implied | gap net of fee (95% CI) | net/$ | placebo z | size/strike | $/day | days |")
P("|---|---|---:|---:|---:|---|---:|---:|---:|---:|---:|")
for name, ser, mx in SERIES:
    rows = run(name, ser, mx)
    if len(rows) < 30: P(f"| {name} | all | <30 obs | | | | | | | | |"); continue
    rows.sort(key=lambda r: r["close"]); mt = np.median([r["close"] for r in rows])
    for half, sel in (("train", lambda r: r["close"] <= mt), ("TEST", lambda r: r["close"] > mt)):
        s = [r for r in rows if sel(r)]
        if len(s) < 20: continue
        gp = defaultdict(list)
        for r in s: gp[r["ev"]].append(r["gap"])
        ks = list(gp); sm = np.array([sum(gp[k]) for k in ks]); ct = np.array([len(gp[k]) for k in ks])
        bs = rng.integers(0, len(ks), (1000, len(ks))); gm = sm[bs].sum(1) / ct[bs].sum(1)
        # placebo: flip signal per event at random -> recompute gap using the opposite side when flipped
        evs = sorted({r["ev"] for r in s}); idx = {e: [r for r in s if r["ev"] == e] for e in evs}
        def gap_for(r, flip):
            # recompute under chosen side: signal side Y if sg>0
            sidey = (r["sg"] > 0) != flip
            # ask/bid unknown after flip: approximate cost of the other side as 1 - (cost of signal side) + 0 (mid-based) -> use implied
            return None
        # exact placebo using stored mid: other side cost ~ 1 - imp + (cost - imp) spread symmetric
        sims = np.zeros(2000)
        for i in range(2000):
            tot = 0.0; n = 0
            for e in evs:
                fl = rng.random() < 0.5
                for r in idx[e]:
                    if not fl: tot += r["gap"]
                    else:
                        c2 = 1 - r["imp"] + (r["cost"] - r["imp"])   # other side: same half-spread
                        w2 = 1 - r["win"]; f2 = 0.07 * c2 * (1 - c2)
                        tot += w2 - c2 - f2
                    n += 1
            sims[i] = tot / n
        real = np.mean([r["gap"] for r in s]); z = (real - sims.mean()) / (sims.std() + 1e-9)
        days = max(1, (max(r["close"] for r in s) - min(r["close"] for r in s)) / 86400)
        perday = sum(r["size"] * r["ret"] for r in s) / days
        P(f"| {name} | {half} | {len(s)} ({len(ks)}) | {np.mean([r['win'] for r in s])*100:.1f}% | {np.mean([r['imp'] for r in s])*100:.1f}% | "
          f"{real*100:+.2f}c ({np.percentile(gm,2.5)*100:+.2f}, {np.percentile(gm,97.5)*100:+.2f}) | {np.mean([r['ret'] for r in s])*100:+.1f}% | {z:+.1f} | "
          f"${np.mean([r['size'] for r in s]):,.0f} | ${perday:,.0f} | {days:.0f} |")
open("scan/OUT-gas-signal-cheap-2026-11-11.md", "w").write("\n".join(L) + "\n")
