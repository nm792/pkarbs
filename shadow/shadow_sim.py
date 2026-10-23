#!/usr/bin/env python3
"""Replay shadow_logger output and ask: would these gaps have filled?

For each run, we "send" one limit buy per leg at the ask seen at t0, sized to the
smallest leg (capped by --max-usd). Orders match at t0 + one-way latency + delay.
A leg fills only from asks at or below its limit at that moment. Matched sets
pay $1; legs left over from a partial set are sold back at the bid after
another delay, paying taker fees.

Usage: python3 shadow_sim.py --data data/ --one-way 0.05 --delays 0,1,3
"""
import argparse, glob, gzip, json, os
from collections import defaultdict


def fee(rate, p):
    return rate * p * (1 - p)


def walk(levels, limit, qty, buy):
    """Fill up to qty from {price: size} at prices no worse than limit. Returns (filled, notional)."""
    filled = notional = 0.0
    for p in sorted(levels, reverse=not buy):
        if (buy and p > limit + 1e-9) or (not buy and p < limit - 1e-9) or filled >= qty:
            break
        q = min(levels[p], qty - filled)
        filled += q
        notional += q * p
    return filled, notional


def read_lines(path):
    """Yield lines from a gzip file, stopping quietly if the logger is still writing it."""
    try:
        with gzip.open(path, "rt") as f:
            yield from f
    except EOFError:
        return


def load(data):
    legs = {}
    for line in open(os.path.join(data, "events.jsonl")):
        ev = json.loads(line)
        legs[ev["id"]] = ev["legs"]
    runs = [json.loads(l) for l in open(os.path.join(data, "runs.jsonl"))] if os.path.exists(os.path.join(data, "runs.jsonl")) else []
    return legs, runs


def replay(data, queries):
    """queries: list of (t, event_id, key). Returns {key: {asset: (bids, asks)}} snapshots."""
    want = sorted(queries, key=lambda q: q[0])
    books = defaultdict(lambda: [{}, {}, 0])  # bids, asks, last exchange ts
    snaps, qi = {}, 0
    for path in sorted(glob.glob(os.path.join(data, "raw-*.jsonl.gz"))):
        for line in read_lines(path):
            try:
                rec = json.loads(line)
            except ValueError:  # partial last line of a file still being written
                continue
            while qi < len(want) and want[qi][0] < rec["r"]:
                t, eid, key, assets = want[qi]
                snaps[key] = {a: (dict(books[a][0]), dict(books[a][1])) for a in assets}
                qi += 1
            msgs = rec["m"] if isinstance(rec["m"], list) else [rec["m"]]
            for m in msgs:
                et = m.get("event_type")
                if et == "book":
                    b = books[m["asset_id"]]
                    if int(m.get("timestamp", 0)) < b[2]:
                        continue
                    b[2] = int(m.get("timestamp", 0))
                    b[0] = {float(x["price"]): float(x["size"]) for x in m.get("bids", [])}
                    b[1] = {float(x["price"]): float(x["size"]) for x in m.get("asks", [])}
                elif et == "price_change":
                    for c in m.get("price_changes") or m.get("changes") or []:
                        b = books[c.get("asset_id") or m.get("asset_id")]
                        b[2] = max(b[2], int(m.get("timestamp", 0)))
                        side = b[0] if c["side"].upper() == "BUY" else b[1]
                        p, s = float(c["price"]), float(c["size"])
                        if s == 0:
                            side.pop(p, None)
                        else:
                            side[p] = s
    for t, eid, key, assets in want[qi:]:
        snaps[key] = {a: (dict(books[a][0]), dict(books[a][1])) for a in assets}
    return snaps


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="data")
    ap.add_argument("--one-way", type=float, default=0.05, help="seconds from detection to order at the CLOB")
    ap.add_argument("--delays", default="0,1,3", help="sports delay values to test, seconds; 'market' uses each leg's secondsDelay")
    ap.add_argument("--max-usd", type=float, default=500.0)
    a = ap.parse_args()

    legs, runs = load(a.data)
    delays = a.delays.split(",")
    queries = []
    for i, r in enumerate(runs):
        lg = legs[r["event"]]
        assets = {l["yes"] for l in lg}
        for d in delays:
            dv = max((l.get("seconds_delay") or 0) for l in lg) if d == "market" else float(d)
            tm = r["t0"] + a.one_way + dv
            queries.append((tm, r["event"], (i, d, "match"), assets))
            queries.append((tm + a.one_way + dv, r["event"], (i, d, "unwind"), assets))
    snaps = replay(a.data, queries)

    for d in delays:
        tot_seen = tot = worst = 0.0
        full = partial = none = 0
        for i, r in enumerate(runs):
            lg = legs[r["event"]]
            q = min(r["size0"], a.max_usd / r["cost0"])
            tot_seen += (1 - r["cost0"]) * q
            m, u = snaps[(i, d, "match")], snaps[(i, d, "unwind")]
            fills = []
            for leg, (ask0, _) in zip(lg, r["quotes0"]):
                f, notional = walk(m[leg["yes"]][1], ask0, q, buy=True)
                fills.append((leg, f, notional + fee(leg["fee_rate"], ask0) * f))
            h = min(f for _, f, _ in fills)
            pnl = h
            for leg, f, paid in fills:
                pnl -= paid
                extra = f - h
                if extra > 1e-9:
                    bids = u[leg["yes"]][0]
                    s, notional = walk(bids, 0.0, extra, buy=False)
                    pnl += notional - fee(leg["fee_rate"], notional / s if s else 0) * s
            tot += pnl
            worst = min(worst, pnl)
            if h >= q - 1e-9:
                full += 1
            elif any(f > 1e-9 for _, f, _ in fills):
                partial += 1
            else:
                none += 1
        print(f"delay={d:>6}  runs={len(runs)}  seen=${tot_seen:8.2f}  sim=${tot:8.2f}  worst=${worst:7.2f}  full={full} partial={partial} none={none}")


if __name__ == "__main__":
    main()
