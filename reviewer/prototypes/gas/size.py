#!/usr/bin/env python3
"""Reviewer prototype: size the gasoline (AAA national average) opportunity on Polymarket.

Analysis only. Places no orders, reads only public data from a snapshot made by pull.py.

What it measures (every number traces to the snapshot file passed in):
  1. Qualifying flow: $ traded per day at prices 0.05 <= p < 0.95, per series, over a window.
     Prices >= 0.99 are dead buckets (Nick); 0.95-0.99 is reported separately as near-dead.
  2. Capacity bound (model-free): $/day <= slice x qualifying $/day x edge per $.
     Gives the edge per $ that a 10% slice (and 100% of all flow) would need to reach $200/day.
  3. Rule test at real fills: a taker BUY print at price p on a token is evidence that the token's
     own ask was at p for that size (SETTLED A1: each token priced only from its own asks). Each
     rule buys at those prints and holds to resolution. Return per $ = (win - p - fee) / p,
     fee = rate * p * (1 - p) per share (feeSchedule on each market: rate 0.04, exponent 1, taker only).
     Event-clustered bootstrap CI. Placebo: same prints, outcome taken from a random other bucket of
     the same event.
  Rules:
     R1 daily_bottom: daily 1c-bucket ladder, buy YES on the open-ended bottom bucket ("<$X").
     R0 all_buys:     every taker buy in the series (what takers as a group earned; zero-sum reference).

Usage: python3 size.py raw/events_trades-<stamp>.json.gz [--window-days 30] [--now <unix>]
"""
import gzip, json, sys, datetime, argparse
from collections import defaultdict
import numpy as np

SLICE = 0.10
BAR = 200.0          # Nick, SETTLED A9: reliably $200/day, CI lower bound decides
LO, HI, DEAD = 0.05, 0.95, 0.99


def ts(s):
    return datetime.datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp() if s else None


def fee_per_share(m, p):
    fs = m.get("feeSchedule") or {}
    if not m.get("feesEnabled"):
        return 0.0
    return float(fs.get("rate", 0.0)) * (p * (1 - p)) ** float(fs.get("exponent", 1))


def resolved_yes(m):
    """1/0 if the market resolved, else None. Uses outcomePrices of closed markets only."""
    if not m.get("closed"):
        return None
    op = json.loads(m.get("outcomePrices") or "[]")
    if len(op) != 2:
        return None
    y = float(op[0])
    if y >= 0.999: return 1
    if y <= 0.001: return 0
    return None


def flow(events, t0, t1):
    """$ traded per series inside [t0, t1], split by price band."""
    out = defaultdict(lambda: defaultdict(float))
    for e in events.values():
        s = e["_series"]
        for m in e["markets"]:
            for t in m["_trades"]:
                if not (t0 <= t["timestamp"] <= t1): continue
                x = t["price"] * t["size"]; p = t["price"]
                out[s]["all"] += x
                if LO <= p < HI: out[s]["qual"] += x
                elif HI <= p < DEAD: out[s]["near_dead"] += x
                elif p >= DEAD: out[s]["dead"] += x
                else: out[s]["tail"] += x
    return out


def rule_rows(events, rule, t0, t1, rng):
    """One row per taker-BUY print the rule would have taken: (event, cost $, pnl $, placebo pnl $)."""
    rows = []
    for slug, e in events.items():
        mk = e["markets"]
        if rule == "daily_bottom" and e["_series"] != "us-gas-price-daily": continue
        res = [resolved_yes(m) for m in mk]
        for i, m in enumerate(mk):
            if res[i] is None: continue
            title = (m.get("groupItemTitle") or "")
            if rule == "daily_bottom" and not title.startswith("<"): continue
            others = [j for j in range(len(mk)) if j != i and res[j] is not None]
            for t in m["_trades"]:
                if t["side"] != "BUY" or not (t0 <= t["timestamp"] <= t1): continue
                p = t["price"]
                if not (LO <= p < HI): continue
                win = res[i] if t["outcome_index"] == 0 else 1 - res[i]
                if rule == "daily_bottom" and t["outcome_index"] != 0: continue
                f = fee_per_share(m, p)
                cost = (p + f) * t["size"]
                pnl = (win - p - f) * t["size"]
                if others:
                    j = others[rng.integers(len(others))]
                    pw = res[j] if t["outcome_index"] == 0 else 1 - res[j]
                    plc = (pw - p - f) * t["size"]
                else:
                    plc = np.nan
                rows.append((slug, cost, pnl, plc))
    return rows


def clustered(rows, rng, n=4000):
    """Return per $ with event-clustered bootstrap 95% CI, and placebo return."""
    if not rows: return None
    ev = defaultdict(lambda: [0.0, 0.0, 0.0])
    for slug, c, p, q in rows:
        ev[slug][0] += c; ev[slug][1] += p; ev[slug][2] += (0.0 if np.isnan(q) else q)
    k = list(ev); C = np.array([ev[x][0] for x in k]); P = np.array([ev[x][1] for x in k]); Q = np.array([ev[x][2] for x in k])
    b = rng.integers(0, len(k), (n, len(k)))
    r = P[b].sum(1) / C[b].sum(1)
    return {"events": len(k), "prints": len(rows), "cost": C.sum(), "pnl": P.sum(),
            "ret": P.sum() / C.sum(), "lo": float(np.percentile(r, 2.5)), "hi": float(np.percentile(r, 97.5)),
            "placebo_ret": Q.sum() / C.sum()}


def verdict(st, days, slice_=SLICE, bar=BAR):
    """$/day for a slice of the rule's own qualifying flow, at the CI lower bound. PASS needs lower bound >= bar."""
    flow_day = st["cost"] / days
    lo_day = slice_ * flow_day * st["lo"]
    mid_day = slice_ * flow_day * st["ret"]
    ok = st["events"] >= 30 and lo_day >= bar
    return flow_day, mid_day, lo_day, ("PASS" if ok else ("UNDERPOWERED" if st["events"] < 30 else "FAIL"))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("snapshot"); ap.add_argument("--window-days", type=float, default=30.0)
    ap.add_argument("--now", type=float, default=None); ap.add_argument("--seed", type=int, default=7)
    a = ap.parse_args(argv)
    events = json.load(gzip.open(a.snapshot, "rt")) if a.snapshot.endswith(".gz") else json.load(open(a.snapshot))
    rng = np.random.default_rng(a.seed)
    now = a.now or max(t["timestamp"] for e in events.values() for m in e["markets"] for t in m["_trades"])
    t0 = now - a.window_days * 86400
    L = []
    P = lambda s="": (print(s), L.append(s))
    P(f"Snapshot: {a.snapshot}; window {a.window_days:.0f} days to {datetime.datetime.fromtimestamp(now, datetime.timezone.utc):%Y-%m-%d %H:%MZ}")
    P("")
    P("## 1. Flow per series ($/day in window; qual = 0.05 <= p < 0.95)")
    P("| series | all $/day | qualifying $/day | near-dead 0.95-0.99 $/day | dead >=0.99 $/day |")
    P("|---|---:|---:|---:|---:|")
    fl = flow(events, t0, now); qtot = 0
    for s, d in sorted(fl.items()):
        first = min(ts(e["startDate"]) for e in events.values() if e["_series"] == s)
        nd = (now - max(t0, first)) / 86400   # days the series was listed inside the window
        qtot += d["qual"] / nd
        P(f"| {s} ({nd:.1f} d listed) | {d['all']/nd:,.0f} | {d['qual']/nd:,.0f} | {d['near_dead']/nd:,.0f} | {d['dead']/nd:,.0f} |")
    P(f"| **all gas** | | **{qtot:,.0f}** | | |")
    P("")
    P("## 2. Capacity bound (model-free)")
    P(f"Edge per $ needed for $200/day: 10% slice {BAR/(SLICE*qtot)*100:,.0f}c per $; 100% of all qualifying flow {BAR/qtot*100:,.0f}c per $.")
    P("")
    P("## 3. Rules at real taker-buy prints (hold to resolution, after taker fee)")
    P("| rule | window | events | prints | rule flow $/day | return per $ (95% CI) | placebo | 10% slice $/day mid | at CI low | verdict |")
    P("|---|---|---:|---:|---:|---|---:|---:|---:|---|")
    for rule, win in (("daily_bottom", a.window_days), ("all_buys", a.window_days), ("all_buys", 400.0)):
        rr = rule_rows(events, rule, now - win * 86400, now, rng)
        st = clustered(rr, rng)
        if not st: P(f"| {rule} | {win:.0f}d | 0 | | | | | | | NO DATA |"); continue
        days = min(win, (now - min(ts(e['startDate']) for e in events.values())) / 86400)  # all_buys: window, capped at data span
        if rule == "daily_bottom":
            d0 = [ts(e["startDate"]) for e in events.values() if e["_series"] == "us-gas-price-daily"]
            days = (now - min(d0)) / 86400
        fd, md, ld, v = verdict(st, days)
        P(f"| {rule} | {win:.0f}d | {st['events']} | {st['prints']} | {fd:,.0f} | {st['ret']*100:+.1f}c ({st['lo']*100:+.1f}, {st['hi']*100:+.1f}) | {st['placebo_ret']*100:+.1f}c | {md:,.1f} | {ld:,.1f} | {v} |")
    return L


if __name__ == "__main__":
    main()
