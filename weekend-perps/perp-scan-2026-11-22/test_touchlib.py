#!/usr/bin/env python3
"""Can-fail tests for touchlib (locked rule tests T1-T7). Run from this directory without -I."""
import datetime, json, random
from touchlib import *

fails = []
def check(name, cond):
    print(("PASS " if cond else "FAIL ") + name)
    if not cond: fails.append(name)

# ---------- T3 candidate logic is in pscanlib.gap_beyond (tested there); here the selection wrapper
S = [dict(kind="HIGH", strike=101, price=0.8, usd=100, win=True), dict(kind="HIGH", strike=110, price=0.1, usd=100, win=False), dict(kind="LOW", strike=95, price=0.2, usd=50, win=False)]
sel = select(S, 103.0, 100.0, 0.002)
check("only the HIGH 101 strike is crossed by the perp 103 (close 100)", [s["strike"] for s in sel] == [101])
check("close already beyond the strike -> nothing selected", select(S, 103.0, 102.0, 0.002) == [])
check("perp inside the margin -> nothing selected", select(S, 101.1, 100.0, 0.002) == [])

# ---------- decision times (DST from tz database)
mon = datetime.date(2026, 11, 16)    # EST: 09:20 NY = 14:20Z
T = decision_ts("STOCK", mon)
check("stock T Monday 14:20Z in November", datetime.datetime.fromtimestamp(T, datetime.timezone.utc).strftime("%a %H:%M") == "Mon 14:20")
Tm = decision_ts("METALS", mon)
check("metals T Sunday 22:50Z in November (17:50 NY)", datetime.datetime.fromtimestamp(Tm, datetime.timezone.utc).strftime("%a %H:%M") == "Sun 22:50")
Tj = decision_ts("STOCK", datetime.date(2026, 6, 15))
check("stock T Monday 13:20Z in June (EDT)", datetime.datetime.fromtimestamp(Tj, datetime.timezone.utc).strftime("%H:%M") == "13:20")

# ---------- T7 no look-ahead: perp_at never uses a candle that closes after T
c = [[(T - 120) * 1000, 100.0], [(T - 60) * 1000, 101.0], [(T + 60) * 1000, 999.0]]
check("perp_at uses the last candle closed at or before T (101), not the 999 after T", perp_at(c, T) == 101.0)
check("perp_at None when every candle is after T", perp_at([[(T + 1) * 1000, 5.0]], T) is None)
check("last_close strictly before the date", last_close({"2026-11-13": 10.0, "2026-11-16": 11.0}, mon) == 10.0)

# ---------- T4/T5/T6 entry from own prints
tok = "YES1"
pr = lambda t, p, s, tk=tok, side="BUY": dict(tok=tk, side=side, p=p, s=s, t=t)
e, why = entry([], tok, T)
check("no prints -> NOPRINT, not a loss", e is None and why == "NOPRINT")
e, why = entry([pr(T - 100, 0.97, 100), pr(T - 100, 0.03, 100)], tok, T)
check("prints at 0.97 and 0.03 are DEAD, excluded", e is None and why == "DEAD")
e, why = entry([pr(T - 100, 0.5, 100000)], tok, T)
check("a huge print counts as $200 (FLOOR cap)", abs(e["usd"] - 200.0) < 1e-6 and abs(e["price"] - 0.5) < 1e-9)
e, why = entry([pr(T, 0.5, 10), pr(T + 30, 0.5, 10)], tok, T)
check("a print AT or AFTER T is not used (no look-ahead)", e is None)
e, why = entry([pr(T - 3601, 0.5, 10)], tok, T)
check("a print older than 60 minutes is not used", e is None)
e, why = entry([pr(T - 100, 0.5, 10, tk="NOPE"), pr(T - 100, 0.5, 10, side="SELL")], tok, T)
check("other tokens and SELL prints are not used (own YES token, taker buys only)", e is None)
e, why = entry([pr(T - 100, 0.40, 100), pr(T - 90, 0.60, 100)], tok, T)
check("size-weighted average price", abs(e["price"] - 0.50) < 1e-9 and e["n"] == 2)

# ---------- yes_wins uses the label, not the position
check("YES wins by label when outcomes are ['No','Yes']", yes_wins('["0","1"]', '["No","Yes"]') is True)
check("a position-0 reader would be wrong on the same row", json.loads('["0","1"]')[0] == "0")
check("unresolved market -> None", yes_wins('["0.6","0.4"]', '["Yes","No"]') is None)

# ---------- T1 planted edge / T2 zero edge on a synthetic panel
def panel(planted, seed=7, weeks=30, tks=("a", "b", "c")):
    rnd = random.Random(seed); by_tk = {tk: [] for tk in tks}; sel_weeks = {}
    for w in range(weeks):
        for tk in tks:
            gapweek = rnd.random() < 0.5
            P, C = (103.0, 100.0) if gapweek else (100.0, 100.0)
            strikes = []
            for K in (101, 102):
                if planted:
                    if gapweek: pr_, win = 0.80, True          # perp crossed: YES under-priced, always wins
                    else: pr_, win = 0.30, False
                else:
                    pr_ = 0.50; win = rnd.random() < pr_       # fair price
                strikes.append(dict(kind="HIGH", strike=K, price=pr_, usd=100.0, win=win))
            by_tk[tk].append((w, P, C, 0.002, strikes))
            sel_weeks[(tk, w)] = select(strikes, P, C, 0.002)
    return by_tk, sel_weeks
by_tk, sw = panel(True)
st = stat(sw)
check("T1 planted: mean gap about +0.19 (1 - 0.80 - fee 0.0064)", abs(st["mean_gap"] - 0.1936) < 0.002)
mon_weeks = {}
for (tk, w), v in sw.items(): mon_weeks.setdefault(w, []).extend(v)
lo, hi = boot_weeks(mon_weeks)
check("T1 planted: CI lower bound > 0", lo > 0)
p = permutation_p(by_tk, st["mean_gap"], n=100)
check("T1 planted: permutation p <= 0.05 (the gap information matters)", p is not None and p <= 0.05)
# T2 zero edge, calibrated over 40 seeds: the PASS rule (CI lower > 0 and placebo p <= 0.05) may fire in at most 4 of 40 no-edge panels,
# and the average mean gap must sit near the fee-only value (about -0.01)
fire = 0; means = []
for sd in range(1, 41):
    by0, sw0 = panel(False, seed=sd)
    st0 = stat(sw0); mw0 = {}
    for (tk, w), v in sw0.items(): mw0.setdefault(w, []).extend(v)
    lo0, hi0 = boot_weeks(mw0, n=2000)
    p0 = permutation_p(by0, st0["mean_gap"], n=60)
    means.append(st0["mean_gap"])
    fire += (lo0 > 0 and p0 is not None and p0 <= 0.05)
check("T2 zero edge: average mean gap within 0.03 of zero (got %.3f)" % (sum(means) / len(means)), abs(sum(means) / len(means)) < 0.03)
check("T2 zero edge: PASS rule fires in <= 4 of 40 no-edge panels (got %d)" % fire, fire <= 4)
check("fee: 0.04*p*(1-p) at 0.5 is 0.01", abs(fee(0.5) - 0.01) < 1e-12)
check("gap sign: win at 0.8 -> +0.1936; loss at 0.8 -> -0.8064", abs(gap(True, 0.8) - 0.1936) < 1e-9 and abs(gap(False, 0.8) + 0.8064) < 1e-9)
check("T6 per-day floor caps deployed $ at $2,000 per Monday", per_day_floor({("a", 1): [dict(kind="HIGH", strike=1, price=0.5, usd=10000.0, win=True)]}, 1) < 0.5 * 10000 * 0.2 + 1 and per_day_floor({("a", 1): [dict(kind="HIGH", strike=1, price=0.5, usd=10000.0, win=True)]}, 1) <= 2000 * 0.49 + 1e-6)

# ---------- Amendment 3: last_print (exploratory) must not look ahead and must use the right token
lp = [dict(tok="Y", side="SELL", p=0.60, s=1, t=T - 5000), dict(tok="Y", side="BUY", p=0.70, s=1, t=T - 100), dict(tok="Y", side="BUY", p=0.99, s=1, t=T + 10), dict(tok="N", side="BUY", p=0.10, s=1, t=T - 50)]
check("last_print: latest YES print before T (0.70, age 100 s), ignoring the print after T and the other token", last_print(lp, "Y", T) == (0.70, 100))
check("last_print: None when only later prints exist", last_print([dict(tok="Y", side="BUY", p=0.5, s=1, t=T)], "Y", T) is None)
print("ALL PASS" if not fails else "FAILED: %s" % fails)
raise SystemExit(1 if fails else 0)
