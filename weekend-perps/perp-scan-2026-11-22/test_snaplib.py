#!/usr/bin/env python3
"""Can-fail tests for snaplib (no network). Run: python3 test_snaplib.py from this directory."""
import json
from snaplib import market_tokens, token_row, candidates

fails = []
def check(name, cond):
    print(("PASS " if cond else "FAIL ") + name)
    if not cond: fails.append(name)

m_yes_first = dict(slug="m1", question="Will X hit (HIGH) $100 in November?", outcomes=json.dumps(["Yes", "No"]), clobTokenIds=json.dumps(["T_YES", "T_NO"]))
m_no_first = dict(slug="m2", question="Will X hit (HIGH) $100 in November?", outcomes=json.dumps(["No", "Yes"]), clobTokenIds=json.dumps(["T_NO", "T_YES"]))
check("outcome/token pairing, Yes first", market_tokens(m_yes_first) == [("Yes", "T_YES"), ("No", "T_NO")])
check("outcome/token pairing, No first (a position-based reader would swap them)", market_tokens(m_no_first) == [("No", "T_NO"), ("Yes", "T_YES")])

# own-token book: YES token asks at 0.60, NO token asks at 0.55 (they do NOT sum to 1; NO must never be derived from YES)
yes_book = {"asks": [{"price": "0.999", "size": "10"}, {"price": "0.60", "size": "100"}], "bids": [{"price": "0.58", "size": "5"}]}
no_book = {"asks": [{"price": "0.55", "size": "40"}], "bids": [{"price": "0.30", "size": "5"}]}
ry = token_row("ev", "TOUCH-X", m_yes_first, "Yes", "T_YES", yes_book, 1)
rn = token_row("ev", "TOUCH-X", m_yes_first, "No", "T_NO", no_book, 1)
check("YES best ask 0.60 from its own book", ry["best_ask"] == 0.60 and ry["book_ok"])
check("NO best ask 0.55 from its own book, not 1-0.58", rn["best_ask"] == 0.55 and abs(rn["best_ask"] - (1 - 0.58)) > 0.1)
check("YES depth $60 (0.60*100), 0.999 level excluded", abs(ry["ask_depth_usd"] - 60.0) < 1e-9)
miss = token_row("ev", "TOUCH-X", m_yes_first, "No", "T_NO", None, 1)
check("token with no book: book_ok False, depth 0, no ask (excluded, never inferred)", (not miss["book_ok"]) and miss["ask_depth_usd"] == 0.0 and miss["best_ask"] is None and not miss["tradable"])
check("404-style error dict is also 'no book'", not token_row("ev", "F", m_yes_first, "No", "T_NO", {"error": "not found"}, 1)["book_ok"])

# candidates: perp already beyond the strike
rows = [dict(ry, under="u", q="Will X hit (HIGH) $100 in November?"),
        dict(rn, under="u", q="Will X hit (HIGH) $100 in November?"),
        dict(ry, under="u", q="Will X hit (HIGH) $120 in November?"),
        dict(ry, under="u", q="Will X dip to (LOW) $90 in November?"),
        dict(ry, under=None, q="Will X hit (HIGH) $100 in November?")]
c = candidates(rows, {"u": 103.0}, {"u": 96.0}, {"u": 0.002})
check("only the YES row whose HIGH strike is already crossed (K=100: close 96 < 100 <= perp 103)", len(c) == 1 and c[0]["strike"] == 100.0 and c[0]["outcome"] == "Yes")
check("no candidates when the perp is inside the margin", candidates(rows, {"u": 100.1}, {"u": 96.0}, {"u": 0.002}) == [])
check("no candidates when the close had already crossed", candidates(rows, {"u": 103.0}, {"u": 101.0}, {"u": 0.002}) == [])
check("LOW strike candidate when perp already below it", len(candidates([dict(ry, under="u", q="Will X dip to (LOW) $90 in November?")], {"u": 88.0}, {"u": 96.0}, {"u": 0.002})) == 1)
print("ALL PASS" if not fails else "FAILED: %s" % fails)
raise SystemExit(1 if fails else 0)
