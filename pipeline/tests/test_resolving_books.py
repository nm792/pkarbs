import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "forward"))
import resolving_books as B

def test_depth_from_best_ask_in_dollars():
    asks = [(0.80, 100), (0.81, 50), (0.83, 1000)]
    assert abs(B.ask_depth_usd(asks, 0.02) - (80 + 40.5)) < 1e-9
    assert abs(B.ask_depth_usd(asks, 0.05) - (80 + 40.5 + 830)) < 1e-9
    assert B.ask_depth_usd([], 0.02) == 0.0

def test_leader_is_highest_own_bid_not_complement():
    bk = {"A": dict(bids=[(0.30, 5)], asks=[(0.32, 5)]), "B": dict(bids=[(0.65, 5)], asks=[(0.70, 9)]), "C": dict(bids=[], asks=[(0.9, 1)])}
    assert B.leader(bk) == "B"
    m = B.measure(bk); assert m["ask"] == 0.70 and m["bid"] == 0.65

def test_candidates_yes_for_brackets_both_for_updown():
    ev = {"markets": [dict(clobTokenIds='["y1","n1"]', outcomes='["Yes","No"]'), dict(clobTokenIds='["u","d"]', outcomes='["Up","Down"]')]}
    assert B.candidates(ev) == ["y1", "u", "d"]

def test_slim_book_sorts_best_last_inputs():
    b = B.slim_book(dict(asks=[dict(price="0.9", size="1"), dict(price="0.5", size="2")], bids=[dict(price="0.1", size="1"), dict(price="0.4", size="3")]))
    assert b["asks"][0][0] == 0.5 and b["bids"][0][0] == 0.4

def test_summarize_groups_by_series_and_lead():
    rows = [dict(series="s", lead_h=1.0, ask=0.8, depth02=10, depth05=20), dict(series="s", lead_h=1.0, ask=0.9, depth02=30, depth05=40), dict(series="s", error="x")]
    s = B.summarize(rows); assert len(s) == 1 and s[0]["n"] == 2 and s[0]["depth02_med"] == 20

def test_due_window_is_plus_minus_60s():
    end = 1_000_000.0
    assert B.due(end, 3.0, end - 3 * 3600) and B.due(end, 3.0, end - 3 * 3600 + 59) and B.due(end, 3.0, end - 3 * 3600 - 59)
    assert not B.due(end, 3.0, end - 3 * 3600 + 61) and not B.due(end, 1.0, end - 3 * 3600)

def test_health_counts_only_own_book_captures_and_errors():
    exp = {("e1", 3.0), ("e2", 3.0), ("e3", 1.0)}
    rows = [dict(event="e1", lead_h=3.0, ask=0.8, token="T1"), dict(event="e2", lead_h=3.0, error="x"), dict(event="e3", lead_h=1.0, ask=0.5)]
    h = B.health(exp, rows)
    assert h["expected"] == 3 and h["captured"] == 1 and h["errors"] == 1 and h["own_book_ok"] is False
    ok = B.health({("e1", 3.0)}, [rows[0]]); assert ok["pct"] == 100.0 and ok["own_book_ok"]
    assert B.health(set(), [])["pct"] is None

def test_single_instance_lock_refuses_second(tmp_path):
    a = B.acquire_lock(str(tmp_path)); assert a is not None
    assert B.acquire_lock(str(tmp_path)) is None
    a.close(); b = B.acquire_lock(str(tmp_path)); assert b is not None

def test_preflight_check_needs_equal_counts_levels_and_rows():
    bk = {"A": dict(asks=[(0.5, 1)], bids=[]), "B": dict(asks=[], bids=[])}
    assert B.preflight_check(2, bk, 10, 10)[0]
    assert not B.preflight_check(3, bk, 10, 10)[0]            # 2 books for 3 tokens
    assert not B.preflight_check(0, {}, 10, 10)[0]            # zero expected
    assert not B.preflight_check(2, bk, 3, 10)[0]             # not enough live rows
    assert not B.preflight_check(1, {"A": dict(asks=[], bids=[])}, 10, 10)[0]   # empty books

def test_closed_markets_are_not_candidates():
    ev = {"markets": [dict(clobTokenIds='["y1","n1"]', outcomes='["Yes","No"]', closed=True), dict(clobTokenIds='["y2","n2"]', outcomes='["Yes","No"]', acceptingOrders=False), dict(clobTokenIds='["y3","n3"]', outcomes='["Yes","No"]', closed=False, acceptingOrders=True)]}
    assert B.candidates(ev) == ["y3"]
