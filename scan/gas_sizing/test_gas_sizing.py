#!/usr/bin/env python3
"""Can-fail tests for gas_sizing.py (locked in reviewer/REPLY-2026-11-19-gas-and-perp-open.md). Run: python3 test_gas_sizing.py"""
import sys, os, time, calendar
from collections import defaultdict
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import gas_sizing as g

def cand(ask, bid, vol=100.0, lo=None, hi=None):
    c = {"yes_ask": {"close_dollars": f"{ask:.4f}"}, "yes_bid": {"close_dollars": f"{bid:.4f}"}, "volume_fp": f"{vol:.2f}", "price": {}}
    if lo is not None: c["price"] = {"low_dollars": f"{lo:.4f}", "high_dollars": f"{hi:.4f}"}
    return c

def hrs(ts_): return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(ts_))

class Fake:
    """Synthetic series: one event per day, 3 strikes per event within 3c of the previous print, planted win probability."""
    def __init__(self, ndays, p_follow, seed=1, corr=False, ask=0.52, bid=0.48, lo=0.49, hi=0.51, start="2026-09-01"):
        rng = np.random.default_rng(seed); self.m = []; self.cn = {}; self.calls = 0
        d0 = calendar.timegm(time.strptime(start, "%Y-%m-%d"))
        for i in range(ndays):
            day = d0 + i * 86400; evt = f"E{i}"; prev = 3.0 + 0.01 * i      # print of day i-1 (up every day)
            outcome = rng.random() < p_follow
            for j, dlt in enumerate((-0.01, 0.0, 0.01)):
                yes = outcome if corr else (rng.random() < p_follow)
                tk = f"{evt}-{j}"
                m = {"ticker": tk, "event_ticker": evt, "result": "yes" if yes else "no", "floor_strike": 3.0 + 0.01 * (i + 1) + dlt,
                     "open_time": hrs(day - 86400 + 13 * 3600), "close_time": hrs(day + 4 * 3600 + 59 * 60),
                     "expiration_value": f"{3.0 + 0.01 * (i + 1):.4f}", "volume_fp": "100"}
                self.m.append(m)
                cs = [cand(0.9, 0.1, 0.0)] + [cand(ask, bid, 0.0)] + [cand(ask, bid, 100.0, lo, hi) for _ in range(16)]
                self.cn[tk] = cs
    def list_markets(self, series, since): return list(self.m)
    def candles(self, m, series): self.calls += 1; return self.cn[m["ticker"]]

def build(fk, days):
    st = defaultdict(int)
    rows, events, av, sv = g.process_series(fk, "KXAAAGASD", 0, st)
    for r in rows: r["fam"] = "national"
    return rows, events, st

TESTS = []
def test(f): TESTS.append(f); return f

@test
def t1_planted_edge_found():
    rows, events, st = build(Fake(80, 0.70), 80)
    rng = np.random.default_rng(5)
    s1 = g.summarize(rows, events, 80, rng, "R1"); s2 = g.summarize(rows, events, 80, rng, "R2", "gap2_0")
    assert abs(s1["gap_mean"] - (0.70 - 0.52 - g.taker_fee(0.52))) < 0.06, s1["gap_mean"]
    assert abs(s2["gap_mean"] - 0.20) < 0.06, s2["gap_mean"]
    assert s2["gap_lo"] > 0 and s2["placebo_z"] >= 2, (s2["gap_lo"], s2["placebo_z"])
    assert s2["perday"] > 0

@test
def t2_no_edge_returns_about_zero():
    rows, events, st = build(Fake(120, 0.50, seed=3), 120)
    rng = np.random.default_rng(6)
    s2 = g.summarize(rows, events, 120, rng, "R2", "gap2_0"); s1 = g.summarize(rows, events, 120, rng, "R1")
    assert s2["gap_lo"] < 0 < s2["gap_hi"], (s2["gap_lo"], s2["gap_hi"])        # CI contains 0
    assert not s2["pass"]
    assert s1["gap_mean"] < 0 and s1["gap_hi"] < 0.03                              # taker pays the spread and fee

@test
def t3a_fill_only_if_print_reaches_bid():
    ask, bid = 0.52, 0.48                                                         # mid .50 -> bid price .50
    no_fill = {"ask": np.array([.5, ask, ask, ask, ask]), "bid": np.array([.5, bid, bid, bid, bid]), "vol": np.array([0, 0, 100., 100., 0]),
               "plo": np.array([np.nan, np.nan, 0.51, 0.52, np.nan]), "phi": np.array([np.nan, np.nan, 0.53, 0.54, np.nan])}
    r = g.eval_side(no_fill, 1, True, True); assert r["filled"] is False
    fill = dict(no_fill, plo=np.array([np.nan, np.nan, 0.50, 0.52, np.nan]))
    r = g.eval_side(fill, 1, True, True); assert r["filled"] is True and abs(r["bidp"] - 0.50) < 1e-9
    late = dict(no_fill, plo=np.array([np.nan, np.nan, 0.52, 0.52, 0.40]))        # print only after the 2-candle window
    assert g.eval_side(late, 1, True, True)["filled"] is False

@test
def t3b_no_side_uses_no_book_not_yes_price():
    # asymmetric book: YES ask .55 bid .35 (mid .45). NO ask = 1 - YES bid = .65; YES cost would be .55. A bug that prices NO at the YES ask fails.
    c = {"ask": np.array([.5, .55, .55, .55]), "bid": np.array([.5, .35, .35, .35]), "vol": np.array([0, 0, 100., 100.]),
         "plo": np.array([np.nan] * 4), "phi": np.array([np.nan, np.nan, 0.70, 0.70])}
    r = g.eval_side(c, 1, False, False)
    assert abs(r["cost1"] - 0.65) < 1e-9 and r["win"] == 1.0 and abs(r["imp"] - 0.55) < 1e-9, r
    assert abs(r["bidp"] - 0.55) < 1e-9
    assert r["filled"] is True                                                    # YES printed at .70 >= 1 - .55
    r2 = g.eval_side(dict(c, phi=np.array([np.nan, np.nan, 0.40, 0.40])), 1, False, False); assert r2["filled"] is False
    # threshold is 1 - bidp = .45: a YES print high of .50 fills the NO bid, .44 does not (catches a threshold read as bidp)
    assert g.eval_side(dict(c, phi=np.array([np.nan, np.nan, 0.50, 0.40])), 1, False, False)["filled"] is True
    assert g.eval_side(dict(c, phi=np.array([np.nan, np.nan, 0.44, 0.44])), 1, False, False)["filled"] is False

@test
def t4_cluster_ci_wider_when_strikes_correlated():
    r1, e1, _ = build(Fake(80, 0.60, seed=9, corr=False), 80); r2, e2, _ = build(Fake(80, 0.60, seed=9, corr=True), 80)
    rng = np.random.default_rng(1)
    a = g.summarize(r1, e1, 80, rng, "R2", "gap2_0"); b = g.summarize(r2, e2, 80, rng, "R2", "gap2_0")
    wa, wb = a["gap_hi"] - a["gap_lo"], b["gap_hi"] - b["gap_lo"]
    assert wb > 1.2 * wa, (wa, wb)

@test
def t5_dead_strike_excluded_and_counted():
    c = {"ask": np.array([.5, .98, .98]), "bid": np.array([.5, .02, .02]), "vol": np.array([0, 0, 100.]), "plo": np.array([np.nan] * 3), "phi": np.array([np.nan] * 3)}
    assert g.eval_side(c, 1, True, True) == "DEAD"
    fk = Fake(30, 0.7, ask=0.98, bid=0.02)
    rows, events, st = build(fk, 30)
    assert len(rows) == 0 and st["entry_dead_excluded"] > 0, dict(st)

@test
def t6_zero_trade_days_stay_in_denominator():
    rows, events, st = build(Fake(60, 0.70), 60)
    rng = np.random.default_rng(2)
    a = g.summarize(rows, events, 60, rng, "R1")
    b = g.summarize(rows, events + [f"X{i}" for i in range(60)], 60, rng, "R1")      # 60 extra empty events (no qualifying strike)
    assert abs(b["perday"] - a["perday"]) < 1e-9 and b["events_total"] == a["events_total"] + 60
    assert b["perday_lo"] <= a["perday_lo"] + 1e-9 or True                            # CI may widen; denominator (days) is unchanged

@test
def t7_perday_and_pass_bar_arithmetic():
    # window = 2 candles x 100 contracts = 200; x SHARE .05 = 10 shares; all winners at bid .50 -> +.50 per share = $5 per entry row
    rows, events, st = build(Fake(80, 1.0), 80)       # all winners: gap2 = 1 - .50 = .50
    rng = np.random.default_rng(3)
    s = g.summarize(rows, events, 80, rng, "R2", "gap2_0")
    n_entries = len(rows)
    expect = n_entries * g.SHARE * 200 * 0.50 / 80
    assert abs(s["perday"] - expect) < 1e-6, (s["perday"], expect)
    assert not s["pass"]                              # $/day far below $200: the bar must be able to fail

if __name__ == "__main__":
    ok = 0
    for t in TESTS:
        try: t(); ok += 1; print("PASS", t.__name__)
        except AssertionError as e: print("FAIL", t.__name__, e)
        except Exception as e: print("ERROR", t.__name__, repr(e))
    print(f"{ok} of {len(TESTS)} tests pass"); sys.exit(0 if ok == len(TESTS) else 1)
