#!/usr/bin/env python3
"""Can-fail tests for pmtrades.check_rows (R-080). Run from this directory without -I."""
from pmtrades import check_rows
fails = []
def check(name, cond):
    print(("PASS " if cond else "FAIL ") + name)
    if not cond: fails.append(name)
def raises(f):
    try: f()
    except AssertionError: return True
    return False
A, B = "0xaaa", "0xbbb"
good = [dict(condition_id=A), dict(condition_id=B), dict(condition_id="0xAAA")]
check("rows inside the event's markets pass (case-insensitive)", check_rows(good, {A, B}) == 3)
check("PLANTED WRONG PARAM: a market-wide page (foreign condition_id) FAILS", raises(lambda: check_rows(good + [dict(condition_id="0xccc")], {A, B})))
check("a row with a missing condition_id FAILS", raises(lambda: check_rows([dict(price=1)], {A})))
check("no allowed ids given FAILS (cannot verify)", raises(lambda: check_rows(good, set())))
check("single-market request: rows of another market FAIL", raises(lambda: check_rows([dict(condition_id=B)], {A})))
check("empty page passes", check_rows([], {A}) == 0)
print("ALL PASS" if not fails else "FAILED: %s" % fails)
raise SystemExit(1 if fails else 0)
