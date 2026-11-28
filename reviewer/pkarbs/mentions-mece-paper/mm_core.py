"""Pure decision logic for the mentions + MECE PAPER node (no Nautilus import). Rules are the FROZEN ones already registered:
MENTIONS (it/mentions_pm_ws_paper.py header, P121/P147): fair YES = per-word causal base rate q at listing (mentions_pm_daily_scorer.q_for), NO fair = 1-q.
  A token is underpriced when its OWN best ask <= fair - 0.10 and >= 0.05. At each decision time (listing+0..60 min every 5 min, T-24h, T-6h, T-1h, T-15m,
  every 5 min over [T-6h, T]; a decision later than 90 s is MISSED) take the own asks at or below the limit (fair - 0.10) for up to $200 per (decision, token).
  $2,000 per UTC day cap across all events. Variant 'during A take' is the one P147's evidence tool scored +$2,345 on 40 decisions (not Nautilus).
MECE (STRATEGY.md row 4): neg-risk event with >= 3 legs; buy every leg's NO at its OWN best ask when sum(NO asks) + fees < legs - 1.
  Equal shares on every leg = min top-of-book size across legs, total cost <= $200; one fire per set per 60 s.
Fills, fees and P&L come from Nautilus (PolymarketFeeModel, 250 ms insert latency), never from here."""
import math

CAP = 200.0
DAYCAP = 2000.0
EDGE = 0.10
FLOOR = 0.05
LATE_S = 90
MECE_CAP = 200.0
MECE_COOLDOWN_S = 60


def slots(t0, T):
    """Identical to it/mentions_pm_ws_paper.slots (frozen decision times)."""
    out = [('listing', t0 + 300 * i) for i in range(13)] + [('T-24h', T - 86400), ('T-6h', T - 6 * 3600), ('T-1h', T - 3600), ('T-15m', T - 900)] + \
          [('during', T - 6 * 3600 + 300 * i) for i in range(72)]
    return [(v, t) for v, t in out if t >= t0]


def due(slot_list, now, done):
    """-> (to_decide, missed): slots whose time has passed and are not done; later than LATE_S = missed."""
    go, miss = [], []
    for s in slot_list:
        if s in done or s[1] > now:
            continue
        (go if now - s[1] <= LATE_S else miss).append(s)
    return go, miss


def mention_order(fair, best_ask, cap=CAP):
    """-> (limit, shares) or None. Marketable IOC limit at fair-EDGE walks every own ask at or below it; shares sized so cost <= cap at the limit."""
    if best_ask is None:
        return None
    limit = round(fair - EDGE, 3)
    if best_ask < FLOOR or best_ask > limit or limit < FLOOR:
        return None
    sh = math.floor(cap / limit)
    return (limit, sh) if sh >= 5 else None


def mece_fire(legs, cap=MECE_CAP):
    """legs: [(no_ask, no_ask_size, fee_rate)] for every leg of ONE set. -> (shares, cost_per_set, edge_per_set) or None.
    Profitable when sum(ask + fee) < n - 1 (exactly n-1 NO tokens pay 1). Fee per share = rate * p * (1 - p)."""
    n = len(legs)
    if n < 3 or any(a is None or s is None or s <= 0 for a, s, _ in legs):
        return None
    cost = sum(a + r * a * (1 - a) for a, _, r in legs)
    edge = (n - 1) - cost
    if edge <= 1e-9:
        return None
    sh = math.floor(min(min(s for _, s, _ in legs), cap / sum(a for a, _, _ in legs)))
    return (sh, cost, edge) if sh >= 5 else None
