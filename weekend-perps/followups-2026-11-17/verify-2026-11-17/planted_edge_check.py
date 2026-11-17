"""Independent planted-edge check for ../ analyze.py, follow23.py, eval1.py, sample_an.py. Synthetic data only."""
import json, os, re, subprocess, gzip, datetime, random, sys, collections
import numpy as np
import os; NEW = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/"; V = os.environ.get("VERIFY_OUT", "/tmp/pe_check"); H = 3600000
T0 = int(datetime.datetime(2026, 6, 1, tzinfo=datetime.timezone.utc).timestamp() * 1000)  # a Monday 00:00 UTC
NW = 14; NH = NW * 168   # 14 weeks = 2352 hourly records per symbol
RES = []
def check(name, ok, detail):
    RES.append((name, ok)); print(("PASS" if ok else "FAIL"), "|", name, "|", detail)
# ---- independent definitions (written from the rule text, not from the code under test)
def wd_hr(ms):
    d = datetime.datetime.fromtimestamp(ms / 1000, datetime.timezone.utc); return d.weekday(), d.hour
def ref_sess(t_end):                       # session of the hour that ENDS at t_end
    wd, hr = wd_hr(t_end - H)
    if (wd == 4 and hr >= 22) or wd == 5 or (wd == 6 and hr < 22): return "weekend"
    if wd < 5 and 13 <= hr < 21: return "weekday-US"
    return "weekday-other"
def wk(ms): return datetime.datetime.fromtimestamp(ms / 1000, datetime.timezone.utc).isocalendar()[:2]
# ---- symbol universe: 36 symbols, OI spread over terciles, xyz bare/prefixed, flx:, km:
SYMS = ["xyz:S%02d" % i for i in range(20)] + ["BARE%02d" % i for i in range(4)] + ["flx:F%02d" % i for i in range(6)] + ["km:K%02d" % i for i in range(6)]
OI = {s: 1e6 * (1.37 ** i) for i, s in enumerate(SYMS)}                      # distinct, increasing
HSP = {s: [0.2, 0.5, 1.0, 2.5][i % 4] for i, s in enumerate(SYMS)}           # bp; 0.2 -> floor binds (3*0.2<1)
GROWTH = {"xyz": {s.replace("xyz:", ""): ("enabled" if i % 2 == 0 else None) for i, s in enumerate(SYMS) if not s.startswith(("flx:", "km:"))}, "flx": {}, "km": {}}
def fee_of(s):
    name = s.split(":")[-1]; dex = s.split(":")[0] if ":" in s and s.split(":")[0] in ("flx", "km") else "xyz"
    return 0.9 if GROWTH[dex].get(name) == "enabled" else 9.0
def cost_of(s): return 2 * (fee_of(s) + max(3 * HSP[s], 1.0))
def write(case, prem, ret, fund):
    """prem[s]: list of premium bp per hour i (record time T0+(i+1)H); ret[s]: candle return of hour i (fraction); fund[s]: rate fraction"""
    d = f"{V}/data_{case}"; os.makedirs(d, exist_ok=True)
    fh = {}; cd = {}
    for s in SYMS:
        px = 100.0; c = {}
        for i in range(NH):
            o = px; px = px * (1 + ret[s][i]); c[str(T0 + i * H)] = [o, px]
        cd[s] = c
        fh[s] = [[T0 + (i + 1) * H, prem[s][i] / 1e4, fund[s][i]] for i in range(NH)]
    json.dump(dict(oi=OI, fund=fh), open(d + "/hist.json", "w")); json.dump(dict(candles=cd, halfspread=HSP), open(d + "/cand.json", "w"))
    json.dump(GROWTH, open(d + "/growth.json", "w")); return d
def event_idx(rng, spacing=30, n=30):
    c = sorted(rng.sample(range(8, NH - 20), 400)); out = []
    for x in c:
        if not out or x - out[-1] >= spacing: out.append(x)
    return sorted(rng.sample(out, n)) if len(out) >= n else out
def run(script, d):
    r = subprocess.run([sys.executable, f"{NEW}/{script}", d], capture_output=True, text=True, cwd=V)
    if r.returncode: print("CRASH", script, d, r.stderr[-800:]); check(f"FINDING {script} crashes on well-formed input {os.path.basename(d)}", False, "crashed: " + r.stderr.strip().splitlines()[-1])
    return r.stdout
def cells_ref(case_d, prem, ret, fund, evs_only=True):
    """reference metric-4 trades per (tier, session): list of (net, gross, f)"""
    o = sorted(OI[s] for s in SYMS); c1, c2 = o[len(o) // 3], o[2 * len(o) // 3]
    tier = lambda s: "thin" if OI[s] <= c1 else ("mid" if OI[s] <= c2 else "liquid")
    out = collections.defaultdict(list)
    for s in SYMS:
        for i in range(NH - 1):
            p = prem[s][i]
            if abs(p) >= 50:
                pos = -np.sign(p); g = pos * ret[s][i + 1] * 1e4; f = -pos * fund[s][i + 1] * 1e4
                out[(tier(s), ref_sess(T0 + (i + 1) * H))].append((g + f - cost_of(s), g, f))
    return out, tier
def compare_analyze(case, d, prem, ret, fund, expect_gross=None, tol=0.02):
    out = run("analyze.py", d); R = json.load(open(d + "/hist_result.json")); ref, tier = cells_ref(d, prem, ret, fund)
    bad = []; n_cells = 0
    for key, row in R.items():
        tr, se = key.split("|"); e = ref.get((tr, se), [])
        if not e and "n_tr" not in row: continue
        n_cells += 1
        if len(e) != row.get("n_tr", 0): bad.append((key, "n", len(e), row.get("n_tr"))); continue
        for nm, ix in (("net", 0), ("gross", 1), ("fund_rx", 2)):
            if abs(np.mean([x[ix] for x in e]) - row[nm if nm != "fund_rx" else "fund_rx"]) > tol: bad.append((key, nm, np.mean([x[ix] for x in e]), row[nm]))
    allr = [x for v in ref.values() for x in v]
    pooled = (np.mean([x[1] for x in allr]), np.mean([x[0] for x in allr]), np.mean([x[2] for x in allr]), len(allr))
    return out, R, bad, n_cells, pooled
def compare_metrics123(R, prem, fund, d):
    """reference size/persistence/funding metrics per cell (tier x session) from my own loops"""
    o = sorted(OI[s] for s in SYMS); c1, c2 = o[len(o) // 3], o[2 * len(o) // 3]
    tier = lambda s: "thin" if OI[s] <= c1 else ("mid" if OI[s] <= c2 else "liquid")
    cell = collections.defaultdict(lambda: dict(p=[], nxt=[], fr=[], fade=[], run=[], pairs=[]))
    for s in SYMS:
        P = prem[s]; i = 0
        for h in range(NH):
            k = (tier(s), ref_sess(T0 + (h + 1) * H)); c = cell[k]; c["p"].append(abs(P[h])); c["fr"].append(abs(fund[s][h] * 1e4))
            if abs(P[h]) >= 25:
                c["fade"].append(np.sign(P[h]) * fund[s][h] * 1e4)
                if h + 1 < NH: c["nxt"].append(int(np.sign(P[h + 1]) == np.sign(P[h]) and abs(P[h + 1]) >= abs(P[h]) / 2))
            if h + 1 < NH: c["pairs"].append((P[h], P[h + 1]))
        h = 0
        while h < NH:
            if abs(P[h]) >= 25:
                j = h
                while j + 1 < NH and abs(P[j + 1]) >= 25 and np.sign(P[j + 1]) == np.sign(P[h]): j += 1
                cell[(tier(s), ref_sess(T0 + (h + 1) * H))]["run"].append(j - h + 1); h = j + 1
            else: h += 1
    bad = []
    for key, row in R.items():
        tr, se = key.split("|"); c = cell[(tr, se)]; p = np.array(c["p"])
        exp = dict(hours=len(p), med=np.median(p), p90=np.percentile(p, 90), p99=np.percentile(p, 99), s25=(p >= 25).mean(), s50=(p >= 50).mean(), fund=np.mean(c["fr"]))
        if c["nxt"]: exp["notrev"] = np.mean(c["nxt"])
        if c["run"]: exp["run"] = np.median(c["run"])
        if c["fade"]: exp["fade_rx"] = np.mean(c["fade"])
        a, b = zip(*c["pairs"]); exp["ar1"] = np.corrcoef(a, b)[0, 1]
        for nm, v in exp.items():
            if row.get(nm) is None or abs(row[nm] - v) > 1e-6 * max(1, abs(v)) + 1e-9:
                if not (isinstance(v, float) and np.isnan(v) and row.get(nm) != row.get(nm)): bad.append((key, nm, v, row.get(nm)))
    return bad
def build_edge(case, kind, seed, sign_mode="mixed", rate=0.0, rev=40.0):
    rng = random.Random(seed); nrng = np.random.default_rng(seed); prem = {}; ret = {}; fund = {}
    for s in SYMS:
        if kind == "noedge":
            prem[s] = list(nrng.normal(0, 30, NH)); ret[s] = list(nrng.normal(0, 20, NH) / 1e4); fund[s] = [0.0] * NH; continue
        pr = list(np.clip(nrng.normal(0, 5, NH), -20, 20)); rt = [0.0] * NH
        for e in event_idx(rng):
            sg = {"mixed": rng.choice((-1, 1)), "pos": 1, "neg": -1}[sign_mode]
            pr[e] = sg * rng.uniform(60, 120)
            if kind == "edge": rt[e + 1] = -sg * rev / 1e4
        prem[s] = pr; ret[s] = rt; fund[s] = [rate] * NH
    return prem, ret, fund
CARRY_RE = re.compile(r"^(all|xyz|flx\+km|persistent)\s*(all|thin|mid|liquid)\s+n=\s*(\d+) weeks=\s*(\d+) gross=\s*(\S+) funding=\s*(\S+) net=\s*(\S+) CI=\((\S+), (\S+)\) \| net at old 9 bp \S+ \| COST UNCHECKED \d+ of \d+ \| (?:VERDICT PASS=(\w+)|no sourced|sensitivity only)")
def parse_carry(out):
    secs = {}; cur = None
    for l in out.splitlines():
        if l.startswith("== Test 2 carry k="): cur = int(l.split("k=")[1].split()[0]); secs[cur] = {}
        elif cur and CARRY_RE.match(l):
            m = CARRY_RE.match(l); secs[cur][(m[1], m[2])] = dict(n=int(m[3]), wk=int(m[4]), gross=float(m[5]), fr=float(m[6]), net=float(m[7]), ci=(float(m[8]), float(m[9])), PASS=m[10] == "True")
        elif l.startswith("== Test 3"): cur = None
    return secs
def ref_carry(prem, ret, fund, k):
    o = sorted(OI[s] for s in SYMS); c1, c2 = o[len(o) // 3], o[2 * len(o) // 3]
    tier = lambda s: "thin" if OI[s] <= c1 else ("mid" if OI[s] <= c2 else "liquid")
    grp = lambda s: "flx+km" if s.startswith(("flx:", "km:")) else "xyz"
    ev = []
    px = {}
    for s in SYMS:
        c = [100.0]
        for i in range(NH): c.append(c[-1] * (1 + ret[s][i]))      # c[i+1] = close of hour i
        px[s] = c
    for s in SYMS:
        free = -1
        for h in range(NH):
            if h < free or abs(prem[s][h]) < 50 or h + k >= NH: continue
            pos = -np.sign(prem[s][h]); g = pos * (px[s][h + 1 + k] / px[s][h + 1] - 1) * 1e4
            fr = sum(-pos * fund[s][h + i] * 1e4 for i in range(1, k + 1))
            per = h >= 2 and all(abs(prem[s][h - i]) >= 100 and np.sign(prem[s][h - i]) == np.sign(prem[s][h]) for i in range(3))
            ev.append((s, g + fr - cost_of(s), g, fr, per, grp(s), tier(s))); free = h + k
    return ev
def compare_carry(out, prem, ret, fund, label):
    sec = parse_carry(out); bad = []; ncell = 0
    for k in (6, 3, 12):
        ev = ref_carry(prem, ret, fund, k)
        for (a, b), r in sec[k].items():
            sel = [e for e in ev if (a == "all" or (a == "persistent" and e[4]) or (a in ("xyz", "flx+km") and e[5] == a)) and (b == "all" or e[6] == b)]
            if a == "persistent" and b != "all": continue
            ncell += 1
            if len(sel) != r["n"]: bad.append((k, a, b, "n", len(sel), r["n"])); continue
            for nm, ix, v in (("net", 1, r["net"]), ("gross", 2, r["gross"]), ("fr", 3, r["fr"])):
                if abs(np.mean([e[ix] for e in sel]) - v) > 0.051: bad.append((k, a, b, nm, np.mean([e[ix] for e in sel]), v))
    check(label, not bad and ncell > 0, f"{ncell} cells over k=3/6/12 compared to independent reference (n exact, means within 0.05 bp); mismatches {bad[:3]}")
    return sec
# ============ CASE 1 planted edge
print("\n#### CASE 1: planted reversion edge (premium 60-120 bp, perp reverts 40 bp next hour, zero funding)")
prem, ret, fund = build_edge("c1", "edge", 11); d1 = write("c1", prem, ret, fund)
out, R, bad, nc, pooled = compare_analyze("c1", d1, prem, ret, fund)
print(out[:1500])
print(f"expected pooled gross 40.00, net = 40 - mean cost; actual-from-reference pooled gross {pooled[0]:.2f} net {pooled[1]:.2f} funding {pooled[2]:.2f} n={pooled[3]}")
rn = sum(r["n_tr"] * r["net"] for r in R.values() if "n_tr" in r) / sum(r["n_tr"] for r in R.values() if "n_tr" in r)
rg = sum(r["n_tr"] * r["gross"] for r in R.values() if "n_tr" in r) / sum(r["n_tr"] for r in R.values() if "n_tr" in r)
check("C1 analyze metric 4 gross == 40 bp in every cell", all(abs(r["gross"] - 40) < 1e-6 for r in R.values() if "n_tr" in r), f"analyze pooled gross {rg:.4f}")
check("C1 analyze net == 40 - 2*(fee+max(3hs,1)) per symbol (per-cell compare to reference)", not bad and nc > 0, f"cells {nc}, pooled net analyze {rn:.3f} vs reference {pooled[1]:.3f}; mismatches {bad[:3]}")
check("C1 analyze cost spot check: S00(hs .2, growth) cost=2*(0.9+1)=3.8; S03(hs 2.5, no growth) cost=2*(9+7.5)=33", abs(cost_of("xyz:S00") - 3.8) < 1e-9 and abs(cost_of("xyz:S03") - 33) < 1e-9, "reference cost fn")
check("C1 analyze metrics 1-3 equal independent reference in all cells", not compare_metrics123(R, prem, fund, d1), str(compare_metrics123(R, prem, fund, d1)[:3]))
check("C1 analyze: some cell flagged tradable (net>0, CI>0, n>=30, weeks>=8)", any(r.get("tradable") for r in R.values()), f"tradable cells {[k for k,r in R.items() if r.get('tradable')]}")
check("C1 analyze: COST UNCHECKED label appears (non-growth symbols exist)", "COST UNCHECKED" in out, "text check")
out2 = run("follow23.py", d1); sec = compare_carry(out2, prem, ret, fund, "C1 follow23 Test 2 carry (k=6 primary, 3, 12) == reference; gross 40 each")
if sec.get(6): check("C1 follow23 k=6 'all|all' gross 40.0", abs(sec[6][("all", "all")]["gross"] - 40) < 0.051, f"gross {sec[6][('all','all')]['gross']} net {sec[6][('all','all')]['net']} n {sec[6][('all','all')]['n']}")
# ============ CASE 2 no edge
print("\n#### CASE 2: no edge (random-walk price sd 20 bp/h, premium N(0,30) independent)")
prem, ret, fund = build_edge("c2", "noedge", 22); d2 = write("c2", prem, ret, fund)
out, R, bad, nc, pooled = compare_analyze("c2", d2, prem, ret, fund)
tot = sum(r["n_tr"] for r in R.values() if "n_tr" in r); rg = sum(r["n_tr"] * r["gross"] for r in R.values() if "n_tr" in r) / tot; rn = sum(r["n_tr"] * r["net"] for r in R.values() if "n_tr" in r) / tot
allc = np.mean([cost_of(s) for s in SYMS]); se = 20 / np.sqrt(tot)
check("C2 analyze gross ~0 (|gross| < 4 SE)", abs(rg) < 4 * se, f"pooled gross {rg:.3f} bp, SE {se:.3f}, n={tot}")
check("C2 analyze net == gross - mean cost (exact vs reference) and no cell tradable", not bad and not any(r.get("tradable") for r in R.values()), f"pooled net {rn:.2f}, reference net {pooled[1]:.2f}; mean cost over symbols {allc:.2f}; mismatches {bad[:3]}")
check("C2 analyze metrics 1-3 equal reference", not compare_metrics123(R, prem, fund, d2), str(compare_metrics123(R, prem, fund, d2)[:3]))
out2 = run("follow23.py", d2); sec = compare_carry(out2, prem, ret, fund, "C2 follow23 Test 2 == reference")
check("C2 follow23: no Test 2 cell PASS", not any(v["PASS"] for s in sec.values() for v in s.values()), f"k=6 all|all net {sec[6][('all','all')]['net']} gross {sec[6][('all','all')]['gross']} n {sec[6][('all','all')]['n']}")
# ============ CASE 3 funding sign
print("\n#### CASE 3: funding sign (constant rate +2 bp/h, zero price move, premium events 60-120 bp)")
RATE = 0.0002
for mode in ("pos", "neg", "mixed"):
    prem, ret, fund = build_edge("c3" + mode, "flat", 33, sign_mode=mode, rate=RATE); d3 = write("c3" + mode, prem, ret, fund)
    out, R, bad, nc, pooled = compare_analyze("c3" + mode, d3, prem, ret, fund)
    exp_f = {"pos": 2.0, "neg": -2.0}.get(mode)
    r_ok = all(abs(r["gross"]) < 1e-9 for r in R.values() if "n_tr" in r)
    f_ok = all(abs(r["fund_rx"] - (exp_f if exp_f is not None else r["fund_rx"])) < 1e-9 for r in R.values() if "n_tr" in r)
    check(f"C3[{mode}] analyze: gross 0, funding received = {exp_f if exp_f is not None else 'mean(-pos*rate)'} bp, net = funding - cost (== reference)", r_ok and f_ok and not bad and nc > 0, f"reference pooled funding {pooled[2]:.3f}, net {pooled[1]:.3f}; analyze cell fund_rx {sorted(set(round(r['fund_rx'],3) for r in R.values() if 'n_tr' in r))}; mismatches {bad[:3]}")
    if exp_f is not None:
        fr_rows = [r["fade_rx"] for r in R.values() if r.get("fade_rx") is not None]
        check(f"C3[{mode}] analyze metric 3 fade_rx == {exp_f}", all(abs(x - exp_f) < 1e-9 for x in fr_rows), f"fade_rx cells {sorted(set(round(x,3) for x in fr_rows))}")
    out2 = run("follow23.py", d3); sec = compare_carry(out2, prem, ret, fund, f"C3[{mode}] follow23 Test 2 == reference")
    if exp_f is not None:
        for k in (3, 6, 12):
            a = sec[k][("all", "all")]; e = exp_f * k
            check(f"C3[{mode}] follow23 k={k}: funding {e:+.1f} bp (= {k} settlements x rate x side), gross 0", abs(a["fr"] - e) < 0.051 and abs(a["gross"]) < 0.051, f"actual funding {a['fr']}, gross {a['gross']}, net {a['net']}, n {a['n']}")
# ============ CASE 5 frozen-oracle episodes (Test 3 + persistent subset)
print("\n#### CASE 5: frozen-oracle episodes for Test 2(c) and Test 3")
rng = random.Random(55); nrng = np.random.default_rng(55); prem = {}; ret = {}; fund = {}; EP = []
for s in SYMS:
    pr = list(np.clip(nrng.normal(0, 5, NH), -20, 20)); rt = [0.0] * NH; last = 8
    for _ in range(22):
        st = last + rng.randint(30, 45); n = rng.randint(3, 8); M = rng.uniform(100, 300); sg = rng.choice((-1, 1)); trans = rng.random() < 1 / 3
        r = st + n + (1 if trans else 0)
        if r + 14 >= NH: break
        for i in range(st, st + n): pr[i] = sg * M
        if trans: pr[st + n] = sg * 60
        pr[r] = sg * 3.0; rt[r] = -sg * 0.5 * M / 1e4; last = r; EP.append((s, st, n, M, sg, trans, r))
    prem[s] = pr; ret[s] = rt; fund[s] = [0.0] * NH
d5 = write("c5", prem, ret, fund); out = run("follow23.py", d5); print("\n".join(l for l in out.splitlines() if not l.startswith(("xyz ", "flx+km ")) or True)[:3500])
sec = compare_carry(out, prem, ret, fund, "C5 follow23 Test 2 incl. persistent subset == reference")
m = re.search(r"== Test 3: episodes (\d+) end: (Counter\(.*?\)) reset in the very next hour: (\d+)", out)
check("C5 Test 3 episode count / immediate-reset count", m and int(m[1]) == len(EP) and int(m[3]) == sum(1 for e in EP if not e[5]), f"expected episodes {len(EP)}, immediate {sum(1 for e in EP if not e[5])}; actual {m.groups() if m else None}")
m = re.search(r"mean ([\-\d.]+) median ([\-\d.]+) mean \|premium\| before ([\d.]+) slope ([\-\d.]+) corr ([\-\d.]+)", out)
exp_mean = np.mean([0.5 * e[3] for e in EP]); xs = np.array([e[3] for e in EP]); ys = 0.5 * xs
check("C5 Test 3(c) reset-hour candle return toward oracle: mean = 0.5*mean|p|, slope about 0.16 (x = premium of the hour just before the reset, literal rule reading)", m and abs(float(m[1]) - exp_mean) < 0.06 and abs(float(m[4]) - 0.16) < 0.01, f"expected mean {exp_mean:.1f} slope 0.16; actual mean {m[1] if m else None} slope {m[4] if m else None}")
tr_ = [e for e in EP]; nn = [e for e in EP if not e[5]]
tx = np.array([e[3] for e in EP if e[5]]); ty = np.array([0.5 * e[3] for e in EP if e[5]])
print("   NOTE literal reading 'versus the premium before the reset' for non-immediate resets (transition hour premium 60 bp): slope would be", round(float(np.polyfit([60 if e[5] else e[3] for e in EP], [0.5 * e[3] for e in EP], 1)[0]), 3), "while code regresses on the last run-hour |premium|")
m = re.search(r"ex-post bound .*?: n (\d+) gross ([\-\d.]+) funding ([\-\d.]+) net ([\-\d.]+)", out)
ec = np.mean([0.5 * e[3] for e in EP]); en = np.mean([0.5 * e[3] - cost_of(e[0]) for e in EP])
check("C5 Test 3 ex-post bound: gross = 0.5*mean|p|, funding 0, net = gross - cost", m and int(m[1]) == len(EP) and abs(float(m[2]) - ec) < 0.06 and abs(float(m[4]) - en) < 0.06, f"expected n {len(EP)} gross {ec:.1f} net {en:.1f}; actual {m.groups() if m else None}")
haz = {}
for l in out.splitlines():
    mm = re.match(r"^(\d+) (\d+) ([\d.]+)$", l)
    if mm: haz[int(mm[1])] = (int(mm[2]), float(mm[3]))
bad = []
for n in haz:
    risk = [e for e in EP if e[2] >= n]; exp_h = round(sum(1 for e in risk if e[2] == n and not e[5]) / len(risk), 3)
    if len(risk) != haz[n][0] or abs(exp_h - haz[n][1]) > 1e-9: bad.append((n, len(risk), exp_h, haz[n]))
check("C5 Test 3(b) hazard table matches reference", haz and not bad, f"rows {len(haz)}, mismatches {bad[:3]}")
check("C5 Test 3(d) logistic regression ran and printed AUC", "AUC out-of-sample" in out, [l for l in out.splitlines() if l.startswith("logistic")][:1])
# ============ EVAL1 (case 4)
print("\n#### CASE 4: eval1.py on synthetic 5 s logs")
def book(mid, hs_bp, deep=False):
    a1 = mid * (1 + hs_bp / 1e4); b1 = mid * (1 - hs_bp / 1e4)
    if deep:
        a2 = a1 * (1 + 5e-4); b2 = b1 * (1 - 5e-4)
        return {"bids": [[repr(b1), repr(400 / b1)], [repr(b2), repr(1e6 / b2)]], "asks": [[repr(a1), repr(400 / a1)], [repr(a2), repr(1e6 / a2)]]}
    return {"bids": [[repr(b1), repr(5000 / b1)]], "asks": [[repr(a1), repr(5000 / a1)]]}
def vw(levels):
    need = 1000.0; c = 0; q = 0
    for px, sz in levels:
        px = float(px); sz = float(sz); t = min(px * sz, need); c += t; q += t / px; need -= t
        if need <= 1e-9: break
    return c / q
def mk_log(name, build):
    """build() -> list of (t, {sym: (index, mid, hs_bp, deep)}) """
    d = f"{V}/log_{name}"; os.makedirs(d, exist_ok=True)
    with gzip.open(d + "/pmhl5s_x.jsonl.gz", "wt") as f:
        for t, snap in build():
            f.write(json.dumps(dict(t=t, pm=[[s, str(v[0]), str(v[0]), str(v[1]), str(v[1])] for s, v in snap.items()], books={s: book(v[1], v[2], v[3]) for s, v in snap.items()}, hl={})) + "\n")
    return d
def day_ts(day, hh, mm): return datetime.datetime(2026, 11, 2 + day, hh, mm, tzinfo=datetime.timezone.utc).timestamp()
def ev1(d, fund=None):
    args = [sys.executable, f"{NEW}/eval1.py", d, "--after", "0"]
    args += ["--funding", fund or os.path.join(V, "fund_empty.json")]
    r = subprocess.run(args, capture_output=True, text=True, cwd=V)
    if r.returncode: print("CRASH eval1", r.stderr[-600:]); check("eval1 runs", False, "crashed")
    return r.stdout
def gap_path(g0=40, sg=1): return [0, sg * g0, sg * g0, sg * g0 / 2, sg * 3, sg * 2] + [0] * 18   # signal, entry, ., trigger(|g|<5), exit-fill
def planted(name, sym_defs, days=3, start_min=15, funding_cross=False):
    """sym_defs: {sym: dict(sg=+1/-1, hs=bp, deep=bool)}; every day 1 h block of 5 s samples with a gap event every 24 samples."""
    def build():
        for day in range(days):
            base = day_ts(day, 10, start_min)
            for k in range(720):
                snap = {}
                for s, df in sym_defs.items():
                    pat = gap_path(40, df["sg"]); pos = k % 24; g = pat[pos] if pos < len(pat) else 0
                    if df.get("noise_only"): g = random.Random(day * 1000 + k).uniform(-2, 2)
                    snap[s] = (100.0, 100.0 * (1 + g / 1e4), df["hs"], df.get("deep", False))
                yield base + 5 * k, snap
    return mk_log(name, build)
def exp_event(sg, hs, deep):
    pos = -sg; mid_in = 100.0 * (1 + sg * 40 / 1e4); mid_out = 100.0 * (1 + sg * 2 / 1e4)
    b_in = book(mid_in, hs, deep); b_out = book(mid_out, hs, deep)
    ep = vw(b_in["bids"] if pos < 0 else b_in["asks"]); ex = vw(b_out["asks"] if pos < 0 else b_out["bids"])
    return pos * (ex / ep - 1) * 1e4
# 4a planted gap reverting in book (two symbols: short side w/ deep book, long side), no funding crossing
sd = {"AAA-USD": dict(sg=1, hs=2.0, deep=True), "BBB-USD": dict(sg=-1, hs=2.0, deep=False)}
d = planted("4a", sd); fp = f"{V}/fund_empty.json"; json.dump({k: [[day_ts(dd, hh, 0), 0.0] for dd in range(3) for hh in range(24)] for k in sd}, open(fp, "w")); out = ev1(d, fp)   # zero-rate settlements for every hour: missing rates would (correctly) force PRELIMINARY; print(out)
mm = re.search(r"events (\d+) missed .*? no usable book (\d+)", out)
exg = {s: exp_event(v["sg"], v["hs"], v["deep"]) for s, v in sd.items()}
per = {m_[1]: (int(m_[2]), float(m_[3])) for m_ in re.finditer(r"^\s+(\S+) (\d+) net (\S+)$", out, re.M)}
check("C4a planted gap: per-symbol net == gross_expected - 8 (VWAP walked through 2 levels for AAA)", all(s in per and per[s][0] == 90 and abs(per[s][1] - (exg[s] - 8)) < 0.06 for s in sd), f"expected net {{{', '.join(f'{s}: {exg[s]-8:.2f}' for s in sd)}}} (gross {{{', '.join(f'{s}: {exg[s]:.2f}' for s in sd)}}}), 90 events each; actual {per}")
check("C4a verdict PASS (n>=30, 3 days, CI>0, beats placebo)", "VERDICT: PASS" in out, [l for l in out.splitlines() if l.startswith(("VERDICT", "placebo", "gross mean"))])
# 4b no edge
def build_noedge():
    r = random.Random(7); mid = 100.0
    for day in range(3):
        base = day_ts(day, 10, 15)
        for k in range(8000 // 3):
            mid *= 1 + r.gauss(0, 1) / 1e4; g = r.gauss(0, 12); idx = mid / (1 + g / 1e4)
            yield base + 5 * k, {"NOE-USD": (idx, mid, 2.0, False)}
d = mk_log("4b", build_noedge); out = ev1(d, fp); print(out[:900])
m = re.search(r"events (\d+) .*\ngross mean ([\-\d.]+) median [\-\d.]+ net mean ([\-\d.]+)", out)
check("C4b no edge: gross ~ -4 bp (round-trip crossing 2x2 bp half-spread, zero drift), net ~ -12, verdict not PASS", m and abs(float(m[2]) + 4) < 1.0 and abs(float(m[3]) + 12) < 1.0 and "VERDICT: PASS" not in out, f"events {m[1] if m else None}, gross {m[2] if m else None}, net {m[3] if m else None}; expected about -4 / -12")
# 4c funding crossing top of hour
def build_fund():
    for day in range(3):
        base = day_ts(day, 10, 59) - 5 * 3 + 60   # shift so that entry sample (k0+1) is 5 s before 11:00: choose base 10:59:50 - 5*1
        base = day_ts(day, 10, 0) + 3600 - 380   # event block k0=72: signal sample k0+1, entry sample k0+2 at 11:00-10s, exit fill sample k0+5 at 11:00+5s
        for k in range(720):
            snap = {}
            for s, sgn in (("FP-USD", 1), ("FN-USD", -1)):
                pat = gap_path(40, sgn); pos = k % 24; g = pat[pos] if pos < len(pat) else 0
                snap[s] = (100.0, 100.0 * (1 + g / 1e4), 2.0, False)
            yield base + 5 * k, snap
d = mk_log("4c", build_fund)
RATEPM = 0.003; fdict = {s: [[day_ts(day, 10, 0) + 3600 * h, RATEPM] for day in range(3) for h in range(0, 3)] for s in ("FP-USD", "FN-USD")}
fund_file = f"{V}/fund_pm.json"; json.dump(fdict, open(fund_file, "w")); out = ev1(d, fund_file); print(out)
per = {m_[1]: (int(m_[2]), float(m_[3])) for m_ in re.finditer(r"^\s+(\S+) (\d+) net (\S+)$", out, re.M)}
# which events cross the boundary? determine by reconstruction; others cross nothing. Compute expected by simulating timing independently
def cross_expect(sgn):
    nets = []
    for day in range(3):
        base = day_ts(day, 10, 0) + 3600 - 380
        for blk in range(720 // 24):
            k0 = blk * 24; t_entry = base + 5 * (k0 + 2); t_exit = base + 5 * (k0 + 5)
            nb = (int(t_entry // 3600) + 1) * 3600; crosses = t_entry < nb <= t_exit
            pos = -sgn; fpaid = pos * RATEPM * 1e4 if crosses else 0.0
            nets.append((exp_event(sgn, 2.0, False) - 8 - fpaid, crosses))
    return nets
for s, sgn in (("FP-USD", 1), ("FN-USD", -1)):
    ne = cross_expect(sgn); mean = np.mean([x[0] for x in ne]); nx = sum(x[1] for x in ne)
    check(f"C4c {s} (short position, positive rate => position RECEIVES) net = gross - 8 - funding paid" if sgn == 1 else f"C4c {s} (long position, positive rate => position PAYS) net = gross - 8 - funding paid", s in per and per[s][0] == 90 and abs(per[s][1] - mean) < 0.06, f"90 events, {nx} cross a top of hour; expected mean net {mean:.2f}; actual {per.get(s)}; funding crossing sign check: pos={-sgn}, paid={-sgn*RATEPM*1e4:+.1f} bp each crossing")
m = re.search(r"funding settlements without a rate: (\d+)", out); check("C4c no funding settlement missing a rate", m and int(m[1]) == 0, m.group(0) if m else out[:200])
# 4d timeout 300 s and missed
def build_to():
    for day in range(3):
        base = day_ts(day, 10, 15)
        for k in range(720):
            pos = k % 240; g = 40 if 3 <= pos <= 200 else 0
            snap = {"TO-USD": (100.0, 100.0 * (1 + g / 1e4), 2.0, False)}
            gm = 30 if k % 24 == 3 else (10 if k % 24 == 4 else 0)
            snap["MS-USD"] = (100.0, 100.0 * (1 + gm / 1e4), 2.0, False)
            yield base + 5 * k, snap
d = mk_log("4d", build_to); out = ev1(d, fp); print(out[:700])
m = re.search(r"events (\d+) missed \(gap gone at entry\) (\d+)", out); h_ = re.search(r"median hold s ([\d.]+)", out)
check("C4d 300 s cap: median hold = 305 s (entry sample -> exit fill one sample after the 300 s trigger; 3 of 4 trades per gap time out); missed trades counted (3 days x 30 = 90)", m and int(m[2]) == 90 and h_ and abs(float(h_[1]) - 305) < 1e-9, f"expected missed 90, hold 305; actual {m.groups() if m else None}, hold {h_[1] if h_ else None}")
# 5 placebo same symbol / same session: A events in session1 (hs 2); A in session2 (hs 20, no events); B in session1 (hs 20, no events)
def build_pl():
    r = random.Random(3)
    for day in range(3):
        for sessname, hh, hsA in (("s1", 10, 2.0), ("s2", 14, 20.0)):   # 10:xx = other, 14:xx = US session
            base = day_ts(day, hh, 15)
            for k in range(720):
                pat = gap_path(40, 1); pos = k % 24; g = pat[pos] if (sessname == "s1" and pos < len(pat)) else r.uniform(-2, 2)
                snap = {"PLA-USD": (100.0, 100.0 * (1 + g / 1e4), hsA, False)}
                if sessname == "s1": snap["PLB-USD"] = (100.0, 100.0 * (1 + r.uniform(-2, 2) / 1e4), 20.0, False)
                yield base + 5 * k, snap
d = mk_log("pl", build_pl); out = ev1(d, fp); print(out[:700])
m = re.search(r"placebo n (\d+) mean net ([\-\d.]+)", out)
check("C5 placebo drawn from same symbol AND same session: mean net ~ -8 - 2*2 = -12 (drawn from PLB (hs20) or the s2 session would give ~ -48 / -52)", m and abs(float(m[2]) + 12) < 1.2, f"placebo n {m[1] if m else None} mean {m[2] if m else None}; expected -12.0 +/- random-direction drift")
# metric 5 sample_an
def mk_sample():
    p = f"{V}/sample.jsonl.gz"; rows = []
    for k in range(360):
        t = 1.7e9 // 3600 * 3600 + 5 * k
        g1 = 0 if k < 20 else (30 if k < 32 else (2 if k >= 32 else 0))    # exceeds 25 at k=20, falls below 5 at k=32 -> 60 s
        rows.append(dict(t=t, v="hl", d="xyz", s="REV", mark=100 * (1 + 0.0004), oracle=100.0, mid=100 * (1 + g1 / 1e4)))
        rows.append(dict(t=t, v="hl", d="xyz", s="STUCK", mark=100.0, oracle=100.0, mid=100 * (1 + (40 if k >= 50 else 0) / 1e4)))
        rows.append(dict(t=t, v="pm", s="CALM", mark=100.0, oracle=100.0, mid=100 * (1 + 10 / 1e4)))
    with gzip.open(p, "wt") as f:
        for r in rows: f.write(json.dumps(r) + "\n")
    return p
p = mk_sample(); r = subprocess.run([sys.executable, f"{NEW}/sample_an.py", p], capture_output=True, text=True, cwd=V); print(r.stdout[-900:], r.stderr[-300:])
R5 = json.load(open(f"{V}/sample_result.json")); rv = [v for k, v in R5.items() if "/REV/" in k][0]; st = [v for k, v in R5.items() if "/STUCK/" in k][0]; ca = [v for k, v in R5.items() if "/CALM/" in k][0]
check("Metric5 sample_an: REV exceed then revert in 60 s, max_mid 30, max_mark 4; STUCK exceeds never reverts; CALM no exceedance", rv["secs_to_revert"] == 60 and abs(rv["max_mid"] - 30) < 1e-6 and abs(rv["max_mark"] - 4) < 1e-6 and st["reverted"] is False and not ca["exceeded"], f"REV {rv}, STUCK {st['max_mid']:.1f}/{st['reverted']}, CALM exceeded {ca['exceeded']}")
print("\n#### SUMMARY"); print(sum(1 for _, o in RES if o), "PASS,", sum(1 for _, o in RES if not o), "FAIL")
for n, o in RES:
    if not o: print("FAIL:", n)
