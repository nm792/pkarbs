#!/usr/bin/env python3
"""Can-fail tests for health_jsonl (must FAIL on a bad log). Run from this directory without -I."""
import gzip, json, os, tempfile
from health_jsonl import read
fails = []
def check(name, cond):
    print(("PASS " if cond else "FAIL ") + name)
    if not cond: fails.append(name)
def mk(rows, gz=True):
    d = tempfile.mkdtemp(); p = d + ("/x.jsonl.gz" if gz else "/x.jsonl")
    with (gzip.open(p, "wt") if gz else open(p, "w")) as f:
        for r in rows: f.write((r if isinstance(r, str) else json.dumps(r)) + "\n")
    return p
T0 = 1_000_000.0
def cyc(n, step=60, extra=None):  # n polling cycles, 2 rows each
    out = []
    for i in range(n):
        for s in ("A", "B"): out.append(dict(ts=T0 + i * step, sym=s, px=1.0, **(extra or {})))
    return out
good = cyc(60)
line, ok = read(mk(good), 59, 60, need="px", pid=7, now=T0 + 59 * 60, free_gb=100); check("healthy 60-minute gz log PASSES and names the pid", ok and "pid 7" in line and "PASS" in line)
line, ok = read(mk(good, gz=False), 59, 60, need="px", now=T0 + 59 * 60, free_gb=100); check("plain jsonl also works", ok)
line, ok = read(mk(cyc(60)[:100]), 59, 60, now=T0 + 59 * 60, free_gb=100); check("PLANTED GAP: only 50 of 60 cycles FAILS", not ok and "cycles" in line)
line, ok = read(mk(good + [dict(ts=T0 + 3000, err="boom")]), 59, 60, now=T0 + 59 * 60, free_gb=100); check("an err row FAILS", not ok and "error" in line)
line, ok = read(mk(good + ["{not json"]), 59, 60, now=T0 + 59 * 60, free_gb=100); check("a corrupt line FAILS", not ok)
line, ok = read(mk([dict(r, px=None) for r in good]), 59, 60, need="px", now=T0 + 59 * 60, free_gb=100); check("rows missing the needed field FAIL", not ok and "missing" in line)
line, ok = read(mk(good), 59, 60, now=T0 + 59 * 60, free_gb=5); check("low disk FAILS", not ok and "disk" in line)
line, ok = read(mk(good), 59, 60, errkeys=("err", "book_err"), now=T0 + 59 * 60, free_gb=100); check("healthy with two error keys still PASSES", ok)
line, ok = read(mk(good + [dict(ts=T0 + 3100, sym="A", book_err="x")]), 59, 60, errkeys=("err", "book_err"), now=T0 + 59 * 60, free_gb=100); check("book_err row FAILS", not ok)
print("ALL PASS" if not fails else "FAILED: %s" % fails)
raise SystemExit(1 if fails else 0)
