"""spx-open by month: event volume, volume in the open minute, ex-post winner-BUY pool (prints < 0.95) around 09:30 ET. Winner from the resolved outcome (no Yahoo)."""
import collections, concurrent.futures as cf, datetime as dt, json, os, sys
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import screen, listing_study as L
ET = L.ET

def main():
    ev = L.load_events()["spx-open-daily-up-or-down"]
    jobs = []
    for e in ev:
        b = screen.binary_resolved(e["markets"][0])
        if b: jobs.append((e, b))
    with cf.ThreadPoolExecutor(8) as ex:
        data = list(ex.map(lambda j: screen.get_trades(j[1]["cond"]), jobs))
    rows = []
    for (e, b), d in zip(jobs, data):
        tr = d["rows"]; end = screen.parse_ts(e["endDate"]); day = dt.datetime.fromtimestamp(end - 7200, ET).date()
        o = dt.datetime(day.year, day.month, day.day, 9, 30, tzinfo=ET).timestamp(); win = b["tokens"][b["win"]]
        def pool(a, z, side="BUY"):
            w = [r for r in tr if r[2] == win and r[1] == side and o + a <= r[0] < o + z and r[3] < 0.95]
            return sum(r[3] * r[4] for r in w), sum((1 - r[3]) * r[4] for r in w)
        tr_trunc = bool(d.get("trunc"))
        all_win = [r for r in tr if o - 300 <= r[0] < o + 900]
        c0, p0 = pool(0, 60); cpre, ppre = pool(-300, 0); clate, plate = pool(60, 900)
        rows.append(dict(date=str(day), month=str(day)[:7], vol=b["vol"], trunc=tr_trunc, n_trades=len(tr),
                         usd_open_window=float(sum(r[3] * r[4] for r in all_win)),
                         usd_open_minute=float(sum(r[3] * r[4] for r in tr if o <= r[0] < o + 60)),
                         cost_pre=cpre, profit_pre=ppre, cost_min0=c0, profit_min0=p0, cost_late=clate, profit_late=plate))
    df = pd.DataFrame(rows); df.to_csv("out/listing1/open_regime.csv", index=False)
    pd.set_option("display.width", 250)
    g = df.groupby("month").agg(days=("date", "size"), trunc=("trunc", "sum"), vol=("vol", "mean"), usd_open_window=("usd_open_window", "mean"), usd_open_min=("usd_open_minute", "mean"),
                                profit_pre=("profit_pre", "mean"), profit_min0=("profit_min0", "mean"), profit_late=("profit_late", "mean"), cost_min0=("cost_min0", "mean"))
    print(g.round(1).to_string())
main()
