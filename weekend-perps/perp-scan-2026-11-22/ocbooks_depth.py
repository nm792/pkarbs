#!/usr/bin/env python3
"""Decision-time OWN-TOKEN depth from the recorded SPX/SPY 'Opens Up or Down' books (book_recorder.py output).
Usage: python3 ocbooks_depth.py DIR_WITH_ocbooks_files [OUTFILE.json]     (run WITHOUT -I from this directory; stdlib only, imports pscanlib)
For every recorded event (slug) and token (Up, Down): the row nearest to T-60, T-30, T-10 minutes before 09:30 New York (max 20 s away), with
best ask, best bid and $ ask depth within 3c of the OWN best ask. Tokens with no row at a checkpoint are counted as MISSING, never filled in.
Prints a summary table plus per-day lines. Read-only."""
import gzip, glob, json, sys, os, re, datetime, calendar, statistics
from zoneinfo import ZoneInfo
from pscanlib import best_ask, best_bid, ask_depth_usd, tradable

def open_ts(d):
    """unix seconds of 09:30 America/New_York on date d (stdlib only: the server need not have numpy)"""
    return datetime.datetime(d.year, d.month, d.day, 9, 30, tzinfo=ZoneInfo("America/New_York")).timestamp()

KS = (60, 30, 10)
MAXD = 20.0

def slug_date(slug):
    m = re.search(r"on-([a-z]+)-(\d+)-(\d{4})$", slug)
    if not m:
        return None
    mon = list(calendar.month_name).index(m.group(1).capitalize())
    return datetime.date(int(m.group(3)), mon, int(m.group(2)))

def nearest(rows, t):
    best = None
    for r in rows:
        d = abs(r["t"] - t)
        if d <= MAXD and (best is None or d < best[0]):
            best = (d, r)
    return best[1] if best else None

def summarize(rows):
    """rows: dicts with t, slug, side, bids, asks (list of [px, sz]) or err. -> list of per-(slug, side, k) records."""
    by = {}
    for r in rows:
        if "err" in r or "slug" not in r or "side" not in r:
            continue
        by.setdefault((r["slug"], r["side"]), []).append(r)
    out = []
    for (slug, side), rs in sorted(by.items()):
        d = slug_date(slug)
        if d is None:
            continue
        T = open_ts(d)
        for k in KS:
            r = nearest(rs, T - 60 * k)
            if r is None:
                out.append(dict(slug=slug, side=side, k=k, missing=True))
                continue
            asks = [{"price": p, "size": s} for p, s in r["asks"]]
            bids = [{"price": p, "size": s} for p, s in r["bids"]]
            ba = best_ask(asks)
            out.append(dict(slug=slug, side=side, k=k, missing=False, best_ask=ba, best_bid=best_bid(bids), depth_usd=ask_depth_usd(asks), tradable=tradable(ba), dt=r["t"] - (T - 60 * k)))
    return out

def load(dirn):
    rows = []
    for f in sorted(glob.glob(os.path.join(dirn, "ocbooks_*.jsonl.gz"))):
        with gzip.open(f, "rt") as fh:
            for line in fh:
                try:
                    rows.append(json.loads(line))
                except Exception:
                    pass
    return rows

def main(dirn, outfile=None):
    rows = load(dirn)
    recs = summarize(rows)
    n_err = sum(1 for r in rows if "err" in r)
    print("rows %d, error rows %d, (slug,side,checkpoint) records %d" % (len(rows), n_err, len(recs)))
    for k in KS:
        rk = [r for r in recs if r["k"] == k]
        have = [r for r in rk if not r["missing"]]
        tr = [r for r in have if r["tradable"]]
        dep = [r["depth_usd"] for r in tr]
        print("T-%2d min: tokens %3d, with a row %3d, missing %3d, tradable (ask in (0.05,0.95)) %3d, median depth $%s, max depth $%s, >=$200: %d" % (
            k, len(rk), len(have), len(rk) - len(have), len(tr), ("%.0f" % statistics.median(dep)) if dep else "n/a", ("%.0f" % max(dep)) if dep else "n/a", sum(x >= 200 for x in dep)))
    for r in recs:
        if r["k"] == 30 and not r["missing"]:
            print("  %-46s %-5s T-30 ask %-6s bid %-6s depth $%7.0f tradable=%s" % (r["slug"][:46], r["side"], r["best_ask"], r["best_bid"], r["depth_usd"], r["tradable"]))
    if outfile:
        json.dump(recs, open(outfile, "w"))

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
