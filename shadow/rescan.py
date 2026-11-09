#!/usr/bin/env python3
"""Re-detect runs (both sides) from raw logs written by any version of shadow_logger.

The first logger only checked the YES side and had no completeness check. This replays
raw-*.jsonl.gz through the current Logger.check, using the leg lists that events.jsonl
held at each moment, and writes OUT/runs.jsonl in the current format.

Completeness for old events.jsonl (no "complete" field): a snapshot counts as complete only
if it has as many legs as the most ever seen for that event and, with --fetch-totals, as many as
the event's total market count from gamma (public endpoint, cached in OUT/totals.json).

Clean-rescan additions (TASK-rescan-clean):
- --gap-s: clear every book when the receive time jumps by more than gap-s, or a new file
  starts after a missing/truncated one. Legs are marked unseeded and only re-seed on a full
  book message. No run opens, and no sim fills, on an unseeded leg.
- Crossed-book check: a run is not opened/extended while any leg has best_bid >= best_ask.
- Dedup: per price change on (asset_id, exchange timestamp, hash) from the change entry, via
  books.Replay, the same replay shadow_sim.py uses; drop runs that repeat (event, side, t0).
- --max-taker-rebate: passed to Logger.check so runs open on the relaxed (post-rebate) edge.
- rebate_rate: older events.jsonl lines lack it; fill 0.15 for sports legs with fee_rate 0.05.
- Trade prints: count last_trade_price messages per raw hour file.

Usage: python3 rescan.py --data data/ --out rescan/ [--fetch-totals] [--gap-s 5] [--max-taker-rebate 0.5]
"""
import argparse, glob, gzip, json, os
from collections import defaultdict
from shadow_logger import Book, Logger, get_json, GAMMA
from books import Replay, read_lines, CORRUPT


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="data")
    ap.add_argument("--out", default="rescan")
    ap.add_argument("--min-edge", type=float, default=0.0)
    ap.add_argument("--fetch-totals", action="store_true", help="read each event's market count from gamma")
    ap.add_argument("--gap-s", type=float, default=5.0, help="receive-time jump that resets every book")
    ap.add_argument("--max-taker-rebate", type=float, default=0.0, help="relaxed-edge threshold for opening runs")
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
            # change 7: older events.jsonl lines lack rebate_rate; fill 0.15 for sports legs at fee 0.05
            for leg in ev["legs"]:
                if "rebate_rate" not in leg:
                    leg["rebate_rate"] = 0.15 if leg.get("fee_rate") == 0.05 else 0.0

    out_runs = os.path.join(a.out, "runs.jsonl")
    if os.path.exists(out_runs):
        os.remove(out_runs)
    lg = Logger(a.out, [], a.min_edge, 0, 0, a.max_taker_rebate)
    for t in times:
        for ev in snaps[t].values():
            for leg in ev["legs"]:
                lg.books.setdefault(leg["yes"], Book())

    ti, n_msgs = -1, 0
    rp = Replay(lg.books, gap_s=a.gap_s)  # same replay as shadow_sim.replay()
    dedup_runs = 0
    crossed_checks = 0
    unseeded_checks = 0
    seen_runs = set()
    trade_prints = defaultdict(int)  # hour -> count
    r = None
    seq = 0

    for path in sorted(glob.glob(os.path.join(a.data, "raw-*.jsonl.gz"))):
        hour = os.path.basename(path).replace("raw-", "").replace(".jsonl.gz", "")
        for line in read_lines(path):
            try:
                rec = json.loads(line)
            except ValueError:
                continue
            r = rec["r"]
            seq += 1  # parsed-record counter; test_gates.py replays to the same count
            while ti + 1 < len(times) and times[ti + 1] <= r:
                ti += 1
                found = snaps[times[ti]]
                for eid in set(lg.events) - set(found):
                    lg.close_run(times[ti], eid)
                lg.events = found
                lg.asset_event = {leg["yes"]: eid for eid, ev in found.items() for leg in ev["legs"]}
            msgs = rec["m"] if isinstance(rec["m"], list) else [rec["m"]]
            n_msgs += len(msgs)
            trade_prints[hour] += sum(1 for m in msgs if m.get("event_type") == "last_trade_price")
            resets_before, prev_r = rp.resets, rp.last_r
            touched = rp.feed(r, msgs)
            if rp.resets != resets_before:  # books were cleared: close open runs at the last record before the gap
                for eid, _ in list(lg.runs):
                    lg.close_run(prev_r, eid)
            for eid in {lg.asset_event.get(x) for x in touched} - {None}:
                ev = lg.events.get(eid)
                if not ev:
                    continue
                legs = [leg["yes"] for leg in ev["legs"]]
                # no run while any leg lacks a full book since the last gap reset
                if not all(rp.is_seeded(x) for x in legs):
                    unseeded_checks += 1
                    lg.close_run(r, eid)
                    continue
                # no run while any leg is crossed
                if any(lg.books[x].best_bid() is not None and lg.books[x].best_ask() is not None
                       and lg.books[x].best_bid() >= lg.books[x].best_ask() for x in legs):
                    crossed_checks += 1
                    lg.close_run(r, eid)
                    continue
                lg.check(r, eid)
                for run in lg.runs.values():
                    run.setdefault("seq0", seq)  # the record that opened the run
    for eid, _ in list(lg.runs):
        lg.close_run(r, eid)
    # change 3: dedup runs by (event, side, t0)
    runs_path = out_runs
    if os.path.exists(runs_path):
        keep = []
        for line in open(runs_path):
            run = json.loads(line)
            k = (run["event"], run["side"], run["t0"])
            if k in seen_runs:
                dedup_runs += 1
                continue
            seen_runs.add(k)
            keep.append(run)
        with open(runs_path, "w") as f:
            for run in keep:
                f.write(json.dumps(run) + "\n")
    print("messages:", n_msgs, "runs written to", out_runs, flush=True)
    print(f"resets={rp.resets} skipped_s={rp.skipped_s:.1f} dedup_changes={rp.dups} "
          f"dedup_runs={dedup_runs} crossed_checks={crossed_checks} unseeded_checks={unseeded_checks} "
          f"corrupt_members_skipped={CORRUPT['skips']} top_checks={rp.top_checks} "
          f"top_mismatch_before_repair={rp.top_mismatch} levels_dropped={rp.levels_dropped}", flush=True)
    print("trade_prints:", dict(trade_prints), flush=True)


if __name__ == "__main__":
    main()
