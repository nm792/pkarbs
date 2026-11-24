#!/usr/bin/env python3
"""Offline self test of goalserve_odds_vs_pm_v3.py on a SYNTHETIC world (no network, no key). Every check can fail (planted lead, planted price-first, null, failed controls, broken join, refusals).
Usage: python3 -I feeds/test_goalserve_odds_vs_pm_v3.py  -> PASS/FAIL lines, exit 0 only if all pass."""
import calendar, collections, gzip, json, os, random, subprocess, sys, tempfile, time
H = os.path.dirname(os.path.abspath(__file__)); V3 = os.path.join(H, "goalserve_odds_vs_pm_v3.py")
sys.path.insert(0, H)
import goalserve_odds_vs_pm_v3 as v3
F = []


def chk(n, c):
    print(("PASS " if c else "FAIL ") + n)
    if not c:
        F.append(n)


T0 = calendar.timegm(time.strptime("2026-11-24T12:00:00", "%Y-%m-%dT%H:%M:%S"))
EVT = ((300, +1), (700, -1), (1100, +1))   # offsets from match start; sign = direction of the HOME probability
JUMP = 0.03


def world(root, n_matches, lag, seed=1, dup_market=False, hockey=True, kind_name="Money Line", away_static=False):
    """Goalserve hour file + poll log + PM recorder dir. PM mid follows the true probability with `lag` seconds (+ = PM after Goalserve, - = PM before)."""
    rnd = random.Random(seed)
    gdir, pdir = os.path.join(root, "gs"), os.path.join(root, "pm")
    os.makedirs(gdir); os.makedirs(pdir)
    sport = "hockey_nhl" if hockey else "esports"
    ev_t, matches, mk, bk = [], [], [], []
    for k in range(n_matches):
        st = T0 + 30 + (k * 53) % 1500
        h, a = ("NJ Team%d" % k, "Rival%d" % k)
        evs = [(st + off + rnd.uniform(0, 40), sg) for off, sg in EVT]
        matches.append((k, st, h, a, evs))
        outs = ["Rival%d" % k, "Team%d" % k] if k % 2 else ["Team%d" % k, "Rival%d" % k]
        toks = ["t%da" % k, "t%db" % k]
        for dup in (0, 1) if (dup_market and k == 0) else (0,):
            mk.append({"cond": "c%d_%d" % (k, dup), "q": "q", "smt": "moneyline", "outcomes": outs, "tokens": [x + str(dup) for x in toks] if dup else toks, "start": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(st))})
        def p_true(x, evs=evs):
            return 0.5 + sum(JUMP * sg for (te, sg) in evs if x >= te)
        for r in range(int(st - 100) // 5 * 5, int(st + 1900), 5):
            ph = p_true(r - lag) + rnd.uniform(-0.002, 0.002)
            pa = (0.5 if away_static else 1 - p_true(r - lag)) + rnd.uniform(-0.002, 0.002)
            for tk, pv in ((toks[outs.index("Team%d" % k)], ph), (toks[outs.index("Rival%d" % k)], pa)):
                bk.append({"recv_ms": r * 1000 + 17, "asset": tk, "bids": [{"price": "%.4f" % (pv - 0.005), "size": "100"}], "asks": [{"price": "%.4f" % (pv + 0.005), "size": "100"}]})
    # Goalserve payloads: one at match start, one at each jump, one at the end (0.0005 change, not a move)
    pay = collections.defaultdict(dict)
    times = {}
    for (k, st, h, a, evs) in matches:
        times[k] = sorted([st] + [te for te, _ in evs] + [st + 1800])
    allt = sorted({(t, k) for k, ts in times.items() for t in ts})
    for (t, _) in allt:
        evd = {}
        for (k, st, h, a, evs) in matches:
            if not (st <= t <= st + 1800):
                continue
            p = 0.5 + sum(JUMP * sg for (te, sg) in evs if t >= te) + (0.0005 if t >= st + 1800 else 0.0)
            evd[str(k)] = {"info": {"league": "NHL"}, "team_info": {"home": {"name": h}, "away": {"name": a}},
                           "odds": {"1": {"name": kind_name, "suspend": 0, "participants": {"0": {"name": h, "value_eu": "%.4f" % (1 / p), "suspend": 0}, "1": {"name": a, "value_eu": "%.4f" % (1 / (1 - p)), "suspend": 0}}}}}
        pay[t] = evd
    hour = time.strftime("%Y%m%d%H", time.gmtime(T0))
    with gzip.open(os.path.join(gdir, "%s_%s.jsonl.gz" % (sport, hour)), "wt") as f:
        for t in sorted(pay):
            f.write(json.dumps({"recv_ns": int(t * 1e9), "body": json.dumps({"events": pay[t], "bm": ""})}) + "\n")
    with open(os.path.join(gdir, "goalserve_20261124.jsonl"), "w") as f:
        x = T0 - 4
        while x < T0 + 3600 + 90:
            f.write(json.dumps({"t": "x", sport: {"recv_ns": int(x * 1e9)}}) + "\n")
            x += 2.0
    with open(os.path.join(pdir, "markets.jsonl"), "w") as f:
        for m in mk:
            f.write(json.dumps(m) + "\n")
    with gzip.open(os.path.join(pdir, "books.jsonl.gz"), "wt") as f:
        for r in sorted(bk, key=lambda r: r["recv_ms"]):
            f.write(json.dumps(r) + "\n")
    return gdir, pdir, sport


def run(root, gdir, pdir, sport, end="2026-11-24T13:00:00Z"):
    out = os.path.join(root, "out.json")
    p = subprocess.run([sys.executable, "-I", V3, "--sport", sport, "--files", os.path.join(gdir, sport + "_*.jsonl.gz"), "--pm", pdir, "--poll-log", os.path.join(gdir, "goalserve_*.jsonl"),
                        "--start-iso", "2026-11-24T12:00:00Z", "--end-iso", end, "--clock-note", "synthetic", "--out", out], capture_output=True, text=True)
    return p, (json.load(open(out)) if os.path.exists(out) else None)


def cell(res):
    c = res["cells"]
    return c[next(iter(c))] if c else {}


# 1. planted FOLLOW lead: PM moves 3 s after the odds
r1 = tempfile.mkdtemp(); g, pm, sp = world(r1, 48, +3)
p, res = run(r1, g, pm, sp); c = cell(res) if res else {}
print("   follow:", p.stdout.strip()[:200], p.stderr.strip()[-200:])
chk("planted lead (PM 3 s after the odds) -> meets bar, mean d10 ~ +0.03", "meets bar" in c.get("verdict", "") and abs(c["d10"]["mean"] - JUMP) < 0.005)
chk("controls all OK on the planted lead (placebo, plants 95-105%, swap, shift)", all(c["controls"]["ok"].values()) and 0.97 < c["controls"]["plant_plus_recovery"] < 1.03 and 0.97 < c["controls"]["plant_minus_recovery"] < 1.03)
chk("sizing block 12 matches never scored; scored = rest", c["sizing_block"] == 12 and c["scored"] == c["matches_total"] - 12)
chk("hockey name join 'NJ Team3' ~ 'Team3' works, outcomes in either order", c["matches_total"] >= 40)
# 2. planted PRICE-FIRST: PM moves 5 s before the odds
r2 = tempfile.mkdtemp(); g, pm, sp = world(r2, 48, -5)
p, res = run(r2, g, pm, sp); c2 = cell(res) if res else {}
chk("planted price-first (PM 5 s before) -> 'price moves first', mean d10 ~ -0.03", "price moves first" in c2.get("verdict", "") and abs(c2["d10"]["mean"] + JUMP) < 0.005)
# 3. null: PM never moves
r3 = tempfile.mkdtemp(); g, pm, sp = world(r3, 48, +100000)
p, res = run(r3, g, pm, sp); c3 = cell(res) if res else {}
chk("null (PM never reacts) -> no lead at 0.2c, closed; NOT 'meets bar'", "no lead at 0.2c" in c3.get("verdict", "") and "meets bar" not in c3.get("verdict", ""))
chk("null: label-swap and time-shift controls read ~0", abs(c3["controls"]["swap_mean_d10"]) < 0.002 and abs(c3["controls"]["shift_mean_d10"]) < 0.002)
# 4. sizing block incomplete
r4 = tempfile.mkdtemp(); g, pm, sp = world(r4, 9, +3)
p, res = run(r4, g, pm, sp); c4 = cell(res) if res else {}
chk("9 matches -> 'sizing block incomplete', nothing scored", "sizing block incomplete" in c4.get("verdict", "") and c4.get("scored") == 0)
# 5. ambiguous rematch market is excluded and counted
r5 = tempfile.mkdtemp(); g, pm, sp = world(r5, 14, +3, dup_market=True)
p, res = run(r5, g, pm, sp)
chk("two PM markets for one match -> excluded, counted (events_ambiguous_market_excluded)", res and res["drops"].get("events_ambiguous_market_excluded", 0) >= 3)
# 6. wrong market name is excluded (counted), never scored
r6 = tempfile.mkdtemp(); g, pm, sp = world(r6, 14, +3, kind_name="Total Goals Over/Under")
p, res = run(r6, g, pm, sp)
chk("a market name outside the allowed set yields no events and no cell", res and not res["cells"] and "Total Goals Over/Under" in json.dumps(res["goalserve_audit"]["market_names_excluded"]))
# 6b. run-level control failure: the OTHER token does not mirror (static) -> label-swap null fails -> no number
r6b = tempfile.mkdtemp(); g, pm, sp = world(r6b, 48, +3, away_static=True)
p, res = run(r6b, g, pm, sp); c6 = cell(res) if res else {}
chk("other token static -> swap control fails -> 'unknown (control failed: swap...' and mean withheld", "control failed" in c6.get("verdict", "") and "swap" in c6.get("verdict", "") and c6["d10"]["mean"] is None)
# 6c. hourly PM files books-YYYYMMDDHH.jsonl.gz (pmcs2 layout) outside the window are skipped and counted; inside ones are read
r6c = tempfile.mkdtemp(); g, pm, sp = world(r6c, 14, +3)
os.rename(os.path.join(pm, "books.jsonl.gz"), os.path.join(pm, "books-2026112412.jsonl.gz"))
open(os.path.join(pm, "books-2026110100.jsonl"), "w").write("not json at all\n")
p, res = run(r6c, g, pm, sp)
chk("hourly books-*.jsonl.gz read; a file hours outside the window is skipped, counted", res and res["drops"].get("pm_book_files_skipped_outside_window") == 1 and res["cells"])
# 7. refusals
p, res = run(r1, g, pm, sp, end="2026-11-24T13:30:00Z")
chk("end later than the poll log -> refuses (exit != 0, no result)", p.returncode != 0)
# 8. unit: decide() with a failed control prints NO number; each control gates the verdict
means = [0.03 + 0.001 * (i % 3) for i in range(40)]
for bad in ("placebo", "plants", "swap", "shift"):
    ok = dict(placebo=True, plants=True, swap=True, shift=True); ok[bad] = False
    d = v3.decide(means, 100, 30, ok)
    chk("control '%s' failed -> unknown, mean withheld" % bad, "unknown" in d["verdict"] and d["mean"] is None)
d = v3.decide(means, 100, 30, dict(placebo=True, plants=True, swap=True, shift=True))
chk("all controls ok + strong effect -> meets bar", "meets bar" in d["verdict"])
d = v3.decide(means[:12], 30, 30, dict(placebo=True, plants=True, swap=True, shift=True))
chk("12 scored matches and 30 events -> unknown (below the event bar)", "unknown" in d["verdict"])
# 9. unit: join rule
chk("contains: 'nj devils' ~ 'devils'", v3.contains("nj devils", "devils") and not v3.contains("nj devils", "vils") and not v3.contains("rangers", "devils"))
chk("map_teams: both must map to DIFFERENT outcomes", v3.map_teams("nj devils", "ny rangers", ["rangers", "devils"]) == (1, 0) and v3.map_teams("nj devils", "devils jr", ["devils", "rangers"]) is None)
chk("kind_of hockey: 'Money Line' ok, 'Total Goals' not; tennis 'To Win' ok", v3.kind_of("hockey_nhl", "Money Line") == "Match Winner" and v3.kind_of("hockey_nhl", "Total Goals") is None and v3.kind_of("tennis", "To Win") == "Match Winner")
print("ALL PASS" if not F else "FAILED: " + "; ".join(F))
sys.exit(1 if F else 0)
