#!/usr/bin/env python3
"""Pure helpers for snapshot.py (no network): turn a gamma market + clob books into per-token OWN-TOKEN rows."""
import json
from pscanlib import best_ask, best_bid, ask_depth_usd, tradable, parse_strike, gap_beyond


def market_tokens(m):
    """[(outcome_label, token_id)] from a gamma market; outcomes and clobTokenIds are JSON strings in parallel order."""
    outs = json.loads(m["outcomes"]) if isinstance(m.get("outcomes"), str) else (m.get("outcomes") or [])
    toks = json.loads(m["clobTokenIds"]) if isinstance(m.get("clobTokenIds"), str) else (m.get("clobTokenIds") or [])
    return list(zip(outs, toks))


def token_row(slug, family, m, outcome, token, book, ts):
    """One own-token row. A token with no recorded book gets book_ok False and is EXCLUDED from capacity (never inferred from the other token)."""
    ok = isinstance(book, dict) and ("asks" in book or "bids" in book)
    asks = book.get("asks") if ok else None
    bids = book.get("bids") if ok else None
    ba = best_ask(asks) if ok else None
    return dict(t=ts, slug=slug, family=family, market=m.get("slug"), q=m.get("question"), outcome=outcome, token=token, book_ok=ok,
                best_ask=ba, best_bid=best_bid(bids) if ok else None, ask_depth_usd=ask_depth_usd(asks) if ok else 0.0,
                n_ask_levels=len(asks or []), tradable=tradable(ba))


def candidates(rows, marks, closes, margins):
    """Rows (YES tokens only) whose strike the perp has ALREADY crossed (gap_beyond). marks/closes: {under: float}; margins: {under: float}.
    Returns the matching rows with strike info attached. A row needs under, strike, perp, close; otherwise it is not a candidate."""
    out = []
    for r in rows:
        if r.get("outcome") != "Yes" or not r.get("under"):
            continue
        ks = parse_strike(r.get("q"))
        u = r["under"]
        if not ks or u not in marks or u not in closes:
            continue
        if gap_beyond(marks[u], closes[u], ks[0], ks[1], margins.get(u, 0.002)):
            out.append(dict(r, kind=ks[0], strike=ks[1], perp=marks[u], close=closes[u]))
    return out
