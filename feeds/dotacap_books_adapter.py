#!/usr/bin/env python3
"""Adapter: dotacap books.jsonl (capture.js, 16-17 Nov) -> recorder format that feeds/ps_lead_test.py reads.
Input row : {"recv_ms":..., "token": "<own token id>", "bid": 0.61, "ask": 0.62, ...}  (top of that token's OWN book)
Output row: {"asset": token, "recv_ms": ..., "bids":[{"price": bid}], "asks":[{"price": ask}]}
ps_lead_test.py computes mid = (max bid + min ask)/2, identical to (bid+ask)/2, so nothing else changes.
Rows without a numeric bid and ask are dropped and counted. No token is derived from another (never NO = 1 - YES).
Usage: dotacap_books_adapter.py IN books.jsonl  OUT_DIR   (writes OUT_DIR/books.jsonl; prints counts only)
"""
import json, os, sys

def convert(row):
    t, b, a, ms = row.get("token"), row.get("bid"), row.get("ask"), row.get("recv_ms")
    if t is None or ms is None or not isinstance(b, (int, float)) or not isinstance(a, (int, float)):
        return None
    return {"asset": t, "recv_ms": ms, "bids": [{"price": b}], "asks": [{"price": a}]}

def main(src, outdir):
    os.makedirs(outdir, exist_ok=True)
    n = k = bad = 0
    with open(src, errors="replace") as f, open(os.path.join(outdir, "books.jsonl"), "w") as o:
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
    print(json.dumps({"rows_in": n, "rows_out": k, "dropped": bad}))

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
