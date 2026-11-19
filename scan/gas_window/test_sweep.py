#!/usr/bin/env python3
"""Can-fail tests for sweep.py and window.py (synthetic trades, planted sweep). Run: python3 test_sweep.py"""
import sys, os, json, calendar
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sweep as s, window as w
END = calendar.timegm((2026, 11, 18, 15, 0, 0))            # 10:00 ET on D (EST)
T0 = calendar.timegm((2026, 11, 18, 8, 17, 10))            # 03:17:10 ET
def rec():
    mk = []
    for i, res in enumerate((["1", "0"], ["0", "1"], ["0", "1"])): mk.append({"q": f"q{i}", "cond": f"c{i}", "res": json.dumps(res)})
    return {"slug": "us-gas-price-on-november-18-2026", "end": "2026-11-18T15:00:00Z", "vol": "100", "mk": mk}
def tr(c, side, idx, price, size, t): return {"side": side, "outcome_index": idx, "price": price, "size": size, "timestamp": t}
def trades(offset=0):
    # winner tokens: c0 Yes(idx0), c1 No(idx1), c2 No(idx1)
    return {"c0": [tr("c0", "BUY", 0, 0.60, 100, T0 + offset)], "c1": [tr("c1", "BUY", 1, 0.995, 50, T0 + 1 + offset)],
            "c2": [tr("c2", "BUY", 1, 0.99, 50, T0 + 2 + offset), tr("c2", "BUY", 1, 0.93, 40, T0 + 120 + offset)]}
TESTS = []
def test(f): TESTS.append(f); return f
@test
def t1_sweep_found_at_planted_time():
    wb = s.winner_buys(rec(), trades()); lo, hi = s.et_window(END, 1, 7); assert s.find_sweep(wb, lo, hi) == T0
@test
def t2_no_sweep_when_prints_are_spread_out():
    t = trades(); t["c1"][0]["timestamp"] += 600; t["c2"][0]["timestamp"] += 1200
    wb = s.winner_buys(rec(), t); lo, hi = s.et_window(END, 1, 7); assert s.find_sweep(wb, lo, hi) is None
@test
def t3_lag_windows_bucket_prices_correctly():
    wb = s.winner_buys(rec(), trades()); L = s.lag_stats(wb, T0, 0.97)
    assert L[0]["shares"] == 100 and abs(L[0]["edge"] - 100 * .40) < 1e-9, L[0]      # .995 and .99 are above the 0.97 cap
    assert L[2]["shares"] == 40 and abs(L[2]["edge"] - 40 * 0.07) < 1e-9 and L[1]["shares"] == 0
@test
def t4_losing_tokens_never_counted():
    t = trades(); t["c0"].append(tr("c0", "BUY", 1, 0.05, 1000, T0 + 3))      # No on a bucket that resolved Yes = loser
    wb = s.winner_buys(rec(), t); assert s.lag_stats(wb, T0, 0.97)[0]["shares"] == 100
@test
def t5_window_edge_requires_buy_side_and_price_cap():
    h = {"x": rec()}; t = trades(); t["c2"].append(tr("c2", "SELL", 1, 0.5, 999, T0 + 5))
    rows, st = w.run(h, t, (3, 17, 0), 0.97, 1.0)       # Tk = 03:17 ET on D, just before the planted sweep
    assert abs(rows[0]["shares"] - 140) < 1e-9, rows[0]
    rows2, st2 = w.run(h, t, (3, 17, 0), 0.90, 1.0); assert abs(rows2[0]["shares"] - 100) < 1e-9, rows2[0]
if __name__ == "__main__":
    ok = 0
    for t in TESTS:
        try: t(); ok += 1; print("PASS", t.__name__)
        except AssertionError as e: print("FAIL", t.__name__, e)
        except Exception as e: print("ERROR", t.__name__, repr(e))
    print(f"{ok} of {len(TESTS)} tests pass"); sys.exit(0 if ok == len(TESTS) else 1)
