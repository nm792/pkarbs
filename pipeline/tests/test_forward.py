import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "forward"))
import books, recorder


def test_depth_within_band():
    b = {"asks": [{"price": "0.80", "size": "100"}, {"price": "0.82", "size": "50"}, {"price": "0.90", "size": "1000"}], "bids": [{"price": "0.78", "size": "10"}]}
    d = books.depth(b, 0.03)
    assert d["best_ask"] == 0.80 and abs(d["ask_usd_within"] - (80 + 41)) < 1e-9 and d["best_bid"] == 0.78 and abs(d["ask_usd_total"] - (80 + 41 + 900)) < 1e-9


def test_parse_aaa():
    html = '<div>Price as of 11/19/26</div><table><tr><td>Current Avg.</td><td>$3.731</td></tr><tr><td>Yesterday Avg.</td><td>$3.744</td></tr></table>'
    d = recorder.parse_aaa(html)
    assert d["price_as_of"] == "11/19/26" and d["current"] == 3.731 and d["yesterday"] == 3.744


def test_windows():
    import datetime as dt
    assert recorder.in_window("gas", dt.datetime(2026, 11, 19, 7, 39, tzinfo=dt.timezone.utc))
    assert not recorder.in_window("gas", dt.datetime(2026, 11, 19, 12, 0, tzinfo=dt.timezone.utc))
    assert recorder.in_window("spxopen", dt.datetime(2026, 11, 19, 14, 30, tzinfo=dt.timezone.utc))  # 09:30 EST
    assert not recorder.in_window("spxopen", dt.datetime(2026, 11, 21, 14, 30, tzinfo=dt.timezone.utc))  # Saturday
