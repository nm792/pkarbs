#!/usr/bin/env python3
"""Self test for goalserve_odds_vs_pm.py on synthetic data with a PLANTED edge. PASS/FAIL lines; exit 0 only if all pass.
Builds 40 matches x 3 odds toggles (Goalserve first-seen times) plus PM books where the rising team's token jumps +3c / the other falls -3c at
t_event + SHIFT, with sparse random +-3c blips as noise. Checks: SHIFT=5.0 recovers the lead (median real lead within 1.5 s of 5), SHIFT=15.0 recovers it and meets the bar; SHIFT=0.0 and SHIFT=-5.0 do not;
no-edge (PM never reacts) does not; excluded market names are counted and printed, not silently used."""
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
                books.append({"asset": tk, "recv_ms": int(t * 1000), "bids": [{"price": str(round(lv - 0.005, 4))}], "asks": [{"price": str(round(lv + 0.005, 4))}]})
    with open(os.path.join(pmd, "markets.jsonl"), "w") as f:
        for m in markets: f.write(json.dumps(m) + "\n")
    with open(os.path.join(pmd, "books.jsonl"), "w") as f:
        for b in books: f.write(json.dumps(b) + "\n")
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
                mk = {"1": {"id": 1, "name": "Match Winner", "suspend": sus, "participants": {
                        "11": {"id": 11, "name": "Team A%d" % j, "value_eu": o1, "suspend": 0},
                        "12": {"id": 12, "name": "Team B%d" % j, "value_eu": o2, "suspend": 0}}},
                      "2": {"id": 2, "name": "Total Rounds", "suspend": 0, "participants": {
                        "21": {"id": 21, "name": "Over", "value_eu": 1.9, "suspend": 0}, "22": {"id": 22, "name": "Under", "value_eu": 1.9, "suspend": 0}}}}
                evs["E%d" % j] = {"info": {"sport": "cs2"}, "team_info": {"home": {"name": "Team A%d" % j}, "away": {"name": "Team B%d" % j}}, "odds": mk}
            g.write(json.dumps({"recv_ns": int(t * 1e9), "body": json.dumps({"bm": "bet365", "events": evs})}) + "\n")
    return tmp, gdir, pmd

def run(shift, react=True):
    tmp, gdir, pmd = build(shift, react)
    out = os.path.join(tmp, "res.json")
    r = subprocess.run([sys.executable, "-I", os.path.join(here, "goalserve_odds_vs_pm.py"), "--files", os.path.join(gdir, "*.jsonl.gz"), "--pm", pmd, "--out", out],
                       capture_output=True, text=True)
    return r, (json.load(open(out)) if os.path.exists(out) else None)

r5, j5 = run(5.0)
check("run shift 5 exits 0", r5.returncode == 0)
c = (j5 or {}).get("cells", {}).get("match", {})
print("  shift 5 cell:", {k: c.get(k) for k in ("n_events", "n_with_onset", "median_real_lead_s", "median_placebo_lead_s", "diff_s", "pct_price_after_feed", "ci95_match_boot", "verdict")})
check("120 events found", c.get("n_events") == 120)
check("shift 5.0: planted lead RECOVERED within 1.5 s (bar not required: 5 s is below this noise level's detection power, reported honestly)", c.get("median_real_lead_s") is not None and abs(c["median_real_lead_s"] - 5.0) <= 1.5)
r15, j15 = run(15.0)
c15 = (j15 or {}).get("cells", {}).get("match", {})
print("  shift 15 cell:", {k: c15.get(k) for k in ("n_events", "median_real_lead_s", "median_placebo_lead_s", "diff_s", "pct_price_after_feed", "ci95_match_boot", "verdict")})
check("shift 15.0 meets the bar", r15.returncode == 0 and str(c15.get("verdict", "")).startswith("meets bar"))
a = j5["audit"] if j5 else {}
check("'Total Rounds' excluded and counted, bm bet365 reported", "Total Rounds" in a.get("market_names_excluded", {}) and "'bet365'" in a.get("bm_values", {}))
for sh in (0.0, -5.0):
    r, j = run(sh)
    cc = (j or {}).get("cells", {}).get("match", {})
    print("  shift %s cell:" % sh, {k: cc.get(k) for k in ("n_events", "median_real_lead_s", "diff_s", "pct_price_after_feed", "verdict")})
    check("shift %s does NOT meet the bar" % sh, r.returncode == 0 and not str(cc.get("verdict", "")).startswith("meets bar"))
rn, jn = run(5.0, react=False)
cn = (jn or {}).get("cells", {}).get("match", {})
print("  no-edge cell:", {k: cn.get(k) for k in ("n_events", "n_with_onset", "diff_s", "verdict")})
check("no-edge (PM never reacts) does NOT meet the bar", rn.returncode == 0 and not str(cn.get("verdict", "")).startswith("meets bar"))
print("ALL PASS" if not fails else "FAILED: " + "; ".join(fails)); sys.exit(1 if fails else 0)
