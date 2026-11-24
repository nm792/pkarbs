#!/usr/bin/env python3
"""Raw data for the weekly-touch vs perp-gap test (LOCKED-RULE-touch-gap-2026-11-22.md). Collects only; computes no outcome number.
Usage: python3 collect_touch.py RUNDIR   -> RUNDIR/touch_events.json.gz, touch_candles.json.gz, touch_closes.json
Public APIs only (gamma, data-api, Hyperliquid info, Yahoo chart). Idempotent per stage (skips a finished file)."""
import calendar, datetime, gzip, json, os, sys, time, urllib.parse, urllib.request
from universe import UNDER
from pmtrades import check_rows   # R-080

G = "https://gamma-api.polymarket.com"; D = "https://data-api.polymarket.com"
TKS = ["xauusd", "xagusd", "ng", "nvda", "aapl", "msft", "meta", "googl", "tsla", "coin", "hood", "pltr", "mu", "amzn", "mstr", "nflx"]
FIRST = datetime.date(2026, 5, 4); LAST = datetime.date(2026, 11, 16)


def req(u, body=None, tries=4):
    err = None
    for i in range(tries):
        try:
            r = urllib.request.Request(u, data=json.dumps(body).encode() if body is not None else None,
                                       headers={"user-agent": "data-scan", "content-type": "application/json"})
            return json.load(urllib.request.urlopen(r, timeout=60))
        except Exception as e:
            err = repr(e)[:100]; time.sleep(1 + 2 * i)
    return {"_error": err}


def mondays():
    d = FIRST
    while d <= LAST:
        yield d
        d += datetime.timedelta(days=7)


def slug(tk, d):
    return "will-%s-hit-week-of-%s-%d-%d" % (tk, calendar.month_name[d.month].lower(), d.day, d.year)


def trades(event_id, conds):
    rows, cur = [], None
    for _ in range(200):
        r = req(D + "/v2/trades?event_id=%s&limit=500" % event_id + ("&cursor=" + urllib.parse.quote(cur) if cur else ""))
        if not isinstance(r, dict) or "_error" in r:
            return rows, False
        data = r.get("data") or []
        check_rows(data, conds, "event %s" % event_id)   # R-080
        rows += [dict(c=x.get("condition_id"), tok=x.get("token_id"), side=x.get("side"), p=x["price"], s=x["size"], t=x["timestamp"], o=x.get("outcome")) for x in data]
        pg = r.get("pagination") or {}
        if not data or not pg.get("has_more") or not pg.get("next_cursor"):
            return rows, True
        cur = pg["next_cursor"]
    return rows, False


def main(run):
    p_ev = run + "/touch_events.json.gz"
    if not os.path.exists(p_ev):
        out = []
        for d in mondays():
            for tk in TKS:
                e = req(G + "/events?slug=" + slug(tk, d))
                if not isinstance(e, list) or not e:
                    out.append(dict(tk=tk, monday=str(d), found=False)); continue
                e = e[0]
                ms = [dict(cid=m.get("conditionId"), q=m.get("question"), outcomes=m.get("outcomes"), tokens=m.get("clobTokenIds"), prices=m.get("outcomePrices"),
                           closed=m.get("closed"), fee=m.get("feeSchedule")) for m in e.get("markets") or []]
                tr, ok = trades(e["id"], {m["cid"] for m in ms if m.get("cid")})
                out.append(dict(tk=tk, monday=str(d), found=True, id=e["id"], closed=e.get("closed"), markets=ms, trades=tr, trades_complete=ok))
                print(slug(tk, d), "markets", len(ms), "trades", len(tr), ok, flush=True)
        with gzip.open(p_ev, "wt") as f: json.dump(out, f)
    p_c = run + "/touch_candles.json.gz"
    if not os.path.exists(p_c):
        cand = {}
        for d in mondays():
            t0 = int(datetime.datetime(d.year, d.month, d.day, tzinfo=datetime.timezone.utc).timestamp() * 1000) - 24 * 3600 * 1000  # Sunday 00:00Z
            t1 = t0 + 41 * 3600 * 1000                                                                                                   # Monday 17:00Z
            for tk in TKS:
                sym = UNDER[tk][0]
                r = req("https://api.hyperliquid.xyz/info", {"type": "candleSnapshot", "req": {"coin": "xyz:" + sym, "interval": "1h", "startTime": t0, "endTime": t1}})
                cand["%s|%s" % (tk, d)] = [[c["T"], float(c["c"])] for c in r] if isinstance(r, list) else None
            print("candles", d, flush=True)
        with gzip.open(p_c, "wt") as f: json.dump(cand, f)
    p_y = run + "/touch_closes.json"
    if not os.path.exists(p_y):
        cl = {}
        for tk in TKS:
            sym = UNDER[tk][1]
            r = req("https://query1.finance.yahoo.com/v8/finance/chart/%s?range=1y&interval=1d" % urllib.parse.quote(sym))
            try:
                x = r["chart"]["result"][0]
                ts = x["timestamp"]; c = x["indicators"]["quote"][0]["close"]
                cl[tk] = {datetime.datetime.fromtimestamp(t, datetime.timezone.utc).strftime("%Y-%m-%d"): v for t, v in zip(ts, c) if v is not None}
            except Exception:
                cl[tk] = None
        json.dump(cl, open(p_y, "w"))
    print("collect done")


if __name__ == "__main__":
    main(sys.argv[1])
