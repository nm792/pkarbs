#!/usr/bin/env python3
"""Re-detect runs (both sides) from raw logs written by any version of shadow_logger.

The first logger only checked the YES side and had no completeness check. This replays
raw-*.jsonl.gz through the current Logger.check, using the leg lists that events.jsonl
held at each moment, and writes OUT/runs.jsonl in the current format.

Completeness for old events.jsonl (no "complete" field): a snapshot counts as complete only
if it has as many legs as the most ever seen for that event and, with --fetch-totals, as many as
the event's total market count from gamma (public endpoint, cached in OUT/totals.json).

Usage: python3 rescan.py --data data/ --out rescan/ [--fetch-totals]
"""
import argparse, glob, gzip, json, os
from collections import defaultdict
from shadow_logger import Book, Logger, get_json, GAMMA


def read_lines(path):
    try:
        with gzip.open(path, "rt") as f:
            yield from f
    except (EOFError, OSError) as e:  # open or truncated file
        print("stopped reading", os.path.basename(path), repr(e), flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="data")
    ap.add_argument("--out", default="rescan")
    ap.add_argument("--min-edge", type=float, default=0.0)
    ap.add_argument("--fetch-totals", action="store_true", help="read each event's market count from gamma")
    a = ap.parse_args()

    snaps = defaultdict(dict)  # refresh time -> {event_id: info}
    for line in open(os.path.join(a.data, "events.jsonl")):
        ev = json.loads(line)
        snaps[ev["t"]][ev["id"]] = ev
    times = sorted(snaps)
    most = defaultdict(int)
    for t in times:
        for eid, ev in snaps[t].items():
            most[eid] = max(most[eid], len(ev["legs"]))

    totals_path = os.path.join(a.out, "totals.json")
    os.makedirs(a.out, exist_ok=True)
    totals = json.load(open(totals_path)) if os.path.exists(totals_path) else {}
    if a.fetch_totals:
        for eid in most:
            if eid in totals:
                continue
            try:
                ev = get_json(f"{GAMMA}/{eid}")
                totals[eid] = len(ev.get("markets", []))
            except Exception as e:
                print("gamma", eid, repr(e), flush=True)
        json.dump(totals, open(totals_path, "w"))

    for t in times:
        for eid, ev in snaps[t].items():
            if "complete" not in ev:
                n = len(ev["legs"])
                ev["complete"] = n == most[eid] and (eid not in totals or n == totals[eid])
                ev["n_markets"] = totals.get(eid)

    out_runs = os.path.join(a.out, "runs.jsonl")
    if os.path.exists(out_runs):
        os.remove(out_runs)
    lg = Logger(a.out, [], a.min_edge, 0, 0)
    for t in times:
        for ev in snaps[t].values():
            for leg in ev["legs"]:
                lg.books.setdefault(leg["yes"], Book())

    ti, n_msgs = -1, 0
    for path in sorted(glob.glob(os.path.join(a.data, "raw-*.jsonl.gz"))):
        for line in read_lines(path):
            try:
                rec = json.loads(line)
            except ValueError:
                continue
            r = rec["r"]
            while ti + 1 < len(times) and times[ti + 1] <= r:
                ti += 1
                found = snaps[times[ti]]
                for eid in set(lg.events) - set(found):
                    lg.close_run(times[ti], eid)
                lg.events = found
                lg.asset_event = {leg["yes"]: eid for eid, ev in found.items() for leg in ev["legs"]}
            msgs = rec["m"] if isinstance(rec["m"], list) else [rec["m"]]
            for m in msgs:
                n_msgs += 1
                touched = lg.apply(r, m)
                for eid in {lg.asset_event.get(x) for x in touched or []}:
                    lg.check(r, eid)
    for eid, _ in list(lg.runs):
        lg.close_run(r, eid)
    print("messages:", n_msgs, "runs written to", out_runs, flush=True)


if __name__ == "__main__":
    main()
