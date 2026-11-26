"""Metric-release stale-ask pickoff: pure decision logic (no Nautilus import, no I/O). 26 Nov 2026.
Design (Nick 04:45Z and 04:46Z):
  * Before the release EVERY token of EVERY market of the event (YES and NO) has a held, unposted order, re-sized from its live own-book ask.
  * On the number, a lookup table decides EVERY market: YES token if the outcome is now true, NO token if it is now false (ladder/threshold/bracket alike),
    and ALL the resulting orders go out in one batch (chunks of <= 15, the documented max for POST /orders).
  * Order = marketable limit BUY, limit MAXP (0.95), IOC, shares = USD_PER_TRADE / own best ask. Fires only if that token's OWN ask < MAXP.
  * Caps: $200 per trade, $2,000 per UTC day (intended stake; the strategy also reconciles to fills).
Fills, fees and P&L are NOT computed here: Nautilus does that.
"""
import re, math

USD_PER_TRADE = 200.0
USD_PER_DAY = 2000.0
MAXP = 0.95
BATCH_MAX = 15
EPS = 1e-9

_NUM = r"(-?\$?\d[\d,]*\.?\d*)\s*(k|m|bn|b|%|bps)?"


def _num(s, unit=None):
    s = s.replace("$", "").replace(",", "")
    v = float(s)
    mult = {"k": 1e3, "m": 1e6, "b": 1e9, "bn": 1e9}.get((unit or "").lower(), 1.0)
    return v * mult


def parse_predicate(question):
    """Question text -> predicate dict, or None (unparseable: the market is NOT traded). Kinds: eq, ge, gt, le, lt, between (inclusive edges flagged ambiguous).
    Wording strictness: 'above/over/more than/greater than/>' strict; 'at least/or more/or higher/>=' inclusive; 'below/under/less than/<' strict; 'or less/at most/or lower' inclusive."""
    q = (question or "").strip().lower().replace("’", "'").replace("–", "-").replace("—", "-")
    if not q:
        return None
    # Fed / central bank decision ladders in bps. value for these markets is the policy change in bps (cut = negative)
    m = re.search(r"(\d+)\s*(?:or more|\+)\s*bps\s*(decrease|cut|increase|hike)|>\s*(\d+)\s*bps\s*(decrease|cut|increase|hike)", q)
    if m:
        n = float(m.group(1) or m.group(3)); d = m.group(2) or m.group(4); sign = -1 if d in ("decrease", "cut") else 1
        return {"kind": "ge" if sign > 0 and m.group(1) else ("le" if m.group(1) else ("gt" if sign > 0 else "lt")), "x": sign * n}
    m = re.search(r"(\d+)\s*-\s*(\d+)\s*bps\s*(decrease|cut|increase|hike)", q)
    if m:
        a, b = float(m.group(1)), float(m.group(2)); sign = -1 if m.group(3) in ("decrease", "cut") else 1
        lo, hi = sorted((sign * a, sign * b)); return {"kind": "between", "lo": lo, "hi": hi}
    m = re.search(r"(decrease|decreases|cut|cuts|increase|increases|hike|hikes)[a-z ]*? by (\d+)\s*bps", q)
    if m:
        sign = -1 if m.group(1).startswith(("decrease", "cut")) else 1; return {"kind": "eq", "x": sign * float(m.group(2))}
    m = re.search(r"(?:^|\W)(?:no change|unchanged)", q)
    if m and "bps" not in q.replace("no change", ""):
        return {"kind": "eq", "x": 0.0}
    # numeric forms
    m = re.search(r"between\s*" + _NUM + r"\s*(?:and|-|to)\s*" + _NUM, q)
    if m:
        u1, u2 = m.group(2), m.group(4) or m.group(2)
        a = _num(m.group(1), u1 or u2); b = _num(m.group(3), u2)
        return {"kind": "between", "lo": min(a, b), "hi": max(a, b)}
    m = re.search(r"\$(\d[\d,]*\.?\d*)\s*-\s*\$(\d[\d,]*\.?\d*)", q)      # price brackets "$105-$110" (stock/commodity weekly closes)
    if m:
        a = _num(m.group(1)); b = _num(m.group(2)); return {"kind": "between", "lo": min(a, b), "hi": max(a, b)}
    m = re.search(r"(\d[\d,]*\.?\d*)\s*-\s*(\d[\d,]*\.?\d*)\s*(k|m)?\s+jobs", q) or re.search(r"(\d[\d,]*\.?\d*)\s*-\s*(\d[\d,]*\.?\d*)\s*(k|m)\b", q)
    if m:
        u = m.group(3); a = _num(m.group(1), u); b = _num(m.group(2), u)
        return {"kind": "between", "lo": min(a, b), "hi": max(a, b)}
    m = re.search(_NUM + r"\s*(or more|or higher|or above|\+)", q) or re.search(r"(?:at least|>=|greater than or equal to|no less than)\s*" + _NUM, q)
    if m:
        g = m.groups(); x = _num(g[0], g[1]); return {"kind": "ge", "x": x}
    m = re.search(_NUM + r"\s*(or less|or lower|or below)", q) or re.search(r"(?:at most|<=|less than or equal to|no more than)\s*" + _NUM, q)
    if m:
        g = m.groups(); x = _num(g[0], g[1]); return {"kind": "le", "x": x}
    m = re.search(r"(?:more than|ore than|above|over|greater than|higher than|>)\s*" + _NUM, q)
    if m:
        return {"kind": "gt", "x": _num(m.group(1), m.group(2))}
    m = re.search(r"(?:less than|below|under|lower than|<)\s*" + _NUM, q)
    if m:
        return {"kind": "lt", "x": _num(m.group(1), m.group(2))}
    m = re.search(r"\bbe\s*" + _NUM + r"\s*(?:in\b|for\b|\?|$)", q)
    if m:
        return {"kind": "eq", "x": _num(m.group(1), m.group(2))}
    return None


def evaluate(pred, value):
    """True/False = outcome now known; None = ambiguous (edge of an interval whose rule wording we do not know): do not trade."""
    if pred is None or value is None:
        return None
    k = pred["kind"]
    if k == "eq":
        return abs(value - pred["x"]) < 1e-6 * max(1.0, abs(pred["x"]))
    if k == "ge": return value >= pred["x"] - EPS
    if k == "le": return value <= pred["x"] + EPS
    if k == "gt": return value > pred["x"] + EPS
    if k == "lt": return value < pred["x"] - EPS
    if k == "between":
        if abs(value - pred["lo"]) < EPS or abs(value - pred["hi"]) < EPS:
            return None            # edge inclusivity differs by market rules text: refuse rather than guess
        return pred["lo"] < value < pred["hi"]
    return None


def _edges(pred):
    return [pred[k] for k in ("x", "lo", "hi") if pred and k in pred]


def truth_table(markets, value, guard_frac=0.0):
    """markets: [{cond, q, tokens:[yes,no], outcomes:['Yes','No']}] -> {cond: True|False|None}. Every market is decided from the SAME number.
    guard_frac > 0: a market whose own edge lies within guard_frac x |value| of the number is None (skipped): protects against a source value that differs slightly from the settlement value."""
    out = {}
    for m in markets:
        p = parse_predicate(m["q"])
        if guard_frac and value is not None and any(abs(value - e) <= guard_frac * abs(value) for e in _edges(p)):
            out[m["cond"]] = None
        else:
            out[m["cond"]] = evaluate(p, value)
    return out


def truth_by_name(markets, winner):
    """Winner-named markets (elections, referendums): YES on the market whose title equals `winner` exactly (case/space-insensitive), NO on every
    other market of the event. If no title matches exactly one market, every market is None (nothing traded: never guess)."""
    norm = lambda x: " ".join((x or "").lower().split())
    hits = [m for m in markets if norm(m.get("title")) == norm(winner)]
    if len(hits) != 1:
        return {m["cond"]: None for m in markets}
    return {m["cond"]: (m is hits[0]) for m in markets}


class HeldOrders:
    """Per-token held (pre-built, unposted) order state, re-priced on every book update. YES and NO of every market both exist before the release."""
    def __init__(self, markets):
        self.markets = {m["cond"]: m for m in markets}
        self.token_cond = {}
        for m in markets:
            for i, t in enumerate(m["tokens"]):
                self.token_cond[t] = (m["cond"], i)       # i 0 = YES, 1 = NO (outcome order in the market)
        self.ask = {}        # token -> (price, size) own best ask, or absent
        self.updated_ms = {}

    def reprice(self, token, best_ask, ask_size, now_ms):
        if token not in self.token_cond:
            return
        if best_ask is None:
            self.ask.pop(token, None)
        else:
            self.ask[token] = (float(best_ask), float(ask_size or 0.0))
        self.updated_ms[token] = now_ms

    def held(self):
        """what would be sent for every token right now (both sides of every market): token -> (shares, limit) or None if no own ask < MAXP."""
        out = {}
        for t in self.token_cond:
            a = self.ask.get(t)
            out[t] = None if (a is None or a[0] >= MAXP) else (math.floor(USD_PER_TRADE / a[0]), MAXP)
        return out


def fire(held, truth, day_spent=0.0, usd_trade=USD_PER_TRADE, usd_day=USD_PER_DAY, maxp=MAXP, stale_ms=None, now_ms=None):
    """The lookup. For every market with a decided outcome: YES token if true, NO token if false. Returns (orders, skipped).
    orders sorted by edge (1-ask)/ask so the daily cap drops the thinnest first; each order: dict(token, cond, side 'YES'|'NO', shares, limit, ask, stake)."""
    cands, skipped = [], []
    for cond, tv in truth.items():
        m = held.markets[cond]
        if tv is None:
            skipped.append((cond, "ambiguous or unparsed")); continue
        i = 0 if tv else 1
        tok = m["tokens"][i]
        a = held.ask.get(tok)
        if a is None:
            skipped.append((cond, "no own ask on winning token")); continue
        if stale_ms is not None and now_ms is not None and now_ms - held.updated_ms.get(tok, 0) > stale_ms:
            skipped.append((cond, "own-ask quote older than %d ms" % stale_ms)); continue
        if a[0] >= maxp:
            skipped.append((cond, "ask %.3f >= %.2f (already repriced)" % (a[0], maxp))); continue
        shares = math.floor(usd_trade / a[0])
        if shares < (m.get("min_size") or 5):
            skipped.append((cond, "below min size")); continue
        cands.append(dict(token=tok, cond=cond, side="YES" if tv else "NO", shares=shares, limit=maxp, ask=a[0], stake=shares * a[0]))
    cands.sort(key=lambda o: -(1 - o["ask"]) / o["ask"])
    orders, spent = [], day_spent
    for o in cands:
        if spent + o["stake"] > usd_day + 1e-9:
            skipped.append((o["cond"], "daily cap")); continue
        spent += o["stake"]; orders.append(o)
    return orders, skipped


def batches(orders, n=BATCH_MAX):
    return [orders[i:i + n] for i in range(0, len(orders), n)]
