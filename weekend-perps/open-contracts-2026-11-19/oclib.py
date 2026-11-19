"""Pure functions for the open-contract test (LOCKED-RULE-open-contracts-2026-11-19.md). No network here."""
import math, datetime, collections
import numpy as np
from zoneinfo import ZoneInfo
NY = ZoneInfo("America/New_York"); KS = (60, 30, 10); PRIMARY_K = 30; THR = 0.03; FEE_RATE = 0.04; SLICE = 0.10; WIN = 120
def open_ts(date_iso):
    """unix seconds of 09:30 America/New_York on date_iso (daylight saving from the tz database)"""
    d = datetime.date.fromisoformat(date_iso)
    return datetime.datetime(d.year, d.month, d.day, 9, 30, tzinfo=NY).timestamp()
def fee_per_share(p): return FEE_RATE * p * (1 - p)
def Phi(z): return 0.5 * (1 + math.erf(z / math.sqrt(2)))
def p_up(x, s): return Phi(x / s)
def fit_s(rows):
    """residual sd of (y - x) over TRAINING rows only"""
    r = np.array([r["y"] - r["x"] for r in rows], float); return float(np.sqrt(np.mean(r ** 2)))
def window_ask(trades, token, t0, win=WIN):
    """FILL PROXY: size-weighted avg price of BUY-side taker trades in this token in [t0, t0+win]; returns (ask, shares) or None"""
    b = [t for t in trades if t["token_id"] == token and t["side"] == "BUY" and t0 <= t["timestamp"] <= t0 + win]
    if not b: return None
    sh = sum(t["size"] for t in b); return sum(t["price"] * t["size"] for t in b) / sh, sh
def decide(pu, ask_up, ask_dn, thr=THR):
    """one side at most: the larger edge above thr. asks are own-token asks (None = missing -> that side not available, never mirrored).
    returns (side, edge, ask) or None"""
    c = []
    if ask_up is not None: c.append(("Up", pu - ask_up - fee_per_share(ask_up), ask_up))
    if ask_dn is not None: c.append(("Down", (1 - pu) - ask_dn - fee_per_share(ask_dn), ask_dn))
    c = [x for x in c if x[1] > thr]
    return max(c, key=lambda x: x[1]) if c else None
def evaluate(rows, s_by_prod, k, ask_fn, thr=THR, flip=False):
    """rows: dicts with date, prod, x{k}, up(bool outcome). ask_fn(row,k) -> dict(up=(ask,shares)|None, dn=(ask,shares)|None).
    returns list of trades dict(date, side, ask, shares, edge, pnl)"""
    out = []; excl = collections.Counter()
    for r in rows:
        x = r["x"].get(k)
        if x is None: excl["no_perp_point"] += 1; continue
        a = ask_fn(r, k); au = a.get("up"); ad = a.get("dn")
        if au is None and ad is None: excl["no_own_token_ask"] += 1; continue
        pu = p_up((-x if flip else x), s_by_prod[r["prod"]])
        d = decide(pu, au[0] if au else None, ad[0] if ad else None, thr)
        if not d: excl["no_edge_over_threshold"] += 1; continue
        side, edge, ask = d; sh = (au if side == "Up" else ad)[1]
        win = (r["up"] if side == "Up" else not r["up"])
        out.append(dict(date=r["date"], prod=r["prod"], side=side, ask=ask, shares=sh, edge=edge, pnl=(1.0 if win else 0.0) - ask - fee_per_share(ask), win=bool(win)))
    return out, excl
def boot_mean(vals_by_date, nboot=10000, seed=1):
    """vals_by_date: {date: [values]}; cluster bootstrap of the pooled mean over dates"""
    ks = list(vals_by_date); sums = np.array([sum(vals_by_date[k]) for k in ks]); cnt = np.array([len(vals_by_date[k]) for k in ks], float)
    idx = np.random.default_rng(seed).integers(0, len(ks), size=(nboot, len(ks)))
    m = sums[idx].sum(1) / cnt[idx].sum(1); return float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))
def boot_perday(day_vals, ndays_total, nboot=10000, seed=1):
    """day_vals: {date: usd that day} for days with trades; days without trades count 0; ndays_total = all test dates. CI of mean USD/day"""
    v = np.zeros(ndays_total); v[:len(day_vals)] = list(day_vals.values())
    idx = np.random.default_rng(seed).integers(0, ndays_total, size=(nboot, ndays_total)); m = v[idx].mean(1)
    return float(v.mean()), float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))
