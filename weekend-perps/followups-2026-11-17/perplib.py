"""Shared definitions for the funding-window and follow-up tests. Every constant here is taken from
LOCKED-RULE-funding-window-divergence-2026-11-17.md or LOCKED-RULE-divergence-followups-2026-11-17.md."""
import json, datetime, collections, numpy as np
H = 3600000
NBOOT = 10000; SEED = 1; SPREAD_MULT = 3.0; SPREAD_FLOOR = 1.0
# Fee model: see LOCKED-RULE-cost-table-2026-11-17.md (source for every term). Hyperliquid base taker 4.5 bp (userFees API) x2 for HIP-3 builder dexes x0.1 when growthMode is enabled = 0.9 bp.
BASE_TAKER = 4.5; HIP3_MULT = 2.0; GROWTH_MULT = 0.1
def load(d="."):
    h = json.load(open(d + "/hist.json")); c = json.load(open(d + "/cand.json"))
    # candles: {sym: {open_time_ms: [open, close]}}
    C = {k: {int(t): v for t, v in dd.items()} for k, dd in c["candles"].items()}
    return h["oi"], h["fund"], C, c["halfspread"]
def load_growth(d="."):
    return json.load(open(d + "/growth.json"))
def series(F, s):
    """hourly records rounded to the hour: (premium bp, fundingRate bp). Record time t settles the hour ENDING at t,
    i.e. its trade candle has open time t-H."""
    rec = sorted((r[0] // H * H, r[1] * 1e4, r[2] * 1e4) for r in F[s])
    return {t: p for t, p, f in rec}, {t: f for t, p, f in rec}
def universe(oi, F):
    """Set A of the funding-window rule: >= 60 days (1440 hourly records) and OI > 0. Tier cut-offs = terciles of OI among A."""
    A = [s for s in F if len(F[s]) >= 1440 and oi.get(s, 0) > 0]
    o = sorted(oi[s] for s in A); return A, o[len(o) // 3], o[2 * len(o) // 3]
def make_tier(oi, c1, c2):
    # same cut-offs for every test; symbols with OI == 0 (not in A) fall below c1, i.e. 'thin'
    return lambda s: "thin" if oi.get(s, 0) <= c1 else ("mid" if oi[s] <= c2 else "liquid")
def is_weekend(ms):
    d = datetime.datetime.fromtimestamp(ms / 1000, datetime.timezone.utc); wd, hr = d.weekday(), d.hour
    return (wd == 4 and hr >= 22) or wd == 5 or (wd == 6 and hr < 22)
def sess(t):
    """session class of the hour covered by record t (hour starts t-H)"""
    d = datetime.datetime.fromtimestamp((t - H) / 1000, datetime.timezone.utc); wd, hr = d.weekday(), d.hour
    if (wd == 4 and hr >= 22) or wd == 5 or (wd == 6 and hr < 22): return "weekend"
    if wd < 5 and 13 <= hr < 21: return "weekday-US"
    return "weekday-other"
def cal_week(ms):
    y, w, _ = datetime.datetime.fromtimestamp(ms / 1000, datetime.timezone.utc).isocalendar(); return (y, w)
def fee_info(sym, growth):
    """(taker fee bp per side, checked?). growth = {dex: {name: 'enabled'|None}} from the live meta call.
    checked=True only for growth-mode xyz assets (0.9 bp, matches the Webb measurement from public fills). Everything else is COST UNCHECKED."""
    dex, name = sym.split(":") if ":" in sym else ("xyz", sym)
    gm = growth.get(dex, {}).get(sym) or growth.get(dex, {}).get(name)
    fee = BASE_TAKER * HIP3_MULT * (GROWTH_MULT if gm == "enabled" else 1.0)
    return fee, (dex == "xyz" and gm == "enabled")
def cost_bp(hs, fee):
    """2 x (fee + max(3 x live half-spread, 1 bp)); None if no live half-spread was measured (symbol is then excluded, never defaulted)"""
    if hs is None: return None
    return 2 * (fee + max(SPREAD_MULT * hs, SPREAD_FLOOR))
def boot(items, nboot=NBOOT, seed=SEED):
    """items: list of (cluster_key, value). Pooled mean, clusters resampled with replacement. returns (lo, hi) 95%."""
    rng = np.random.default_rng(seed); by = collections.defaultdict(list)
    for k, v in items: by[k].append(v)
    keys = list(by); sums = np.array([sum(by[k]) for k in keys]); cnt = np.array([len(by[k]) for k in keys], float)
    idx = rng.integers(0, len(keys), size=(nboot, len(keys)))
    m = sums[idx].sum(1) / cnt[idx].sum(1)
    return round(float(np.percentile(m, 2.5)), 1), round(float(np.percentile(m, 97.5)), 1)
