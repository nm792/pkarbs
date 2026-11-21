#!/usr/bin/env python3
"""Scoring layer for the gas paper run under reviewer/MODELLING-PRINCIPLES.md (R-004, APPLY-2026-11-21-principles-to-gas-paper.md).
Inputs: decisions from paper_post.run (no hindsight: the page read at the decision, never the settlement), the logged books, Gamma resolutions.
 markouts()      score each decision against the token's OWN best bid at +1 min, +5 min, +30 min and 10:00 ET (item 2); None when no book is within max_gap_s.
 capacity_row()  fillable own-token ask depth at a decision price that passes the rule, at the decision moment, and the $ edge at that depth (item 6).
 cs_bounds()     always-valid (time-uniform) confidence interval for mean daily P&L: two-sided normal-mixture boundary (Robbins; Howard et al. 2021), registered sigma (item 5).
 cell_status()   success / futility / inconclusive-ranked per cell; also whether the interval can reach $200/day (A9).
 shrink()        empirical-Bayes shrinkage across cells (item 3).
 power_days()    days needed to detect a daily edge at one-sided 5% and 80% power (item 4).
No orders are ever sent (A6/A7)."""
import json, math, os, sys, statistics
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
H = (("+1min", 60), ("+5min", 300), ("+30min", 1800))
def best_bid(tokrec): return max((p for p, s in tokrec.get("bids") or []), default=None)
def snap_at(books, t_ns, max_gap_s):
    """last snapshot at or before t_ns, if it is no older than max_gap_s; books sorted by recv_ns."""
    best = None
    for b in books:
        if b["recv_ns"] <= t_ns: best = b
        else: break
    return best if best is not None and (t_ns - best["recv_ns"]) / 1e9 <= max_gap_s else None
def markouts(decisions, books, end_ns=None, max_gap_s=30.0):
    """Adds mark[label] = (bid, pnl_net_of_entry_fee) per horizon; pnl = shares*(bid-price) - entry fee; missing book -> None; no bid -> bid 0.0 (nothing realisable)."""
    out = []
    pts = list(H) + ([("10:00ET", None)] if end_ns else [])
    for d in decisions:
        m = {}
        for lab, h in pts:
            t = end_ns if h is None else d["recv_ns"] + int(h * 1e9)
            sn = snap_at(books, t, max_gap_s)
            if sn is None or d["token"] not in sn["tok"]: m[lab] = None; continue
            bid = best_bid(sn["tok"][d["token"]]); bid = 0.0 if bid is None else bid
            m[lab] = (bid, d["shares"] * (bid - d["price"]) - d["fee"])
        out.append(dict(d, mark=m))
    return out
def markout_summary(rows):
    res = {}
    for lab in [l for l, _ in H] + ["10:00ET"]:
        v = [r["mark"][lab][1] for r in rows if lab in r["mark"] and r["mark"][lab] is not None]
        cost = sum(r["cost"] for r in rows if lab in r["mark"] and r["mark"][lab] is not None)
        res[lab] = dict(n=len(v), missing=sum(1 for r in rows if lab not in r["mark"] or r["mark"][lab] is None), pnl=sum(v), per_usd=(sum(v) / cost if cost else None))
    return res
def capacity_row(snapshot, tok_side, prm, kind="post"):
    """snapshot: the book at the decision moment; tok_side: {token_id: True if the rule wants that token}. Counts own-token ask depth at prices that PASS the rule."""
    import rule as R
    q = prm.post_q; sh = 0.0; usd = 0.0; edge = 0.0
    for tid, want in tok_side.items():
        if not want or tid not in snapshot["tok"]: continue
        for p, s in snapshot["tok"][tid]["asks"]:
            if R.eligible(kind, q, p, prm):
                sh += s; usd += s * p; edge += s * (q - p - R.fee_per_share(p, prm.fee_rate))
    return dict(eligible_shares=sh, eligible_usd=usd, edge_usd_at_depth=edge)
def cs_bounds(xs, sigma, alpha=0.05, n_star=45):
    """Two-sided always-valid interval for the mean of xs (one value per EVENT DAY), sub-Gaussian with registered sigma.
    half-width = sqrt( 2 s^2 (n r2 + 1) / (n^2 r2) * ln( 2 sqrt(n r2 + 1) / alpha ) ), r2 tuned to be tightest at n_star (Howard, Ramdas, McAuliffe & Sekhon 2021, normal mixture)."""
    n = len(xs)
    if n == 0: return None
    la = math.log(2.0 / alpha); r2 = (la * 2 + math.log(la * 2 + 1)) / n_star
    hw = math.sqrt(2 * sigma ** 2 * (n * r2 + 1) / (n * n * r2) * math.log(2 * math.sqrt(n * r2 + 1) / alpha)); m = sum(xs) / n
    return m - hw, m + hw
def cell_status(xs, sigma, max_days=60, target=200.0, alpha=0.05):
    """Registered boundaries for one cell on daily net P&L (fees already in P&L, so cost = 0):
    success: lower bound > 0 | futility: upper bound < 0 | after max_days with neither: inconclusive, ranked (NOT dead)."""
    b = cs_bounds(xs, sigma, alpha)
    if b is None: return dict(days=0, status="no data", ci=None, can_reach_target=None)
    lo, hi = b; n = len(xs)
    st = "SUCCESS (lower bound > 0)" if lo > 0 else ("FUTILE (upper bound < 0)" if hi < 0 else ("inconclusive, ranked (max sample reached)" if n >= max_days else "continue"))
    return dict(days=n, mean=sum(xs) / n, ci=(lo, hi), status=st, can_reach_target=hi >= target, target=target)
def shrink(cells):
    """cells: {name: (mean, se)}. Normal-normal empirical Bayes: shrunk = m0 + tau2/(tau2+se2) (m - m0), m0 = precision-weighted mean, tau2 = max(0, var(m) - mean(se2)). With 3 cells this is crude; it is a ranking aid."""
    names = list(cells); m = [cells[k][0] for k in names]; se2 = [cells[k][1] ** 2 for k in names]
    w = [1 / s for s in se2]; m0 = sum(wi * mi for wi, mi in zip(w, m)) / sum(w)
    tau2 = max(0.0, (statistics.pvariance(m) if len(m) > 1 else 0.0) - statistics.mean(se2))
    return {k: dict(raw=cells[k][0], shrunk=m0 + (tau2 / (tau2 + s) if tau2 + s > 0 else 0) * (cells[k][0] - m0), tau2=tau2) for k, s in zip(names, se2)}
def power_days(mu, sigma, z_alpha=1.645, z_beta=0.8416):
    """days needed to detect a mean daily edge mu with per-day SD sigma at one-sided 5% and 80% power: ((z_a + z_b) sigma / mu)^2."""
    return float("inf") if mu <= 0 else ((z_alpha + z_beta) * sigma / mu) ** 2
