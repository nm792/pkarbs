"""Collect inputs for the open-contract test (public APIs, no keys). usage: collect.py OUTDIR [first_date last_date]
Writes markets.json, perp.json, yahoo.json, trades.json. Dates: trading days first..last inclusive (default 2026-08-03 .. 2026-11-18)."""
import sys, json, time, datetime, calendar, os, requests
from oclib import open_ts, KS
OUT = sys.argv[1]; A = sys.argv[2] if len(sys.argv) > 2 else "2026-08-03"; Z = sys.argv[3] if len(sys.argv) > 3 else "2026-11-18"
G = "https://gamma-api.polymarket.com"; P = "https://api.perpetuals.polymarket.com"; D = "https://data-api.polymarket.com"
import os as _os, sys as _sys
_sys.path.insert(0, _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..", "perp-scan-2026-11-22"))
from pmtrades import check_rows   # R-080

def get(u, **q):
    for k in range(5):
        try:
            r = requests.get(u, params=q, timeout=40, headers={"user-agent": "Mozilla/5.0 (data-logger)"})
            if r.status_code == 200: return r.json()
            if r.status_code in (404,): return None
        except Exception as e: err = e
        time.sleep(1.5)
    return None
days = []; d = datetime.date.fromisoformat(A)
while d <= datetime.date.fromisoformat(Z):
    if d.weekday() < 5: days.append(d)
    d += datetime.timedelta(1)
mk = []; missing = []
for d in ([] if os.path.exists(OUT + '/markets.json') else days):
    for prod, pre in (("SPX", "spx"), ("SPY", "spy")):
        slug = f"{pre}-opens-up-or-down-on-{calendar.month_name[d.month].lower()}-{d.day}-{d.year}"
        e = get(G + "/events", slug=slug)
        if not e: missing.append((prod, d.isoformat(), "no event")); continue
        m = e[0]["markets"][0]; toks = json.loads(m["clobTokenIds"]); outs = json.loads(m["outcomes"]); pr = [float(x) for x in json.loads(m["outcomePrices"])]
        res = dict(zip(outs, pr))
        mk.append(dict(prod=prod, date=d.isoformat(), slug=slug, cond=m["conditionId"], up_token=toks[outs.index("Up")], dn_token=toks[outs.index("Down")],
                       up_price=res["Up"], dn_price=res["Down"], closed=bool(m.get("closed")), volume=m.get("volumeNum"), resolution=m.get("umaResolutionStatus"), start=m.get("startDate")))
if not os.path.exists(OUT + "/markets.json"): json.dump(dict(markets=mk, missing=missing), open(OUT + "/markets.json", "w"), indent=0)
mk = json.load(open(OUT + "/markets.json"))["markets"]; print("markets", len(mk))
# perp marks
ins = get(P + "/v1/info/instruments"); ins = ins["data"] if isinstance(ins, dict) else ins
iid = [i["instrument_id"] for i in ins if i["symbol"] == "SP500-USD"][0]; perp = {}
for date in ([] if os.path.exists(OUT + '/perp.json') else sorted({m["date"] for m in mk})):
    T = open_ts(date)
    for k in KS:
        t = int((T - k * 60) * 1000)
        r = get(P + "/v1/info/mark-history", instrument_id=iid, interval="1s", start_timestamp=t - 120000, end_timestamp=t + 1000)
        pts = [x for x in (r or {}).get("data", []) if x[0] <= t]
        perp[f"{date}|{k}"] = dict(ts=pts[-1][0], mark=float(pts[-1][1]), target=t) if pts else None
if not os.path.exists(OUT + "/perp.json"): json.dump(perp, open(OUT + "/perp.json", "w"))
perp = json.load(open(OUT + "/perp.json")); print("perp points", sum(1 for v in perp.values() if v), "of", len(perp))
# yahoo
yh = {}
for sym in ("^GSPC", "SPY"):
    r = get(f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}", period1=int(time.mktime(datetime.date(2026, 7, 1).timetuple())), period2=int(time.time()) + 86400, interval="1d", events="div")
    res = r["chart"]["result"][0]; q = res["indicators"]["quote"][0]
    bars = {datetime.datetime.fromtimestamp(t, datetime.timezone.utc).strftime("%Y-%m-%d"): dict(o=q["open"][i], c=q["close"][i]) for i, t in enumerate(res["timestamp"])}
    divs = {datetime.datetime.fromtimestamp(v["date"], datetime.timezone.utc).strftime("%Y-%m-%d"): v["amount"] for v in res.get("events", {}).get("dividends", {}).values()}
    yh[sym] = dict(bars=bars, divs=divs, tz=res["meta"].get("exchangeTimezoneName"), gmtoffset=res["meta"].get("gmtoffset"))
json.dump(yh, open(OUT + "/yahoo.json", "w")); print({k: len(v["bars"]) for k, v in yh.items()}, {k: v["divs"] for k, v in yh.items()})
# own-token trades
tr = {}
for m in mk:
    rows = []; cur = None
    while True:
        r = get(D + "/v2/trades", condition_id=m["cond"], limit=500, **({"cursor": cur} if cur else {}))
        if not r: break
        check_rows(r["data"], {m["cond"]}, m["slug"])   # R-080: v2 ignores unknown params; verify the filter took
        rows += [dict(token_id=x["token_id"], side=x["side"], price=x["price"], size=x["size"], timestamp=x["timestamp"]) for x in r["data"]]
        cur = r["pagination"].get("next_cursor")
        if not r["pagination"].get("has_more") or not cur: break
    tr[m["slug"]] = rows
json.dump(tr, open(OUT + "/trades.json", "w")); print("trades total", sum(len(v) for v in tr.values()), "markets with 0 trades", sum(1 for v in tr.values() if not v))
