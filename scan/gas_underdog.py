#!/usr/bin/env python3
"""Kalshi national daily AAA gas (KXAAAGASD): contract anatomy + when the non-favourite wins (Nick 11 Nov 04:58Z).
Per event D: ladder of 'above X' strikes (0.5c steps), settles on AAA national average regular for date D
(expiration_value). Reference 'AAA at open' = previous event's expiration_value."""
import sys, os, random, time, calendar
from collections import defaultdict
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import volume_first_scan as v, gas_leader as g

random.seed(11)
ms = g.list_markets("KXAAAGASD")
ev = defaultdict(list)
for m in ms: ev[m["event_ticker"]].append(m)
days = sorted(ev, key=lambda e: g.ts(ev[e][0]["close_time"]))
expv = {e: float(ev[e][0]["expiration_value"]) for e in days if ev[e][0].get("expiration_value")}
L = []
def P(s=""): print(s, flush=True); L.append(s)
m0 = ms[0]
P("## Contract")
P(f"Rule: {m0['rules_primary']}")
P(f"Opens ~{m0['open_time'][11:16]}Z on D-1, closes {m0['close_time'][11:16]}Z on D (midnight US Eastern), settles on AAA's published D value ~{m0['settlement_ts'][11:16]}Z on D. "
  f"Ladder of ~17 'above X' strikes in 0.5c steps around the expected value; {len(days)} events in history ({days[0][-5:]} .. {days[-1][-5:]}).\n")
sample = random.sample(days, min(80, len(days)))
rows, flips = [], []
for e in sample:
    prev_e = days[days.index(e) - 1] if days.index(e) > 0 else None
    if e not in expv or prev_e not in expv: continue
    prev, act = expv[prev_e], expv[e]
    for m in ev[e]:
        r = g.candles(m, "KXAAAGASD")
        if not r: continue
        ask, bid, vol, ot, ct = r
        n = len(ask)
        if n < 4 or np.isnan(ask[1]) or np.isnan(bid[1]): continue
        mid = (ask + bid) / 2; y = int(m["result"] == "yes")
        side = "Y" if mid[1] >= 0.5 else "N"
        fav_win = (y == 1) == (side == "Y")
        und_cost = (1 - bid[1]) if side == "Y" else ask[1]       # price of the underdog side at hour 1
        fav_cost = ask[1] if side == "Y" else 1 - bid[1]
        strike = float(m["floor_strike"])
        # flip: first hour index after which mid stays on the winning side of 0.5
        win_side = (mid > 0.5) if y == 1 else (mid < 0.5)
        bad = np.where(~win_side[1:])[0]
        flip_h = 0 if len(bad) == 0 else int(bad[-1] + 2)
        rows.append({"ev": e, "strike": strike, "prev": prev, "act": act, "fav_win": fav_win, "und_cost": und_cost,
                     "fav_cost": fav_cost, "dist": (strike - prev) * 100, "move": (act - prev) * 100, "flip_h": flip_h,
                     "life_h": n, "side": side})
P(f"Analysed {len({r['ev'] for r in rows})} random events, {len(rows)} strikes (hour-1 favourite = side priced >=50c).\n")
fw = np.array([r["fav_win"] for r in rows])
P(f"Favourite wins {fw.mean()*100:.1f}% of strikes; underdog wins {100-fw.mean()*100:.1f}% ({(~fw).sum()} cases).\n")
P("## Underdog cost vs win rate at hour 1 (underdog side ask)")
P("| underdog ask | strikes | underdog wins | cost | gap (win - cost, before fee) |\n|---|---:|---:|---:|---:|")
for lo, hi in [(0, .03), (.03, .10), (.10, .25), (.25, .5)]:
    s = [r for r in rows if lo <= r["und_cost"] < hi]
    if len(s) < 10: continue
    w = np.mean([not r["fav_win"] for r in s]); c = np.mean([r["und_cost"] for r in s])
    P(f"| {lo*100:.0f}-{hi*100:.0f}c | {len(s)} | {w*100:.1f}% | {c*100:.1f}c | {(w-c)*100:+.1f}c |")
und = [r for r in rows if not r["fav_win"]]
P("\n## Underdog-win cases: what separated them")
dist_all = np.array([abs(r["dist"]) for r in rows]); dist_und = np.array([abs(r["dist"] - r["move"]) for r in und])
P(f"- Actual AAA move (cents vs previous day) across analysed events: mean {np.mean([r['move'] for r in rows]):+.2f}c, sd {np.std([r['move'] for r in rows]):.2f}c.")
# implied median at hour 1 vs actual, per event
P("- Underdog wins happen at strikes the actual value finished close to: " +
  f"median |actual - strike| = {np.median([abs(r['act']*100 - r['strike']*100) for r in und]):.2f}c for underdog wins vs "
  f"{np.median([abs(r['act']*100 - r['strike']*100) for r in rows if r['fav_win']]):.2f}c for favourite wins.")
within = np.mean([abs(r['act'] * 100 - r['strike'] * 100) <= 1.0 for r in und])
P(f"- Share of underdog wins where AAA finished within 1c of the strike: {within*100:.0f}% (all strikes within 1c: "
  f"{np.mean([abs(r['act']*100 - r['strike']*100) <= 1.0 for r in rows])*100:.0f}%).")
P(f"- Flip timing (hours after open until price stayed on the winning side): median {np.median([r['flip_h'] for r in und]):.0f}h of a ~{np.median([r['life_h'] for r in rows]):.0f}h life; "
  f"{np.mean([r['flip_h'] >= 0.7 * r['life_h'] for r in und])*100:.0f}% flipped after 70% of life.")
P("\n| event | strike | AAA at open (prev day) | AAA actual | move | strike - AAA open | fav ask @open | underdog ask @open | flip (h of life) |\n|---|---:|---:|---:|---:|---:|---:|---:|---|")
for r in sorted(und, key=lambda r: r["ev"])[:18]:
    P(f"| {r['ev'][-5:]} | {r['strike']:.3f} | {r['prev']:.3f} | {r['act']:.3f} | {r['move']:+.1f}c | {r['dist']:+.1f}c | {r['fav_cost']*100:.0f}c | {r['und_cost']*100:.0f}c | {r['flip_h']} of {r['life_h']} |")
# market-implied median vs naive
P("\n## Is the ladder's centre biased vs a naive forecast?")
errs_m, errs_n = [], []
for e in {r["ev"] for r in rows}:
    rs = sorted([r for r in rows if r["ev"] == e], key=lambda r: r["strike"])
    st = np.array([r["strike"] for r in rs]); pyes = np.array([(r["fav_cost"] if r["side"] == "Y" else 1 - r["fav_cost"]) for r in rs])
    if len(rs) < 6 or not (pyes.max() > 0.5 > pyes.min()): continue
    k = np.where(pyes < 0.5)[0][0]
    if k == 0: continue
    x0, x1, y0, y1 = st[k - 1], st[k], pyes[k - 1], pyes[k]
    med = x0 + (y0 - 0.5) / (y0 - y1) * (x1 - x0)
    errs_m.append((rs[0]["act"] - med) * 100)
    pe = days[days.index(e) - 1]; pe2 = days[days.index(e) - 2] if days.index(e) > 1 else None
    if pe2 in expv: errs_n.append((rs[0]["act"] - (expv[pe] + (expv[pe] - expv[pe2]))) * 100)
if errs_m:
    P(f"- Market-implied median at open vs actual: mean error {np.mean(errs_m):+.2f}c, MAE {np.mean(np.abs(errs_m)):.2f}c over {len(errs_m)} events.")
if errs_n:
    P(f"- Naive 'yesterday + yesterday's move': MAE {np.mean(np.abs(errs_n)):.2f}c over {len(errs_n)} events.")
P("- RBOB/wholesale data was NOT tested (needs a futures series; not in this run).")
open("scan/OUT-gas-underdog-2026-11-11.md", "w").write("\n".join(L) + "\n")
