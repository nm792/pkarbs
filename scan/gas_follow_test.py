#!/usr/bin/env python3
"""Runs scan/LOCKED-gas-follow-rule-2026-11-11.md (one test, no variants)."""
import sys, os, calendar, time
from collections import defaultdict
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import volume_first_scan as v, gas_leader as g
rng = np.random.default_rng(13)
STATES = "AK AL AR AZ CO CT DE HI IA ID KS KY LA MA MD ME MN MO MS MT ND NE NH NM NV OK OR RI SC SD TN UT VT WV WY".split()
OUT = "scan/OUT-gas-follow-test-2026-11-11.md"


def run(st, n_ev=30):
    ser = f"KXAAAGASD{st}"; ms = g.list_markets(ser, hist_pages=3)
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
            cy, cn = ask[1], 1 - bid[1]
            if not (0.05 < cy < 0.95 and 0.05 < cn < 0.95): continue
            y = int(m["result"] == "yes"); wy, wn = float(y == 1), float(y == 0)
            gy = wy - cy - 0.07 * cy * (1 - cy); gn = wn - cn - 0.07 * cn * (1 - cn)
            up = chg > 0
            c = cy if up else cn; gp = gy if up else gn
            rows.append({"ev": e, "st": st, "win": wy if up else wn, "imp": mid if up else 1 - mid, "cost": c,
                         "gap": gp, "alt": gn if up else gy, "close": ct,
                         "size": float(vol[1:3].sum()) * 0.5 * c * 0.10, "ret": gp / c})
    return rows


L = []
def P(s=""): print(s, flush=True); L.append(s)


def stats(rs, name):
    if len(rs) < 10: P(f"{name}: only {len(rs)} strikes"); return
    gp = defaultdict(list)
    for r in rs: gp[r["ev"]].append((r["gap"], r["alt"]))
    ks = list(gp)
    sm = np.array([sum(a for a, _ in gp[k]) for k in ks]); sa = np.array([sum(b for _, b in gp[k]) for k in ks])
    ct = np.array([len(gp[k]) for k in ks])
    bs = rng.integers(0, len(ks), (2000, len(ks))); gm = sm[bs].sum(1) / ct[bs].sum(1)
    fl = rng.random((2000, len(ks))) < 0.5
    sims = np.where(fl, sa, sm).sum(1) / ct.sum()
    real = sm.sum() / ct.sum(); z = (real - sims.mean()) / (sims.std() + 1e-9)
    lo, hi = np.percentile(gm, 2.5), np.percentile(gm, 97.5)
    hit, imp = np.mean([r["win"] for r in rs]), np.mean([r["imp"] for r in rs])
    days = max(1, (max(r["close"] for r in rs) - min(r["close"] for r in rs)) / 86400)
    pdy = sum(r["size"] * r["ret"] for r in rs) / days
    ok = real > 0 and lo > 0 and hit > imp and z >= 2 and len(rs) >= 100 and len(ks) >= 40
    P(f"{name}: {len(rs)} strikes, {len(ks)} events: hit {hit*100:.1f}% vs implied {imp*100:.1f}%, gap {real*100:+.2f}c "
      f"(95% CI {lo*100:+.2f}, {hi*100:+.2f}), placebo z {z:+.1f}, size/strike ${np.mean([r['size'] for r in rs]):,.0f}, "
      f"${pdy:,.0f}/day over {days:.0f}d -> {'PASS' if ok else 'FAIL/UNPROVEN'}")


allr = []
P("# Follow rule, locked test (fresh states only)\n| state | strikes (events) | hit | implied | gap |\n|---|---:|---:|---:|---:|")
for st in STATES:
    try: r = run(st)
    except Exception as e: P(f"| {st} | error {e} | | | |"); continue
    allr += r
    if r: P(f"| {st} | {len(r)} ({len({x['ev'] for x in r})}) | {np.mean([x['win'] for x in r])*100:.1f}% | {np.mean([x['imp'] for x in r])*100:.1f}% | {np.mean([x['gap'] for x in r])*100:+.1f}c |")
    open(OUT, "w").write("\n".join(L) + "\n")
if allr:
    cl = sorted(r["close"] for r in allr); mid = cl[len(cl) // 2]
    P(""); stats([r for r in allr if r["close"] < mid], "train"); stats([r for r in allr if r["close"] >= mid], "TEST"); stats(allr, "POOLED")
open(OUT, "w").write("\n".join(L) + "\n")
