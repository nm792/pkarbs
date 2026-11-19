#!/usr/bin/env python3
"""Live own-token book snapshot for every open Polymarket gas market (public CLOB /book). No orders.
Usage: python3 books.py <out.json>. Prints, per series: open tokens, tokens with any ask, $ of asks at
0.05 <= best ask < 0.95 and within 5c of the best ask (each token priced only from its own asks, SETTLED A1)."""
import json, sys, time, urllib.request
from collections import defaultdict
def get(u):
    return json.load(urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "research-client"}), timeout=30))
out = {"t": time.time(), "books": []}; agg = defaultdict(lambda: defaultdict(float))
for s in ["us-gas-price-daily", "gas-price-hits-weekly", "gas-price-hits"]:
    for e in get(f"https://gamma-api.polymarket.com/series?slug={s}")[0]["events"]:
        if e.get("closed"): continue
        ev = get(f"https://gamma-api.polymarket.com/events?slug={e['slug']}")[0]
        for m in ev["markets"]:
            if m.get("closed"): continue
            for oi, tok in enumerate(json.loads(m["clobTokenIds"])):
                try: b = get(f"https://clob.polymarket.com/book?token_id={tok}")
                except Exception as ex: agg[s]["book_err"] += 1; continue
                asks = [(float(x["price"]), float(x["size"])) for x in b.get("asks", [])]
                bids = [(float(x["price"]), float(x["size"])) for x in b.get("bids", [])]
                out["books"].append({"series": s, "event": e["slug"], "bucket": m.get("groupItemTitle"), "outcome_index": oi,
                                     "token": tok, "asks": asks, "bids": bids, "ts": b.get("timestamp")})
                a = agg[s]; a["tokens"] += 1; a["with_ask"] += bool(asks)
                ba = min((p for p, q in asks), default=None)
                if ba is not None and 0.05 <= ba < 0.95:   # best own ask in the qualifying band
                    a["tokens_best_ask_qual"] += 1
                    a["ask_usd_within_5c_of_best"] += sum(p * q for p, q in asks if p <= ba + 0.05)
json.dump(out, open(sys.argv[1], "w"))
print(time.strftime("%Y-%m-%d %H:%M:%SZ", time.gmtime(out["t"])))
for s, a in agg.items(): print(s, {k: round(v) for k, v in a.items()})
