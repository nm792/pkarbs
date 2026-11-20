"""No-hindsight backtest of rule.py on the recorded Polymarket tapes (35 events, 16 Oct-19 Nov 2026).
Model inputs per event (mean, sd) come from nowcast v0 computed BEFORE listing (data/nowcast_inputs.json, made by nohind.py: ridge alpha 10, spot_lag 2).
A taker BUY print at (price, size) is treated as an ask we could have lifted, up to its printed size: an UPPER bound (no queue, no latency).
Windows: PRE = listing .. 03:00 ET on D; POST = from 03:30 ET on D (AAA page read; the page value is taken as P_D = Kalshi expiration value / AAA page); 03:00-03:30 ET is skipped."""
import json, math, os, re, sys, datetime as dt, statistics
from zoneinfo import ZoneInfo
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, ".."))   # nowcast.py lives one folder up (model code stays separate from the rule)
import rule as R, nowcast as N
AAA = os.environ.get("GAS_AAA", "/mnt/project-files/gas/data/kalshi_aaa_prints_to_18nov.json")   # Kalshi KXAAAGASD expiration values (analysis only, A6)
TAPE = os.environ.get("GAS_TAPE", "/mnt/project-files/gas/data/gas_all_markets_16oct-19nov.json")   # 212 KB tape, regenerate with pull_all.py; sha256 b6f4d526b5f5e88c... in the REPLY
ET = ZoneInfo("America/New_York")
def bounds(q): return N.bucket_bounds(q)
def load(P_extra={dt.date(2026, 11, 19): 3.7212}):
    P = N.load_prints(AAA); P.update(P_extra)
    mk = json.load(open(TAPE)); nh = json.load(open(os.path.join(HERE, "data", "nowcast_inputs.json")))
    ev = {}
    for m in mk: ev.setdefault(m["date"], []).append(m)
    return P, ev, nh
def run_event(date, ms, nh, P, prm, rules=("yes_fav", "no_out", "post")):
    D = dt.date.fromisoformat(date); ms = sorted(ms, key=lambda m: bounds(m["q"])[0]); bs = [bounds(m["q"]) for m in ms]
    mean, sd = nh["mean"], nh["sd"]
    q = [N.norm_cdf((hi - mean) / sd) - N.norm_cdf((lo - mean) / sd) for lo, hi in bs]; s = sum(q); q = [x / s for x in q]
    actual = P[D]; win = next(j for j, b in enumerate(bs) if b[0] <= actual < b[1]); fav = max(range(len(q)), key=lambda j: q[j])
    cr = dt.datetime.fromisoformat(min(m["created"] for m in ms).replace("Z", "+00:00")).timestamp()
    pre_end = dt.datetime(D.year, D.month, D.day, 3, 0, tzinfo=ET).timestamp(); post_start = dt.datetime(D.year, D.month, D.day, 3, 30, tzinfo=ET).timestamp()
    prints = sorted(((t[0], j, t[1], t[3], t[4]) for j, m in enumerate(ms) for t in m["tr"] if t[2] == "BUY"))   # ts, bucket idx, outcome, price, size
    spent = {}; spent_ev = {}; fills = []
    for ts, j, out, p, sz in prints:
        if ts < cr: continue
        yes = out == "Yes"; kind = None; qq = None
        if ts < pre_end:
            if "yes_fav" in rules and yes and j == fav: kind, qq = "yes_fav", q[j]
            elif "no_out" in rules and (not yes) and q[j] <= prm.out_q: kind, qq = "no_out", 1 - q[j]
        elif ts >= post_start and "post" in rules:
            kind, qq = "post", prm.post_q if (j == win) == yes else None     # YES of the page bucket, or NO of any other bucket
            if qq is None: kind = None
        if not kind: continue
        key = (j, out, kind); used = spent_ev.get(kind if prm.rule_caps else 'all', 0.0); sh = R.take(kind, qq, p, sz, spent.get(key, 0.0), used, prm)
        if sh <= 0: continue
        cost = sh * p; fee = R.fee_per_share(p, prm.fee_rate) * sh; wins = (j == win) == yes
        pnl = (sh * (1 - p) if wins else -cost) - fee
        spent[key] = spent.get(key, 0.0) + cost; spent_ev[kind if prm.rule_caps else 'all'] = used + cost; fills.append(dict(kind=kind, j=j, out=out, p=p, sh=sh, cost=cost, fee=fee, pnl=pnl, win=wins, ts=ts))
    return dict(date=date, fav=fav, win=win, q=q, fills=fills, ruled_out_won=[j for j in range(len(q)) if q[j] <= prm.out_q and j == win], n_ruled_out=sum(1 for x in q if x <= prm.out_q), q_win=q[win])
def summarize(res, label, skip=()):
    rs = [r for r in res if r["date"] not in skip]; n = len(rs); out = {}
    for kind in ("yes_fav", "no_out", "post", "ALL"):
        f = [x for r in rs for x in r["fills"] if kind == "ALL" or x["kind"] == kind]
        day = [sum(x["pnl"] for x in r["fills"] if kind == "ALL" or x["kind"] == kind) for r in rs]
        cost = sum(x["cost"] for x in f); pnl = sum(x["pnl"] for x in f)
        out[kind] = dict(fills=len(f), shares=sum(x["sh"] for x in f), cost=cost, pnl=pnl, per_day=pnl / n, worst_day=min(day), best_day=max(day), days_traded=sum(1 for d in day if d != 0),
                        hit=(sum(1 for x in f if x["win"]) / len(f)) if f else float("nan"), roc=(pnl / cost) if cost else float("nan"), losing_days=sum(1 for d in day if d < 0))
    print(f"== {label}: {n} days")
    for k, v in out.items():
        print(f"  {k:8} fills {v['fills']:4d} shares {v['shares']:8.0f} cost ${v['cost']:8.0f} net ${v['pnl']:8.1f} per day ${v['per_day']:6.2f} return on cost {v['roc']*100:5.2f}% hit(by fill) {v['hit']*100:5.1f}% days traded {v['days_traded']:2d} losing days {v['losing_days']:2d} worst day ${v['worst_day']:7.1f} best ${v['best_day']:7.1f}")
    return out
if __name__ == "__main__":
    P, ev, nh = load()
    for name, prm in (("v1 shared cap 15% of bank per event", R.Params()), ("v2 per-rule caps: yes_fav 10%, no_out 5%, post 10%", R.Params(rule_caps=(("yes_fav", 0.10), ("no_out", 0.05), ("post", 0.10))))):
        print("#####", name)
        res = [run_event(d, ev[d], nh[d], P, prm) for d in sorted(ev) if d in nh]
        summarize(res, "ALL 35 events"); summarize(res, "excl 14 Nov", skip=("2026-11-14",))
    print("calibration: events", len(res), "| buckets with q<=0.02 per event (mean)", round(statistics.mean(r["n_ruled_out"] for r in res), 2), "| ruled-out buckets that WON:", sum(len(r["ruled_out_won"]) for r in res), "of", sum(r["n_ruled_out"] for r in res), "| mean q of the winning bucket", round(statistics.mean(r["q_win"] for r in res), 3))
    print("events where winner had q<=0.05:", [(r["date"], round(r["q_win"], 3)) for r in res if r["q_win"] <= 0.05])
    print("per-day net P&L (ALL rules):"); print([(r["date"][5:], round(sum(x["pnl"] for x in r["fills"]), 1)) for r in res])
