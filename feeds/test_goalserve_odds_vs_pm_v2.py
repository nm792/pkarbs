#!/usr/bin/env python3
"""Self test for goalserve_odds_vs_pm_v2.py (locked rerun, non-onset). Synthetic data, offline, no key, no real paths. PASS/FAIL lines; exit 0 only if all pass.
World: N matches x K alternating odds moves (Goalserve payload times, REAL names 'Home/Away', participants 'Home'/'Away', league 'CS2 - Test League', real PM book schema ms/sent/tk).
PM: the rising team's own token jumps +3c at t+SHIFT (mode 'mirror': the other token falls -3c; 'own_only': the other token stays flat; 'other_only': only the OTHER token falls, the rising token stays flat) plus sparse +-3c blips.
TRAP: after each true event the market is suspended 100 s later and reopens 110 s later at a different price; PM does not react. v1 counted that reopen jump as an event; v2 must not.
Checks: event count exact (trap not counted), baseline-cleared counted; planted +15 s meets the bar and the plant is recovered; no-edge never meets the bar over 20 seeds; PM-first (-20 s) is 'PM moved first'; own-book-only still meets the bar, other-side-only does NOT (no inference from the other book);
match cap 40 applied and counted; too few matches = unknown."""
import os, sys, gzip, json, tempfile, subprocess, random
here = os.path.dirname(os.path.abspath(__file__))
fails = []
def check(n, c):
    print(("PASS " if c else "FAIL ") + n)
    if not c: fails.append(n)

def build(shift, mode="mirror", react=True, seed=7, N=20, K=4, trap=True, outage=False):
    rnd = random.Random(seed)
    tmp = tempfile.mkdtemp(); pmd = os.path.join(tmp, "pm"); os.makedirs(pmd)
    T0 = 1_800_000_000.0
    markets, tl, books = [], [], []
    for i in range(N):
        A, B = "Team A%d" % i, "Team B%d" % i
        markets.append({"cond": "c%d" % i, "q": "%s vs %s" % (A, B), "smt": "moneyline", "outcomes": [A, B], "tokens": ["tA%d" % i, "tB%d" % i]})
        t_first = T0 + i * 5000.0
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
            tt += rnd.expovariate(1 / 150.0)
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
    with open(os.path.join(pl, "goalserve_2026111800.jsonl"), "w") as f:
        x = T0 - 100
        while x < max(tt for (tt, _, _, _) in tl) + 5:
            if not (gap and gap[0] <= x <= gap[1]):
                f.write(json.dumps({"esports": {"recv_ns": int(x * 1e9)}}) + "\n")
            x += 2.0
    gdir = os.path.join(tmp, "gs"); os.makedirs(gdir)
    with gzip.open(os.path.join(gdir, "esports_2026111800.jsonl.gz"), "wt") as g:
        for (t, i, st, sus) in tl:
            cur[i] = (st, sus)
            evs = {}
            for j in range(N):
                (o1, o2), s = cur[j]
                mk = {"1": {"id": 1, "name": "Home/Away", "suspend": s, "participants": {
                        "11": {"id": 11, "name": "Home", "value_eu": o1, "suspend": 0},
                        "12": {"id": 12, "name": "Away", "value_eu": o2, "suspend": 0}}},
                      "4": {"id": 4, "name": "Odd/Even (1st map)", "suspend": 0, "participants": {
                        "41": {"id": 41, "name": "Odd", "value_eu": 1.9, "suspend": 0}, "42": {"id": 42, "name": "Even", "value_eu": 1.9, "suspend": 0}}}}
                evs["E%d" % j] = {"info": {"sport": "Esports", "league": "CS2 - Test League"}, "team_info": {"home": {"name": "Team A%d" % j}, "away": {"name": "Team B%d" % j}}, "odds": mk}
            g.write(json.dumps({"recv_ns": int(t * 1e9), "body": json.dumps({"bm": "", "events": evs})}) + "\n")
    return tmp, gdir, pmd, pl

CELL = "cs2|Match Winner"
def run(shift, mode="mirror", react=True, seed=7, **kw):
    tmp, gdir, pmd, pl = build(shift, mode, react, seed, **kw)
    out = os.path.join(tmp, "res.json")
    r = subprocess.run([sys.executable, "-I", os.path.join(here, "goalserve_odds_vs_pm_v2.py"), "--files", os.path.join(gdir, "*.jsonl.gz"), "--pm", pmd, "--poll-log", os.path.join(pl, "*.jsonl"),
                        "--clock-note", "selftest", "--seed", str(seed), "--out", out], capture_output=True, text=True)
    if r.returncode != 0: print(r.stderr[-800:])
    j = json.load(open(out)) if os.path.exists(out) else None
    return r, j, ((j or {}).get("cells", {}).get(CELL, {}))

def meets(c): return str(c.get("verdict", "")).startswith("meets bar")

r, j, c = run(15.0)
check("planted +15 s run exits 0", r.returncode == 0)
print("  +15 cell:", {k: c.get(k) for k in ("n_matches", "n_events", "mean_d_per_match", "ci95_match_boot", "share_events_real_gt_placebo_pct", "plant_detected", "min_detectable_effect", "verdict")})
check("event count exact: 20 matches x 4 = 80 (suspend/reopen trap NOT counted)", j["goalserve_events_total"] == 80 and c.get("n_events") == 80)
check("baseline cleared on suspended payloads (counted)", j["audit"]["counters"].get("baseline_cleared_not_valid_open", 0) >= 80)
check("real names used, Odd/Even excluded and counted, bm '' reported", set(j["audit"]["market_names_used"]) == {"Home/Away"} and "Odd/Even (1st map)" in j["audit"]["market_names_excluded"] and "''" in j["audit"]["bm_values"])
check("planted +15 s: bar met and the 1c power check detected", meets(c) and c["plant_detected"] is True)
check("match list: 20 matched PM markets, cell cs2|Match Winner", len(j["match_list"]) == 20 and all("excluded" not in m for m in j["match_list"]))
check("book rows without a time counted (1) and time source counted from ms", j["drops"].get("book_rows_no_time") == 1 and j["drops"].get("pm_book_rows_time_from_ms", 0) > 1000 and j["drops"].get("pm_book_rows_time_from_recv_ms", 0) == 0)
check("cs2|Match Winner is a primary cell; primary list is exactly cs2 and dota2 Match Winner; wording present; plant_c 0.01 and seed 20261118 recorded when omitted from the CLI",
      c.get("role") == "primary" and j["primary_cells"] == ["cs2|Match Winner", "dota2|Match Winner"] and "never 'lead of N seconds'" in j["wording"])
check("first 20 events of the biggest cell printed with token and R", j["first20_events_biggest_cell"]["cell"] == "cs2|Match Winner" and len(j["first20_events_biggest_cell"]["rows"]) == 20 and "token" in j["first20_events_biggest_cell"]["rows"][0])
_, jo2, co2 = run(15.0, outage=True)
check("capture outage (no polls for the 60 s up to one event): that event is NOT counted (79), baselines cleared and counted", co2.get("n_events") == 79 and jo2["audit"]["counters"].get("payloads_after_poll_gap_gt_10s", 0) >= 1 and jo2["audit"]["counters"].get("baseline_cleared_poll_gap_gt_10s", 0) >= 1)
_, jn, cn = run(0.0, react=False)
check("no-edge: not 'meets bar'; 1c plant detectable on this noise (verdict 'no lead detected')", not meets(cn) and cn.get("plant_detected") is True and str(cn.get("verdict", "")).startswith("no lead"))
_, jf, cf = run(-20.0)
print("  PM-first cell:", {k: cf.get(k) for k in ("mean_d_per_match", "ci95_match_boot", "plant_detected", "verdict")})
check("PM moves 20 s BEFORE the odds -> 'PM moved first', never 'meets bar'", str(cf.get("verdict", "")).startswith("PM moved first") and not meets(cf))
_, jo, co = run(15.0, mode="own_only")
check("own book only (other token flat): still meets bar", meets(co))
_, jx, cx = run(15.0, mode="other_only")
check("only the OTHER team's book moves, the rising team's token flat: NOT 'meets bar' (no inference from the other book)", not meets(cx))
_, jc, cc = run(15.0, K=50)
check("cap: 50 events per match -> 40 kept, 200 dropped (20 matches x 10), counted", cc.get("n_events") == 800 and jc["drops"].get("events_dropped_by_match_cap") == 200)
_, jt, ct = run(15.0, N=8)
check("only 8 matches -> unknown (needs >= 12)", str(ct.get("verdict", "")).startswith("unknown"))
SEEDS = range(1, 21)
p15 = [meets(run(15.0, seed=s)[2]) for s in SEEDS]
p0 = [meets(run(0.0, react=False, seed=s)[2]) for s in SEEDS]
p10 = [meets(run(10.0, seed=s)[2]) for s in SEEDS]
check("20 seeds: planted +15 s passes >= 18 of 20 (got %d)" % sum(p15), sum(p15) >= 18)
check("20 seeds: planted +10 s passes >= 15 of 20 (got %d; reported, this is the real-series plant size)" % sum(p10), sum(p10) >= 15)
check("20 seeds: no-edge false passes <= 1 of 20 (got %d)" % sum(p0), sum(p0) <= 1)
print("ALL PASS" if not fails else "FAILED: " + "; ".join(fails))
sys.exit(1 if fails else 0)
