#!/usr/bin/env python3
"""Read-only: for each Polymarket market in a recorder dir, are BOTH tokens' own books recorded?
Usage: pm_token_coverage.py DIR [TAIL_BYTES]   (reads markets.jsonl(.gz) fully and the last TAIL_BYTES of books.jsonl, default 2 GB)
Prints per sport: markets with books for both tokens / one token only / none, and book rows per side. Writes nothing."""
import sys, os, json, gzip, collections
d = sys.argv[1]; tail = int(sys.argv[2]) if len(sys.argv) > 2 else 2_000_000_000
def op(p): return gzip.open(p, "rt", errors="replace") if p.endswith(".gz") else open(p, errors="replace")
mk = {}
for f in ("markets.jsonl", "markets.jsonl.gz"):
    p = os.path.join(d, f)
    if os.path.exists(p):
        for line in op(p):
            try: m = json.loads(line)
            except Exception: continue
            t = m.get("tokens") or []
            if len(t) == 2: mk[m.get("cond") or tuple(t)] = (m.get("sport", "?"), t[0], t[1])
rows = collections.Counter(); p = os.path.join(d, "books.jsonl")
with open(p, "rb") as f:
    size = os.path.getsize(p); f.seek(max(0, size - tail))
    if f.tell(): f.readline()
    for raw in f:
        try: r = json.loads(raw)
        except Exception: continue
        tk = r.get("tk") or r.get("asset") or r.get("token")
        if tk: rows[tk] += 1
both = collections.Counter(); one = collections.Counter(); none = collections.Counter()
for c, (sp, a, b) in mk.items():
    x = (rows[a] > 0) + (rows[b] > 0)
    (both if x == 2 else one if x == 1 else none)[sp] += 1
print("books bytes read", min(size, tail), "markets with 2 tokens", len(mk))
for sp in sorted({v[0] for v in mk.values()}):
    ra = sum(rows[a] for (s, a, b) in mk.values() if s == sp); rb = sum(rows[b] for (s, a, b) in mk.values() if s == sp)
    print(sp, "markets both-tokens", both[sp], "one-token-only", one[sp], "no-books", none[sp], "rows token0", ra, "rows token1", rb)
