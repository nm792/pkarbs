import json, os, sys, time, math, datetime as dt
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "forward"))
import elon_listing as E


def hourly_const(t0, v=2.0, days=25):
    start = (int(t0) // 3600) * 3600 - days * 86400
    return {start + 3600 * i: v for i in range(days * 24)}


def ev(end="2026-11-23T17:00:00Z"):
    qs = ["<40", "40-64", "65-89", "90-114", "115-139", "140-164", "165-189", "190-214", "215-239", "240+"]
    ms = []
    for i, q in enumerate(qs):
        ms.append(dict(question=f"Will Elon Musk post {q} tweets from November 21 to November 23, 2026?", conditionId=f"c{i}", outcomes='["Yes","No"]',
                       clobTokenIds=json.dumps([f"y{i}", f"n{i}"])))
    return dict(id="E1", title="t", endDate=end, markets=ms)


def test_parse_bracket():
    assert E.parse_bracket("Will Elon Musk post <40 tweets from") == (0, 39)
    assert E.parse_bracket("post 40-64 tweets") == (40, 64) and E.parse_bracket("post 240+ tweets")[1] > 10 ** 8
    assert E.parse_bracket("something else") is None


def test_model_probs_sum_and_pick():
    t0 = dt.datetime(2026, 11, 19, 17, 7, tzinfo=dt.timezone.utc).timestamp()
    h = hourly_const(t0, 2.0)                  # 2 per hour -> 96 per 48 h window
    od = E.orders_for(ev(), h, t0)
    assert abs(od["mu"] - 96 * (1 - 0.0342)) < 1e-6 and abs(sum(o["p"] for o in od["orders"]) - 1) < 0.01 and not od["stale"]
    best = max(od["orders"], key=lambda o: o["p"]); assert (best["lo"], best["hi"]) == (90, 114) or (best["lo"], best["hi"]) == (65, 89)


def test_stale_and_only_material_orders():
    t0 = dt.datetime(2026, 11, 19, 17, 7, tzinfo=dt.timezone.utc).timestamp()
    h = {k: v for k, v in hourly_const(t0 - 10 * 86400).items()}  # file ends 10 days before t0
    assert E.orders_for(ev(), h, t0)["stale"]
    od = E.orders_for(ev(), hourly_const(t0), t0)
    for o in od["orders"]:
        assert (o["shares"] > 0) == (o["p"] >= 0.10 and o["bid"] >= 0.02)
        if o["shares"] > 0: assert o["shares"] * o["bid"] <= E.STAKE_CAP + 1e-9 and o["bid"] <= o["p"] - 0.05 + 1e-9


def snap(t, asks):
    return dict(t_local=t, t_resp=t + .3, books={"y1": dict(asks=asks, bids=[(0.01, 10)], ts="1")})


def meta_for(bid=0.30, shares=100.0):
    return dict(orders=dict(orders=[dict(yes="y1", lo=40, hi=64, p=0.4, bid=bid, shares=shares)]))


def test_fill_at_ask_not_bid_and_no_fill_above_bid():
    m = meta_for(bid=0.30, shares=100)
    f = E.simulate(m, [snap(1, [(0.35, 500)]), snap(2, [(0.29, 40), (0.30, 30), (0.31, 999)])])[0]["fills"]
    assert [round(x["px"], 2) for x in f] == [0.29, 0.30] and abs(sum(x["shares"] for x in f) - 70) < 1e-9   # filled at asks 0.29/0.30, nothing at 0.31


def test_no_double_counting_same_level():
    m = meta_for(bid=0.30, shares=100)
    snaps = [snap(t, [(0.30, 40)]) for t in range(1, 6)]          # the same 40 shares displayed five times
    f = E.simulate(m, snaps)[0]["fills"]
    assert abs(sum(x["shares"] for x in f) - 40) < 1e-9


def test_settle_signs():
    fl = [dict(yes="y1", fills=[dict(px=0.30, shares=10)]), dict(yes="y2", fills=[dict(px=0.20, shares=10)])]
    pnl, stake = E.settle(fl, "y1"); assert abs(pnl - (7 - 2)) < 1e-9 and abs(stake - 5) < 1e-9


def test_cadence_and_poll_window():
    assert E.cadence_ok(0, 10, 0) == 1.0 and E.cadence_ok(0, 3600, 0) == 5.0 and E.cadence_ok(0, 20000, 0) == 30.0 and E.cadence_ok(0, 40000, 0) == 300.0
    assert E.in_poll_window(dt.datetime(2026, 11, 19, 17, 7, tzinfo=dt.timezone.utc)) and E.in_poll_window(dt.datetime(2026, 7, 19, 16, 7, tzinfo=dt.timezone.utc))
    assert not E.in_poll_window(dt.datetime(2026, 11, 19, 12, 0, tzinfo=dt.timezone.utc))


def test_check_flags_bad_capture(tmp_path):
    d = tmp_path / "E1"; d.mkdir()
    toks = [t for i in range(10) for t in (f"y{i}", f"n{i}")]
    brackets = [dict(yes=f"y{i}", no=f"n{i}", lo=0, hi=0, cond=f"c{i}") for i in range(10)]
    t0 = time.time()
    meta = dict(t0=t0, createdAt=dt.datetime.fromtimestamp(t0 - 5, dt.timezone.utc).isoformat().replace("+00:00", "Z"), tokens=toks, brackets=brackets,
                orders=dict(orders=[dict(p=0.1) for _ in range(10)], stale=False, hourly_age_days=0.1))
    json.dump(meta, open(d / "meta.json", "w"))
    good = {t: dict(asks=[(0.2, 5)], bids=[(0.1, 5)], ts="1") for t in toks}
    with open(d / "books.jsonl", "w") as f:
        for i in range(30): f.write(json.dumps(dict(t_local=t0 + i, t_resp=t0 + i + .2, books=good)) + "\n")
    r = {n: ok for n, ok, _ in E.check(str(tmp_path))}; assert all(r.values()), r
    bad = dict(good); bad["y3"] = dict(asks=[(0.1, 5)], bids=[(0.2, 5)], ts="1")      # crossed book
    with open(d / "books.jsonl", "w") as f:
        for i in range(30): f.write(json.dumps(dict(t_local=t0 + i * 15, t_resp=t0 + i * 15 + .2, books=bad)) + "\n")
    r = {n: ok for n, ok, _ in E.check(str(tmp_path))}
    assert not r["bid < ask and prices in (0,1)"] and not r["snapshot gaps first 5 min"]


def test_refresh_merges_and_reports_age(tmp_path):
    import refresh_elon_hourly as R, json as j
    p = tmp_path / "h.json"; now = dt.datetime(2026, 11, 20, 12, 30, tzinfo=dt.timezone.utc).timestamp()
    j.dump({"2026-11-19T10:00:00.000Z": 1}, open(p, "w"))
    def g(url):
        if url.endswith("/trackings"): return {"data": [dict(id="a", endDate="2026-11-30T00:00:00Z"), dict(id="old", endDate="2026-01-01T00:00:00Z")]}
        assert "/a?" in url; return {"data": {"stats": {"daily": [{"date": "2026-11-20T10:00:00.000Z", "count": 5}, {"date": "2026-11-19T10:00:00.000Z", "count": 2}]}}}
    n, age = R.refresh(str(p), 40, getter=g, now=now)
    h = j.load(open(p)); assert n == 2 and h["2026-11-19T10:00:00.000Z"] == 2 and abs(age - 2.5) < 1e-9
