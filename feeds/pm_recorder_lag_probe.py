#!/usr/bin/env python3
"""Read-only probe of the Polymarket book recorder timing (checker, 19 Nov 2026). Question: how stale is mid_at(t) = 'last stored row at or before t'?
Rows are written only on change, stamped ms = our receive time after the /books response (batch of 50 tokens, sequential), sent = cycle start, ts = Polymarket's own snapshot timestamp.
Prints: row count; percentiles of (ms - sent) = how late in the cycle a token is read; percentiles of the gap between consecutive DISTINCT cycle starts = the polling cycle;
percentiles of (ms - ts) if ts is numeric = response age; and, for each of the --tokens-file tokens (one per line, optional), rows per hour. No output contains keys or tokens beyond counts.
Usage: python3 -I feeds/pm_recorder_lag_probe.py BOOKS.jsonl[.gz] [--max-rows 3000000]"""
import argparse, collections, gzip, json, sys


def pct(x, qs=(5, 25, 50, 75, 95, 99)):
    x = sorted(x)
    return {("p%d" % q): (x[min(len(x) - 1, int(q / 100 * len(x)))] if x else None) for q in qs}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    ap.add_argument("--max-rows", type=int, default=3000000)
    a = ap.parse_args()
    op = gzip.open if a.path.endswith(".gz") else open
    lag, age, sents, n, bad, ts_types = [], [], set(), 0, 0, collections.Counter()
    first = last = None
    try:
        with op(a.path, "rt", errors="replace") as f:
            for l in f:
                try:
                    r = json.loads(l)
                except Exception:
                    bad += 1
                    continue
                if "sent" not in r or "ms" not in r:
                    continue
                n += 1
                lag.append((r["ms"] - r["sent"]) / 1000.0)
                sents.add(r["sent"])
                first = r["ms"] if first is None else first
                last = r["ms"]
                ts = r.get("ts")
                ts_types[type(ts).__name__] += 1
                try:
                    age.append((r["ms"] - float(ts)) / 1000.0)
                except (TypeError, ValueError):
                    pass
                if n >= a.max_rows:
                    break
    except (EOFError, OSError) as e:
        print("PARTIAL FILE", type(e).__name__, e, file=sys.stderr)
    s = sorted(sents)
    gaps = [(b - a_) / 1000.0 for a_, b in zip(s, s[1:])]
    print(json.dumps(dict(rows=n, bad_lines=bad, first_ms=first, last_ms=last, distinct_cycles=len(s), ms_minus_sent_s=pct(lag), cycle_gap_s=pct(gaps), ms_minus_ts_s=pct(age) if age else None, ts_types=dict(ts_types),
                          note="a move that happens right after a poll is seen one cycle later; stale_bound_s is p95 of cycle_gap_s plus p95 of ms_minus_sent_s", stale_bound_s=((pct(gaps)["p95"] or 0) + (pct(lag)["p95"] or 0))), indent=1))


if __name__ == "__main__":
    main()
