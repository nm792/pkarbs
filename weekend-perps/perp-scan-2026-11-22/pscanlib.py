#!/usr/bin/env python3
"""Pure functions for the perp-related arbs scan (R-036 item 2, 22 Nov 2026). No network here.

Rule (SETTLED capacity rule, Nick 22 Nov 05:27Z): capacity is measured from OWN-TOKEN order-book depth at decision time,
at $200 per trade (or the nearest available ask), $2,000/day cap. Print-sized backtests are labelled FLOOR.

Order-book note: the clob /book lists bids ascending and asks DESCENDING (best ask = LAST level). This library never relies on
list order: it sorts levels by price itself (test_pscanlib.py plants both orders and must fail a first-element reader).
"""
import re, math

PER_TRADE = 200.0
DAY_CAP = 2000.0
NEAR = 0.03          # depth is counted from the best ask up to best ask + NEAR (3c, the locked threshold)
PROB_LO, PROB_HI = 0.05, 0.95   # dead-bucket rule: tokens priced outside (0.05, 0.95) are not findings


def levels(raw):
    """[{'price':'0.4','size':'10'},...] -> [(price, size)] sorted ascending by price, bad rows dropped."""
    out = []
    for x in raw or []:
        try:
            p, s = float(x["price"]), float(x["size"])
        except Exception:
            continue
        if 0 < p < 1 and s > 0:
            out.append((p, s))
    return sorted(out)


def best_ask(asks):
    """lowest ask price (NOT the first or last list element) or None"""
    a = levels(asks)
    return a[0][0] if a else None


def best_bid(bids):
    b = levels(bids)
    return b[-1][0] if b else None


def ask_depth_usd(asks, near=NEAR):
    """$ cost of buying every share offered from the best ask up to best ask + near (inclusive, float-safe)."""
    a = levels(asks)
    if not a:
        return 0.0
    top = a[0][0] + near + 1e-9
    return sum(p * s for p, s in a if p <= top)


def tradable(ask):
    return ask is not None and PROB_LO < ask < PROB_HI


def parse_strike(question):
    """('HIGH'|'LOW', strike float) from a Polymarket 'hit' question; None if not parseable.
    'Will WTI Crude Oil (WTI) hit (HIGH) $160 in November?' -> ('HIGH', 160.0); 'dip to (LOW) $3,500' -> ('LOW', 3500.0)"""
    q = question or ""
    m = re.search(r"\$\s*([0-9][0-9,]*\.?[0-9]*)", q)
    if not m:
        return None
    k = float(m.group(1).replace(",", ""))
    if re.search(r"\(LOW\)|\bdip\b|\bfall\b", q, re.I):
        return ("LOW", k)
    if re.search(r"\(HIGH\)|\bhit\b|\breach\b", q, re.I):
        return ("HIGH", k)
    return None


def gap_beyond(perp, close, kind, strike, margin=0.002):
    """True when the perp already sits beyond the strike by `margin` AND the last cash close was not yet beyond it
    (so the touch has not already happened at the last close). HIGH: close < K <= perp*(1-margin). LOW: perp*(1+margin) <= K < close."""
    if perp is None or close is None or strike is None:
        return False
    if kind == "HIGH":
        return close < strike and perp * (1 - margin) >= strike
    if kind == "LOW":
        return close > strike and perp * (1 + margin) <= strike
    return False


def per_decision_usd(depth_usd, per_trade=PER_TRADE):
    """$ we could actually deploy in one decision on one token: min($200, depth)."""
    return min(per_trade, max(0.0, depth_usd))


def day_capacity(depth_list, decisions_per_day=1.0, per_trade=PER_TRADE, cap=DAY_CAP):
    """$ deployed per day = min(cap, decisions_per_day * sum over distinct tokens of min($200, depth)). depth_list = $ depths of
    DISTINCT tokens that are decision candidates at the same decision time."""
    one = sum(per_decision_usd(d, per_trade) for d in depth_list)
    return min(cap, one * decisions_per_day)


def pct_of_200(usd_per_day):
    return 100.0 * usd_per_day / 200.0


def notional(trades, t0=None, t1=None):
    """sum price*size of rows (dicts with price,size,timestamp); optional [t0,t1) window in unix seconds."""
    tot = 0.0
    for r in trades:
        ts = r.get("timestamp")
        if t0 is not None and ts < t0:
            continue
        if t1 is not None and ts >= t1:
            continue
        tot += float(r["price"]) * float(r["size"])
    return tot


def perp_depth_usd(levels_px_sz, mid, bps=5.0, side="ask"):
    """$ notional resting within `bps` basis points of mid on one side of a perp book. levels_px_sz = [(px, sz)] in any order.
    side 'ask': px in [mid, mid*(1+bps/1e4)] ; side 'bid': px in [mid*(1-bps/1e4), mid]. Notional = px*sz (sz in base units)."""
    if not mid or mid <= 0:
        return 0.0
    lo, hi = (mid, mid * (1 + bps / 1e4)) if side == "ask" else (mid * (1 - bps / 1e4), mid)
    return sum(px * sz for px, sz in levels_px_sz if lo - 1e-12 <= px <= hi + 1e-12)
