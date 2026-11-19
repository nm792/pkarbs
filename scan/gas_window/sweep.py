#!/usr/bin/env python3
"""Gas daily-sweep timing on Polymarket 'US gas price on <date>' events. Analysis only, public /v2/trades data.
T_s = first trade of a burst where winner-side tokens are bought (side BUY, i.e. a taker lifting that token's own ask) in >= MINMK
different buckets within WIN seconds, searched inside 01:00-07:00 America/New_York on the event day. Reports, per event and pooled:
the UTC and ET time of T_s, and what was bought at what price (each token's own trade price) in lag windows after T_s."""
import json, sys, time, calendar, collections, numpy as np
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo
NY = ZoneInfo("America/New_York")
WIN, MINMK = 10, 3
LAGS = ((0, 10), (10, 60), (60, 600), (600, 3600))
def end_ts(s): return calendar.timegm(time.strptime(s[:19], "%Y-%m-%dT%H:%M:%S"))
def et_window(end, h0, h1):
    e = datetime.fromtimestamp(end, timezone.utc).astimezone(NY)
    d0 = e.replace(hour=h0, minute=0, second=0, microsecond=0)
    return int(d0.timestamp()), int((e.replace(hour=h1, minute=0, second=0, microsecond=0)).timestamp())
def winner_buys(rec, trades):
    out = []
    for m in rec["mk"]:
        res = json.loads(m["res"]); win_idx = 0 if res[0] == "1" else 1
        for t in trades.get(m["cond"], []):
            if t["outcome_index"] == win_idx: out.append((t["timestamp"], m["cond"], t["side"], t["price"], t["size"]))
    return sorted(out)
def find_sweep(wb, lo, hi):
    b = [x for x in wb if x[2] == "BUY" and lo <= x[0] <= hi]
    for i, x in enumerate(b):
        mk = {y[1] for y in b[i:] if y[0] - x[0] <= WIN}
        if len(mk) >= MINMK: return x[0]
    return None
def lag_stats(wb, ts_, pmax):
    res = []
    for a, b in LAGS:
        sh = cost = 0.0; n = 0
        for (t, c, side, p, s) in wb:
            if side == "BUY" and ts_ + a <= t < ts_ + b and p <= pmax: sh += s; cost += s * p; n += 1
        res.append({"lag": (a, b), "shares": sh, "cost": cost, "edge": sh - cost, "n": n})
    return res
def analyse(hist, trades, pmax=0.97, exclude=()):
    rows = []
    for slug, rec in sorted(hist.items(), key=lambda kv: kv[1]["end"]):
        if any(slug.endswith(x) for x in exclude): continue
        end = end_ts(rec["end"]); lo, hi = et_window(end, 1, 7); wb = winner_buys(rec, trades)
        ts_ = find_sweep(wb, lo, hi)
        r = {"slug": slug, "t_sweep": ts_}
        if ts_ is not None: r["lags"] = lag_stats(wb, ts_, pmax)
        rows.append(r)
    return rows
def boot(x, rng, draws=4000):
    x = np.asarray(x, float)
    if len(x) == 0: return (float("nan"),) * 3
    m = x[rng.integers(0, len(x), (draws, len(x)))].mean(1); return float(x.mean()), float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))
if __name__ == "__main__":
    hist = json.load(open("pm_hist.json")); trades = json.load(open("pm_trades.json")); rng = np.random.default_rng(20261119)
    for lab, ex in (("all 28 days", ()), ("without 14 Nov", ("november-14-2026",))):
        rows = analyse(hist, trades, 0.97, ex); found = [r for r in rows if r["t_sweep"] is not None]
        print(f"== {lab}: sweep found on {len(found)} of {len(rows)} days")
        et = [(datetime.fromtimestamp(r["t_sweep"], timezone.utc).astimezone(NY)) for r in found]
        mins = [e.hour * 60 + e.minute + e.second / 60 for e in et]
        if mins: print(f"   sweep time ET: median {int(np.median(mins))//60:02d}:{int(np.median(mins))%60:02d}, min {int(min(mins))//60:02d}:{int(min(mins))%60:02d}, max {int(max(mins))//60:02d}:{int(max(mins))%60:02d}")
        for i, (a, b) in enumerate(LAGS):
            e = [r["lags"][i]["edge"] for r in rows if r["t_sweep"] is not None]
            e_all = [r["lags"][i]["edge"] if r["t_sweep"] is not None else 0.0 for r in rows]
            sh = [r["lags"][i]["shares"] for r in rows if r["t_sweep"] is not None]
            m, lo, hi = boot(e_all, rng)
            print(f"   +{a}..{b}s after sweep start: winner-token taker buys at <=0.97: {np.mean(sh):.0f} shares/day, edge at 100% ${m:.1f}/day (95% CI {lo:.1f}, {hi:.1f}), 10% slice ${m*0.1:.1f}/day")
    for r in analyse(hist, trades, 0.97):
        if r["t_sweep"]:
            e = datetime.fromtimestamp(r["t_sweep"], timezone.utc); print(r["slug"][-13:], e.strftime("%H:%M:%SZ"), e.astimezone(NY).strftime("%H:%M:%S ET"), " ".join(f"{l['shares']:.0f}sh/${l['edge']:.0f}" for l in r["lags"]))
        else: print(r["slug"][-13:], "no sweep found")
