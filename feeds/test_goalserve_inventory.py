#!/usr/bin/env python3
"""Offline test for goalserve_inventory.py on synthetic payload files. PASS/FAIL lines, exit 0 only if all pass."""
import os, sys, gzip, json, tempfile, subprocess
here = os.path.dirname(os.path.abspath(__file__))
tmp = tempfile.mkdtemp()

def ev(o1, o2, sus=0, name="Match Winner"):
    return {"info": {"sport": "cs2" , "name": "A vs B"}, "team_info": {"home": {"name": "A"}, "away": {"name": "B"}},
            "stats": {"kills": 1},
            "odds": {"1": {"id": 1, "name": name, "suspend": sus, "participants": {
                "11": {"id": 11, "name": "A", "value_eu": o1, "suspend": 0}, "12": {"id": 12, "name": "B", "value_eu": o2, "suspend": 0}}}}}

def body(o1, o2, bm="", extra=None):
    d = {"bm": bm, "events": {"E1": ev(o1, o2)}}
    if extra: d["events"]["E2"] = extra
    return json.dumps(d)

f = os.path.join(tmp, "esports_2026111700.jsonl.gz")
t0 = 1_000_000_000_000
with gzip.open(f, "wt") as g:
    # E1 odds change at +0, +2 s, +2.5 s (changed), unchanged at +1 s and +3 s
    for dt, (a, b) in [(0, (1.5, 2.5)), (1, (1.5, 2.5)), (2, (1.6, 2.3)), (2.5, (1.7, 2.2)), (3, (1.7, 2.2))]:
        g.write(json.dumps({"recv_ns": int(t0 + dt * 1e9), "body": body(a, b)}) + "\n")
    # a row that mentions Pinnacle inside a market name
    g.write(json.dumps({"recv_ns": int(t0 + 4e9), "body": body(1.7, 2.2, extra=ev(1.9, 1.9, name="Pinnacle Match Winner"))}) + "\n")
    g.write("{truncated json line\n")
out = os.path.join(tmp, "inv.md")
r = subprocess.run([sys.executable, "-I", os.path.join(here, "goalserve_inventory.py"), "--files", os.path.join(tmp, "*.jsonl.gz"), "--out", out],
                   capture_output=True, text=True)
t = open(out).read() if os.path.exists(out) else ""
fails = []
def check(n, c):
    print(("PASS " if c else "FAIL ") + n)
    if not c: fails.append(n)
check("exit 0", r.returncode == 0)
check("6 rows read, bad line skipped", "stored payload rows: 6" in t)
check("2 distinct events", "distinct events: 2" in t)
check("bm empty string reported as ''", "'' (6)" in t)
check("pinnacle string found in 1 row, verdict yes", "contains the string 'pinnacle' (any case): 1" in t and "PINNACLE in stored in-play bodies: yes (1 rows)" in t)
check("markets listed with title", "- cs2: Match Winner" in t)
check("update gaps: changes at +2.0 s (gap 2.0 from +0) and +2.5 s (gap 0.5) -> n=2, median 1.25", "n changes: 2; median 1.25 s" in t)
check("field names listed", "event keys:" in t and "odds (" in t and "kills" in t)
print("ALL PASS" if not fails else "FAILED: " + "; ".join(fails)); sys.exit(1 if fails else 0)
