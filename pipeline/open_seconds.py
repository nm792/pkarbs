"""spx-open: winner-token BUY (<0.95) profit per day by seconds after 09:30:00 ET, by month. profit = size*(1-price)."""
import datetime as dt, os, sys, collections
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import screen, listing_study as L
ET = L.ET
EDGES = [(-300, 0, "pre-open -5m..0"), (0, 3, "0-3s"), (3, 10, "3-10s"), (10, 30, "10-30s"), (30, 60, "30-60s"), (60, 300, "1-5m")]

def main():
    rows = []
    for e in L.load_events()["spx-open-daily-up-or-down"]:
        b = screen.binary_resolved(e["markets"][0])
        if not b: continue
        end = screen.parse_ts(e["endDate"]); d = dt.datetime.fromtimestamp(end - 7200, ET).date()
        o = dt.datetime(d.year, d.month, d.day, 9, 30, tzinfo=ET).timestamp()
        tr = screen.get_trades(b["cond"])["rows"]; win = b["tokens"][b["win"]]
        r = dict(month=str(d)[:7], date=str(d))
        for a, z, n in EDGES:
            r[n] = sum((1 - x[3]) * x[4] for x in tr if x[2] == win and x[1] == "BUY" and x[3] < 0.95 and o + a <= x[0] < o + z)
        rows.append(r)
    df = pd.DataFrame(rows); df.to_csv("out/listing1/open_seconds_days.csv", index=False)
    g = df.groupby("month").mean(numeric_only=True); g["days"] = df.groupby("month").size()
    g["after_3s"] = g["3-10s"] + g["10-30s"] + g["30-60s"] + g["1-5m"]; g["after_10s"] = g["10-30s"] + g["30-60s"] + g["1-5m"]
    pd.set_option("display.width", 250); print(g.round(1).to_string())
    h = df[df.month < "2026-05"].mean(numeric_only=True); print("Jan-Apr mean/day:", h.round(1).to_dict())
    print("days with profit after 3s (Jan-Apr):", int(((df[df.month<'2026-05'][['3-10s','10-30s','30-60s','1-5m']].sum(axis=1))>0).sum()), "of", int((df.month<'2026-05').sum()))
    g.to_csv("out/listing1/open_seconds_month.csv")
main()
