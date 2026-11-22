#!/usr/bin/env python3
"""Pure functions for the weekly-touch vs perp-gap test (LOCKED-RULE-touch-gap-2026-11-22.md). No network here."""
import datetime, json, random, math
from zoneinfo import ZoneInfo
from pscanlib import gap_beyond, parse_strike, PER_TRADE, DAY_CAP, PROB_LO, PROB_HI

NY = ZoneInfo("America/New_York")
FEE_RATE = 0.04
WIN_SEC = 3600


def decision_ts(kind, monday):
    """T (unix s). STOCK/INDEX: Monday 09:20 NY. METALS/OIL: Sunday 17:50 NY (10 min before the 18:00 reopen)."""
    if kind in ("METALS", "OIL"):
        d = monday - datetime.timedelta(days=1)
        return datetime.datetime(d.year, d.month, d.day, 17, 50, tzinfo=NY).timestamp()
    return datetime.datetime(monday.year, monday.month, monday.day, 9, 20, tzinfo=NY).timestamp()


def perp_at(candles, T):
    """close of the last 1m candle whose CLOSE time (ms, first element) is <= T; None if none. Never a later candle (no look-ahead)."""
    best = None
    for tc, c in candles or []:
        if tc <= T * 1000 and (best is None or tc > best[0]):
            best = (tc, c)
    return best[1] if best else None


def last_close(closes, before_date):
    """last daily close strictly before before_date (datetime.date); closes = {'YYYY-MM-DD': float}"""
    if not closes:
        return None
    ds = [d for d in closes if d < before_date.isoformat()]
    return closes[max(ds)] if ds else None


def yes_wins(prices, outcomes):
    """True/False when resolved (YES price >= 0.99 / <= 0.01), None if unresolved or unreadable. Uses the 'Yes' outcome by LABEL, not position."""
    try:
        p = json.loads(prices) if isinstance(prices, str) else prices
        o = json.loads(outcomes) if isinstance(outcomes, str) else outcomes
        i = [x.lower() for x in o].index("yes")
        v = float(p[i])
    except Exception:
        return None
    return True if v >= 0.99 else (False if v <= 0.01 else None)


def entry(prints, yes_token, T, win=WIN_SEC, cap=PER_TRADE):
    """FLOOR entry from the YES token's own taker BUY prints in [T-win, T), price in (0.05, 0.95), each print capped at $cap.
    -> dict(price=size-weighted avg, usd=capped $ total, n=prints) ; or ('NOPRINT'|'DEAD', counts) when nothing usable."""
    use, dead, seen = [], 0, 0
    for r in prints:
        if r["tok"] != yes_token or r["side"] != "BUY" or not (T - win <= r["t"] < T):
            continue
        seen += 1
        p, s = float(r["p"]), float(r["s"])
        if not (PROB_LO < p < PROB_HI):
            dead += 1
            continue
        s = min(s, cap / p)
        use.append((p, s))
    if not use:
        return None, ("DEAD" if dead else "NOPRINT")
    sh = sum(s for _, s in use)
    return dict(price=sum(p * s for p, s in use) / sh, usd=sum(p * s for p, s in use), n=len(use)), "OK"


def fee(p, rate=FEE_RATE):
    return rate * p * (1 - p)


def gap(win, price, rate=FEE_RATE):
    return (1.0 if win else 0.0) - price - fee(price, rate)


def select(week_strikes, perp, close, margin):
    """week_strikes: [dict(kind, strike, price, usd, win, rate)] -> those that are candidates under (perp, close, margin)."""
    return [s for s in week_strikes if gap_beyond(perp, close, s["kind"], s["strike"], margin)]


def stat(weeks):
    """weeks: {week_id: [strike dicts selected]} -> dict(n, weeks, mean_gap ($-weighted), win, price). None if empty."""
    rows = [s for v in weeks.values() for s in v]
    if not rows:
        return None
    w = sum(s["usd"] for s in rows)
    mg = sum(s["usd"] * gap(s["win"], s["price"], s.get("rate", FEE_RATE)) for s in rows) / w
    return dict(n=len(rows), weeks=sum(1 for v in weeks.values() if v), mean_gap=mg, win=sum(s["win"] for s in rows) / len(rows), price=sum(s["price"] for s in rows) / len(rows), usd=w)


def boot_weeks(weeks, n=10000, seed=1):
    """bootstrap CI (2.5, 97.5) of the $-weighted mean gap, resampling WEEKS (cluster); weeks with no selection are skipped."""
    ids = [k for k, v in weeks.items() if v]
    if not ids:
        return None
    rnd = random.Random(seed)
    num = {k: sum(s["usd"] * gap(s["win"], s["price"], s.get("rate", FEE_RATE)) for s in weeks[k]) for k in ids}
    den = {k: sum(s["usd"] for s in weeks[k]) for k in ids}
    out = []
    for _ in range(n):
        pick = [ids[rnd.randrange(len(ids))] for _ in ids]
        d = sum(den[k] for k in pick)
        out.append(sum(num[k] for k in pick) / d)
    out.sort()
    return out[int(0.025 * n)], out[int(0.975 * n) - 1]


def permutation_p(by_tk, observed, n=200, seed=1):
    """by_tk: {tk: [(week_id, perp, close, margin, [all strikes with an entry that week])]}. Shuffle the (perp, close) pair across weeks within each
    ticker, rebuild candidates from the REAL week strikes, recompute the $-weighted mean gap. p = share of permutations >= observed."""
    rnd = random.Random(seed)
    ge = 0; used = 0
    for _ in range(n):
        weeks = {}
        for tk, lst in by_tk.items():
            pc = [(p, c) for (_, p, c, _, _) in lst]
            rnd.shuffle(pc)
            for (wid, _, _, m, strikes), (p, c) in zip(lst, pc):
                weeks[(tk, wid)] = select(strikes, p, c, m)
        st = stat(weeks)
        if st is None:
            continue
        used += 1
        ge += st["mean_gap"] >= observed - 1e-12
    return (ge / used) if used else None


def per_day_floor(weeks_sel, n_mondays, per_trade=PER_TRADE, cap=DAY_CAP):
    """FLOOR $/day: $-weighted expected gap summed over all selected strikes in a Monday (each strike's $ already capped per print),
    deployed $ per Monday capped at $2,000 (scaled pro rata), averaged over the number of Mondays in the sample."""
    by_mon = {}
    for (tk, wid), v in weeks_sel.items():
        by_mon.setdefault(wid, []).extend(v)
    tot = 0.0
    for wid, rows in by_mon.items():
        dep = sum(s["usd"] for s in rows)
        pnl = sum(s["usd"] * gap(s["win"], s["price"], s.get("rate", FEE_RATE)) for s in rows)
        tot += pnl * (min(1.0, cap / dep) if dep > 0 else 0.0)
    return tot / n_mondays if n_mondays else 0.0
