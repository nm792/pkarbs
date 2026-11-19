"""Amendment 2 of LOCKED-RULE-open-contracts-2026-11-19.md: stale-print test (A, verdict on TEST) and lag measurement (C). usage: analyze_stale.py RUNDIR"""
import sys, json, math, collections, numpy as np
from oclib import *
R = sys.argv[1]
src = open(__file__.replace("analyze_stale.py", "analyze_oc.py")).read().split("def ask_fn_factory")[0]
sys.argv = [sys.argv[0], R]; exec(src)
p1 = json.load(open(R + "/perp1m.json")); B = {d: ([x[0] for x in v], [x[1] for x in v]) for d, v in p1.items()}
print("plausibility: events with 1 m perp bars", sum(1 for v in p1.values() if len(v) > 300), "of", len(p1), "| median bars per event", int(np.median([len(v) for v in p1.values()])))
def run(rs, flip=False):
    out = []; cnt = collections.Counter()
    for r in rs:
        st, c = stale_prints(r, trd[r["slug"]], B[r["date"]][0], B[r["date"]][1], S[r["prod"]], flip=flip); out += [dict(s, prod=r["prod"]) for s in st]; cnt.update(c)
    return out, cnt
def report(label, rs):
    st, cnt = run(rs); stf, cntf = run(rs, flip=True); ndays = len({r["date"] for r in rs})
    buyusd = sum(t["price"] * t["size"] for r in rs for t in trd[r["slug"]] if t["side"] == "BUY" and r["T"] - 6 * 3600 <= t["timestamp"] < r["T"] and t["token_id"] in (r["up_token"], r["dn_token"]))
    print(f"--- {label}: events {len(rs)}, days {ndays}, buy prints {cnt['buy_prints']} (USD {buyusd:,.0f}), skipped no perp mark {cnt['no_perp_mark']}, STALE prints {cnt['stale']} (USD {sum(s['usd'] for s in st):,.0f}) [placebo flip: {len(stf)} prints]")
    if not st: return None
    byd = collections.defaultdict(list)
    for s in st: byd[s["date"]].append(s["pnl"])
    lo, hi = boot_mean(byd); usd = collections.defaultdict(float)
    for s in st: usd[s["date"]] += SLICE * s["usd"] * s["pnl"] / s["price"] if False else SLICE * s["size"] * s["pnl"]
    m_d, lo_d, hi_d = boot_perday(usd, ndays); pl = np.mean([s["pnl"] for s in stf]) if stf else None
    print(f"    mean pnl/share {np.mean([s['pnl'] for s in st]):+.4f} CI ({lo:+.4f},{hi:+.4f}) hit {np.mean([s['win'] for s in st]):.2f} mean price {np.mean([s['price'] for s in st]):.2f} mean model edge {np.mean([s['edge'] for s in st]):+.3f} dates {len(byd)} | $/day at 10% {m_d:+.2f} CI ({lo_d:+.2f},{hi_d:+.2f}) | placebo mean pnl {pl if pl is None else round(float(pl),4)}")
    for name, a, b in (("T-6h..T-2h", 120, 360), ("T-2h..T-30m", 30, 120), ("T-30m..T", 0, 30)):
        x = [s for s in st if a <= s["tau"] < b]
        if x: print(f"    bucket {name}: prints {len(x)} USD {sum(s['usd'] for s in x):,.0f} mean pnl/share {np.mean([s['pnl'] for s in x]):+.4f} hit {np.mean([s['win'] for s in x]):.2f}")
    return dict(n=len(st), dates=len(byd), pnl=float(np.mean([s["pnl"] for s in st])), ci=(lo, hi), usd_day=m_d, usd_day_ci=(lo_d, hi_d), placebo=None if pl is None else float(pl), placebo_n=len(stf))
res = {"TEST (verdict)": report("TEST (verdict)", test), "train": report("train", train), "all": report("all", rows)}
t = res["TEST (verdict)"]
if t is None: verdict = "unknown, N too small (no stale prints)"
elif t["n"] < 30 or t["dates"] < 20: verdict = f"unknown, N too small (n={t['n']}, dates={t['dates']})"
elif t["pnl"] > 0 and t["ci"][0] > 0 and (t["placebo"] is None or t["placebo"] < 0) and t["usd_day_ci"][0] >= 200: verdict = "PASS"
elif not (t["pnl"] > 0 and t["ci"][0] > 0): verdict = "fails on edge"
else: verdict = "fails on size"
print("VERDICT (locked rule B):", verdict)
# ---- C. lag measurement (descriptive)
lags = []; notmeas = 0; censored = 0
for r in rows:
    ts, mk = B[r["date"]]; T = r["T"]; tr = trd[r["slug"]]; s30 = S[r["prod"]]
    if len(ts) < 20: continue
    impl = sorted((t["timestamp"], t["price"] if t["token_id"] == r["up_token"] else 1 - t["price"]) for t in tr if t["token_id"] in (r["up_token"], r["dn_token"]) and T - 6 * 3600 - 900 <= t["timestamp"] < T)
    last_move = -1e18; i = 0
    for j in range(5, len(ts)):
        tj = ts[j] / 1000 + 60                                    # bar closes at ts+60 s: usable from then
        if tj - last_move < 600 or tj >= T or tj < T - 6 * 3600: continue
        dm = abs(math.log(mk[j] / mk[j - 5])) * 1e4
        if dm < 10: continue
        last_move = tj; tau = (T - tj) / 60; tau5 = (T - (tj - 300)) / 60
        pu = fair_token(mk[j], r["cs"], s30, tau, True); pu0 = fair_token(mk[j - 5], r["cs"], s30, tau5, True); dp = pu - pu0
        pre = [p for tt, p in impl if tj - 900 <= tt <= tj - 300]
        if not pre or abs(dp) < 0.02: notmeas += 1; continue
        lvl = float(np.median(pre)); got = None
        for tt, p in impl:
            if tt <= tj: continue
            if tt - tj > 1800: break
            if (p - lvl) * np.sign(dp) >= 0.5 * abs(dp): got = tt - tj; break
        if got is None: censored += 1
        else: lags.append(got)
n = len(lags) + censored
print(f"LAG (descriptive): perp moves >=10 bp in 5 min with a model jump >= 2c: measurable {n}, not measurable (no pre-level print or jump < 2c) {notmeas}; caught up within 30 min {len(lags)}, censored {censored}")
if lags: print(f"    lag seconds: median {np.median(lags):.0f}, quartiles {np.percentile(lags,25):.0f} / {np.percentile(lags,75):.0f}, share within 60 s {np.mean(np.array(lags) <= 60):.2f} (of caught-up), share within 60 s of all measurable {np.sum(np.array(lags) <= 60)/n:.2f}")
res["lag"] = dict(measurable=n, notmeas=notmeas, censored=censored, median=None if not lags else float(np.median(lags)))
json.dump(res, open(R + "/result_stale.json", "w"), indent=1, default=float)
