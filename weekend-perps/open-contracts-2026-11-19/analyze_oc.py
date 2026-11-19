"""Open-contract test per LOCKED-RULE-open-contracts-2026-11-19.md. usage: analyze_oc.py RUNDIR [--books DIR_WITH_ocbooks]  -> prints and writes RUNDIR/result.json"""
import sys, json, math, collections, glob, gzip, numpy as np
from oclib import *
R = sys.argv[1]
mk = json.load(open(R + "/markets.json")); perp = json.load(open(R + "/perp.json")); yh = json.load(open(R + "/yahoo.json")); trd = json.load(open(R + "/trades.json"))
drop = collections.Counter(); rows = []
for m in mk["markets"]:
    if m["up_price"] not in (0.0, 1.0): drop["resolution_not_0_1 (50-50 or open)"] += 1; continue
    sym = "^GSPC" if m["prod"] == "SPX" else "SPY"; bars = yh[sym]["bars"]; spx = yh["^GSPC"]["bars"]; dts = sorted(bars)
    if m["date"] not in bars or bars[m["date"]]["o"] is None: drop["no_yahoo_open"] += 1; continue
    prev = [d for d in dts if d < m["date"]]; sprev = [d for d in sorted(spx) if d < m["date"]]
    if not prev or not sprev or bars[prev[-1]]["c"] is None: drop["no_prior_close"] += 1; continue
    o = bars[m["date"]]["o"] + yh[sym]["divs"].get(m["date"], 0.0)   # ex-dividend add-back (SPY)
    c = bars[prev[-1]]["c"]; cs = spx[sprev[-1]]["c"]; y = math.log(o / c)
    x = {}
    for k in KS:
        p = perp.get(f"{m['date']}|{k}")
        if p: x[k] = math.log(p["mark"] / cs)
    rows.append(dict(date=m["date"], prod=m["prod"], slug=m["slug"], x=x, y=y, up=bool(m["up_price"] == 1.0), yahoo_up=bool(o > c), up_token=m["up_token"], dn_token=m["dn_token"], T=open_ts(m["date"]), x30=x.get(30)))
agree = np.mean([r["up"] == r["yahoo_up"] for r in rows]); print("rows", len(rows), "dropped", dict(drop), "| Polymarket resolution vs Yahoo open>close agreement", round(float(agree), 4))
bad = [(r["slug"], r["up"], r["yahoo_up"]) for r in rows if r["up"] != r["yahoo_up"]]; print("disagreements:", bad[:10])
dates = sorted({r["date"] for r in rows}); cut = dates[len(dates) // 2]; train = [r for r in rows if r["date"] < cut]; test = [r for r in rows if r["date"] >= cut]
print("train dates", dates[0], "..", [d for d in dates if d < cut][-1], "n", len(train), "| test dates", cut, "..", dates[-1], "n", len(test))
sub = [r for r in train if r["x"].get(PRIMARY_K) is not None]
S = {}
for prod in ("SPX", "SPY"):
    rr = [r for r in sub if r["prod"] == prod and True]; S[prod] = fit_s([dict(x=r["x"][PRIMARY_K], y=r["y"]) for r in rr])
print("train residual sd s (k=30):", S, "| mean x vs y corr (train, k=30):", round(float(np.corrcoef([r["x"][PRIMARY_K] for r in sub], [r["y"] for r in sub])[0, 1]), 3), "sign agreement x vs y:", round(float(np.mean([np.sign(r["x"][PRIMARY_K]) == np.sign(r["y"]) for r in sub])), 3))
# own-token books recorded? (BOOK level)
nb = 0
if "--books" in sys.argv:
    bd = sys.argv[sys.argv.index("--books") + 1]; nb = len(glob.glob(bd + "/ocbooks_*.jsonl.gz"))
print("BOOK level: recorded own-token book files:", nb, "-> rows with a recorded book on history: 0; verdict at this level: unknown, N too small")
def ask_fn_factory(k):
    def f(r, kk):
        t0 = r["T"] - kk * 60; tr = trd[r["slug"]]
        u = window_ask(tr, r["up_token"], t0); d = window_ask(tr, r["dn_token"], t0); return dict(up=u, dn=d)
    return f
res = {}
for label, rs in (("TEST (verdict)", test), ("train", train), ("all", rows)):
    for k in KS:
        for thr in (0.03, 0.01, 0.05):
            if label != "TEST (verdict)" and (thr != 0.03): continue
            if label == "TEST (verdict)" or k == PRIMARY_K or True:
                tr, ex = evaluate(rs, S, k, ask_fn_factory(k), thr)
                n = len(tr); key = f"{label}|k={k}|thr={thr}"
                if n == 0: res[key] = dict(n=0, excl=dict(ex)); print(key, "n=0", dict(ex)); continue
                byd = collections.defaultdict(list)
                for t in tr: byd[t["date"]].append(t["pnl"])
                lo, hi = boot_mean(byd); ndays = len({r["date"] for r in rs})
                usd = collections.defaultdict(float); cap = collections.defaultdict(float)
                for t in tr: usd[t["date"]] += SLICE * t["shares"] * t["pnl"]; cap[t["date"]] += SLICE * t["shares"] * t["ask"]
                m_d, lo_d, hi_d = boot_perday(usd, ndays)
                trf, _ = evaluate(rs, S, k, ask_fn_factory(k), thr, flip=True); pm = float(np.mean([t["pnl"] for t in trf])) if trf else None
                res[key] = dict(n=n, dates=len(byd), hit=float(np.mean([t["win"] for t in tr])), mean_ask=float(np.mean([t["ask"] for t in tr])), mean_edge=float(np.mean([t["edge"] for t in tr])),
                                pnl=float(np.mean([t["pnl"] for t in tr])), ci=(lo, hi), depth_sh=float(np.median([t["shares"] for t in tr])), depth_usd=float(np.median([t["shares"] * t["ask"] for t in tr])),
                                usd_day=m_d, usd_day_ci=(lo_d, hi_d), capital_day=float(sum(cap.values()) / ndays), placebo_flip_pnl=pm, placebo_n=len(trf), excl=dict(ex), test_days=ndays)
                r_ = res[key]; print(f"{key:34s} n={n:4d} dates={r_['dates']:3d} hit={r_['hit']:.2f} ask={r_['mean_ask']:.2f} edge={r_['mean_edge']:+.3f} pnl/sh={r_['pnl']:+.3f} CI=({lo:+.3f},{hi:+.3f}) depth {r_['depth_sh']:.0f}sh ${r_['depth_usd']:.0f} | $/day@10% {m_d:+.2f} CI({lo_d:+.2f},{hi_d:+.2f}) cap/day ${r_['capital_day']:.1f} | flip pnl {pm if pm is None else round(pm,3)} (n {len(trf)}) | excl {dict(ex)}")
# plausibility: rows with perp point, with fills in the window, own-token volume
for k in KS:
    npp = sum(1 for r in rows if r["x"].get(k) is not None); nfill = sum(1 for r in rows if ask_fn_factory(k)(r, k)["up"] or ask_fn_factory(k)(r, k)["dn"])
    print(f"plausibility k={k}: rows with perp point {npp}/{len(rows)}, rows with an own-token BUY fill in the 120 s window (either side) {nfill}/{len(rows)}")
vol60 = []; volwin = []
for r in rows:
    tr = trd[r["slug"]]; vol60.append(sum(t["price"] * t["size"] for t in tr if r["T"] - 3600 <= t["timestamp"] <= r["T"])); 
print("USD traded (all sides, own tokens, last 60 min before the open) per event: median", round(float(np.median(vol60)), 1), "mean", round(float(np.mean(vol60)), 1), "total events", len(vol60), "| whole-life market volume (gamma) median", round(float(np.median([m["volume"] or 0 for m in mk["markets"]])), 0))
# size ceiling: 100% of the chosen side's BUY volume in the last 60 min x model edge, per test day
ceil = collections.defaultdict(float)
tr30, _ = evaluate(test, S, PRIMARY_K, ask_fn_factory(PRIMARY_K), THR)
rowidx = {(r["date"], r["prod"]): r for r in test}
for t in tr30:
    r = rowidx[(t["date"], t["prod"])]; tok = r["up_token"] if t["side"] == "Up" else r["dn_token"]
    sh = sum(x["size"] for x in trd[r["slug"]] if x["token_id"] == tok and x["side"] == "BUY" and r["T"] - 3600 <= x["timestamp"] <= r["T"]); ceil[t["date"]] += sh * t["edge"]
nd = len({r["date"] for r in test}); print("CEILING (test, k=30, thr 0.03): 100% of the chosen side's BUY volume in the last 60 min x model edge per share =", round(sum(ceil.values()) / nd, 2), "USD per test day (", nd, "days)")
res["_meta"] = dict(S=S, agree=float(agree), train_end=[d for d in dates if d < cut][-1], test_start=cut, rows=len(rows), dropped=dict(drop), ceiling_usd_day=sum(ceil.values()) / nd)
json.dump(res, open(R + "/result.json", "w"), indent=1, default=float)
