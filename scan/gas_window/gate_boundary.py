#!/usr/bin/env python3
"""Gate for the pre-registered boundary rule (DESIGN-amendment-2): each rule must (1) place an order, (2) get a fill from recorded prints, (3) be able to fail.
No orders are ever sent (SETTLED A7): everything runs on a recorded book snapshot and recorded taker prints.
Queue priority is UNSOURCED (MECHANICS addendum), so a resting bid is credited with a fill only when a recorded SELL print on that token crosses its price after the post time."""
TICK = 0.001
MIN_SIZE = 5
def decide(margin_cents, p, bid, bank, depth_cap):
    """Boundary rule: trade only when margin >= 0.5c and p > bid; quarter Kelly stake = 0.25*bank*(p-bid)/(1-bid), capped by depth. Returns shares or 0."""
    if margin_cents < 0.5 or p <= bid or not (0 < bid < 1): return 0.0
    stake = 0.25 * bank * (p - bid) / (1 - bid)
    return min(stake / bid, depth_cap)
def can_post(bid, size, token_book):
    """A resting bid is postable if it is on the tick grid, at least the minimum size, and strictly below the best ask (post-only: a crossing order would be a taker)."""
    if size < MIN_SIZE: return False
    if abs(bid / TICK - round(bid / TICK)) > 1e-6: return False
    ask = token_book.get("best_ask")
    return ask is None or bid < ask
def fill_shares(bid, t_post, prints, bucket, outcome):
    """prints: rows [ts, bucket, outcome, side, price, size, ...]. A bid fills only against a recorded SELL print on the same token at a price <= bid after t_post."""
    return sum(r[5] for r in prints if r[0] >= t_post and r[1] == bucket and r[2] == outcome and r[3] == "SELL" and r[4] <= bid + 1e-9)
def run_gate(book_row, token_label, bucket, outcome, bid, size, t_post, prints):
    """Returns dict(post, fill_shares). token_label is the suffix of the recorded label, e.g. 'less than $3.7000 on November 20?|Yes'."""
    tok = next(v for v in book_row["tok"].values() if v["label"].endswith(token_label))
    ok = can_post(bid, size, tok)
    return {"post": ok, "fill_shares": fill_shares(bid, t_post, prints, bucket, outcome) if ok else 0.0, "best_ask": tok["best_ask"], "best_bid": tok["bids"][0][0] if tok["bids"] else None}
