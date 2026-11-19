"""spx/spy-open pre-open test with the Polymarket SP500-USD perp 1 s marks (Nick 06:24Z). Reuses the perps thread's markets and own-token trades
(weekend-perps/open-contracts-2026-11-19/run-2026-11-19/{markets,trades,yahoo}.json.gz, 3 Aug-18 Nov) and fetches 1 s marks for 09:20:00-09:30:15 ET and the prior 16:00 ET.
Signal at time s: sign of perp(s-1) / perp(prior 16:00 ET) - 1 (only marks at or before s-1). Own-token BUY prints on the picked token in [-300 s, +10 s] around 09:30:00 ET.
P&L per share = win - price; no fees. Buckets are seconds relative to the open."""
import bisect, collections, datetime as dt, gzip, json, math, os, sys, time
import numpy as np, pandas as pd, requests
from zoneinfo import ZoneInfo
ET = ZoneInfo("America/New_York")
D = "/home/user/oc"; P = "https://api.perpetuals.polymarket.com"; H = {"user-agent": "Mozilla/5.0 (data-logger)"}
BUCKETS = [(-300, -180), (-180, -60), (-60, -10), (-10, 0), (0, 10)]


def get(u, **q):
    for k in range(5):
        try:
            r = requests.get(u, params=q, timeout=40, headers=H)
            if r.status_code == 200: return r.json()
        except Exception: pass
        time.sleep(1.5)
    return None


def marks(iid, t0, t1, cache={}):
    key = (iid, t0, t1)
    p = f"/home/user/pk_cache/perp_{t0}_{t1}.json"
    if os.path.exists(p): return json.load(open(p))
    r = get(P + "/v1/info/mark-history", instrument_id=iid, interval="1s", start_timestamp=t0 * 1000, end_timestamp=t1 * 1000)
    pts = [(x[0] / 1000, float(x[1])) for x in (r or {}).get("data", [])]
    json.dump(pts, open(p, "w")); return pts


def at(pts, s):
    """last mark at or before s (and not older than 120 s)"""
    ts = [x[0] for x in pts]; i = bisect.bisect_right(ts, s) - 1
    return pts[i][1] if i >= 0 and s - ts[i] <= 120 else None


def main():
    mk = json.load(gzip.open(f"{D}/markets.json.gz"))["markets"]; tr = json.load(gzip.open(f"{D}/trades.json.gz")); yh = json.load(gzip.open(f"{D}/yahoo.json.gz"))
    ins = get(P + "/v1/info/instruments"); ins = ins["data"] if isinstance(ins, dict) else ins
    iid = [i["instrument_id"] for i in ins if i["symbol"] == "SP500-USD"][0]
    bars = yh["^GSPC"]["bars"]; days = sorted(bars)
    dates = sorted({m["date"] for m in mk}); pm = {}
    for d in dates:
        y, mo, dd = map(int, d.split("-")); o = dt.datetime(y, mo, dd, 9, 30, tzinfo=ET).timestamp()
        i = days.index(d) if d in days else None
        if not i: continue
        prev = days[i - 1]; py, pmo, pd_ = map(int, prev.split("-")); pc = dt.datetime(py, pmo, pd_, 16, 0, tzinfo=ET).timestamp()
        cl = [bars[k]["c"] for k in days[max(0, i - 21):i]]
        sig = float(np.std(np.diff(np.log(cl)), ddof=1)) if len(cl) >= 6 else None
        pm[d] = dict(o=o, w=marks(iid, int(o - 600), int(o + 15)), ref=at(marks(iid, int(pc - 300), int(pc + 5)), pc), sig=sig)
    rows = []; chk = []
    for m in mk:
        d = m["date"]
        if d not in pm or not pm[d]["ref"] or not pm[d]["sig"]: continue
        o = pm[d]["o"]; w = pm[d]["w"]; ref = pm[d]["ref"]; sig = pm[d]["sig"]
        up_won = m["up_price"] == 1.0
        t = tr[m["slug"]]
        # nowcast quality at three clocks: perp sign vs outcome, vs the market favourite (last own-token UP print within 10 min)
        for off in (-300, -120, -30, -5):
            pk = at(w, o + off)
            if pk is None: continue
            ret = pk / ref - 1
            ups = sorted((x["timestamp"], x["price"]) for x in t if x["token_id"] == m["up_token"] and x["timestamp"] <= o + off and o + off - x["timestamp"] <= 600)
            mkt = (ups[-1][1] >= 0.5) if ups else None
            chk.append(dict(prod=m["prod"], date=d, off=off, ret=ret, z=abs(ret) / sig, perp_hit=((ret > 0) == up_won), mkt_hit=(None if mkt is None else (mkt == up_won))))
        for x in t:
            s = x["timestamp"] - o
            if x["side"] != "BUY" or not (-300 <= s < 10): continue
            pk = at(w, x["timestamp"] - 1)
            if pk is None: continue
            ret = pk / ref - 1; pick_up = ret > 0
            tok = m["up_token"] if pick_up else m["dn_token"]
            if x["token_id"] != tok: continue
            won = (pick_up == up_won)
            rows.append(dict(prod=m["prod"], date=d, s=s, price=x["price"], size=x["size"], z=abs(ret) / sig, won=won, ret=ret))
    df = pd.DataFrame(rows); ck = pd.DataFrame(chk)
    out = "out/listing1"; df.to_csv(f"{out}/open_perp_prints.csv", index=False); ck.to_csv(f"{out}/open_perp_check.csv", index=False)
    ndays = len(pm); nd_by = collections.Counter(m["prod"] for m in mk if m["date"] in pm)
    print("dates", ndays, "events", sum(nd_by.values()), dict(nd_by))
    print("\nperp sign hit vs market favourite hit (all events with a market print), by clock:")
    c = ck.dropna(subset=["mkt_hit"]); print(c.groupby("off").agg(n=("perp_hit", "size"), perp=("perp_hit", "mean"), mkt=("mkt_hit", "mean")).round(3).to_string())
    c2 = ck[ck.z >= 0.1]; print("z>=0.1 perp hit by clock:"); print(c2.groupby("off").agg(n=("perp_hit", "size"), perp=("perp_hit", "mean")).round(3).to_string())
    df["usd"] = df.price * df["size"]; df["pnl"] = (df.won.astype(float) - df.price) * df["size"]
    res = []
    for a, b in BUCKETS:
        g = df[(df.s >= a) & (df.s < b)]
        gl = g[g.price < 0.95]
        res.append(dict(bucket=f"{a}..{b}s", prints=len(g), cost=g.usd.sum() / ndays, pnl_per_day=g.pnl.sum() / ndays, edge_per_share=(g.pnl.sum() / g["size"].sum() if len(g) else np.nan),
                        hit=g.won.mean() if len(g) else np.nan, mean_price=(g.usd.sum() / g["size"].sum() if len(g) else np.nan),
                        lt95_prints=len(gl), lt95_cost_day=gl.usd.sum() / ndays, lt95_pnl_day=gl.pnl.sum() / ndays, lt95_edge=(gl.pnl.sum() / gl["size"].sum() if len(gl) else np.nan)))
    r = pd.DataFrame(res); pd.set_option("display.width", 250); print("\nper-day figures use all", ndays, "dates in the denominator"); print(r.round(3).to_string(index=False))
    r.to_csv(f"{out}/open_perp_buckets.csv", index=False)
    for pr in ("SPX", "SPY"):
        g = df[df["prod"] == pr]; print(pr, "pnl/day all buckets %.1f  cost/day %.1f  (<0.95: %.1f)" % (g.pnl.sum() / ndays, g.usd.sum() / ndays, g[g.price < 0.95].pnl.sum() / ndays))
    # day-level concentration
    d = df[df.price < 0.95].groupby("date").pnl.sum().sort_values(ascending=False); print("top days of <0.95 pnl:", d.head(5).round(1).to_dict(), "days with any:", len(d), "total", d.sum().round(1))
    # bootstrap CI on pnl/day (days as units), all buckets, price<0.95 filter excluded
    byday = df.groupby("date").pnl.sum().reindex(sorted(pm), fill_value=0.0).values; rng = np.random.default_rng(7)
    bs = [rng.choice(byday, len(byday)).mean() for _ in range(5000)]; print("pnl/day mean %.2f CI %.2f..%.2f (days bootstrap)" % (byday.mean(), np.percentile(bs, 2.5), np.percentile(bs, 97.5)))
main()
