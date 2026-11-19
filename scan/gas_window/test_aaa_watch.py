#!/usr/bin/env python3
"""Can-fail tests for aaa_watch.parse on a synthetic page shaped like the table the Polymarket rules describe. Run: python3 test_aaa_watch.py"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import aaa_watch as a
HTML = "<div>Price as of 11/19/26</div><table><tr><th></th><th>Regular</th></tr><tr><td>Current Avg.</td><td>$3.731</td></tr><tr><td>Yesterday Avg.</td><td>$3.744</td></tr><tr><td>Week Ago Avg.</td><td>$3.801</td></tr></table>"
def t1_parses_fields():
    p = a.parse(HTML); assert p["price_as_of"] == "11/19/26" and p["regular_current"] == 3.731 and p["regular_yesterday"] == 3.744 and p["regular_week_ago"] == 3.801, p
def t2_unparseable_page_gives_nulls_not_crash():
    p = a.parse("<html>maintenance</html>"); assert p["price_as_of"] is None and p["regular_current"] is None and p["snippet"] is None
def t3_a_changed_number_is_visible():
    assert a.parse(HTML.replace("$3.731", "$3.726"))["regular_current"] == 3.726
TESTS = [t1_parses_fields, t2_unparseable_page_gives_nulls_not_crash, t3_a_changed_number_is_visible]
if __name__ == "__main__":
    ok = 0
    for t in TESTS:
        try: t(); ok += 1; print("PASS", t.__name__)
        except AssertionError as e: print("FAIL", t.__name__, e)
    print(f"{ok} of {len(TESTS)} tests pass"); sys.exit(0 if ok == len(TESTS) else 1)
