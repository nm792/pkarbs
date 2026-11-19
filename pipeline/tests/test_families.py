import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import families as F


def ev(i, title, vol, day, series=None):
    e = dict(id=str(i), title=title, volume=vol, endDate=f"2026-11-{day:02d}T12:00:00Z")
    if series: e["series"] = [dict(slug=series, recurrence="daily")]
    return e


def test_family_key_prefers_series_then_template():
    assert F.family_key(ev(1, "x", 1, 1, "btc-daily")) == "series:btc-daily"
    assert F.family_key(ev(2, "Highest temperature in NYC on November 5?", 1, 1)) == F.family_key(
        ev(3, "Highest temperature in NYC on November 17?", 1, 1))


def test_frequency_and_volume():
    evs = [ev(i, "a", 100 * (i + 1), i % 10 + 1, "daily-s") for i in range(20)] + [ev(99, "b", 5, 3, "rare")] * 2
    rows = {r["family"]: r for r in F.screen(evs, 10)}
    assert "series:rare" not in rows  # below min_events
    r = rows["series:daily-s"]
    assert r["events_per_day"] == 2.0 and r["active_day_share"] == 1.0 and r["median_vol"] == 1050


def test_exclusions():
    assert F.excluded_reason(dict(tags=["Crypto", "Sports"]))
    assert F.excluded_reason(dict(tags=["Esports"]))
    assert F.excluded_reason(dict(tags=["Daily Temperature"]))
    assert F.excluded_reason(dict(tags=["Crypto"], series=[{"slug": "btc-up-or-down-5m"}]))
    assert F.excluded_reason(dict(tags=["Finance", "Stocks"], series=[{"slug": "spx-up-or-down-daily"}])) is None
    assert F.excluded_reason(dict(tags=["Crypto"], series=[{"slug": "btc-up-or-down-15m"}]))  # crypto now excluded


def test_crypto_excluded_but_finance_kept():
    assert F.excluded_reason(dict(tags=["Crypto Prices"]))
    assert F.excluded_reason(dict(tags=[], series=[{"slug": "bitcoin-hit-price-daily"}]))
    assert F.excluded_reason(dict(tags=[], series=[{"slug": "eth-up-or-down-hourly"}]))
    assert F.excluded_reason(dict(tags=["Finance"], series=[{"slug": "spx-daily-up-or-down"}])) is None
    assert F.excluded_reason(dict(tags=["Finance"], series=[{"slug": "gold-up-or-down-15m"}])) is None
