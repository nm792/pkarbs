#!/usr/bin/env python3
"""HEALTH READ for a snapshot run (Nick standing rule R-037). Usage: python3 health_read.py RUNDIR LABEL [PID]
Prints one INBOX-ready line: share of expected snapshots captured (tokens with a recorded own book / tokens listed), unhandled errors (err rows),
price source, disk free, pid, PASS/FAIL. FAIL if capture < 99%, any err row, marks/closes missing, or disk < 15 GB."""
import json, os, shutil, sys

def read(run, label, pid=None, disk_path=None, free_gb=None):
    rows = [json.loads(l) for l in open("%s/snap_%s.jsonl" % (run, label))]
    meta = [r for r in rows if r["kind"] == "meta"][-1]
    toks = [r for r in rows if r["kind"] == "tok"]; errs = [r for r in rows if r["kind"] == "err"]
    ok = sum(r["book_ok"] for r in toks)
    cap = ok / len(toks) if toks else 0.0
    nm = sum(v is not None for v in meta["marks"].values()); nc = sum(v is not None for v in meta["closes"].values())
    nd = sum(v is not None for v in (meta.get("hl_depth") or {}).values())
    if free_gb is None:   # real run: measure the disk; tests inject a value so they do not depend on the machine's free space
        free_gb = shutil.disk_usage(disk_path or run).free / 1e9
    fails = []
    if cap < 0.99: fails.append("capture %.1f%% < 99%%" % (100 * cap))
    if errs: fails.append("%d err rows" % len(errs))
    if nm < len(meta["marks"]) or nc < len(meta["closes"]): fails.append("marks %d/%d closes %d/%d" % (nm, len(meta["marks"]), nc, len(meta["closes"])))
    if free_gb < 15: fails.append("disk %.1f GB < 15" % free_gb)
    if not toks: fails.append("no token rows")
    line = ("HEALTH READ %s: %s | captured %d of %d tokens (%.1f%%) | unhandled errors %d | prices: each token's OWN /books asks list via snaplib.token_row (best_ask = lowest ask in that token's book; NO never derived from YES) | "
            "perp marks %d, closes %d, perp depth %d | disk free %.0f GB | pid %s") % (label, "FAIL: " + "; ".join(fails) if fails else "PASS", ok, len(toks), 100 * cap, len(errs), nm, nc, nd, free_gb, pid if pid else os.getpid())
    return line, not fails

if __name__ == "__main__":
    line, ok = read(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
    print(line); raise SystemExit(0 if ok else 1)
