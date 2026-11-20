#!/usr/bin/env python3
"""Record every public trade of one 'US gas price on <date>' event at ~1 s, all six markets (YES and NO tokens), with wallet and tx hash,
so a sweep can be matched to the books recorded by pm_gas_books.py. Read-only. data-api /v2/trades limit 300 req/10 s: six markets per second = 60 req/10 s.
usage: pm_gas_trades.py --slug S --out DIR --until ISOZ [--interval 1] [--max-seconds N]
Appends one line per NEW trade to DIR/<slug>.trades.jsonl: {recv_ns, ...raw data-api row}. Rows are deduplicated on (tx hash, token, price, size, timestamp)."""
import json, os, sys, time, argparse, calendar
import pm_gas_books as b
def condition_ids(slug):
    return [m["conditionId"] for m in b._get(f"https://gamma-api.polymarket.com/events?slug={slug}")[0]["markets"]]
def fetch(cid, limit=500):
    j = b._get(f"https://data-api.polymarket.com/v2/trades?conditionId={cid}&limit={limit}")
    return j["data"] if isinstance(j, dict) and "data" in j else j
def key(r): return (r.get("transaction_hash"), r.get("token_id"), r.get("price"), r.get("size"), r.get("timestamp"))
def new_rows(rows, seen):
    out = []
    for r in rows:
        k = key(r)
        if k not in seen: seen.add(k); out.append(r)
    return out
def run(slug, out, until, interval=1.0, max_seconds=2400, fetch_fn=fetch, cids=None, sleep=time.sleep, now=time.time):
    os.makedirs(out, exist_ok=True); cids = cids or condition_ids(slug); seen = set(); n = 0; err = 0; t_start = now()
    with open(os.path.join(out, slug + ".trades.jsonl"), "a") as f:
        while now() < until and now() - t_start < max_seconds:
            t0 = now()
            for c in cids:
                try:
                    for r in new_rows(fetch_fn(c), seen): f.write(json.dumps(dict(r, recv_ns=time.time_ns())) + "\n"); n += 1
                    f.flush()
                except Exception as ex: err += 1; print("ERR", repr(ex)[:100], flush=True)    # never exit on a failed poll
            sleep(max(0.0, interval - (now() - t0)))
    print(f"new trades {n} errors {err}"); return n, err
if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--slug", required=True); ap.add_argument("--out", required=True); ap.add_argument("--until", required=True)
    ap.add_argument("--interval", type=float, default=1.0); ap.add_argument("--max-seconds", type=float, default=2400); a = ap.parse_args()
    run(a.slug, a.out, calendar.timegm(time.strptime(a.until, "%Y-%m-%dT%H:%M:%SZ")), a.interval, a.max_seconds)
