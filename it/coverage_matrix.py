#!/usr/bin/env python3
"""READ-ONLY coverage matrix: for each Goalserve sport, how many distinct matches of the last --hours h have a winner market and a unique
Polymarket market in the recorder folders, and how many of those tokens have book rows in the tail of the books file (own token book; never 1-YES).
Goalserve rows are sampled (every --every-th row), so a match shorter than a few minutes can be missed: counts are LOWER bounds on matches, the rates are what matters.
Usage: FEEDS_DIR=<exported feeds dir> python3 -I coverage_matrix.py --pm-dir NAME=DIR [--pm-dir ...] --gs-dir esports=DIR [--gs-dir tennis=DIR ...] --out coverage.json [--hours 24] [--tail-mb 1500]
(NAME=DIR: DIR holds markets.jsonl and books.jsonl or books.jsonl.gz.)"""
import argparse, collections, glob, gzip, json, os, re, sys, time
sys.path.insert(0, os.environ.get("FEEDS_DIR") or os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "feeds"))
import goalserve_odds_vs_pm_v2 as v2
from ps_lead_test import norm, find, load_pm, mk_index


def matches(files, sport, every):
    v2.SPORT = sport
    seen = {}
    for p in files:
        n = 0
        try:
            with gzip.open(p, "rt") as f:
                for l in f:
                    n += 1
                    if n % every:
                        continue
                    try:
                        d = json.loads(json.loads(l)["body"])
                    except Exception:
                        continue
                    for eid, e in (d.get("events") or {}).items():
                        ti = e.get("team_info") or {}
                        h, a = norm((ti.get("home") or {}).get("name")), norm((ti.get("away") or {}).get("name"))
                        if not h or not a:
                            continue
                        for m in (e.get("odds") or {}).values():
                            if isinstance(m, dict) and v2.kind_of(m.get("name") or "?") == "Match Winner":
                                seen[(eid, h, a)] = True
        except (EOFError, OSError):
            pass
    return list(seen)


def tail_tokens(d, need, tail_mb):
    p = find(d, "books")
    if not p:
        return set(), "no books file"
    got = set()
    if p.endswith(".gz"):
        op, size = (lambda: gzip.open(p, "rt")), os.path.getsize(p)
        try:
            for l in op():
                try:
                    r = json.loads(l)
                except Exception:
                    continue
                if (r.get("tk") or r.get("asset")) in need:
                    got.add(r.get("tk") or r.get("asset"))
        except (EOFError, OSError):
            pass
        return got, "gz whole file %d bytes" % size
    size = os.path.getsize(p)
    with open(p, "rb") as f:
        start = max(0, size - int(tail_mb * 1e6))
        f.seek(start)
        if start:
            f.readline()      # drop the partial first line only when we did not start at byte 0
        for l in f:
            m = re.search(rb'"(?:asset|tk)":\s*"(\d+)"', l)
            if m and m.group(1).decode() in need:
                got.add(m.group(1).decode())
    return got, "tail %d MB of %d bytes" % (min(size, tail_mb * 1e6) / 1e6, size)


def run(a):
    now = time.time()
    idx = {}
    for nm, d in (x.split("=", 1) for x in a.pm_dir):
        idx[nm] = (d, mk_index(load_pm([d])))
    res = {}
    for s, d in (x.split("=", 1) for x in a.gs_dir):
        files = [p for p in sorted(glob.glob(os.path.join(d, "*.jsonl.gz"))) if now - os.path.getmtime(p) < a.hours * 3600 + 3600]
        ms = matches(files, s, a.every)
        row = dict(hour_files_read=len(files), goalserve_matches_24h=len(ms), by_recorder={})
        for nm, (pd, ix) in idx.items():
            hit = [m for m in ms if len([x for x in ix.get(frozenset((m[1], m[2])), []) if x["kind"] == "Match Winner"]) == 1]
            need = {t for m in hit for x in ix[frozenset((m[1], m[2]))] if x["kind"] == "Match Winner" for t in x["tokens"]}
            got, how = tail_tokens(pd, need, a.tail_mb)
            row["by_recorder"][nm] = dict(matches_with_unique_pm_market=len(hit), match_rate_pct=100.0 * len(hit) / len(ms) if ms else None,
                                          tokens_needed=len(need), tokens_with_book_rows_in_tail=len(got & need), books_read=how)
        res[s] = row
    return res


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--pm-dir", action="append", required=True)
    ap.add_argument("--gs-dir", action="append", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--hours", type=float, default=24)
    ap.add_argument("--every", type=int, default=20)
    ap.add_argument("--tail-mb", type=float, default=1500)
    a = ap.parse_args()
    r = run(a)
    json.dump(r, open(a.out, "w"), indent=1, sort_keys=True)
    for s, v in r.items():
        print(s, json.dumps(v))
