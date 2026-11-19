"""Book snapshots and depth metrics for release-window recording (own-token books only)."""
import json, os, sys, time
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import pit_store as P


def depth(book, band=0.03):
    asks = sorted((float(a["price"]), float(a["size"])) for a in book.get("asks", []))
    bids = sorted(((float(b["price"]), float(b["size"])) for b in book.get("bids", [])), reverse=True)
    out = dict(best_ask=asks[0][0] if asks else None, best_ask_size=asks[0][1] if asks else None,
               best_bid=bids[0][0] if bids else None, best_bid_size=bids[0][1] if bids else None)
    if asks:
        ba = asks[0][0]
        out["ask_usd_within"] = sum(p * s for p, s in asks if p <= ba + band + 1e-12)
        out["ask_shares_within"] = sum(s for p, s in asks if p <= ba + band + 1e-12)
        out["ask_usd_total"] = sum(p * s for p, s in asks)
    return out


def snapshot(token_id):
    t0 = time.time(); b = P.http_json(f"https://clob.polymarket.com/book?token_id={token_id}", timeout=15, tries=1)
    d = depth(b); d["token"] = token_id; d["t_local"] = t0; d["t_resp"] = time.time(); d["book_ts"] = b.get("timestamp")
    return d


def open_event(series_slug):
    d = P.http_json(f"https://gamma-api.polymarket.com/events/keyset?closed=false&limit=5&series_slug={series_slug}")
    return d.get("events", [])
