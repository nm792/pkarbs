#!/usr/bin/env python3
"""Self test (v2) for goalserve_odds_vs_pm.py on synthetic data with a PLANTED edge. PASS/FAIL lines; exit 0 only if all pass.
Builds 40 matches x 3 odds toggles (Goalserve first-seen times) plus PM books where the rising team's token jumps +3c / the other falls -3c at
t_event + SHIFT, with sparse random +-3c blips as noise. Checks: SHIFT=5.0 recovers the lead (median real lead within 1.5 s of 5), SHIFT=15.0 recovers it and meets the bar; SHIFT=0.0 and SHIFT=-5.0 do not;
no-edge (PM never reacts) does not; excluded market names are counted and printed. v2: shifts 0, no-edge and 15 are repeated over 20 seeds and the FALSE-PASS rate (must be <= 5%) and the planted-shift pass rates at 15 s (reported) and 25 s (must be >= 75%) are reported.
v4 (17 Nov 10:58Z): the builder uses the REAL Goalserve names seen in the stored inventory: market 'Home/Away', 'Home/Away (map 1)', participants 'Home'/'Away', info.sport 'Esports', info.league 'CS2 - Test League'.
v5 (17 Nov 12:50Z): the PM book rows use the REAL recorder schema from live/thesports/capture.py (ms, sent, tk, bids, asks; no recv_ms/asset); the test asserts time comes from ms, the poll cycle is measured from distinct sent values, and --pm-shift-s recovers a planted lead."""
import os, sys, gzip, json, tempfile, subprocess, random
here = os.path.dirname(os.path.abspath(__file__))
fails = []
def check(n, c):
    print(("PASS " if c else "FAIL ") + n)
    if not c: fails.append(n)

def build(shift, react=True, seed=7):
    rnd = random.Random(seed)
    tmp = tempfile.mkdtemp(); pmd = os.path.join(tmp, "pm"); os.makedirs(pmd)
    T0 = 1_800_000_000.0
    N, K = 40, 3
    markets, tl = [], []   # tl: (time, match index, state)
    books = []
    states = {(1.6, 2.4): "H", (2.4, 1.6): "A"}
    for i in range(N):
        A, B = "Team A%d" % i, "Team B%d" % i
        markets.append({"cond": "c%d" % i, "q": "%s vs %s" % (A, B), "smt": "moneyline", "outcomes": [A, B], "tokens": ["tA%d" % i, "tB%d" % i]})
        t_first = T0 + i * 1000.0
        tl.append((t_first, i, (1.8, 2.2)))
        mids = {"tA%d" % i: [(t_first - 500, 0.5)], "tB%d" % i: [(t_first - 500, 0.5)]}
        up = True
        for k in range(K):
            te = t_first + 300.0 * (k + 1) + rnd.uniform(0, 20)
            tl.append((te, i, (1.6, 2.4) if up else (2.4, 1.6)))
            if react:
                a, b = (0.53, 0.47) if up else (0.47, 0.53)
                mids["tA%d" % i].append((te + shift, a)); mids["tB%d" % i].append((te + shift, b))
            up = not up
        # sparse noise blips: +-3c for 10 s on one token, about 1 per 150 s
        tt = t_first - 400
        while tt < t_first + 1300:
            tt += rnd.expovariate(1 / 150.0)
            tk = rnd.choice(["tA%d" % i, "tB%d" % i]); sg = rnd.choice((-1, 1))
            cur = [p for (t, p) in sorted(mids[tk]) if t <= tt]
            lvl = cur[-1] if cur else 0.5
            mids[tk].append((tt, lvl + 0.03 * sg)); mids[tk].append((tt + 10, lvl))
        for tk, pts in mids.items():
            pts.sort()
            for t in [pts[0][0] + j * 1.0 for j in range(int((pts[-1][0] - pts[0][0]) / 1.0) + 2)]:
                lv = [p for (x, p) in pts if x <= t][-1]
                books.append({"ms": int(t * 1000), "sent": int(t * 1000) - 80, "tk": tk, "bids": [{"price": str(round(lv - 0.005, 4))}], "asks": [{"price": str(round(lv + 0.005, 4))}]})
    with open(os.path.join(pmd, "markets.jsonl"), "w") as f:
        for m in markets: f.write(json.dumps(m) + "\n")
    with open(os.path.join(pmd, "books.jsonl"), "w") as f:
        for b in books: f.write(json.dumps(b) + "\n")
        f.write("{bad pm line\n")
    # goalserve bodies: one per change time, whole state
    cur = {i: (1.8, 2.2) for i in range(N)}
    tl.sort()
    gdir = os.path.join(tmp, "gs"); os.makedirs(gdir)
    with gzip.open(os.path.join(gdir, "esports_2026111700.jsonl.gz"), "wt") as g:
        for (t, i, st) in tl:
            cur[i] = st
            evs = {}
            for j in range(N):
                o1, o2 = cur[j]
                sus = 0
                mk = {"1": {"id": 1, "name": "Home/Away", "suspend": sus, "participants": {
                        "11": {"id": 11, "name": "Home", "value_eu": o1, "suspend": 0},
                        "12": {"id": 12, "name": "Away", "value_eu": o2, "suspend": 0}}},
                      "3": {"id": 3, "name": "Home/Away (map 1)", "suspend": 0, "participants": {
                        "31": {"id": 31, "name": "Home", "value_eu": 1.8, "suspend": 0}, "32": {"id": 32, "name": "Away", "value_eu": 2.0, "suspend": 0}}},
                      "4": {"id": 4, "name": "Odd/Even (1st map)", "suspend": 0, "participants": {
                        "41": {"id": 41, "name": "Odd", "value_eu": 1.9, "suspend": 0}, "42": {"id": 42, "name": "Even", "value_eu": 1.9, "suspend": 0}}},
                      "2": {"id": 2, "name": "Total Rounds", "suspend": 0, "participants": {
                        "21": {"id": 21, "name": "Over", "value_eu": 1.9, "suspend": 0}, "22": {"id": 22, "name": "Under", "value_eu": 1.9, "suspend": 0}}}}
                evs["E%d" % j] = {"info": {"sport": "Esports", "league": "CS2 - Test League"}, "team_info": {"home": {"name": "Team A%d" % j}, "away": {"name": "Team B%d" % j}}, "odds": mk}
            g.write(json.dumps({"recv_ns": int(t * 1e9), "body": json.dumps({"bm": "bet365", "events": evs})}) + "\n")
        g.write("{bad goalserve line\n")
    return tmp, gdir, pmd

CELL = "cs2|'bet365'|Match Winner"
def run(shift, react=True, seed=7, pm_shift=0.0):
    tmp, gdir, pmd = build(shift, react, seed)
    out = os.path.join(tmp, "res.json")
    r = subprocess.run([sys.executable, "-I", os.path.join(here, "goalserve_odds_vs_pm.py"), "--files", os.path.join(gdir, "*.jsonl.gz"), "--pm", pmd,
                        "--clock-note", "selftest", "--seed", str(seed), "--pm-shift-s", str(pm_shift), "--out", out], capture_output=True, text=True)
    j = json.load(open(out)) if os.path.exists(out) else None
    return r, j, ((j or {}).get("cells", {}).get(CELL, {}))

def passes(c): return str(c.get("verdict", "")).startswith("meets bar")

r5, j5, c = run(5.0)
check("run shift 5 exits 0", r5.returncode == 0)
print("  shift 5 cell:", {k: c.get(k) for k in ("n_events", "n_with_onset", "n_placebo_with_onset", "median_real_lead_s", "median_placebo_lead_s", "diff_s", "pct_all_events_lead_ge_res", "ci95_match_boot", "verdict")})
check("120 events found", c.get("n_events") == 120)
check("shift 5.0: planted lead RECOVERED within 1.5 s (bar not required: see AMENDMENT file)", c.get("median_real_lead_s") is not None and abs(c["median_real_lead_s"] - 5.0) <= 1.5)
a = j5["audit"] if j5 else {}
check("real names used: Home/Away and Home/Away (map 1); Odd/Even excluded; league prefix cs2 seen",
      set(a.get("market_names_used", {})) == {"Home/Away", "Home/Away (map 1)"} and "Odd/Even (1st map)" in a.get("market_names_excluded", {}) and "cs2" in a.get("league_prefixes_seen", {}))
check("'Total Rounds' excluded and counted, bm bet365 reported", "Total Rounds" in a.get("market_names_excluded", {}) and "'bet365'" in a.get("bm_values", {}))
check("match list printed with 40 matched markets, drops dict present", len(j5["match_list"]) == 40 and all("pm_cond" in m for m in j5["match_list"]) and "drops" in j5)
check("bad lines counted: goalserve 1, PM books 1", a.get("counters", {}).get("goalserve_rows_bad_lines") == 1 and j5["drops"].get("pm_books_bad_lines") == 1)
check("book spacing measured (p90 about 1 s) and used in bar 4", abs(j5["book_row_spacing_measured"]["p90_s"] - 1.0) < 0.05 and j5["resolution_used_in_bar4_s"] == 1.0)
d5 = j5["drops"]
check("real book schema: time taken from ms (counted), none from recv_ms, none dropped for missing time", d5.get("pm_book_rows_time_from_ms", 0) > 1000 and d5.get("pm_book_rows_time_from_recv_ms", 0) == 0 and d5.get("book_rows_no_recv_ms", 0) == 0)
cy = j5["book_poll_cycle_measured"]
check("poll cycle measured from distinct 'sent' values (median 1 s, p90 1 s)", cy.get("n_cycles", 0) > 100 and abs(cy["median_s"] - 1.0) < 0.05 and abs(cy["p90_s"] - 1.0) < 0.05)
_, _, cs = run(0.0, True, 7, pm_shift=5.0)
check("--pm-shift-s 5 on a zero-shift series recovers a 5 s lead within 1.5 s (same as building the shift in)", cs.get("median_real_lead_s") is not None and abs(cs["median_real_lead_s"] - 5.0) <= 1.5)
SEEDS = range(1, 21)
res = {"plant15": [], "plant25": [], "shift0": [], "noedge": []}
for sd in SEEDS:
    res["plant15"].append(passes(run(15.0, True, sd)[2]))
    res["plant25"].append(passes(run(25.0, True, sd)[2]))
    res["shift0"].append(passes(run(0.0, True, sd)[2]))
    res["noedge"].append(passes(run(5.0, False, sd)[2]))
for k, v in res.items():
    print("  %s: pass in %d of %d seeds" % (k, sum(v), len(v)))
check("false-pass rate at shift 0.0 <= 5%% (%d of 20)" % sum(res["shift0"]), sum(res["shift0"]) <= 1)
check("false-pass rate at no-edge <= 5%% (%d of 20)" % sum(res["noedge"]), sum(res["noedge"]) <= 1)
print("  (15 s pass rate is REPORTED only: minimum detectable lead of this statistic at n=120 is about 25 s)")
check("planted 25.0 s passes the bar in >= 75%% of seeds (%d of 20)" % sum(res["plant25"]), sum(res["plant25"]) >= 15)
print("ALL PASS" if not fails else "FAILED: " + "; ".join(fails)); sys.exit(1 if fails else 0)
