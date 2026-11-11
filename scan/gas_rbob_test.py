#!/usr/bin/env python3
"""Runs scan/LOCKED-gas-rbob-rule-2026-11-11.md (RBOB = EIA/FRED NY Harbor conventional spot, same series as DGASNYH) (one test, no variants)."""
import sys, os, calendar, time
from collections import defaultdict
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import volume_first_scan as v, gas_leader as g
rng = np.random.default_rng(13)
import pandas as pd
SER = ["KXAAAGASD"] + [f"KXAAAGASD{s}" for s in "CA TX FL NY IL NJ WA NC OH PA GA VA".split()]
px = pd.read_excel("/tmp/eia.xls", sheet_name="Data 1", skiprows=2); px.columns = ["d", "p"]
px["d"] = pd.to_datetime(px["d"]).dt.strftime("%Y-%m-%d"); px = px.dropna().reset_index(drop=True)
dates = list(px["d"]); prices = list(px["p"])
def signal(day):  # latest print strictly before D-1 13:00Z: prints dated <= D-2 are public; use dates <= D-2
    d2 = time.strftime("%Y-%m-%d", time.gmtime(calendar.timegm(time.strptime(day, "%Y-%m-%d")) - 2 * 86400))
    idx = [i for i, d in enumerate(dates) if d <= d2]
    if len(idx) < 4: return None
    i = idx[-1]
    if dates[-1] < d2 and False: return None
    return prices[i] - prices[i - 3]
def run(ser, n_ev=70):
    ms = g.list_markets(ser, hist_pages=3); ev = defaultdict(list)
    for m in ms: ev[m["event_ticker"]].append(m)
    day = {e: time.strftime("%Y-%m-%d", time.gmtime(g.ts(l[0]["close_time"]) + 3600)) for e, l in ev.items()}
    byday = {d: e for e, d in day.items()}
    expv = {e: float(l[0]["expiration_value"]) for e, l in ev.items() if l[0].get("expiration_value")}
    pd_ = lambda d, k: time.strftime("%Y-%m-%d", time.gmtime(calendar.timegm(time.strptime(d, "%Y-%m-%d")) - 86400 * k))
    rows = []
    for d in sorted(x for x in byday if x <= "2026-11-04")[-n_ev:]:
        e = byday[d]; e1 = byday.get(pd_(d, 1))
        if e not in expv or e1 not in expv: continue
        sg = signal(d)
        if sg is None or abs(sg) < 0.01: continue
        prev = expv[e1]; up = sg > 0
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
            c = cy if up else cn; gp = gy if up else gn
            rows.append({"ev": e + ser, "st": ser, "win": wy if up else wn, "imp": mid if up else 1 - mid, "cost": c, "gap": gp,
                         "alt": gn if up else gy, "close": ct, "size": float(vol[1:3].sum()) * 0.5 * c * 0.10, "ret": gp / c})
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
P("# RBOB signal rule, locked test (EIA NY Harbor spot through 3 Nov)\n| series | strikes (events) | hit | implied | gap |\n|---|---:|---:|---:|---:|")
for s in SER:
    try: r = run(s)
    except Exception as e: P(f"| {s} | error {e} | | | |"); continue
    allr += r
    if r: P(f"| {s} | {len(r)} ({len({x['ev'] for x in r})}) | {np.mean([x['win'] for x in r])*100:.1f}% | {np.mean([x['imp'] for x in r])*100:.1f}% | {np.mean([x['gap'] for x in r])*100:+.1f}c |")
    open(OUT, "w").write("\n".join(L) + "\n")
if allr:
    cl = sorted(r["close"] for r in allr); mid = cl[len(cl) // 2]
    P(""); stats([r for r in allr if r["close"] < mid], "train"); stats([r for r in allr if r["close"] >= mid], "TEST"); stats(allr, "POOLED")
open(OUT, "w").write("\n".join(L) + "\n")
