#!/usr/bin/env python3
"""Adapter: dotacap books.jsonl (capture.js, 16-17 Nov) -> recorder format that feeds/ps_lead_test.py reads.
Input row : {"recv_ms":..., "token": "<own token id>", "bid": 0.61, "ask": 0.62, ...}  (top of that token's OWN book)
Output row: {"asset": token, "recv_ms": ..., "bids":[{"price": bid}], "asks":[{"price": ask}]}
ps_lead_test.py computes mid = (max bid + min ask)/2, identical to (bid+ask)/2, so nothing else changes.
Rows without a numeric bid and ask are dropped and counted. No token is derived from another (never NO = 1 - YES).
Usage: dotacap_books_adapter.py IN [IN ...] OUT_DIR   (last argument is the output dir; writes OUT_DIR/books.jsonl; prints counts only)
"""
import gzip, glob, json, os, sys, zlib

def convert(row):
    t, b, a, ms = row.get("token"), row.get("bid"), row.get("ask"), row.get("recv_ms")
    if t is None or ms is None or not isinstance(b, (int, float)) or not isinstance(a, (int, float)):
        return None
    return {"asset": t, "recv_ms": ms, "bids": [{"price": b}], "asks": [{"price": a}]}

def opn(p):
    return gzip.open(p, "rt", errors="replace") if p.endswith(".gz") else open(p, errors="replace")


def main(srcs, outdir):
    """srcs: one or more files or globs (plain or .gz, e.g. 'books.*.jsonl.gz books.jsonl'); damaged gzip tails keep rows read so far."""
    os.makedirs(outdir, exist_ok=True)
    files = sorted({f for s_ in srcs for f in (glob.glob(s_) or ([] if '*' in s_ else [s_]))})
    n = k = bad = partial = 0
    with open(os.path.join(outdir, "books.jsonl"), "w") as o:
        for src in files:
            try:
                with opn(src) as f:
                    for l in f:
                        n += 1
                        try:
                            r = convert(json.loads(l))
                        except Exception:
                            r = None
                        if r is None:
                            bad += 1
                            continue
                        o.write(json.dumps(r) + "\n")
                        k += 1
            except (EOFError, OSError, zlib.error) as e:
                partial += 1
                sys.stderr.write("PARTIAL FILE %s: %s\n" % (src, e))
    print(json.dumps({"files": len(files), "rows_in": n, "rows_out": k, "dropped": bad, "partial_files": partial}))


if __name__ == "__main__":
    main(sys.argv[1:-1], sys.argv[-1])
