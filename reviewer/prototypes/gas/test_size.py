#!/usr/bin/env python3
"""Tests for size.py that can fail and pass. Run: python3 test_size.py

T1 planted edge: a daily ladder where the bottom bucket is bought at 0.50 and always wins, with
   enough flow, must give a positive return with CI low > 0 and a PASS.
T2 null: bottom bucket bought at 0.50, wins half the time at random -> CI must straddle 0, not PASS.
T3 capacity: real-sized flow ($1.6k/day qualifying) cannot reach $200/day for a 10% slice even at a
   planted +50c per $ -> must not PASS.
T4 dead-bucket exclusion: prints at >= 0.99 must never enter qualifying flow or a rule.
T5 placebo: on T1 data the placebo (outcome of another bucket) must be far below the rule.
"""
import numpy as np
import size

DAY = 86400


def ladder(n_events, price, win_fn, size_shares, t_start=1_700_000_000, extra_price=None):
    ev = {}
    for k in range(n_events):
        t0 = t_start + k * DAY
        w = win_fn(k)
        mk = []
        for j, title in enumerate(["<$3.00", "$3.00-3.0099", "$3.01+"]):
            yes = (1 if w else 0) if j == 0 else (0 if w else (1 if j == 1 else 0))
            tr = []
            if j == 0:
                tr.append({"side": "BUY", "price": price, "size": size_shares, "timestamp": t0 + 3600,
                           "outcome_index": 0, "token_id": "x", "proxy_wallet": "y"})
                if extra_price:
                    tr.append({"side": "BUY", "price": extra_price, "size": size_shares, "timestamp": t0 + 3700,
                               "outcome_index": 0, "token_id": "x", "proxy_wallet": "y"})
            mk.append({"groupItemTitle": title, "closed": True, "outcomePrices": f'["{yes}", "{1-yes}"]',
                       "feesEnabled": True, "feeSchedule": {"rate": 0.04, "exponent": 1}, "_trades": tr})
        ev[f"e{k}"] = {"_series": "us-gas-price-daily", "startDate": _iso(t0), "endDate": _iso(t0 + DAY), "markets": mk}
    return ev


def _iso(t):
    import datetime
    return datetime.datetime.fromtimestamp(t, datetime.timezone.utc).isoformat().replace("+00:00", "Z")


def run_rule(ev, rule="daily_bottom", seed=1):
    rng = np.random.default_rng(seed)
    now = max(t["timestamp"] for e in ev.values() for m in e["markets"] for t in m["_trades"])
    rows = size.rule_rows(ev, rule, 0, now, rng)
    st = size.clustered(rows, rng)
    days = len(ev)
    return st, size.verdict(st, days)


def test_planted():
    ev = ladder(60, 0.50, lambda k: True, 20000)   # $10k/day flow at 0.50, always wins
    st, (fd, md, ld, v) = run_rule(ev)
    assert st["lo"] > 0 and v == "PASS", (st, v)
    assert st["placebo_ret"] < st["ret"] - 0.5, st          # T5
    return f"T1 planted: ret {st['ret']*100:+.1f}c lo {st['lo']*100:+.1f}c {v}; T5 placebo {st['placebo_ret']*100:+.1f}c"


def test_null():
    r = np.random.default_rng(3).random(60) < 0.5
    ev = ladder(60, 0.50, lambda k: bool(r[k]), 20000)
    st, (fd, md, ld, v) = run_rule(ev)
    assert st["lo"] < 0 < st["hi"] and v != "PASS", (st, v)
    return f"T2 null: ret {st['ret']*100:+.1f}c CI ({st['lo']*100:+.1f}, {st['hi']*100:+.1f}) {v}"


def test_capacity():
    # $1,645/day at 0.50 -> 3290 shares/day; 75% win rate at 0.50 = about +50c per $
    r = np.random.default_rng(5).random(60) < 0.75
    ev = ladder(60, 0.50, lambda k: bool(r[k]), 3290)
    st, (fd, md, ld, v) = run_rule(ev)
    assert v != "PASS", (st, ld, v)
    return f"T3 capacity: flow ${fd:,.0f}/day ret {st['ret']*100:+.1f}c -> 10% slice ${md:,.0f}/day (lo ${ld:,.0f}) {v}"


def test_dead_excluded():
    ev = ladder(40, 0.995, lambda k: True, 20000)
    fl = size.flow(ev, 0, 10**11)["us-gas-price-daily"]
    assert fl["qual"] == 0 and fl["dead"] > 0, fl
    rows = size.rule_rows(ev, "daily_bottom", 0, 10**11, np.random.default_rng(0))
    assert rows == [], rows
    return "T4 dead buckets excluded from flow and rules"


if __name__ == "__main__":
    fails = 0
    for f in (test_planted, test_null, test_capacity, test_dead_excluded):
        try: print("PASS", f())
        except AssertionError as e: fails += 1; print("FAIL", f.__name__, e)
    raise SystemExit(fails)
