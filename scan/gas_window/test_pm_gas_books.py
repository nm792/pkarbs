#!/usr/bin/env python3
"""Can-fail tests for pm_gas_books.parse_book. Run: python3 test_pm_gas_books.py"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pm_gas_books as b
RAW = {"asks": [{"price": "0.999", "size": "21080"}, {"price": "0.998", "size": "5.32"}, {"price": "0.60", "size": "100"}, {"price": "0.62", "size": "40"}],
       "bids": [{"price": "0.001", "size": "75"}, {"price": "0.55", "size": "10"}], "last_trade_price": "0.61", "timestamp": "1795063073739"}
def t1_best_ask_is_lowest_not_first():
    p = b.parse_book(RAW); assert p["best_ask"] == 0.60 and p["asks"][0] == (0.60, 100.0) and p["bids"][0] == (0.55, 10.0), p
def t2_depth_counts_only_stale_levels():
    p = b.parse_book(RAW); assert p["ask_depth_le_97"] == 140.0, p            # 100 at .60 and 40 at .62; .998/.999 excluded
def t3_empty_book_is_safe():
    p = b.parse_book({"asks": [], "bids": []}); assert p["best_ask"] is None and p["ask_depth_le_97"] == 0 and p["ltp"] is None
TESTS = [t1_best_ask_is_lowest_not_first, t2_depth_counts_only_stale_levels, t3_empty_book_is_safe]
if __name__ == "__main__":
    ok = 0
    for t in TESTS:
        try: t(); ok += 1; print("PASS", t.__name__)
        except AssertionError as e: print("FAIL", t.__name__, e)
    print(f"{ok} of {len(TESTS)} tests pass"); sys.exit(0 if ok == len(TESTS) else 1)
