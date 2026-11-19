"""Close race: winner-token BUY (<0.95) profit per day by seconds after 16:00:00 ET (market close), and PM convergence latency, per series.
Resolution sources: SPX/DJIA/RUT = WSJ 'Close' (Historical Prices); SPY/META/NVDA/PLTR = Pyth 1-minute candle Close of the final regular minute."""
import collections, datetime as dt, os, sys
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import screen, listing_study as L
ET = L.ET
SER = {"spx-daily-up-or-down": "WSJ", "dow-jones-daily-up-or-down": "WSJ", "russell-2000-daily-up-or-down": "WSJ", "spy-daily-up-or-down": "Pyth", "meta-daily-up-down": "Pyth", "nvda-daily-up-down": "Pyth", "pltr-daily-up-or-down": "Pyth"}
EDGES = [(-300, 0, "last5m<16:00"), (0, 3, "0-3s"), (3, 10, "3-10s"), (10, 30, "10-30s"), (30, 60, "30-60s"), (60, 300, "1-5m"), (300, 1800, "5-30m")]

def load(first="2026-01-01"):
    import json, collections
    out = collections.defaultdict(dict)
    for p in ("/home/user/pk_cache/events.jsonl", "/home/user/pk_cache/events_deep.jsonl"):
        for l in open(p):
            e = json.loads(l)
            if e.get("seriesSlug") in SER and len(e["markets"]) == 1: out[e["seriesSlug"]][e["id"]] = e
    return out

def main():
    ev = load(); rows = []; lat = []
    for s, es in ev.items():
        for e in es.values():
            b = screen.binary_resolved(e["markets"][0])
            if not b: continue
            end = screen.parse_ts(e["endDate"]); d = dt.datetime.fromtimestamp(end - 7200, ET).date()
            c = dt.datetime(d.year, d.month, d.day, 16, 0, tzinfo=ET).timestamp()
            tr = screen.get_trades(b["cond"])["rows"]; win = b["tokens"][b["win"]]
            r = dict(series=s, src=SER[s], month=str(d)[:7], date=str(d), vol=b["vol"])
            for a, z, n in EDGES:
                r[n] = sum((1 - x[3]) * x[4] for x in tr if x[2] == win and x[1] == "BUY" and x[3] < 0.95 and c + a <= x[0] < c + z)
            # convergence: first winner print >= 0.95 at/after 15:55; was it already >=0.95 at 15:59:59?
            wp = sorted((x[0], x[3]) for x in tr if x[2] == win)
            pre = [p for t, p in wp if t < c]; r["win_px_at_close"] = pre[-1] if pre else np.nan
            post = [(t, p) for t, p in wp if t >= c]
            r["first_print_after_s"] = (post[0][0] - c) if post else np.nan
            hi = [t for t, p in post if p >= 0.95]; r["first_ge95_after_s"] = (hi[0] - c) if hi else np.nan
            r["converged_before_close"] = bool(pre and pre[-1] >= 0.95)
            r["closed_after_s"] = (screen.parse_ts(e["markets"][0].get("closedTime")) or np.nan) - c if e["markets"][0].get("closedTime") else np.nan
            rows.append(r)
    df = pd.DataFrame(rows); df.to_csv("out/listing1/close_race_days.csv", index=False)
    pd.set_option("display.width", 250); pd.set_option("display.max_columns", 30)
    cols = [n for _, _, n in EDGES]
    g = df.groupby("series")[cols].mean(); g["days"] = df.groupby("series").size(); g["vol/day"] = df.groupby("series").vol.mean()
    g["after_3s"] = g[["3-10s", "10-30s", "30-60s", "1-5m", "5-30m"]].sum(axis=1); print(g.round(1).to_string())
    h = df.groupby("series").agg(conv_before=("converged_before_close", "mean"), px_close=("win_px_at_close", "median"), first_print_s=("first_print_after_s", "median"),
                                 ge95_s=("first_ge95_after_s", "median"), closed_after_s=("closed_after_s", "median")); print(h.round(2).to_string())
    for sr in ("spx-daily-up-or-down", "spy-daily-up-or-down"):
        x = df[df.series == sr].groupby("month")[cols].mean(); x["days"] = df[df.series == sr].groupby("month").size(); x["vol"] = df[df.series == sr].groupby("month").vol.mean(); print(sr); print(x.round(1).to_string())
    g.to_csv("out/listing1/close_race_series.csv")
main()
