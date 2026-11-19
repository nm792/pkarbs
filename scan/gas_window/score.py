#!/usr/bin/env python3
"""Score the pre-release nowcast against the Polymarket favourite at the same timestamps. See nowcast.py for the model."""
import json, sys, time, calendar, math, datetime as dt, numpy as np
sys.path.insert(0, '.')
import nowcast as n
SCORE_TIMES = (("16:00Z D-1", -1, 16), ("03:00Z D", 0, 3), ("05:00Z D", 0, 5))
def last_price(hist, t):
    p = None
    for x in hist:
        if x["t"] <= t: p = x["p"]
        else: break
    return p
def taker_buys(trades, cond, token_idx, t0, t1):
    return [(x["price"], x["size"]) for x in trades.get(cond, []) if x["side"] == "BUY" and x["outcome_index"] == token_idx and t0 <= x["timestamp"] < t1]
def run(exclude=(), train_from=dt.date(2026, 3, 26), alpha=10.0, win_s=1800, share=0.10):
    hist = json.load(open("pm_hist.json")); trades = json.load(open("pm_trades.json"))
    P = n.load_prints(); ny = n.load_spot("dgasnyh.csv"); gu = n.load_spot("dgasgulf.csv")
    res = {lab: [] for lab, _, _ in SCORE_TIMES}
    for slug, rec in sorted(hist.items(), key=lambda kv: kv[1]["end"]):
        if any(slug.endswith(x) for x in exclude): continue
        D = dt.datetime.strptime(rec["end"][:10], "%Y-%m-%d").date()
        mk = rec["mk"]; bounds = [n.bucket_bounds(m["q"]) for m in mk]
        win_i = [i for i, m in enumerate(mk) if json.loads(m["res"])[0] == "1"]
        if len(win_i) != 1 or D not in P: continue
        win_i = win_i[0]
        for lab, off, hh in SCORE_TIMES:
            day = D + dt.timedelta(days=off); t = calendar.timegm((day.year, day.month, day.day, hh, 0, 0))
            lag = 2 if off == -1 else 1
            nc = n.oos_predict(P, ny, gu, D, lag, train_from, alpha)
            if nc is None: continue
            mu, sg = nc; mean = P[D - dt.timedelta(days=1)] + mu / 100; sd = sg / 100
            probs = np.array(n.bucket_probs(mean, sd, bounds)); probs = probs / probs.sum()
            mp = np.array([last_price(m["hist"], t) if last_price(m["hist"], t) is not None else np.nan for m in mk], float)
            if np.isnan(mp).any(): continue
            mpn = mp / mp.sum()
            nc_i, mk_i = int(probs.argmax()), int(mpn.argmax())
            eps = 1e-3
            row = {"slug": slug, "nc_hit": nc_i == win_i, "mk_hit": mk_i == win_i, "nc_ll": -math.log(max(probs[win_i], eps)), "mk_ll": -math.log(max(mpn[win_i], eps)),
                   "nc_p_top": float(probs[nc_i]), "mk_p_top": float(mpn[mk_i]), "differs": nc_i != mk_i, "mu": mu, "sd": sg,
                   "actual_d": (P[D] - P[D - dt.timedelta(days=1)]) * 100}
            sh = cost = 0.0
            for (pr, sz) in taker_buys(trades, mk[nc_i]["cond"], 0, t, t + win_s): sh += sz; cost += sz * pr
            row.update(fill_shares=sh, fill_cost=cost, fill_pnl=(sh - cost) if nc_i == win_i else -cost)
            res[lab].append(row)
    return res
def boot_diff(a, b, rng, draws=5000):
    d = np.array(a, float) - np.array(b, float)
    if len(d) == 0: return (float("nan"),) * 3
    m = d[rng.integers(0, len(d), (draws, len(d)))].mean(1); return float(d.mean()), float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))
def report(res, label):
    rng = np.random.default_rng(20261119); print(f"=== {label}")
    for lab, rows in res.items():
        if not rows: print(lab, "no rows"); continue
        nh = [r["nc_hit"] for r in rows]; mh = [r["mk_hit"] for r in rows]
        dh = boot_diff(nh, mh, rng); dl = boot_diff([r["mk_ll"] for r in rows], [r["nc_ll"] for r in rows], rng)
        pnl = sum(r["fill_pnl"] for r in rows); sh = sum(r["fill_shares"] for r in rows)
        print(f"{lab} | events {len(rows)} | nowcast top-bracket hit {np.mean(nh)*100:.0f}% | market favourite hit {np.mean(mh)*100:.0f}% | hit diff {dh[0]*100:+.0f}pp (95% CI {dh[1]*100:+.0f}, {dh[2]*100:+.0f}) | log-loss gain {dl[0]:+.2f} (CI {dl[1]:+.2f}, {dl[2]:+.2f}) | brackets differ on {sum(r['differs'] for r in rows)} | "
              f"nowcast YES taker prints in next 30 min: {sh:.0f} shares, pnl at 100% ${pnl:.1f} over {len(rows)} days, 10% slice ${0.1*pnl/len(rows):.2f}/day")
if __name__ == "__main__":
    report(run(), "all 28 days"); report(run(("november-14-2026",)), "without 14 Nov")
