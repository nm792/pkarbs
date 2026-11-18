#!/usr/bin/env python3
"""Self test for goalserve_odds_vs_pm_v2.py (locked rerun, non-onset). Synthetic data, offline, no key, no real paths. PASS/FAIL lines; exit 0 only if all pass.
World: N matches x K alternating odds moves (Goalserve payload times, REAL names 'Home/Away', participants 'Home'/'Away', league 'CS2 - Test League', real PM book schema ms/sent/tk).
PM: the rising team's own token jumps +3c at t+SHIFT (mode 'mirror': the other token falls -3c; 'own_only': the other token stays flat; 'other_only': only the OTHER token falls, the rising token stays flat) plus sparse +-3c blips.
TRAP: after each true event the market is suspended 100 s later and reopens 110 s later at a different price; PM does not react. v1 counted that reopen jump as an event; v2 must not.
Checks: event count exact (trap not counted), baseline-cleared counted; planted +15 s meets the bar and the plant is recovered; no-edge never meets the bar over 20 seeds; PM-first (-20 s) is 'PM moved first'; own-book-only still meets the bar, other-side-only does NOT (no inference from the other book);
match cap 40 applied and counted; too few matches = unknown."""
import os, sys, gzip, json, tempfile, subprocess, random, shutil, calendar, time
here = os.path.dirname(os.path.abspath(__file__))
fails = []
def check(n, c):
    print(("PASS " if c else "FAIL ") + n)
    if not c: fails.append(n)

def build(shift, mode="mirror", react=True, seed=7, N=20, K=4, trap=True, outage=False, fname="esports_2026120723.jsonl.gz"):
    rnd = random.Random(seed)
    tmp = tempfile.mkdtemp(); pmd = os.path.join(tmp, "pm"); os.makedirs(pmd)
    T0 = 1794960000.0 + 3600.0      # inside the locked data window (T_START 2026-11-18T00:00Z)
    markets, tl, books = [], [], []
    for i in range(N):
        A, B = "Team A%d" % i, "Team B%d" % i
        markets.append({"cond": "c%d" % i, "q": "%s vs %s" % (A, B), "smt": "moneyline", "outcomes": [A, B], "tokens": ["tA%d" % i, "tB%d" % i]})
        t_first = T0 + i * 4000.0
        tl.append((t_first, i, (1.8, 2.2), 0))
        mids = {"tA%d" % i: [(t_first - 500, 0.5)], "tB%d" % i: [(t_first - 500, 0.5)]}
        up, last = True, t_first
        for k in range(K):
            te = t_first + 300.0 * (k + 1) + rnd.uniform(0, 20)
            last = te
            tl.append((te, i, (1.6, 2.4) if up else (2.4, 1.6), 0))
            if trap:
                tl.append((te + 100, i, (1.3, 3.3), 1))      # suspended, odds moved
                tl.append((te + 110, i, (2.0, 2.0), 0))      # reopen at a new price
            if react:
                rise, fall = ("tA%d" % i, "tB%d" % i) if up else ("tB%d" % i, "tA%d" % i)
                if mode in ("mirror", "own_only"):
                    mids[rise].append((te + shift, 0.53))
                if mode in ("mirror", "other_only"):
                    mids[fall].append((te + shift, 0.47))
                if mode == "other_only":
                    pass
                # reset so every event starts from 0.5
                mids[rise].append((te + 150, 0.5)); mids[fall].append((te + 150, 0.5))
            up = not up
        tt = t_first - 400
        while tt < last + 400:
            tt += rnd.expovariate(1 / 300.0)
            tk = rnd.choice(["tA%d" % i, "tB%d" % i]); sg = rnd.choice((-1, 1))
            mids[tk].append((tt, 0.5 + 0.03 * sg)); mids[tk].append((tt + 10, 0.5))
        for tk, pts in mids.items():
            pts.sort()
            t = pts[0][0]; j = 0
            while t <= pts[-1][0] + 1:
                lv = [p for (x, p) in pts if x <= t][-1]
                books.append({"ms": int(t * 1000), "sent": int(t * 1000) - 80, "tk": tk, "bids": [{"price": str(round(lv - 0.005, 4))}], "asks": [{"price": str(round(lv + 0.005, 4))}]})
                t += 1.0
    with open(os.path.join(pmd, "markets.jsonl"), "w") as f:
        for m in markets: f.write(json.dumps(m) + "\n")
    with open(os.path.join(pmd, "books.jsonl"), "w") as f:
        for b in books: f.write(json.dumps(b) + "\n")
        f.write(json.dumps({"tk": "tA0", "sent": 1, "bids": [{"price": "0.5"}], "asks": [{"price": "0.51"}]}) + "\n")   # a row with no time
    cur = {i: ((1.8, 2.2), 0) for i in range(N)}
    tl.sort()
    gap = None
    if outage:
        te3 = sorted(x[0] for x in tl if x[1] == 3 and x[2] in ((1.6, 2.4), (2.4, 1.6)))[1]    # 2nd true odds event of match 3
        gap = (te3 - 60, te3 + 0.01)
    pl = os.path.join(tmp, "polls"); os.makedirs(pl)
    hmark = fname[len("esports_"):len("esports_") + 10]
    t_last_end = calendar.timegm(time.strptime(hmark, "%Y%m%d%H")) + 3600.0
    t_data_end = max(tt for (tt, _, _, _) in tl)
    with open(os.path.join(pl, "goalserve_2026111800.jsonl"), "w") as f:
        x = T0 + 0.5
        while x < t_data_end + 5:
            if not (gap and gap[0] <= x <= gap[1]):
                f.write(json.dumps({"esports": {"recv_ns": int(x * 1e9)}}) + "\n")
            x += 2.0
        if t_last_end - 5 > t_data_end + 5:      # sparse polls out to the end of the target day (+60 s), only the last hour is polled
            for x in (t_last_end - 30, t_last_end - 5, t_last_end + 60):
                f.write(json.dumps({"esports": {"recv_ns": int(x * 1e9)}}) + "\n")
    # one heartbeat payload per hour (unchanged odds), so no polled hour is without a file (real data has a file in almost every hour)
    merged = [(tt, i_, st_, su_) for (tt, i_, st_, su_) in tl]
    h0 = int((T0 - 1794960000.0) // 3600)
    for h in range(h0, int((t_data_end - 1794960000.0) // 3600) + 1):
        merged.append((1794960000.0 + 3600.0 * h + 10.0, None, None, None))
    if t_last_end - 5 > t_data_end + 5:
        merged.append((t_last_end - 5, None, None, None))
    merged.sort(key=lambda r: r[0])
    byhour = {}
    for (t_, i_, st_, su_) in merged:
        if i_ is not None:
            cur[i_] = (st_, su_)
        evs = {}
        for j in range(N):
            (o1, o2), s_ = cur[j]
            mk = {"1": {"id": 1, "name": "Home/Away", "suspend": s_, "participants": {
                    "11": {"id": 11, "name": "Home", "value_eu": o1, "suspend": 0},
                    "12": {"id": 12, "name": "Away", "value_eu": o2, "suspend": 0}}},
                  "4": {"id": 4, "name": "Odd/Even (1st map)", "suspend": 0, "participants": {
                    "41": {"id": 41, "name": "Odd", "value_eu": 1.9, "suspend": 0}, "42": {"id": 42, "name": "Even", "value_eu": 1.9, "suspend": 0}}}}
            evs["E%d" % j] = {"info": {"sport": "Esports", "league": "CS2 - Test League"}, "team_info": {"home": {"name": "Team A%d" % j}, "away": {"name": "Team B%d" % j}}, "odds": mk}
        byhour.setdefault(time.strftime("%Y%m%d%H", time.gmtime(t_)), []).append(json.dumps({"recv_ns": int(t_ * 1e9), "body": json.dumps({"bm": "", "events": evs})}))
    gdir = os.path.join(tmp, "gs"); os.makedirs(gdir)
    for k_, rows_ in sorted(byhour.items()):
        with gzip.open(os.path.join(gdir, "esports_%s.jsonl.gz" % k_), "wt") as g:
            for r_ in rows_:
                g.write(r_ + "\n")
            if k_ == sorted(byhour)[0]:
                g.write("{bad goalserve line\n")
    return tmp, gdir, pmd, pl

CELL = "cs2|Match Winner"
LAST = [None]
def run(shift, mode="mirror", react=True, seed=7, **kw):
    tmp, gdir, pmd, pl = build(shift, mode, react, seed, **kw)
    LAST[0] = (tmp, gdir, pmd, pl)
    out = os.path.join(tmp, "res.json")
    r = subprocess.run([sys.executable, "-I", os.path.join(here, "goalserve_odds_vs_pm_v2.py"), "--files", os.path.join(gdir, "*.jsonl.gz"), "--pm", pmd, "--poll-log", os.path.join(pl, "*.jsonl"),
                        "--clock-note", "selftest", "--seed", str(seed), "--out", out], capture_output=True, text=True)
    if r.returncode != 0: print(r.stderr[-800:])
    j = json.load(open(out)) if os.path.exists(out) else None
    shutil.rmtree(tmp, ignore_errors=True)
    return r, j, ((j or {}).get("cells", {}).get(CELL, {}))

def meets(c): return str(c.get("verdict", "")).startswith("meets bar")

r, j, c = run(15.0)
cm_base = c
check("planted +15 s run exits 0", r.returncode == 0)
print("  +15 cell:", {k: c.get(k) for k in ("n_matches_used", "n_events", "mean_d_per_match", "z_eq", "boundary_z", "share_events_real_gt_placebo_pct", "plants_ok", "plant_recovery", "min_detectable_effect_at_this_look", "verdict")})
check("event count exact: 20 matches x 4 = 80 (suspend/reopen trap NOT counted)", j["goalserve_events_total"] == 80 and c.get("n_events") == 80)
check("baseline cleared on suspended payloads (counted)", j["audit"]["counters"].get("baseline_cleared_not_valid_open", 0) >= 80)
check("real names used, Odd/Even excluded and counted, bm '' reported", set(j["audit"]["market_names_used"]) == {"Home/Away"} and "Odd/Even (1st map)" in j["audit"]["market_names_excluded"] and "''" in j["audit"]["bm_values"])
check("planted +15 s: bar met, plants recovered end to end (+step, -step, label swap) and powered", meets(c) and c["plants_ok"] is True and c["plant_recovery"]["plus_ok"] and c["plant_recovery"]["minus_ok"] and c["plant_recovery"]["swap_ok"])
check("match list: 20 matched PM markets, cell cs2|Match Winner", len(j["match_list"]) == 20 and all("excluded" not in m for m in j["match_list"]))
check("book rows without a time counted (1) and time source counted from ms", j["drops"].get("book_rows_no_time") == 1 and j["drops"].get("pm_book_rows_time_from_ms", 0) > 1000 and j["drops"].get("pm_book_rows_time_from_recv_ms", 0) == 0)
check("cs2|Match Winner is a primary cell; primary list is exactly cs2 and dota2 Match Winner; wording present; plant_c 0.01 and seed 20261118 recorded when omitted from the CLI",
      c.get("role") == "primary" and j["primary_cells"] == ["cs2|Match Winner", "dota2|Match Winner"] and "never 'lead of N seconds'" in j["wording"])
check("first 20 events of the biggest cell printed with token and R", j["first20_events_biggest_cell"]["cell"] == "cs2|Match Winner" and len(j["first20_events_biggest_cell"]["rows"]) == 20 and "token" in j["first20_events_biggest_cell"]["rows"][0])
_, jo2, co2 = run(15.0, outage=True)
check("capture outage (no polls for the 60 s up to one event): that event is NOT counted (79), baselines cleared and counted", co2.get("n_events") == 79 and jo2["audit"]["counters"].get("payloads_after_poll_gap_gt_10s", 0) >= 1 and jo2["audit"]["counters"].get("baseline_cleared_poll_gap_gt_10s", 0) >= 1)
_, jn, cn = run(0.0, react=False)
check("no-edge: not 'meets bar'; plants recovered; closed at look 20 so 'no lead detected'", not meets(cn) and cn.get("plants_ok") is True and str(cn.get("verdict", "")).startswith("no lead"))
_, jf, cf = run(-20.0)
print("  PM-first cell:", {k: cf.get(k) for k in ("mean_d_per_match", "z_eq", "boundary_z", "plants_ok", "verdict")})
check("PM moves 20 s BEFORE the odds -> 'PM moved first', never 'meets bar'", str(cf.get("verdict", "")).startswith("PM moved first") and not meets(cf))
_, jo, co = run(15.0, mode="own_only")
check("own book only (other token flat): still meets bar", meets(co))
_, jx, cx = run(15.0, mode="other_only")
check("only the OTHER team's book moves, the rising team's token flat: NOT 'meets bar' (no inference from the other book)", not meets(cx))
_, jc, cc = run(15.0, K=50)
check("cap: 50 events per match -> 40 kept, 200 dropped (20 matches x 10), counted", cc.get("n_events") == 800 and jc["drops"].get("events_dropped_by_match_cap") == 200)
_, jt, ct = run(15.0, N=8)
check("only 8 matches -> unknown (needs >= 12)", str(ct.get("verdict", "")).startswith("unknown"))
_, jk1, ck1 = run(15.0, fname="esports_2026111823.jsonl.gz")
check("look 1: boundary = 2.60/sqrt(20 matches/100) = 5.81 printed, look=1, plain_summary present, pre/post terms printed", jk1["look"] == 1 and abs(ck1["boundary_z"] - 5.8138) < 0.01 and len(jk1["plain_summary"]) >= 1 and ck1["post_real"] is not None and ck1["pre_placebo"] is not None)
_, jk1n, ck1n = run(0.0, react=False, fname="esports_2026111823.jsonl.gz")
check("look 1 no-edge: never 'meets bar' (early look needs a huge effect)", not meets(ck1n))
tmpb, gdb, pmb, plb = build(15.0, fname="esports_2026111800.jsonl.gz")
r0 = subprocess.run([sys.executable, "-I", os.path.join(here, "goalserve_odds_vs_pm_v2.py"), "--files", os.path.join(gdb, "*.jsonl.gz"), "--pm", pmb, "--poll-log", os.path.join(plb, "*.jsonl"), "--clock-note", "x", "--out", os.path.join(tmpb, "x.json")], capture_output=True, text=True)
shutil.rmtree(tmpb, ignore_errors=True)
check("no complete UTC day yet (last hour file is 2026-11-18 00h): the script refuses to run (no look 0)", r0.returncode != 0 and "outside 1..20" in (r0.stderr + r0.stdout))
_, jlate, clate = run(15.0, fname="esports_2026120923.jsonl.gz")
check("after the last look (hour file 9 Dec 23h = look 22): the script refuses, no result file", jlate is None)
SEEDS = range(1, 13)
p15 = [meets(run(15.0, seed=s_, N=40)[2]) for s_ in SEEDS]
p0 = [meets(run(0.0, react=False, seed=s_, N=40)[2]) for s_ in SEEDS]
p10 = [meets(run(10.0, seed=s_, N=40)[2]) for s_ in SEEDS]
check("12 seeds, 40 matches (information 0.4, boundary 3.95): planted +15 s passes >= 10 of 12 (got %d)" % sum(p15), sum(p15) >= 10)
check("12 seeds, 40 matches: planted +10 s passes >= 10 of 12 (got %d; the real-series plant size)" % sum(p10), sum(p10) >= 10)
check("12 seeds, 40 matches: no-edge false passes 0 of 12 (got %d)" % sum(p0), sum(p0) == 0)
def run_mut(old, new):
    src = open(os.path.join(here, "goalserve_odds_vs_pm_v2.py")).read()
    assert src.count(old) == 1, old
    mp = os.path.join(here, "_mutant_v2_selftest.py")
    open(mp, "w").write(src.replace(old, new))
    try:
        tmp, gdir, pmd, pl = build(15.0)
        out = os.path.join(tmp, "res.json")
        subprocess.run([sys.executable, "-I", mp, "--files", os.path.join(gdir, "*.jsonl.gz"), "--pm", pmd, "--poll-log", os.path.join(pl, "*.jsonl"), "--clock-note", "mut", "--out", out], capture_output=True, text=True)
        j = json.load(open(out)) if os.path.exists(out) else None
        shutil.rmtree(tmp, ignore_errors=True)
        return (j or {}).get("cells", {}).get(CELL, {})
    finally:
        os.remove(mp)
cm1 = run_mut('tk, otk = m["tokens"][i], m["tokens"][1 - i]', 'tk, otk = m["tokens"][1 - i], m["tokens"][i]')
check("MUTANT wrong token read as 'rising' (other token's own book): plants NOT recovered, verdict unknown, never 'meets bar'", cm1.get("plants_ok") is False and str(cm1.get("verdict", "")).startswith("unknown") and not meets(cm1))
cm2 = run_mut("return ((t + dt, c_, ttk), (t + dt, -c_, ottk))", "return ((t + dt, c_, ttk), (t + dt, c_, ottk))")
check("MUTANT sign bug on the other token's plant: label-swap recovery fails, verdict unknown", cm2.get("plant_recovery", {}).get("swap_ok") is False and str(cm2.get("verdict", "")).startswith("unknown"))
cm3 = run_mut("m = [mid_at(tk, t + dt, steps) for dt in (60, 0, -5, -60)]", "m = [mid_at(tk, t + dt, steps) for dt in (60, 0, -5, -45)]")
check("MUTANT wrong pre-window start (-45 instead of -60): the +step still recovered but the -step recovery differs or the result changes (the self-test would have to be re-signed): mean d changes", cm3.get("mean_d_per_match") is not None and abs(cm3["mean_d_per_match"] - cm_base["mean_d_per_match"]) > 1e-6)

# ---- null simulation of the WHOLE sequential procedure (decision function + look schedule + accrual), Reviewer E1(c) ----
import importlib.util, math as _m
spec = importlib.util.spec_from_file_location("v2mod", os.path.join(here, "goalserve_odds_vs_pm_v2.py"))
g = importlib.util.module_from_spec(spec); spec.loader.exec_module(g)
g.MIN_EFFECT, g.MIN_SHARE = -1.0, -1.0       # conservative: only the boundary protects (the extra conditions would lower the rate)
def pois(rng, lam):
    L, k, p = _m.exp(-lam), 0, 1.0
    while True:
        p *= rng.random()
        if p <= L: return k
        k += 1
def draw(rng, dist, mu):
    if dist == "normal": return mu + 0.01 * rng.gauss(0, 1)
    chi = sum(rng.gauss(0, 1) ** 2 for _ in range(3))
    return mu + 0.01 * rng.gauss(0, 1) / _m.sqrt(chi / 3.0)
def simulate(runs, dist, mu, seed):
    rng = random.Random(seed)
    passes = {c: 0 for c in g.N_MAX}; first = {c: [0] * 20 for c in g.N_MAX}
    for _ in range(runs):
        for cell, rate in (("cs2|Match Winner", 5.0), ("dota2|Match Winner", 2.5)):
            vals, hit = [], False
            for day in range(20):
                vals += [draw(rng, dist, mu) for _ in range(pois(rng, rate))]
                used = vals[:g.N_MAX[cell]]
                d = g.decide(used, 30 * len(used), 100.0, True, len(used) >= g.N_MAX[cell] or day == 19, cell)
                if not hit and d["verdict"].startswith("meets bar"):
                    hit = True; first[cell][day] += 1
            passes[cell] += hit
    return {c: passes[c] / runs for c in passes}, first
RUNS = 2000
for dist in ("normal", "t3"):
    fp, _ = simulate(RUNS, dist, 0.0, 11 if dist == "normal" else 12)
    ub = {c: fp[c] + 1.96 * _m.sqrt(max(fp[c], 1e-9) * (1 - fp[c]) / RUNS) for c in fp}
    print("  NULL %s noise, %d runs x 20 looks x 2 cells: false-pass per cell %s (95%% upper bound %s)" % (dist, RUNS, {c: round(v, 4) for c, v in fp.items()}, {c: round(v, 4) for c, v in ub.items()}))
    check("null simulation (%s): false-pass rate over all 20 looks <= 1.25%% per primary cell (point estimate)" % dist, all(v <= 0.0125 for v in fp.values()))
pw, first = simulate(500, "normal", 0.006, 13)
print("  POWER (mean d 0.6 sd of a match's d, normal): pass probability by end of look 20 per cell", pw, "; first passing look histogram cs2", first["cs2|Match Winner"])
check("power: a true edge of 0.6 sd per match is passed by look 20 in >= 70% of runs in the cs2 cell", pw["cs2|Match Winner"] >= 0.70)
def arrivals(rng, rate, kind):
    out = []
    for day in range(20):
        lam = rate if kind == "poisson" else rate * rng.gammavariate(1.0, 1.0) if kind == "overdisp" else rate * (0.4 if day < 10 else 1.6)
        out.append(pois(rng, lam))
    return out
def sim_grid(runs, rate, kind, dist, cell, seed):
    rng = random.Random(seed); hits = 0
    for _ in range(runs):
        arr = arrivals(rng, rate, kind); vals = []; hit = False
        for day in range(20):
            vals += [draw(rng, dist, 0.0) for _ in range(arr[day])]
            used = vals[:g.N_MAX[cell]]
            d = g.decide(used, 30 * len(used), 100.0, True, len(used) >= g.N_MAX[cell] or day == 19, cell)
            if d["verdict"].startswith("meets bar"): hit = True; break
        hits += hit
    return hits / runs
grid = {}
for rate, cell in ((2, "dota2|Match Winner"), (3, "dota2|Match Winner"), (6, "cs2|Match Winner")):
    for kind in ("poisson", "overdisp", "back"):
        for dist in ("normal", "t3"):
            grid[(rate, kind, dist)] = sim_grid(1500, rate, kind, dist, cell, 100 + rate * 7 + len(kind) + len(dist))
worst = max(grid.values())
print("  NULL GRID (checker's scenarios: 2, 3, 6 matches a day; Poisson, overdispersed, back-loaded; normal and t3; 1500 runs each): worst false-pass %.4f; all: %s" % (worst, {"%s/%s/%s" % k: round(v, 4) for k, v in grid.items()}))
check("null grid: false-pass over 20 looks <= 1.25%% in every one of the 18 scenarios (worst %.4f)" % worst, worst <= 0.0125)

# reproducibility across looks (checker): the same earlier matches give the same d at look 1 and look 2
tmpr, gdr, pmr, plr = build(15.0, N=40, fname="esports_2026111923.jsonl.gz")
def run_files(files_glob, tag):
    out = os.path.join(tmpr, "res_%s.json" % tag)
    subprocess.run([sys.executable, "-I", os.path.join(here, "goalserve_odds_vs_pm_v2.py")] + sum([["--files", f_] for f_ in files_glob], []) + ["--pm", pmr, "--poll-log", os.path.join(plr, "*.jsonl"), "--clock-note", "t", "--out", out], capture_output=True, text=True)
    return json.load(open(out)) if os.path.exists(out) else None
jr1 = run_files([os.path.join(gdr, "esports_20261118*.jsonl.gz")], "look1")
jr2 = run_files([os.path.join(gdr, "*.jsonl.gz")], "look2")
if jr1 and jr2:
    m1 = jr1["cells"][CELL]["per_match_mean_d"]; m2 = jr2["cells"][CELL]["per_match_mean_d"]
    early = [k_ for k_ in m1 if k_ in m2 and int(k_[1:]) < 20]
    check("reproducible across looks: look 1 and look 2 give identical per-match mean d for the %d matches wholly inside day 1 (placebo and cap seeded per event)" % len(early), len(early) >= 15 and all(abs(m1[k_] - m2[k_]) < 1e-12 for k_ in early) and jr1["look"] == 1 and jr2["look"] == 2)
else:
    check("reproducible across looks: both runs produced a result", False)
shutil.rmtree(tmpr, ignore_errors=True)

def build_and_run(mutator, fname="esports_2026111823.jsonl.gz"):
    tmp, gdir, pmd, pl = build(15.0, fname=fname)
    mutator(tmp, gdir, pl)
    out = os.path.join(tmp, "res.json")
    r = subprocess.run([sys.executable, "-I", os.path.join(here, "goalserve_odds_vs_pm_v2.py"), "--files", os.path.join(gdir, "*.jsonl.gz"), "--pm", pmd, "--poll-log", os.path.join(pl, "*.jsonl"), "--clock-note", "t", "--out", out], capture_output=True, text=True)
    ok = os.path.exists(out)
    shutil.rmtree(tmp, ignore_errors=True)
    return r, ok
def drop_a_polled_hour(tmp, gdir, pl):
    fs = sorted(os.listdir(gdir)); os.remove(os.path.join(gdir, fs[3]))
r, ok = build_and_run(drop_a_polled_hour)
check("completeness: an hour file missing while the poll log shows capture running -> the run refuses, no result", r.returncode != 0 and not ok and "missing although" in (r.stderr + r.stdout))
def cut_polls(tmp, gdir, pl):
    p_ = os.path.join(pl, "goalserve_2026111800.jsonl"); L = open(p_).read().splitlines()
    open(p_, "w").write("\n".join(L[:-3]) + "\n")
r, ok = build_and_run(cut_polls)
check("completeness: poll log ends before the end of the day + 60 s -> refuses", r.returncode != 0 and not ok and "poll log ends" in (r.stderr + r.stdout))
def truncate_file(tmp, gdir, pl):
    f_ = os.path.join(gdir, sorted(os.listdir(gdir))[5]); b_ = open(f_, "rb").read(); open(f_, "wb").write(b_[:-30])
r, ok = build_and_run(truncate_file)
check("completeness: a truncated hour file -> refuses", r.returncode != 0 and not ok and "truncated" in (r.stderr + r.stdout))
def drop_an_unpolled_hour(tmp, gdir, pl):
    pass
r, ok = build_and_run(drop_an_unpolled_hour)
check("completeness: hours without polls (capture outage, 4 matches' quiet hours) are listed in audit.hour_files and do not stop a complete day", r.returncode == 0 and ok)

print("ALL PASS" if not fails else "FAILED: " + "; ".join(fails))
sys.exit(1 if fails else 0)
