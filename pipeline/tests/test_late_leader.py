import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import late_leader as L

def R(ts, side, tok, px, sz): return (ts, side, tok, px, sz, 0)

def cands(rows_a, rows_b, won_a=True):
    rows = rows_a + rows_b
    return [("A", won_a, rows), ("B", not won_a, rows)]

def test_leader_uses_own_last_print_not_complement():
    rows = [R(100, "BUY", "A", 0.40, 10), R(110, "BUY", "B", 0.70, 10)]
    d = L.decide(cands([r for r in rows if r[2] == "A"], [r for r in rows if r[2] == "B"]), 200)
    assert d[0] == "B" and d[3] == 0.70            # B printed 0.70; A's 0.40 is NOT turned into 0.60

def test_stale_print_ignored_and_future_ignored():
    rows = [R(0, "BUY", "A", 0.9, 1), R(500, "BUY", "B", 0.6, 1), R(100_000, "BUY", "B", 0.99, 1)]
    d = L.decide([("A", True, rows), ("B", False, rows)], 100 + L.STALE)
    assert d[0] == "B" and d[3] == 0.6              # A is older than STALE, B's 0.99 print is after t

def test_fill_earliest_buy_and_depth_window():
    rows = [R(1000, "SELL", "A", 0.50, 99), R(1010, "BUY", "A", 0.50, 100), R(1100, "BUY", "A", 0.51, 100), R(1200, "BUY", "A", 0.60, 100), R(2000, "BUY", "A", 0.50, 100)]
    px, dep, ts = L.fill(rows, "A", 1000)
    assert (px, ts) == (0.50, 1010) and abs(dep - (0.5 * 100 + 0.51 * 100)) < 1e-9   # 0.60 beyond +0.02, 2000 outside the 10 min window

def test_event_bet_pnl_win_and_loss_with_fee():
    rows = [R(100, "BUY", "A", 0.50, 10), R(1000, "BUY", "A", 0.50, 1000)]
    c = [("A", True, rows)]
    r = L.event_bet(c, 900)
    assert r["bet"] == L.BET                         # depth 500 > 200
    exp = 200 * (1 / 0.5 - 1) - 200 / 0.5 * L.fee_ps(0.5)
    assert abs(r["pnl"] - exp) < 1e-9
    r2 = L.event_bet([("A", False, rows)], 900)
    assert abs(r2["pnl"] - (-200 - 200 / 0.5 * L.fee_ps(0.5))) < 1e-9

def test_bet_limited_by_printed_depth_and_nofill():
    rows = [R(100, "BUY", "A", 0.50, 10), R(1000, "BUY", "A", 0.50, 20)]
    assert abs(L.event_bet([("A", True, rows)], 900)["bet"] - 10.0) < 1e-9   # only $10 printed
    assert L.event_bet([("A", True, rows)], 5000)["skip"] == "nofill" if L.decide([("A", True, rows)], 5000) else True

def test_price_band_skip():
    rows = [R(100, "BUY", "A", 0.99, 10), R(1000, "BUY", "A", 0.99, 1000)]
    assert L.event_bet([("A", True, rows)], 900)["skip"] == "px"

def test_daily_cap():
    day = 1_700_000_000
    bets = [dict(ts=day + i, bet=200.0, pnl=10.0) for i in range(15)]
    k = L.apply_cap(bets)
    assert abs(sum(b["bet"] for b in k) - L.DAYCAP) < 1e-9 and abs(sum(b["pnl"] for b in k) - 100.0) < 1e-9

def test_late_pool_is_winner_only_banded_cheapest_first():
    rows = [R(29000, "BUY", "A", 0.80, 100), R(29100, "BUY", "A", 0.90, 1000), R(29200, "BUY", "A", 0.99, 1000), R(100, "BUY", "A", 0.70, 1000), R(29300, "BUY", "B", 0.75, 1000)]
    r = L.late_pool([("A", True, rows), ("B", False, rows)], 30_000, hours=3.0)
    assert abs(r["bet"] - 200.0) < 1e-9
    exp = 80 * (1 / 0.8 - 1) - 80 / 0.8 * L.fee_ps(0.8) + 120 * (1 / 0.9 - 1) - 120 / 0.9 * L.fee_ps(0.9)
    assert abs(r["pnl"] - exp) < 1e-9
