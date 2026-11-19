"""Daily-series listing study (Nick 06:05Z 19 Nov): for each series, (1) listing time and first-30-min own-token price path,
(2) public input, (3) nowcast + boundary-distance rule vs the market at +1 and +10 min, (4) printed depth.

Nowcast for Up/Down daily series: sign of (last 5m bar CLOSED at or before decision time t) / (prior regular-session close) - 1.
Boundary rule: z = |ret| / sigma_daily (sigma = std of the previous 20 daily close-to-close returns); trade only if z >= ZMIN.
Market price = the chosen token's OWN last print at/before t (never 1 - other token), then at t+1 and t+10 min.
Resolution: spx-open / spy-open use the OPEN (regular-session first bar open) vs prior close; others use the close vs prior close.
"""
import bisect, collections, concurrent.futures as cf, datetime as dt, json, math, os, sys
from zoneinfo import ZoneInfo
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pit_store as P, screen, ext

ET = ZoneInfo("America/New_York")
CACHE = "/home/user/pk_cache/hist"
# series -> (yahoo ticker used for the nowcast, resolves on 'open' or 'close')
SERIES = {"spx-open-daily-up-or-down": ("SPY", "open"), "spx-daily-up-or-down": ("^GSPC", "close"),
          "spy-daily-up-or-down": ("SPY", "close"), "dow-jones-daily-up-or-down": ("^DJI", "close"),
          "russell-2000-daily-up-or-down": ("^RUT", "close"), "meta-daily-up-down": ("META", "close"),
          "nvda-daily-up-down": ("NVDA", "close"), "pltr-daily-up-or-down": ("PLTR", "close")}
# decision clocks, ET wall time. Open-series: only before 09:30 (outcome known at the open).
CLOCKS_ET = [(4, 0), (8, 0), (9, 0), (9, 25), (10, 0), (11, 0), (12, 0), (13, 0), (14, 0), (15, 0)]
ZMIN = 0.5


def session_days(ts, px):
    """group 5m bars by ET date -> regular session (09:30-16:00 ET) arrays. bar ts = bar START."""
    by = collections.defaultdict(list)
    for t, p in zip(ts, px):
        d = dt.datetime.fromtimestamp(t, ET)
        by[d.date()].append((t, d.hour * 60 + d.minute, p))
    return by


def build(tk, cache_dir="/home/user/pk_cache/yahoo"):
    p = f"{cache_dir}/{tk.replace('^','_').replace('=','_')}.json"
    r = json.load(open(p))["chart"]["result"][0]
    ts = r["timestamp"]; q = r["indicators"]["quote"][0]
    rows = [(t, q["open"][i], q["close"][i]) for i, t in enumerate(ts) if q["close"][i] is not None and q["open"][i] is not None]
    t = np.array([x[0] for x in rows], float); o = np.array([x[1] for x in rows]); c = np.array([x[2] for x in rows])
    dd = collections.defaultdict(list)
    for i, tt in enumerate(t):
        d = dt.datetime.fromtimestamp(tt, ET); m = d.hour * 60 + d.minute
        if 570 <= m < 960: dd[d.date()].append(i)
    days = {d: dict(open=float(o[ix[0]]), close=float(c[ix[-1]]), n=len(ix)) for d, ix in dd.items() if len(ix) >= 20}
    return t, c, days


def prev_trading_day(days, d):
    ks = sorted(k for k in days if k < d)
    return ks[-1] if ks else None


def sigma(days, d, n=20):
    ks = sorted(k for k in days if k < d)[-(n + 1):]
    if len(ks) < 6: return None
    cl = np.array([days[k]["close"] for k in ks]); r = np.diff(np.log(cl))
    return float(r.std(ddof=1)) if len(r) >= 5 else None


def nowcast(t, c, days, d, t_dec):
    """return (ret, z) using only 5m bars whose END (start+300) <= t_dec and the prior regular close."""
    pd_ = prev_trading_day(days, d)
    if pd_ is None: return None
    s = sigma(days, d)
    if not s: return None
    i = bisect.bisect_right(t + 300, t_dec) - 1
    if i < 0 or t_dec - (t[i] + 300) > 3600: return None   # stale: no bar in the last hour
    ret = c[i] / days[pd_]["close"] - 1
    return ret, abs(ret) / s


def hist(token, t0, t1):
    os.makedirs(CACHE, exist_ok=True)
    p = f"{CACHE}/{token[:20]}_{int(t0)}_{int(t1)}.json"
    if os.path.exists(p): return json.load(open(p))
    d = P.http_json(f"https://clob.polymarket.com/prices-history?market={token}&startTs={int(t0)}&endTs={int(t1)}&fidelity=1")
    h = [(x["t"], x["p"]) for x in d.get("history", [])]
    json.dump(h, open(p, "w")); return h


def last_at(h, t, max_age=3600):
    """last own-token print at/before t (None if none or older than max_age s)."""
    ts = [x[0] for x in h]; i = bisect.bisect_right(ts, t) - 1
    if i < 0 or t - ts[i] > max_age: return None
    return h[i][1]


def load_events():
    out = collections.defaultdict(list)
    for path in ("/home/user/pk_cache/events.jsonl", "/home/user/pk_cache/events_deep.jsonl"):
        for l in open(path):
            e = json.loads(l)
            if e.get("seriesSlug") in SERIES and len(e["markets"]) == 1: out[e["seriesSlug"]].append(e)
    seen = set(); res = {}
    for s, es in out.items():
        u = {e["id"]: e for e in es}
        res[s] = sorted(u.values(), key=lambda e: e["endDate"])
    return res


def study(first="2026-09-02"):
    evs = load_events(); rows = []; listing = []
    tasks = []
    for s, es in evs.items():
        for e in es:
            if e["endDate"][:10] < first or e["endDate"][:10] > "2026-11-18": continue
            b = screen.binary_resolved(e["markets"][0])
            if not b: continue
            labs = [x.lower() for x in b["labels"]]
            if "up" not in labs: continue
            tasks.append((s, e, b, labs.index("up")))
    print(len(tasks), "markets", flush=True)
    tabs = {tk: build(tk) for tk in set(v[0] for v in SERIES.values())}

    def work(task):
        s, e, b, iu = task
        ls = screen.parse_ts(e["startDate"]); end = screen.parse_ts(e["endDate"])
        hu = hist(b["tokens"][iu], ls - 600, end + 3600); hd = hist(b["tokens"][1 - iu], ls - 600, end + 3600)
        tr = screen.get_trades(b["cond"])["rows"]
        return task, hu, hd, tr
    with cf.ThreadPoolExecutor(8) as ex:
        res = list(ex.map(work, tasks))
    for (s, e, b, iu), hu, hd, tr in res:
        tk, kind = SERIES[s]; t, c, days = tabs[tk]
        end = screen.parse_ts(e["endDate"]); ls = screen.parse_ts(e["startDate"])
        d = dt.datetime.fromtimestamp(end - 7200, ET).date()          # session date of the market
        if d not in days: continue
        pd_ = prev_trading_day(days, d)
        if pd_ is None: continue
        up_won = (b["win"] == iu)
        truth = bool(days[d]["open"] > days[pd_]["close"]) if kind == "open" else bool(days[d]["close"] > days[pd_]["close"])
        # sanity: Yahoo-derived truth must agree with the resolved outcome; mismatches are logged, not dropped silently
        agree = (truth == up_won)
        # listing path (up token own prints)
        lst = dict(series=s, date=str(d), listed=e["startDate"], first_print_s=None, p1=None, p5=None, p30=None, n5=0, n30=0, usd5=0.0, usd30=0.0)
        up_tok, dn_tok = b["tokens"][iu], b["tokens"][1 - iu]
        mine = sorted(r for r in tr if r[0] >= ls)
        if mine: lst["first_print_s"] = mine[0][0] - ls
        for lab, off in (("p1", 60), ("p5", 300), ("p30", 1800)): lst[lab] = last_at(hu, ls + off, 3600)
        for lab, off in (("5", 300), ("30", 1800)):
            w = [r for r in mine if r[0] <= ls + off]
            lst["n" + lab] = len(w); lst["usd" + lab] = float(sum(r[4] * r[3] for r in w))
        listing.append(lst)
        for hh, mm in CLOCKS_ET:
            t_dec = dt.datetime(d.year, d.month, d.day, hh, mm, tzinfo=ET).timestamp()
            if kind == "open" and (hh, mm) >= (9, 30): continue
            if t_dec >= end - 600: continue
            nc = nowcast(t, c, days, d, t_dec)
            pu = last_at(hu, t_dec); pu1 = last_at(hu, t_dec + 60); pu10 = last_at(hu, t_dec + 600)
            pdn = last_at(hd, t_dec); pdn1 = last_at(hd, t_dec + 60); pdn10 = last_at(hd, t_dec + 600)
            if nc is None or pu is None: continue
            ret, z = nc
            pick_up = bool(ret > 0)
            # printed depth on the picked token in [t_dec, t_dec+10min]: BUY prints only (takers lifting asks)
            tok = up_tok if pick_up else dn_tok
            w = [r for r in tr if r[2] == tok and r[1] == "BUY" and t_dec <= r[0] <= t_dec + 600]
            def fbuy(off):
                w2 = [r for r in tr if r[2] == tok and r[1] == "BUY" and t_dec + off <= r[0] <= t_dec + off + 900]
                return min(w2)[3] if w2 else None   # earliest BUY print at/after t+off (rows sorted by tuple: ts first)
            rows.append(dict(series=s, buy1=fbuy(60), buy10=fbuy(600), date=str(d), clock=f"{hh:02d}:{mm:02d}", ret=ret, z=z, nc_up=pick_up, up_won=up_won, agree=agree,
                             pu=pu, pu1=pu1, pu10=pu10, pdn=pdn, pdn1=pdn1, pdn10=pdn10,
                             fill_px=(pu1 if pick_up else pdn1), fill_px10=(pu10 if pick_up else pdn10),
                             depth_usd=float(sum(r[4] * r[3] for r in w)), depth_n=len(w)))
    return rows, listing


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "out/listing1"
    os.makedirs(out, exist_ok=True)
    rows, listing = study()
    json.dump(rows, open(f"{out}/rows.json", "w")); json.dump(listing, open(f"{out}/listing.json", "w"))
    print(len(rows), "decision rows,", len(listing), "listings")


if __name__ == "__main__":
    main()
