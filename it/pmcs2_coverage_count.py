#!/usr/bin/env python3
"""READ-ONLY: count Polymarket CS2 markets starting on a UTC date whose BOTH tokens have own-book rows in pmcs2 books-*.jsonl[.gz].
usage: python3 -I pmcs2_coverage_count.py PMCS2_DIR YYYY-MM-DD   (prints one JSON object; changes nothing)
A market = markets.jsonl line {cond,q,outcomes,tokens,start}; start is the game start (ISO). Rows are counted per token from the books files whose hour is the date or the day after."""
import sys, os, json, gzip, glob, collections

def lines(p):
    op = gzip.open if p.endswith(".gz") else open
    try:
        with op(p, "rt") as f:
            for l in f:
                yield l
    except Exception as e:
        sys.stderr.write("skip %s: %s\n" % (os.path.basename(p), e))

def main(d, day):
    mk = {}
    for l in lines(os.path.join(d, "markets.jsonl")):
        try: m = json.loads(l)
        except Exception: continue
        if str(m.get("start") or "").startswith(day) and len(m.get("tokens") or []) == 2: mk[m["cond"]] = m
    want = {t for m in mk.values() for t in m["tokens"]}
    rows = collections.Counter(); first = {}
    nxt = day[:8] + "%02d" % (int(day[8:]) + 1)
    files = sorted(glob.glob(os.path.join(d, "books-*.jsonl*")))
    used = [p for p in files if os.path.basename(p)[6:16].startswith((day.replace("-", ""), nxt.replace("-", "")))]
    for p in used:
        for l in lines(p):
            try: r = json.loads(l)
            except Exception: continue
            a = r.get("asset")
            if a in want:
                rows[a] += 1; first.setdefault(a, r.get("recv_ms"))
    both = [c for c, m in mk.items() if all(rows[t] > 0 for t in m["tokens"])]
    out = dict(day=day, markets_starting=len(mk), markets_both_tokens_rows=len(both), files_read=[os.path.basename(p) for p in used],
               missing=[(mk[c]["q"], [rows[t] for t in mk[c]["tokens"]]) for c in mk if c not in both][:40],
               both=[(mk[c]["q"], mk[c]["start"], [rows[t] for t in mk[c]["tokens"]]) for c in both][:60])
    print(json.dumps(out, indent=1))

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
