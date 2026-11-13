#!/usr/bin/env python3
"""Typical daily AAA move from Kalshi settlement values (national + every state with data)."""
import sys, os, re, time, calendar
from collections import defaultdict
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import volume_first_scan as v, gas_leader as g
sl = (v.get(v.KAL + "/series", {"limit": 5000}, sleep=0.4) or {}).get("series", [])
ticks = sorted(s["ticker"] for s in sl if re.fullmatch(r"KXAAAGASD([A-Z]{2})?", s["ticker"]))
rows = []
for t in ticks:
    ms = g.list_markets(t, hist_pages=3)
    ev = {}
    for m in ms:
        if m.get("expiration_value"):
            d = time.strftime("%Y-%m-%d", time.gmtime(g.ts(m["close_time"]) + 3600)); ev[d] = float(m["expiration_value"])
    ds = sorted(ev); mv = []
    for a, b in zip(ds, ds[1:]):
        if calendar.timegm(time.strptime(b, "%Y-%m-%d")) - calendar.timegm(time.strptime(a, "%Y-%m-%d")) == 86400:
            mv.append(abs(ev[b] - ev[a]) * 100)
    if len(mv) < 20: continue
    mv = np.array(mv)
    rows.append((t.replace("KXAAAGASD", "") or "NATIONAL", len(mv), float(np.median(mv)), float(np.percentile(mv, 90)), float((mv < 0.5).mean())))
L = ["# Daily AAA move (absolute, cents), Kalshi settlement values, consecutive days only",
     "| series | days | median | 90th pct | share under 0.5c |", "|---|---:|---:|---:|---:|"]
for r in sorted(rows, key=lambda r: (r[0] != "NATIONAL", r[2])):
    L.append(f"| {r[0]} | {r[1]} | {r[2]:.2f}c | {r[3]:.2f}c | {r[4]*100:.0f}% |")
allm = [r for r in rows if r[0] != "NATIONAL"]
L.append(f"\nStates: median of state medians {np.median([r[2] for r in allm]):.2f}c, median 90th pct {np.median([r[3] for r in allm]):.2f}c, "
         f"median share under 0.5c {np.median([r[4] for r in allm])*100:.0f}% ({len(allm)} states).")
open("scan/OUT-gas-daily-moves-2026-11-11.md", "w").write("\n".join(L) + "\n"); print("\n".join(L))
