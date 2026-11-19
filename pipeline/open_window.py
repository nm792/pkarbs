"""spx-open window study (Nick 06:16Z): volume by ET minute, and informed-taker depth after the open is public.
Outcome known from the official open (^GSPC first regular bar OPEN, available at 09:30:00 ET; I allow 09:31 for the print to publish)."""
import collections, datetime as dt, json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import screen, listing_study as L
ET = L.ET

def main():
    t, c, days = L.build("^GSPC")
    ev = L.load_events()["spx-open-daily-up-or-down"]
    rows = []; minute_vol = collections.Counter(); minute_n = collections.Counter()
    for e in ev:
        if not ("2026-09-02" <= e["endDate"][:10] <= "2026-11-18"): continue
        b = screen.binary_resolved(e["markets"][0])
        if not b: continue
        end = screen.parse_ts(e["endDate"]); d = dt.datetime.fromtimestamp(end - 7200, ET).date()
        if d not in days: continue
        pdy = L.prev_trading_day(days, d)
        up = bool(days[d]["open"] > days[pdy]["close"]); labs = [x.lower() for x in b["labels"]]
        if labs.index("up" if up else "down") != b["win"]: continue        # Yahoo outcome disagrees with resolved: drop
        tr = screen.get_trades(b["cond"])["rows"]; win = b["tokens"][b["win"]]; lose = b["tokens"][1 - b["win"]]
        o = dt.datetime(d.year, d.month, d.day, 9, 30, tzinfo=ET).timestamp()
        for r in tr:
            m = int((r[0] - o) // 60)
            if -60 <= m < 90: minute_vol[m] += r[3] * r[4]; minute_n[m] += 1
        def win_buys(a, z, cap=0.95):
            return [r for r in tr if r[2] == win and r[1] == "BUY" and o + a * 60 <= r[0] < o + z * 60 and r[3] < cap]
        # before-open: what the favourite-by-SPY-premarket would have bought is in listing_study; here after-open informed takers
        w = win_buys(1, 15)
        cost = sum(r[3] * r[4] for r in w); prof = sum((1 - r[3]) * r[4] for r in w)
        w0 = win_buys(-5, 1)
        rows.append(dict(date=str(d), vol=b["vol"], n_all_open_window=sum(1 for r in tr if o - 300 <= r[0] < o + 900),
                         usd_all_open_window=float(sum(r[3] * r[4] for r in tr if o - 300 <= r[0] < o + 900)),
                         winbuy_cost_0931_0945=float(cost), winbuy_profit_0931_0945=float(prof), n_winbuy=len(w),
                         winbuy_cost_0925_0931=float(sum(r[3] * r[4] for r in w0)), winbuy_profit_0925_0931=float(sum((1 - r[3]) * r[4] for r in w0)),
                         first_win_buy_s=(min(r[0] for r in w) - o) if w else None,
                         px_avg=(cost / sum(r[4] for r in w)) if w else None))
    json.dump(dict(rows=rows, minute_vol={k: v for k, v in sorted(minute_vol.items())}, minute_n=dict(sorted(minute_n.items()))), open("out/listing1/open_window.json", "w"))
    import pandas as pd
    r = pd.DataFrame(rows); print(len(r), "days")
    print("event vol/day: mean %.0f median %.0f" % (r.vol.mean(), r.vol.median()))
    print("traded $ 09:25-09:45 ET per day: mean %.0f median %.0f ; share of event volume %.1f%%" % (r.usd_all_open_window.mean(), r.usd_all_open_window.median(), 100 * r.usd_all_open_window.sum() / r.vol.sum()))
    print("winner BUY prints <0.95 in 09:31-09:45: days with any %d/%d ; cost mean %.0f median %.0f ; profit mean %.1f median %.1f" % ((r.n_winbuy > 0).sum(), len(r), r.winbuy_cost_0931_0945.mean(), r.winbuy_cost_0931_0945.median(), r.winbuy_profit_0931_0945.mean(), r.winbuy_profit_0931_0945.median()))
    print("pre-open 09:25-09:31 winner buys <0.95: cost mean %.0f profit mean %.1f" % (r.winbuy_cost_0925_0931.mean(), r.winbuy_profit_0925_0931.mean()))
    print("first winner buy after open s: median", r.first_win_buy_s.median(), "avg px", r.px_avg.mean())
    mv = pd.Series(minute_vol) / len(r)
    print("mean $/day by minute from the open:"); print(mv[(mv.index >= -30) & (mv.index < 30)].round(0).to_string())
main()
