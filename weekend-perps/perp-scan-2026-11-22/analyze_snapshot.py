#!/usr/bin/env python3
"""Per-family capacity from one snapshot file. Usage: python3 analyze_snapshot.py RUNDIR LABEL
Prints, per family: tokens, tokens with a recorded book, tradable tokens (own ask in (0.05,0.95)), median/total $ ask depth within 3c of the
own best ask, tokens with >= $200 depth, and the perp-gap candidates (strike already crossed by the perp) with their YES ask and depth."""
import json, sys, statistics
from collections import defaultdict
from snaplib import candidates
from pscanlib import PER_TRADE, per_decision_usd

def load(run, label):
    rows = [json.loads(l) for l in open("%s/snap_%s.jsonl" % (run, label))]
    return [r for r in rows if r["kind"] == "meta"][-1], [r for r in rows if r["kind"] == "tok"]

def main(run, label):
    meta, toks = load(run, label)
    by = defaultdict(list)
    for r in toks: by[r["family"]].append(r)
    print("snapshot", label, "t", meta["t"], "marks", {k: round(v, 2) for k, v in meta["marks"].items()}, "\ncloses", {k: v for k, v in meta["closes"].items() if v})
    print("%-15s %5s %6s %7s %10s %10s %7s" % ("family", "toks", "books", "tradbl", "medDepth$", "sumDepth$", ">=$200"))
    for f, rs in sorted(by.items()):
        tr = [r for r in rs if r["tradable"]]
        d = [r["ask_depth_usd"] for r in tr]
        print("%-15s %5d %6d %7d %10.0f %10.0f %7d" % (f, len(rs), sum(r["book_ok"] for r in rs), len(tr), statistics.median(d) if d else 0, sum(d), sum(x >= PER_TRADE for x in d)))
    c = candidates(toks, meta["marks"], meta["closes"], meta["margins"])
    print("\nperp-gap candidates (YES token, strike already crossed by the HL xyz mark):", len(c))
    for r in sorted(c, key=lambda r: (r["family"], r["under"], r["strike"])):
        print("  %-14s %-6s %-4s K=%-9g perp=%-9.2f close=%-9.2f YES ask %s depth$ %.0f tradable=%s | %s" % (r["family"], r["under"], r["kind"], r["strike"], r["perp"], r["close"], r["best_ask"], r["ask_depth_usd"], r["tradable"], r["slug"][:40]))

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
