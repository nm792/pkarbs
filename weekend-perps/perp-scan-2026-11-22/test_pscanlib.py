#!/usr/bin/env python3
"""Can-fail tests for pscanlib. Run: python3 test_pscanlib.py (from this directory, without -I)."""
from pscanlib import *

fails = []
def check(name, cond):
    print(("PASS " if cond else "FAIL ") + name)
    if not cond: fails.append(name)

# T1 book order: Polymarket lists asks DESCENDING (best ask last) and bids ASCENDING (best bid last)
asks_desc = [{"price": "0.999", "size": "1000"}, {"price": "0.62", "size": "50"}, {"price": "0.60", "size": "100"}]
bids_asc = [{"price": "0.01", "size": "5"}, {"price": "0.55", "size": "20"}, {"price": "0.58", "size": "30"}]
check("best ask is the lowest price, not first element (0.60)", best_ask(asks_desc) == 0.60)
check("a first-element reader would be wrong (planted: 0.999)", asks_desc[0]["price"] == "0.999")
check("best bid is the highest price (0.58)", best_bid(bids_asc) == 0.58)
check("same answer when the order is reversed", best_ask(list(reversed(asks_desc))) == 0.60)

# T2 depth: 0.60x100 + 0.62x50 inside best+3c ; 0.999 excluded
d = ask_depth_usd(asks_desc)
check("depth within 3c = 0.60*100 + 0.62*50 = 91.0", abs(d - 91.0) < 1e-9)
check("depth excludes a level just outside 3c (0.64 vs best 0.60)", abs(ask_depth_usd([{"price": "0.60", "size": "10"}, {"price": "0.64", "size": "10"}]) - 6.0) < 1e-9)
check("empty or junk book gives depth 0 and no best ask", ask_depth_usd([]) == 0.0 and best_ask([{"price": "x", "size": "1"}]) is None)

# T3 dead-bucket rule
check("ask 0.97 is dead (not tradable)", not tradable(0.97) and not tradable(0.04) and tradable(0.50) and not tradable(None))

# T4 strike parsing
check("HIGH strike with comma", parse_strike("Will Gold (XAUUSD) hit (HIGH) $4,600 in November?") == ("HIGH", 4600.0))
check("LOW strike via dip", parse_strike("Will Gold (GC) dip to (LOW) $3,500 by end of December?") == ("LOW", 3500.0))
check("unparseable returns None", parse_strike("Will Hyperliquid launch a token?") is None)

# T5 gap_beyond: must fail when the close is already beyond or the perp is short of the margin
check("HIGH gap beyond: close 95, strike 100, perp 101", gap_beyond(101, 95, "HIGH", 100))
check("HIGH not beyond when perp inside margin (100.1 vs 100, margin 20bp)", not gap_beyond(100.1, 95, "HIGH", 100))
check("HIGH not a gap when the close was already above the strike", not gap_beyond(105, 101, "HIGH", 100))
check("LOW gap beyond: close 105, strike 100, perp 99", gap_beyond(99, 105, "LOW", 100))
check("LOW not a gap when close already below", not gap_beyond(95, 98, "LOW", 100))
check("missing inputs never qualify", not gap_beyond(None, 95, "HIGH", 100))

# T6 capacity: $200 per decision per token, $2,000/day cap
check("one token with $50 depth deploys $50", per_decision_usd(50) == 50)
check("one token with $5,000 depth deploys $200", per_decision_usd(5000) == 200)
check("3 tokens ($50, $5,000, $120) -> $370 per decision", abs(day_capacity([50, 5000, 120]) - 370) < 1e-9)
check("cap binds: 20 decisions/day * $370 = $7,400 -> $2,000", day_capacity([50, 5000, 120], decisions_per_day=20) == 2000.0)
check("pct of $200: $2 -> 1.0%", abs(pct_of_200(2.0) - 1.0) < 1e-9)

# T7 notional window
rows = [{"price": 0.5, "size": 100, "timestamp": 10}, {"price": 0.2, "size": 100, "timestamp": 20}, {"price": 0.9, "size": 10, "timestamp": 30}]
check("notional full", abs(notional(rows) - 79.0) < 1e-9)
check("notional window [15,30) excludes both ends", abs(notional(rows, 15, 30) - 20.0) < 1e-9)

print("ALL PASS" if not fails else "FAILED: %s" % fails)
raise SystemExit(1 if fails else 0)
