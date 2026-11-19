#!/usr/bin/env python3
"""Gas resolution-window test on Polymarket 'US gas price on <date>' events (analysis only, public data).
For each resolved event: from time Tk (AAA value assumed knowable: 23:15 America/New_York on D-1, or a 2am-ET sensitivity),
until the event end (10:00 ET on D), what did takers pay for the WINNING token? Input: pm_hist.json, pm_trades.json."""
import json, sys, time, calendar, numpy as np
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
NY = ZoneInfo("America/New_York")
def end_ts(s): return calendar.timegm(time.strptime(s[:19], "%Y-%m-%dT%H:%M:%S"))
def tk_ts(end, hh, mm, day_offset):   # local ET wall time on D-1 (day_offset=-1) or D (0)
    e = datetime.fromtimestamp(end, timezone.utc).astimezone(NY)
    d = (e + __import__('datetime').timedelta(days=day_offset)).replace(hour=hh, minute=mm, second=0, microsecond=0)
    return int(d.timestamp())
def event_stats(rec, trades, tk, pmax, fee=0.0):
    """trades: dict cond->list. Returns dict for one event. Winner token = the token that resolved to 1."""
    end = end_ts(rec["end"]); out = {"slug": rec["slug"], "vol_total": float(rec["vol"] or 0)}
    n_shares = 0.0; cost = 0.0; edge = 0.0; n_tr = 0; first_hi = None; last_lo = None; mkt_vol_after = 0.0
    for m in rec["mk"]:
        res = json.loads(m["res"]); yes_wins = res[0] == "1"
        win_idx = 0 if yes_wins else 1
        for t in trades.get(m["cond"], []):
            if not (tk <= t["timestamp"] <= end): continue
            mkt_vol_after += t["size"] * t["price"]
            if t["outcome_index"] != win_idx: continue
            if t["price"] >= 0.9 and (first_hi is None or t["timestamp"] < first_hi): first_hi = t["timestamp"]
            if t["price"] < 0.9: last_lo = max(last_lo or 0, t["timestamp"])
            if t["side"] == "BUY" and t["price"] <= pmax:
                n_shares += t["size"]; cost += t["size"] * t["price"]; edge += t["size"] * (1 - t["price"] - fee); n_tr += 1
    out.update(shares=n_shares, cost=cost, edge=edge, n_tr=n_tr, vol_after=mkt_vol_after,
               hi_lag_min=None if first_hi is None else (first_hi - tk) / 60.0,
               last_lo_lag_min=None if last_lo is None else (last_lo - tk) / 60.0)
    return out
def boot_ci(x, rng, draws=4000):
    x = np.asarray(x, float)
    if len(x) == 0: return (float("nan"),) * 3
    idx = rng.integers(0, len(x), (draws, len(x))); m = x[idx].mean(1)
    return float(x.mean()), float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))
def run(hist, trades, tkspec, pmax, share, exclude=(), fee=0.0, seed=20261119):
    rng = np.random.default_rng(seed); rows = []
    for slug, rec in sorted(hist.items(), key=lambda kv: kv[1]["end"]):
        if any(slug.endswith(x) for x in exclude): continue
        tk = tk_ts(end_ts(rec["end"]), *tkspec)
        rows.append(event_stats(rec, trades, tk, pmax, fee))
    per = [share * r["edge"] for r in rows]          # $ per day at 'share' of the printed taker volume
    m, lo, hi = boot_ci(per, rng)
    return rows, {"days": len(rows), "perday": m, "lo": lo, "hi": hi, "shares_per_day": float(np.mean([r["shares"] for r in rows])),
                  "cost_per_day": float(np.mean([share * r["cost"] for r in rows])), "events_with_any": int(sum(1 for r in rows if r["shares"] > 0))}
if __name__ == "__main__":
    hist = json.load(open("pm_hist.json")); trades = json.load(open("pm_trades.json"))
    for lab, spec in (("Tk 23:15 ET D-1 (Nick)", (23, 15, -1)), ("Tk 02:00 ET D (late days)", (2, 0, 0))):
        for pmax in (0.90, 0.97):
            for ex, exl in (((), "all days"), ((("november-14-2026",)), "without 14 Nov")):
                rows, s = run(hist, trades, spec, pmax, 0.10, ex)
                print(f"{lab} | buy winner at <= {pmax} | {exl} | days {s['days']} ({s['events_with_any']} with prints) | taker shares/day {s['shares_per_day']:.0f} | 10% slice $/day {s['perday']:.1f} (95% CI {s['lo']:.1f}, {s['hi']:.1f}) | capital/day ${s['cost_per_day']:.1f}")
