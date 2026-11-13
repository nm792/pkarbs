#!/usr/bin/env python3
"""Descriptive only (no outcomes): where does the gas state volume trade, and at what spread, by UTC hour. Reuses cached candles."""
import sys, os, calendar, time
from collections import defaultdict
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import volume_first_scan as v, gas_leader as g
STATES = "AK AL AR AZ CO CT DE HI IA ID KS KY LA MA MD ME MN MO MS MT ND NE NH NM NV OK OR RI SC SD TN UT VT WV WY".split()
hv_all = defaultdict(float); hv_near = defaultdict(float); sp = defaultdict(list); spn = defaultdict(list); days = set(); per_state = {}
for st in STATES:
    ser = f"KXAAAGASD{st}"; ms = g.list_markets(ser, hist_pages=3); ev = defaultdict(list)
    for m in ms: ev[m["event_ticker"]].append(m)
    day = {e: time.strftime("%Y-%m-%d", time.gmtime(g.ts(l[0]["close_time"]) + 3600)) for e, l in ev.items()}
    byday = {d: e for e, d in day.items()}
    expv = {e: float(l[0]["expiration_value"]) for e, l in ev.items() if l[0].get("expiration_value")}
    pdd = lambda d, k: time.strftime("%Y-%m-%d", time.gmtime(calendar.timegm(time.strptime(d, "%Y-%m-%d")) - 86400 * k))
    tot = 0; nd = 0
    for d in sorted(byday)[-30:]:
        e = byday[d]; e1 = byday.get(pdd(d, 1))
        if e1 not in expv: continue
        prev = expv[e1]; days.add(d); nd += 1
        for m in ev[e]:
            r = g.candles(m, ser)
            if not r: continue
            ask, bid, vol, ot, ct = r
            near = abs(float(m["floor_strike"]) - prev) <= 0.03
            for i in range(len(ask)):
                if np.isnan(ask[i]) or np.isnan(bid[i]) or ask[i] <= bid[i]: continue
                h = (ot + 3600 * i) // 3600 % 24; mid = (ask[i] + bid[i]) / 2
                usd = vol[i] * min(mid, 1 - mid) * 2 if False else vol[i] * mid
                hv_all[h] += usd; tot += usd
                if near and 0.25 <= mid <= 0.75:
                    hv_near[h] += usd; spn[h].append(ask[i] - bid[i])
                sp[h].append(ask[i] - bid[i])
    per_state[st] = tot / max(nd, 1)
nd = len(days); L = []
def P(s=""): print(s, flush=True); L.append(s)
P(f"# Gas state markets (35 fresh states), volume and spread by UTC hour, last 30 events/state, {nd} distinct days. NO outcomes used.")
P(f"Total $ traded (contracts x mid) across the 35 states: ${sum(hv_all.values())/nd:,.0f}/day; in near-strike (<=3c of prior AAA) with YES mid 25-75c: ${sum(hv_near.values())/nd:,.0f}/day")
P("| UTC hour | all $/day | near-strike $/day | mean spread (all) | mean spread (near) |\n|---:|---:|---:|---:|---:|")
for h in range(24):
    if hv_all[h] or sp[h]:
        P(f"| {h:02d} | {hv_all[h]/nd:,.0f} | {hv_near[h]/nd:,.0f} | {np.mean(sp[h])*100:.1f}c | {(np.mean(spn[h])*100 if spn[h] else float('nan')):.1f}c |")
open("scan/OUT-gas-volume-spread-2026-11-11.md", "w").write("\n".join(L) + "\n")
