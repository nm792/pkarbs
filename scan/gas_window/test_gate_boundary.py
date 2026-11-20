#!/usr/bin/env python3
"""Planted tests for gate_boundary.py. Run: python3 test_gate_boundary.py (needs fixtures/ in this folder).
Each test can fail: a planted bug (wrong margin test, crossing bid, sell above bid, sell before the post) must be caught."""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import gate_boundary as g
BOOKS = json.load(open(os.path.join(HERE, "fixtures", "gas20_books_two_snapshots.json")))
PRINTS = json.load(open(os.path.join(HERE, "fixtures", "gas20_trades_all.json")))
FAV = "less than $3.7000 on November 20?|Yes"; BUCKET, OUT = "$3.7000", "Yes"
T_POST = 1795100462    # 15:01:02Z, first book
def t1_margin_below_cutoff_does_not_trade():
    assert g.decide(0.45, 0.65, 0.50, 1000, 1e9) == 0.0 and g.decide(0.5, 0.65, 0.50, 1000, 1e9) > 0   # 0.45c (the real 20 Nov margin) must not trade
def t2_no_edge_no_trade_and_depth_cap():
    assert g.decide(1.0, 0.50, 0.50, 1000, 1e9) == 0.0 and g.decide(1.0, 0.40, 0.50, 1000, 1e9) == 0.0
    assert g.decide(1.0, 0.90, 0.50, 1000, 40) == 40                    # depth caps the size
    assert abs(g.decide(1.0, 0.90, 0.50, 1000, 1e9) - 0.25 * 1000 * 0.4 / 0.5 / 0.5) < 1e-9   # quarter Kelly
def t3_bid_posts_on_empty_book_and_crossing_bid_is_rejected():
    r = g.run_gate(BOOKS["first"], FAV, BUCKET, OUT, 0.50, 20, T_POST, PRINTS); assert r["post"] and r["best_ask"] == 0.99
    r = g.run_gate(BOOKS["first"], FAV, BUCKET, OUT, 0.99, 20, T_POST, PRINTS); assert not r["post"]          # planted: bid at the ask crosses
    assert not g.can_post(0.5005, 20, {"best_ask": 0.99}) and not g.can_post(0.50, 4, {"best_ask": 0.99})  # off tick, under min size
def t4_planted_sell_print_fills_only_when_it_crosses_after_post():
    p = [[T_POST + 5, BUCKET, OUT, "SELL", 0.49, 30.0, ""]]
    assert g.fill_shares(0.50, T_POST, p, BUCKET, OUT) == 30.0
    assert g.fill_shares(0.50, T_POST, [[T_POST + 5, BUCKET, OUT, "SELL", 0.51, 30.0, ""]], BUCKET, OUT) == 0   # sell above the bid
    assert g.fill_shares(0.50, T_POST, [[T_POST - 5, BUCKET, OUT, "SELL", 0.49, 30.0, ""]], BUCKET, OUT) == 0  # before the post
    assert g.fill_shares(0.50, T_POST, [[T_POST + 5, BUCKET, OUT, "BUY", 0.49, 30.0, ""]], BUCKET, OUT) == 0   # a buy never fills a bid
    assert g.fill_shares(0.50, T_POST, [[T_POST + 5, "$3.7100 and $3.7199", OUT, "SELL", 0.49, 30.0, ""]], BUCKET, OUT) == 0  # other token
def t5_real_20nov_record_posts_but_never_fills():
    # Recorded fact, not a pass: all 61 recorded prints for the event are taker BUYs, so a 0.50 bid on the favourite posts (ask 0.99, then 0.98 with bid 0.81 at 15:08:41Z) and gets NO fill.
    assert all(r[3] == "BUY" for r in PRINTS) and len(PRINTS) == 61
    r1 = g.run_gate(BOOKS["first"], FAV, BUCKET, OUT, 0.50, 20, T_POST, PRINTS); r2 = g.run_gate(BOOKS["at_1508"], FAV, BUCKET, OUT, 0.50, 20, 1795100921, PRINTS)
    assert r1["post"] and r1["fill_shares"] == 0 and r2["post"] and r2["best_bid"] == 0.81 and r2["fill_shares"] == 0
TESTS = [t1_margin_below_cutoff_does_not_trade, t2_no_edge_no_trade_and_depth_cap, t3_bid_posts_on_empty_book_and_crossing_bid_is_rejected, t4_planted_sell_print_fills_only_when_it_crosses_after_post, t5_real_20nov_record_posts_but_never_fills]
if __name__ == "__main__":
    ok = 0
    for t in TESTS:
        try: t(); ok += 1; print("PASS", t.__name__)
        except AssertionError as e: print("FAIL", t.__name__, e)
    print(f"{ok} of {len(TESTS)} tests pass"); sys.exit(0 if ok == len(TESTS) else 1)
