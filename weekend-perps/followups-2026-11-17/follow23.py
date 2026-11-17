"""Tests 2 and 3 of LOCKED-RULE-divergence-followups-2026-11-17.md. usage: follow23.py [DATADIR]"""
import sys, collections, numpy as np
from perplib import *
D = sys.argv[1] if len(sys.argv) > 1 else "."
oi, F, C, HS = load(D); GR = load_growth(D); A, c1, c2 = universe(oi, F); tier = make_tier(oi, c1, c2)   # same cut-offs as the funding-window test
syms = [s for s in F if len(F[s]) >= 1440 and (oi.get(s, 0) > 0 or s.split(":")[0] in ("flx", "km")) and s in C]
grp = lambda s: "flx+km" if s.split(":")[0] in ("flx", "km") else "xyz"
sg = np.sign
S = {s: series(F, s) for s in syms}
noHS = sorted(s for s in syms if HS.get(s) is None); print("symbols", len(syms), "no live half-spread (excluded from every trade):", noHS)
FI = {s: fee_info(s, GR) for s in syms}; cost = {s: cost_bp(HS.get(s), FI[s][0]) for s in syms}
# ---------- Test 2: primary non-overlapping event stream; (c) is a subset of that stream
def carry(k):
    ev = []
    for s in syms:
        if cost[s] is None: continue
        P, FR = S[s]; cs = C[s]; free = 0
        for t in sorted(P):
            if t < free or abs(P[t]) < 50: continue
            x0 = cs.get(t - H); x1 = cs.get(t + (k - 1) * H)   # close of hour h (open t-H) -> close of hour h+k (open t+(k-1)H)
            if not x0 or not x1: continue
            pos = -sg(P[t]); g = pos * (x1[1] / x0[1] - 1) * 1e4
            fr = sum(-pos * FR.get(t + i * H, 0) for i in range(1, k + 1))
            persist = all((t - i * H) in P and abs(P[t - i * H]) >= 100 and sg(P[t - i * H]) == sg(P[t]) for i in range(3))
            ev.append(dict(s=s, wk=cal_week(t), net=g + fr - cost[s], g=g, fr=fr, persist=persist, grp=grp(s), tier=tier(s), chk=FI[s][1])); free = t + k * H
    return ev
def report(ev, label):
    print("==", label)
    cells = collections.defaultdict(list)
    for e in ev:
        for key in (("all", "all"), (e["grp"], "all"), ("all", e["tier"]), (e["grp"], e["tier"])): cells[key].append(e)
        if e["persist"]: cells[("persistent", "all")].append(e)
    for key in sorted(cells):
        v = cells[key]
        if len(v) < 10: continue
        net = np.mean([x["net"] for x in v]); ci = boot([(x["wk"], x["net"]) for x in v]); wks = len(set(x["wk"] for x in v))
        print(f"{key[0]:10s}{key[1]:7s} n={len(v):5d} weeks={wks:2d} gross={np.mean([x['g'] for x in v]):7.1f} funding={np.mean([x['fr'] for x in v]):6.1f} net={net:7.1f} CI={ci} PASS={bool(len(v) >= 30 and wks >= 8 and net > 0 and ci[0] > 0)} {'COST UNCHECKED (%d of %d)' % (sum(1 for x in v if not x['chk']), len(v)) if any(not x['chk'] for x in v) else 'cost sourced'}")
for k in (6, 3, 12): report(carry(k), f"Test 2 carry k={k} ({'primary' if k == 6 else 'sensitivity only'})")
# ---------- Test 3
eps = []
for s in syms:
    P, FR = S[s]; ts = sorted(P); i = 0
    while i < len(ts):
        t = ts[i]
        if abs(P[t]) >= 100:
            j = i
            while j + 1 < len(ts) and ts[j + 1] == ts[j] + H and abs(P[ts[j + 1]]) >= 100 and sg(P[ts[j + 1]]) == sg(P[t]): j += 1
            n = j - i + 1
            if n >= 3:
                # reset = the FIRST hour after the run with |premium| < 25 (searched over contiguous hours; a data gap censors)
                r = None; u = ts[j]
                while (u + H) in P:
                    u += H
                    if abs(P[u]) < 25: r = u; break
                eps.append(dict(s=s, start=t, n=n, last=ts[j], p=P[ts[j]], sign=sg(P[t]), reset_t=r, reset=r is not None,
                                immediate=(r is not None and r == ts[j] + H), end_kind=("reset" if r else "censored/never")))
            i = j + 1
        else: i += 1
print("== Test 3: episodes", len(eps), "end:", collections.Counter(e["end_kind"] for e in eps), "reset in the very next hour:", sum(e["immediate"] for e in eps))
for gname in ("xyz", "flx+km"):
    for tn in ("thin", "mid", "liquid"):
        v = [e for e in eps if grp(e["s"]) == gname and tier(e["s"]) == tn]
        if v: print(gname, tn, "episodes", len(v), "median run", np.median([e["n"] for e in v]), "p90 run", np.percentile([e["n"] for e in v], 90), "median |p| before end", round(float(np.median([abs(e["p"]) for e in v])), 0))
print("hazard: run length n -> P(reset in the next hour | run reached n), episodes at risk")
for n in range(3, 13):
    risk = [e for e in eps if e["n"] >= n]
    if len(risk) < 10: break
    print(n, len(risk), round(sum(1 for e in risk if e["n"] == n and e["immediate"]) / len(risk), 3))
y = []; x = []; tr = []
for e in eps:
    if not e["reset"]: continue
    s = e["s"]; cs = C[s]; c_reset = cs.get(e["reset_t"] - H)   # candle of the reset hour (open reset_t - H)
    if c_reset:
        mv = (c_reset[1] / c_reset[0] - 1) * 1e4 * (-e["sign"]); y.append(mv); x.append(abs(e["p"]))
        t3 = e["start"] + 2 * H; ent = cs.get(t3 - H)    # close of the third hour of the episode
        if ent and cost[s] is not None:
            pos = -e["sign"]; g = pos * (c_reset[1] / ent[1] - 1) * 1e4; FRs = S[s][1]
            fr = sum(-pos * FRs.get(t, 0) for t in range(t3 + H, e["reset_t"] + 1, H))
            tr.append((cal_week(e["start"]), g + fr - cost[s], g, fr, grp(s), FI[s][1]))
print("reset episodes with a reset-hour candle", len(y), "| ex-post trades with COST UNCHECKED:", sum(1 for a in tr if not a[5]), "of", len(tr))
if len(y) > 5:
    y = np.array(y); x = np.array(x)
    print("candle return toward the oracle in the reset hour (bp): mean", y.mean().round(1), "median", np.median(y).round(1), "mean |premium| before", x.mean().round(1), "slope", np.polyfit(x, y, 1)[0].round(3), "corr", np.corrcoef(x, y)[0, 1].round(3))
    print("ex-post bound (enter close of 3rd hour, exit close of reset hour): n", len(tr), "gross", np.mean([a[2] for a in tr]).round(1), "funding", np.mean([a[3] for a in tr]).round(1), "net", np.mean([a[1] for a in tr]).round(1), "CI", boot([(a[0], a[1]) for a in tr]), "weeks", len(set(a[0] for a in tr)))
    for gname in ("xyz", "flx+km"):
        v = [a for a in tr if a[4] == gname]
        if len(v) >= 5: print("  ", gname, len(v), "net", np.mean([a[1] for a in v]).round(1), boot([(a[0], a[1]) for a in v]))
# (d) logistic regression on run length, |premium|, weekend indicator; out-of-sample = last 30% of CALENDAR WEEKS
rows = []
for e in eps:
    P = S[e["s"]][0]
    for n in range(3, e["n"] + 1):
        t = e["start"] + (n - 1) * H; nxt = t + H
        if nxt not in P: continue
        rows.append((cal_week(t), [1, n, abs(P[t]) / 100, 1 if is_weekend(nxt - H) else 0], 1 if (n == e["n"] and e["immediate"]) else 0))
wks = sorted(set(r[0] for r in rows)); cutw = set(wks[:int(len(wks) * 0.7)])
trn = [r for r in rows if r[0] in cutw]; tst = [r for r in rows if r[0] not in cutw]
Xtr = np.array([r[1] for r in trn], float); ytr = np.array([r[2] for r in trn], float); Xte = np.array([r[1] for r in tst], float); yte = np.array([r[2] for r in tst], float)
w = np.zeros(Xtr.shape[1])
for _ in range(50):
    p = 1 / (1 + np.exp(-Xtr @ w)); W = p * (1 - p) + 1e-6; w = w + np.linalg.solve(Xtr.T @ (Xtr * W[:, None]) + 1e-3 * np.eye(len(w)), Xtr.T @ (ytr - p))
sc = Xte @ w
def auc(yv, sv):
    pos = sv[yv == 1]; neg = sv[yv == 0]
    return float(np.mean([(q > neg).mean() + 0.5 * (q == neg).mean() for q in pos])) if len(pos) and len(neg) else None
print("logistic rows", len(rows), "weeks", len(wks), "test weeks", len(wks) - len(cutw), "train resets", int(ytr.sum()), "test resets", int(yte.sum()), "AUC out-of-sample", auc(yte, sc), "coefs [const,run,|p|/100,weekend]", w.round(2))
