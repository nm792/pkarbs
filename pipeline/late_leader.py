"""R-036 item 1: deep-volume contracts whose prices resolve late. One ranked table (paper only).

Per recurring family (screened 90, last 40 resolved events each, window ends at the newest cached resolution):
  daily $ volume  = sum(price*size) over ALL trades of every market of the sampled events / calendar span (NOT gamma volumeNum, which is shares)
  resolutions/day = sampled events / span
  CAUSAL RULE (no hindsight): at t = endDate - LEAD the LEADER token = highest own last print (<= 12 h old) among the event's candidate tokens
                  (YES tokens of bracket events; both tokens of a single Up/Down market). Buy it at the earliest BUY print in [t, t+10 min]
                  and hold to resolution. Fill $ = min($200, printed BUY $ in that window at <= fill+0.02)  <- print-limited, so every number is a FLOOR.
  cap = $2,000/day of fills (ET day). Fee conservative: 0.05*p*(1-p) per share. $/day as % of $200.
  CEILING (hindsight, for scale only) = pool90_day from listing_hours (winner BUYs <= 0.90, ex post).
Own-token prices only (never 1 - other token). Leads reported: 3 h, 1 h (primary, fixed before the run), 0.5 h.
"""
import bisect, collections, datetime as dt, json, math, os, sys
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import screen
from zoneinfo import ZoneInfo
ET = ZoneInfo("America/New_York")
BET = 200.0; DAYCAP = 2000.0; FEE = 0.05; WINDOW = 600; STALE = 12 * 3600; SLACK = 0.02; PMIN = 0.05; PMAX = 0.97
LEADS = (3.0, 1.0, 0.5); PRIMARY = 1.0


def fee_ps(p): return FEE * p * (1 - p)


def candidates(markets):
    """list of (token, won) for the event's candidate tokens. markets: output of screen.binary_resolved (+'rows' attached by caller)."""
    out = []
    for b in markets:
        yn = set(x.lower() for x in b["labels"]) == {"yes", "no"}
        idx = [b["labels"].index(next(l for l in b["labels"] if l.lower() == "yes"))] if yn else [0, 1]
        for i in idx: out.append((b["tokens"][i], b["win"] == i, b["rows"]))
    return out


def decide(cands, t):
    """leader by own last print <= t (age <= STALE); returns (token, won, rows, last_px) or None"""
    best = None
    for tok, won, rows in cands:
        tr = [r for r in rows if r[2] == tok and r[0] <= t]
        if not tr: continue
        last = max(tr, key=lambda r: r[0])
        if t - last[0] > STALE: continue
        if best is None or last[3] > best[3]: best = (tok, won, rows, last[3])
    return best


def fill(rows, tok, t, until=None):
    """earliest BUY print of tok in [t, t+WINDOW]; depth = printed BUY $ in the window at <= fill + SLACK. returns (px, depth_usd, ts) or None"""
    hi = t + WINDOW if until is None else min(t + WINDOW, until)
    w = sorted((r for r in rows if r[2] == tok and r[1] == "BUY" and t <= r[0] <= hi), key=lambda r: r[0])
    if not w: return None
    p0 = w[0][3]
    dep = sum(r[3] * r[4] for r in w if r[3] <= p0 + SLACK)
    return p0, dep, w[0][0]


def event_bet(cands, t, until=None):
    d = decide(cands, t)
    if d is None: return None
    tok, won, rows, last = d
    if not (PMIN <= last <= PMAX): return dict(skip="px", last=last)
    f = fill(rows, tok, t, until)
    if f is None: return dict(skip="nofill", last=last)
    p, dep, ts = f
    if not (PMIN <= p <= PMAX): return dict(skip="px", last=last)
    bet = min(BET, dep)
    pnl = bet * ((1.0 / p if won else 0.0) - 1.0) - bet / p * fee_ps(p)
    return dict(last=last, px=p, depth=dep, bet=bet, pnl=pnl, won=bool(won), ts=ts)


def late_pool(cands, end, lo=0.70, hi=0.95, hours=3.0):
    """HINDSIGHT ceiling: the winning candidate token's BUY prints priced lo..hi in the last `hours` before end; cheapest first up to $BET; returns (bet, pnl, ts)."""
    pr = []
    for tok, won, rows in cands:
        if not won: continue
        pr += [(r[3], r[4], r[0]) for r in rows if r[2] == tok and r[1] == "BUY" and end - hours * 3600 <= r[0] <= end and lo <= r[3] <= hi]
    if not pr: return None
    pr.sort(); bet = 0.0; pnl = 0.0; ts0 = min(x[2] for x in pr)
    for p, s, t in pr:
        take = min(p * s, BET - bet)
        if take <= 0: break
        pnl += take * (1.0 / p - 1.0) - take / p * fee_ps(p); bet += take
    return dict(bet=bet, pnl=pnl, ts=ts0)


def apply_cap(bets):
    """bets: list of dict with ts, bet, pnl. Daily notional cap by ET date, chronological. returns kept list (bet scaled to what is left)."""
    used = collections.defaultdict(float); out = []
    for b in sorted(bets, key=lambda b: b["ts"]):
        d = dt.datetime.fromtimestamp(b["ts"], ET).date(); room = DAYCAP - used[d]
        if room <= 0: continue
        k = min(1.0, room / b["bet"]) if b["bet"] > 0 else 0.0
        used[d] += b["bet"] * k; out.append(dict(b, bet=b["bet"] * k, pnl=b["pnl"] * k))
    return out


def boot_lo(per_event_pnl, span_days, n=2000, seed=7):
    """cluster (event) bootstrap lower 2.5% of PnL/day; events without a bet count as 0"""
    rng = np.random.default_rng(seed); x = np.array(per_event_pnl, float)
    if len(x) < 5: return float("nan")
    s = rng.choice(x, size=(n, len(x)), replace=True).sum(1) / span_days
    return float(np.quantile(s, 0.025))


def lead_set(fam):
    """decision leads (hours before endDate) scaled to the contract's life: 15-minute and hourly contracts cannot use 3 h / 1 h leads."""
    if fam.endswith("-15m"): return (10 / 60, 5 / 60, 2 / 60), 0.25, "10m/5m/2m"
    if fam.endswith("-1h"): return (30 / 60, 15 / 60, 5 / 60), 1.0, "30m/15m/5m"
    return LEADS, 3.0, "3h/1h/30m"


def family_rows(fam, events, tapes_by_cond):
    """events: sorted list of gamma events. returns dict per lead + volume stats."""
    ends = [screen.parse_ts(e["endDate"]) for e in events]
    n = len(events); span = max((max(ends) - min(ends)) / 86400 * n / (n - 1), 1.0) if n > 1 else 1.0   # n events cover n periods
    vol = 0.0; kept_events = []
    for e in events:
        ms = []
        for m in e["markets"]:
            b = screen.binary_resolved(m)
            if not b: continue
            tp = tapes_by_cond.get(b["cond"])
            if tp is None: continue
            b["rows"] = tp; ms.append(b); vol += sum(r[3] * r[4] for r in tp)
        if ms: kept_events.append((e, candidates(ms)))
    out = dict(fam=fam, n_ev=len(events), n_used=len(kept_events), span_d=span, ev_day=len(events) / span, vol_day=vol / span)
    leads, pool_h, lname = lead_set(fam); out["lead_set"] = lname
    for L, key in zip(leads, ("L3", "L1", "L0.5")):
        bets = []; per_event = []; skips = collections.Counter()
        for e, c in kept_events:
            en = screen.parse_ts(e["endDate"]); t = en - L * 3600; r = event_bet(c, t, en)
            if r is None: skips["nodecision"] += 1; per_event.append(0.0); continue
            if "skip" in r: skips[r["skip"]] += 1; per_event.append(0.0); continue
            bets.append(r)
        kept = apply_cap(bets); pk = {id(b): 0 for b in kept}
        pnl = sum(b["pnl"] for b in kept); notional = sum(b["bet"] for b in kept)
        # per-event vector for the bootstrap (apply_cap preserves order by ts, so rebuild by matching ts)
        pe = [b["pnl"] for b in kept] + [0.0] * (len(kept_events) - len(kept))
        k = key
        out.update({f"{k}_bets": len(kept), f"{k}_nofill": skips["nofill"], f"{k}_nodec": skips["nodecision"] + skips["px"],
                    f"{k}_px": float(np.mean([b["px"] for b in kept])) if kept else np.nan,
                    f"{k}_lead_px": float(np.mean([b["last"] for b in kept])) if kept else np.nan,
                    f"{k}_win": float(np.mean([b["won"] for b in kept])) if kept else np.nan,
                    f"{k}_depth": float(np.mean([b["depth"] for b in kept])) if kept else np.nan,
                    f"{k}_bet": float(np.mean([b["bet"] for b in kept])) if kept else np.nan,
                    f"{k}_pnl_day": pnl / span, f"{k}_pct200": pnl / span / BET * 100, f"{k}_lo_day": boot_lo(pe, span),
                    f"{k}_roi": pnl / notional if notional else np.nan})
    hp = []
    for e, c in kept_events:
        r = late_pool(c, screen.parse_ts(e["endDate"]), hours=pool_h)
        if r: hp.append(r)
    hk = apply_cap(hp); out.update(hs_events=len(hk), hs_pnl_day=sum(b["pnl"] for b in hk) / span, hs_pct200=sum(b["pnl"] for b in hk) / span / BET * 100)
    return out


def main(outdir="out/listing1"):
    import late_pull, gzip
    tg = late_pull.targets(); base = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), outdir, "listing_hours_series2.csv")).set_index("fam")
    rows = []
    for k, es in sorted(tg.items()):
        tapes = {}
        for e in es:
            for m in e["markets"]:
                c = m["conditionId"]
                try: tapes[c] = [tuple(r) for r in screen.get_trades(c)["rows"]]
                except Exception: pass
        r = family_rows(k, es, tapes); name = k.replace("series:", "")
        if name in base.index:
            b = base.loc[name]; r.update(rec=b["rec"], win_usd_day=b["win_usd_day"], ceiling_pool90_day=b["pool90_day"], px_1h=b["px_1h"], px_3h=b["px_3h"], px_24h=b["px_24h"], cross_h=b["cross_h"], lead_h=b["lead_h"], clock=b["clock"])
        rows.append(r); print(name, r["n_used"], round(r["vol_day"]), round(r["L1_pnl_day"], 2), flush=True)
    df = pd.DataFrame(rows); df.to_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), outdir, "late_leader_families.csv"), index=False)


if __name__ == "__main__": main()
