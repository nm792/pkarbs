#!/usr/bin/env python3
"""EXPLORATORY block of LOCKED-RULE-touch-gap-2026-11-22.md Amendment 3. Usage: python3 analyze_touch_explore.py RUNDIR"""
import datetime, gzip, json, sys, statistics
from collections import Counter
from universe import UNDER
from pscanlib import parse_strike, gap_beyond
from touchlib import decision_ts, perp_at, last_close, yes_wins, last_print, gap, NY
from analyze_touch import fee_rate

def main(run):
    ev = json.load(gzip.open(run + "/touch_events.json.gz", "rt")); cand = json.load(gzip.open(run + "/touch_candles.json.gz", "rt")); closes = json.load(open(run + "/touch_closes.json"))
    rows = []; allstrikes = 0
    for e in ev:
        if not e.get("found"): continue
        tk, mon = e["tk"], datetime.date.fromisoformat(e["monday"]); kind = UNDER[tk][2]; T = decision_ts(kind, mon)
        P = perp_at(cand.get("%s|%s" % (tk, mon)), T); C = last_close(closes.get(tk), datetime.datetime.fromtimestamp(T, NY).date())
        if P is None or C is None: continue
        for m in e["markets"]:
            ks = parse_strike(m["q"]); w = yes_wins(m["prices"], m["outcomes"])
            if not ks or w is None: continue
            allstrikes += 1
            if not gap_beyond(P, C, ks[0], ks[1], UNDER[tk][3]): continue
            outs = json.loads(m["outcomes"]); toks = json.loads(m["tokens"]); yt = toks[[o.lower() for o in outs].index("yes")]
            lp = last_print([t for t in e["trades"] if t["c"] == m["cid"]], yt, T)
            rows.append(dict(tk=tk, monday=e["monday"], kind=kind, K=ks[1], dirn=ks[0], P=P, C=C, win=w, lp=lp, rate=fee_rate(m.get("fee"))))
    n = len(rows); print("resolved strikes with perp and close:", allstrikes, "| candidates (perp crossed the strike):", n)
    if not n: return
    print("(a) YES win rate over ALL candidates: %.3f (%d of %d); by kind: %s" % (sum(r["win"] for r in rows) / n, sum(r["win"] for r in rows), n,
          {k: "%d/%d" % (sum(r["win"] for r in rows if r["kind"] == k), sum(1 for r in rows if r["kind"] == k)) for k in sorted({r["kind"] for r in rows})}))
    print("    mondays with a candidate:", len({r["monday"] for r in rows}), "| tickers:", dict(Counter(r["tk"] for r in rows)))
    wp = [r for r in rows if r["lp"]]; nop = n - len(wp)
    print("(c) candidates with NO print at all before T: %d of %d (%.0f%%)" % (nop, n, 100 * nop / n))
    if wp:
        ages = [r["lp"][1] / 3600 for r in wp]; gs = [gap(r["win"], r["lp"][0], r["rate"]) for r in wp]
        print("(b) last-print reference on %d candidates: median price %.2f, median age %.1f h, mean gap %.3f, YES win %.2f" % (len(wp), statistics.median(r["lp"][0] for r in wp), statistics.median(ages), sum(gs) / len(gs), sum(r["win"] for r in wp) / len(wp)))
        live = [r for r in wp if 0.05 < r["lp"][0] < 0.95]
        if live:
            gl = [gap(r["win"], r["lp"][0], r["rate"]) for r in live]
            print("    of which tradable-priced (0.05-0.95): %d, mean gap %.3f, win %.2f, median price %.2f" % (len(live), sum(gl) / len(gl), sum(r["win"] for r in live) / len(live), statistics.median(r["lp"][0] for r in live)))
        young = [r for r in wp if r["lp"][1] <= 6 * 3600 and 0.05 < r["lp"][0] < 0.95]
        if young:
            gy = [gap(r["win"], r["lp"][0], r["rate"]) for r in young]
            print("    last print within 6 h of T and tradable: %d, mean gap %.3f, win %.2f" % (len(young), sum(gy) / len(gy), sum(r["win"] for r in young) / len(young)))
    json.dump(rows, open(run + "/explore_touch_rows.json", "w"), default=str)

if __name__ == "__main__":
    main(sys.argv[1])
