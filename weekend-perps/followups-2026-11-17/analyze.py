"""Funding-window divergence test, metrics 1-4 of LOCKED-RULE-funding-window-divergence-2026-11-17.md. usage: analyze.py [DATADIR]"""
import sys, json, collections, numpy as np
from perplib import *
D = sys.argv[1] if len(sys.argv) > 1 else "."
oi, F, C, HS = load(D); GR = load_growth(D); A, c1, c2 = universe(oi, F); tier = make_tier(oi, c1, c2)
print("symbols", len(A), "OI cut-offs $m", round(c1 / 1e6, 2), round(c2 / 1e6, 2))
agg = collections.defaultdict(lambda: dict(p=[], nxt=[], ar=[], fr=[], fade=[], run=[]))
trades = collections.defaultdict(list); excluded = set()
for s in A:
    P, FR = series(F, s); T = sorted(P); tr = tier(s); cs = C.get(s, {}); fi = fee_info(s, GR); cost = cost_bp(HS.get(s), fi[0]); chk = fi[1]
    for t in T:
        k = (tr, sess(t)); a = agg[k]; p = P[t]; n = P.get(t + H)
        a["p"].append(abs(p)); a["fr"].append(abs(FR[t]))
        if abs(p) >= 25:
            a["fade"].append(np.sign(p) * FR[t])  # fading side = -sign(p); receives -(-sign(p))*rate = sign(p)*rate
            if n is not None: a["nxt"].append(1 if (np.sign(n) == np.sign(p) and abs(n) >= abs(p) / 2) else 0)
        if n is not None: a["ar"].append((p, n))
        if abs(p) >= 50 and n is not None:       # metric 4: reversion trade
            if cost is None: excluded.add(s); continue
            c0 = cs.get(t - H); c1_ = cs.get(t)   # close of hour h candle (open t-H) -> close of hour h+1 candle (open t)
            if c0 and c1_ and (t + H) in FR:
                pos = -np.sign(p); g = pos * (c1_[1] / c0[1] - 1) * 1e4; f = -pos * FR[t + H]   # long pays +rate
                trades[k].append((cal_week(t), g + f - cost, g, f, chk))
    # runs of consecutive same-sign hours with |p| >= 25 (timestamps contiguous), assigned to the session of the first hour
    i = 0
    while i < len(T):
        if abs(P[T[i]]) >= 25:
            j = i
            while j + 1 < len(T) and T[j + 1] == T[j] + H and abs(P[T[j + 1]]) >= 25 and np.sign(P[T[j + 1]]) == np.sign(P[T[i]]): j += 1
            agg[(tr, sess(T[i]))]["run"].append(j - i + 1); i = j + 1
        else: i += 1
print("excluded from metric 4 (no live half-spread):", sorted(excluded))
out = {}
for tr in ("thin", "mid", "liquid"):
    for se in ("weekend", "weekday-US", "weekday-other"):
        a = agg[(tr, se)]; p = np.array(a["p"])
        if len(p) < 50: print(f"{tr} {se}: {len(p)} hours (< 50), not summarised"); continue
        ar = float(np.corrcoef(*zip(*a["ar"]))[0, 1]) if len(a["ar"]) > 50 else float("nan")
        row = dict(tier=tr, session=se, hours=len(p), med=float(np.median(p)), p90=float(np.percentile(p, 90)), p99=float(np.percentile(p, 99)),
                   s25=float((p >= 25).mean()), s50=float((p >= 50).mean()), n25=len(a["nxt"]), notrev=float(np.mean(a["nxt"])) if a["nxt"] else None,
                   ar1=ar, run=float(np.median(a["run"])) if a["run"] else None, fund=float(np.mean(a["fr"])),
                   fade_rx=float(np.mean(a["fade"])) if a["fade"] else None)
        row["material"] = row["s25"] >= 0.05; row["persistent"] = bool(row["notrev"] is not None and row["notrev"] >= 0.5)
        tt = trades.get((tr, se), [])
        if tt:
            row.update(n_unchecked_cost=sum(1 for x in tt if not x[4]), n_tr=len(tt), weeks=len(set(x[0] for x in tt)), gross=float(np.mean([x[2] for x in tt])), fund_rx=float(np.mean([x[3] for x in tt])),
                       net=float(np.mean([x[1] for x in tt])), ci=boot([(x[0], x[1]) for x in tt]))
            row["tradable"] = bool(row["net"] > 0 and row["ci"][0] > 0 and row["n_tr"] >= 30 and row["weeks"] >= 8)
        out[f"{tr}|{se}"] = row
        print(f"{tr:6s}{se:14s}|{len(p):7d}| med {row['med']:5.1f} p90 {row['p90']:6.1f} p99 {row['p99']:7.1f} | >=25 {row['s25']*100:5.1f}% >=50 {row['s50']*100:5.1f}% | n25 {row['n25']:5d} notrev {row['notrev']} | AR1 {ar:.2f} | run {row['run']} | |fund| {row['fund']:.2f} fade_rx {row['fade_rx']} | material={row['material']} persistent={row['persistent']}")
        if tt: print(f"     {'COST UNCHECKED for %d of %d trades' % (row['n_unchecked_cost'], len(tt)) if row['n_unchecked_cost'] else 'cost sourced'} | reversion trade n={len(tt)} weeks={row['weeks']} gross={row['gross']:.1f} funding_rx={row['fund_rx']:.1f} net={row['net']:.1f} CI={row['ci']} tradable={row['tradable']}")
json.dump(out, open(D + "/hist_result.json", "w"), indent=1, default=float)
