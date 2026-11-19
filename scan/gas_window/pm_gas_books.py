#!/usr/bin/env python3
"""Record Polymarket CLOB books (each token's OWN asks and bids) for one 'US gas price on <date>' event at ~1 s, so depth at stale
prices can be read around the daily sweep. Read-only public endpoints, no orders. Usage:
  pm_gas_books.py --slug us-gas-price-on-november-19-2026 --out DIR --until 2026-11-19T08:45:00Z [--interval 1.0] [--max-seconds 540]
Appends one JSON line per poll to DIR/<slug>.books.jsonl: {recv_ns, tok:{token_id:{label, best_ask, ask_depth_le_97, asks:[[p,s]..], bids:[[p,s]..], ltp, book_ts}}}"""
import json, os, sys, time, argparse, calendar, urllib.request
def _get(u, data=None):
    r = urllib.request.Request(u, data=data, headers={"User-Agent": "Mozilla/5.0", "Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(r, timeout=20))
def parse_book(b, top=12):
    """one /books entry -> own asks sorted best (lowest) first, bids best (highest) first. The API lists levels in descending price order."""
    asks = sorted(((float(x["price"]), float(x["size"])) for x in b.get("asks", [])))[:top]
    bids = sorted(((float(x["price"]), float(x["size"])) for x in b.get("bids", [])), reverse=True)[:top]
    ltp = b.get("last_trade_price"); ltp = float(ltp) if ltp not in (None, "") else None
    return {"best_ask": asks[0][0] if asks else None, "ask_depth_le_97": sum(s for p, s in asks if p <= 0.97), "asks": asks, "bids": bids, "ltp": ltp,
            "book_ts": int(b["timestamp"]) if b.get("timestamp") else None}
def event_tokens(slug):
    e = _get(f"https://gamma-api.polymarket.com/events?slug={slug}")[0]; out = []
    for m in e["markets"]:
        for lab, t in zip(json.loads(m["outcomes"]), json.loads(m["clobTokenIds"])): out.append((t, f"{m['question'][-50:]}|{lab}"))
    return out
def poll(tokens):
    arr = _get("https://clob.polymarket.com/books", json.dumps([{"token_id": t} for t, _ in tokens]).encode())
    lab = dict(tokens); res = {}
    for b in arr: res[b["asset_id"]] = dict(parse_book(b), label=lab.get(b["asset_id"]))
    return res
if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--slug", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--until", required=True); ap.add_argument("--interval", type=float, default=1.0); ap.add_argument("--max-seconds", type=float, default=540)
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
    until = calendar.timegm(time.strptime(a.until, "%Y-%m-%dT%H:%M:%SZ")); toks = event_tokens(a.slug)
    path = os.path.join(a.out, f"{a.slug}.books.jsonl"); t_start = time.time(); n = 0; err = 0
    with open(path, "a") as f:
        while time.time() < until and time.time() - t_start < a.max_seconds:
            t0 = time.time()
            try: f.write(json.dumps({"recv_ns": time.time_ns(), "tok": poll(toks)}) + "\n"); f.flush(); n += 1
            except Exception as ex: err += 1; print("ERR", repr(ex)[:120], flush=True)
            time.sleep(max(0.0, a.interval - (time.time() - t0)))
    print(f"polls {n} errors {err} file {path}")
