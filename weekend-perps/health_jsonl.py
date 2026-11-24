#!/usr/bin/env python3
"""HEALTH READ for a polling logger that writes JSON lines (plain or .gz) with a unix-seconds time key (R-037 / R-058). No network.
Usage: python3 health_jsonl.py FILE WINDOW_MIN INTERVAL_S [--tskey ts] [--errkeys err,book_err] [--need KEY] [--pid N] [--min-rows N]
Counts polling cycles (distinct time-key values) in the last WINDOW_MIN minutes of the file against the cycles expected at INTERVAL_S.
FAIL if cycles < 99% of expected, any row with an error key, any row in the window missing the --need field, fewer than --min-rows rows,
or free disk < 15 GB. Also prints the on-disk size per day extrapolated from the file (MB/day, compressed as stored)."""
import gzip, json, os, shutil, sys, time


def read(path, window_min, interval_s, tskey="ts", errkeys=("err",), need=None, min_rows=1, pid=None, now=None, free_gb=None):
    op = gzip.open if path.endswith(".gz") else open
    rows = []
    with op(path, "rt") as f:
        for ln in f:
            try:
                rows.append(json.loads(ln))
            except Exception:
                rows.append({"_bad": True})
    ts_all = [r[tskey] for r in rows if tskey in r]
    now = now if now is not None else (max(ts_all) if ts_all else time.time())
    lo = now - window_min * 60
    win = [r for r in rows if r.get(tskey, 0) >= lo or r.get("_bad")]
    cycles = len({r[tskey] for r in win if tskey in r})
    expected = window_min * 60 / interval_s
    errs = sum(1 for r in win if r.get("_bad") or any(k in r for k in errkeys))
    miss = sum(1 for r in win if need and tskey in r and not any(k in r for k in errkeys) and r.get(need) is None)
    span_days = max((max(ts_all) - min(ts_all)) / 86400.0, 1e-9) if ts_all else 1e-9
    mb_day = os.path.getsize(path) / 1e6 / span_days if ts_all else 0.0
    if free_gb is None:
        free_gb = shutil.disk_usage(os.path.dirname(os.path.abspath(path))).free / 1e9
    fails = []
    if len(win) < min_rows: fails.append("rows %d < %d" % (len(win), min_rows))
    if expected and cycles < 0.99 * expected: fails.append("cycles %d of %.0f expected (%.1f%%) < 99%%" % (cycles, expected, 100 * cycles / expected))
    if errs: fails.append("%d error/bad rows" % errs)
    if miss: fails.append("%d rows missing %s" % (miss, need))
    if free_gb < 15: fails.append("disk %.1f GB < 15" % free_gb)
    line = ("HEALTH READ %s: %s | window %d min, %d rows, %d polling cycles of %.0f expected (%.1f%%) | error rows %d | rows missing %s: %d | file %.1f MB, about %.1f MB/day as stored | disk free %.0f GB | pid %s"
            % (os.path.basename(path), "FAIL: " + "; ".join(fails) if fails else "PASS", window_min, len(win), cycles, expected, 100 * cycles / expected if expected else 0, errs, need, miss, os.path.getsize(path) / 1e6, mb_day, free_gb, pid or os.getpid()))
    return line, not fails


if __name__ == "__main__":
    a = sys.argv[1:]
    kv = {}
    pos = []
    i = 0
    while i < len(a):
        if a[i].startswith("--"): kv[a[i][2:]] = a[i + 1]; i += 2
        else: pos.append(a[i]); i += 1
    line, ok = read(pos[0], float(pos[1]), float(pos[2]), kv.get("tskey", "ts"), tuple(kv.get("errkeys", "err").split(",")), kv.get("need"), int(kv.get("min-rows", 1)), kv.get("pid"))
    print(line); raise SystemExit(0 if ok else 1)
