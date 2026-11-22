#!/usr/bin/env python3
"""Can-fail tests for health_read (must FAIL on a bad snapshot). Run from this directory without -I."""
import json, os, tempfile
from health_read import read
fails = []
def check(name, cond):
    print(("PASS " if cond else "FAIL ") + name)
    if not cond: fails.append(name)
def mk(rows):
    d = tempfile.mkdtemp()
    with open(d + "/snap_x.jsonl", "w") as f:
        for r in rows: f.write(json.dumps(r) + "\n")
    return d
meta = dict(kind="meta", marks={"a": 1.0}, closes={"a": 1.0}, hl_depth={"a": {"mid": 1}})
good = [meta] + [dict(kind="tok", book_ok=True) for _ in range(200)]
line, ok = read(mk(good), "x", 7); check("healthy snapshot PASSES and names the pid", ok and "pid 7" in line and "PASS" in line)
bad = [meta] + [dict(kind="tok", book_ok=(i % 10 != 0)) for i in range(200)]
line, ok = read(mk(bad), "x", 7); check("90% capture FAILS", (not ok) and "capture" in line)
line, ok = read(mk(good + [dict(kind="err", slug="s", err="e")]), "x", 7); check("an err row FAILS", not ok and "err rows" in line)
line, ok = read(mk([dict(meta, marks={"a": None})] + good[1:]), "x", 7); check("missing perp mark FAILS", not ok)
line, ok = read(mk([meta]), "x", 7); check("no token rows FAILS", not ok)
print("ALL PASS" if not fails else "FAILED: %s" % fails); raise SystemExit(1 if fails else 0)
