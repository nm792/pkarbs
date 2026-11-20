"""Pure daily rule for the US gas price series: decides how many shares to take from ONE displayed ask, given the model's win probability for that token.
No I/O, no venue names: any market adapter (Polymarket now, Kalshi later: SETTLED A6, analysis only) feeds quotes in and reads decisions out.
Pre-registered parameters (DESIGN-gas-daily-rule.md, written before the NO-side and post-AAA results were seen; the YES gap 0.05 is from DESIGN-amendment-2, PR 447)."""
from dataclasses import dataclass
@dataclass(frozen=True)
class Params:
    bank: float = 1000.0          # paper bankroll in USD (ASSUMED, scale-free results are also reported)
    frac: float = 0.25            # quarter Kelly (Nick, 19 Nov)
    yes_gap: float = 0.05         # YES on the pre-AAA favourite only when ask <= q - gap
    out_q: float = 0.02           # NO only on buckets the nowcast rules out: q_bucket <= out_q
    out_min_edge: float = 0.005   # NO: q_no - ask - fee per share >= this
    post_q: float = 0.995         # after the AAA read: win probability given to the bucket the page shows (ASSUMED 0.5% page/resolution risk)
    post_min_edge: float = 0.003
    event_cap: float = 0.15       # v1: ONE shared cap on total cost per event (used when rule_caps is None)
    rule_caps: tuple = None       # v2: ((kind, fraction of bank), ...) separate cost cap per rule and event
    fee_rate: float = 0.04
def fee_per_share(p, rate=0.04): return rate * p * (1 - p)
def kelly_target(q, p, bank, frac):
    """USD stake target for a binary at price p with win probability q (full Kelly fraction (q-p)/(1-p))."""
    return max(0.0, frac * bank * (q - p) / (1 - p)) if 0 < p < 1 else 0.0
def eligible(kind, q, p, prm):
    """kind: 'yes_fav' (window pre-AAA), 'no_out' (pre-AAA, NO of a bucket with q_bucket<=out_q), 'post' (after the AAA read)."""
    if kind == "yes_fav": return q - p >= prm.yes_gap
    if kind == "no_out": return q - p - fee_per_share(p, prm.fee_rate) >= prm.out_min_edge
    if kind == "post": return q - p - fee_per_share(p, prm.fee_rate) >= prm.post_min_edge
    raise ValueError(kind)
def cap_usd(kind, prm):
    return (dict(prm.rule_caps)[kind] if prm.rule_caps else prm.event_cap) * prm.bank
def take(kind, q, p, size, spent_token, spent_event, prm):
    """shares to take from one displayed ask (price p, size): limited by the ask size, the token's Kelly target and the cap (spent_event = cost already spent against that cap: all rules in v1, this rule only in v2)."""
    if not eligible(kind, q, p, prm): return 0.0
    room_tok = kelly_target(q, p, prm.bank, prm.frac) - spent_token
    room_ev = cap_usd(kind, prm) - spent_event
    usd = min(room_tok, room_ev)
    if usd <= 0: return 0.0
    return min(size, usd / p)
