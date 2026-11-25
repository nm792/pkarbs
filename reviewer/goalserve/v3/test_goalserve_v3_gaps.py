#!/usr/bin/env python3
"""GAP TESTS for goalserve_v3_look.py (sign-off audit by the Goalserve thread, 24 Nov 2026). The Reviewer's test_goalserve_v3_look.py PASSES with each of these six mutations applied;
every check below FAILS under one of them (mutation table in reviewer/goalserve/v3/SIGNOFF-v3-rule-to-code-2026-11-24.md). Unit level: score_cell() and gs_events() on crafted inputs.
Usage: python3 -I test_goalserve_v3_gaps.py  -> PASS/FAIL lines, ALL PASS."""
import gzip, json, os, random, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import goalserve_v3_look as G
F = []


def chk(n, c, info=""):
    print(("PASS " if c else "FAIL ") + n + ("" if c else "  " + str(info)))
    if not c:
        F.append(n)


def recs(sizing, test, ok=True, plant_scale=1.0, seed=3):
    """one event per match; sizing / test = lists of per-match d10 values. Controls consistent (placebo 0, plants +-1c, swap negated, shift 0) unless plant_scale != 1."""
    out, t = [], 1000.0
    for i, d in enumerate(list(sizing) + list(test)):
        t += 600
        sw = -d
        out.append(dict(m=("e%d" % i, "Match Winner"), t=t, d10=d, d2=d, d60=d, plc=0.0, pP=d + 0.01 * plant_scale, pM=d - 0.01 * plant_scale, sw=sw, pS=sw + 0.01 * plant_scale, ts=0.0))
    return out


def jit(n, mu, sd, seed):
    r = random.Random(seed)
    return [mu + r.gauss(0, sd) for _ in range(n)]


# 1. information time: z >= 2.6 at 20 of N_MAX = 100 test matches is NOT yet a pass (needs z*sqrt(t) >= 2.6)
sz = [0.03 if i % 2 else -0.03 for i in range(12)]            # sigma ~ 3c -> N_MAX = 100
te = jit(20, 0.003, 0.0045, 11)
r = G.score_cell("nhl|Match Winner", recs(sz, te))
chk("information time: z_eq ~3 at 20 of 100 matches is 'no pass yet', NOT 'lead'", r["n_max"] == 100 and r["test"]["z_eq"] >= 2.6 and not r["verdict"].startswith("lead") and "no pass yet" in r["verdict"], r.get("verdict"))
# 2. controls gate: a strong effect with plants NOT recovered (50%) -> 'no verdict', never 'lead'
sz = jit(12, 0.03, 0.002, 5); te = jit(12, 0.03, 0.002, 6)
r_ok = G.score_cell("nhl|Match Winner", recs(sz, te))
r_bad = G.score_cell("nhl|Match Winner", recs(sz, te, plant_scale=0.5))
chk("strong effect + controls OK -> lead (the test can say yes)", r_ok["verdict"].startswith("lead"), r_ok["verdict"])
chk("strong effect + plants recovered at 50% -> 'no verdict: controls failed', NOT lead", "no verdict" in r_bad["verdict"] and not r_bad["verdict"].startswith("lead"), r_bad["verdict"])
# 3. sizing block: fewer than 12 matches -> 'sizing block incomplete', nothing tested
r = G.score_cell("nhl|Match Winner", recs(jit(8, 0.03, 0.002, 7), []))
chk("8 matches -> 'sizing block incomplete', no test block", "sizing block incomplete" in r["verdict"] and "test" not in r, r["verdict"])
# 4. sizing block is NEVER tested: sizing d10 = +5c, test d10 = 0 -> test n = 12, mean ~ 0, not lead
r = G.score_cell("nhl|Match Winner", recs(jit(12, 0.05, 0.002, 8), jit(12, 0.0, 0.002, 9)))
chk("sizing matches excluded from the test: test n = 12 and mean ~ 0, verdict not lead", r["test"]["n_matches"] == 12 and abs(r["test"]["mean_d10"]) < 0.003 and not r["verdict"].startswith("lead"), r["verdict"])


# 5/6. event rule and outage rule on crafted Goalserve payloads
def body(p, h="NJ Devils", a="Rangers"):
    o1, o2 = 1 / p, 1 / (1 - p)
    return json.dumps({"events": {"7": {"info": {"league": "NHL"}, "team_info": {"home": {"name": h}, "away": {"name": a}},
                                         "odds": {"1": {"name": "Home/Away", "suspend": 0, "participants": {"0": {"name": h, "value_eu": "%.4f" % o1, "suspend": 0}, "1": {"name": a, "value_eu": "%.4f" % o2, "suspend": 0}}}}}}})


def events(series, polls, t_lo=0.0, t_hi=1e9):
    d = tempfile.mkdtemp(); p = os.path.join(d, "hockey_nhl_2026112400.jsonl.gz")
    with gzip.open(p, "wt") as f:
        for (t, pr) in series:
            f.write(json.dumps({"recv_ns": int(t * 1e9), "body": body(pr)}) + "\n")
    return G.gs_events("hockey_nhl", [p], sorted(polls), t_lo, t_hi)[0]


cont = [x * 2.0 for x in range(0, 200)]
ev = events([(10, 0.50), (30, 0.512), (50, 0.55)], cont)
chk("event threshold: a 1.2c move is NOT an event, the later 3.8c move is (exactly 1 event)", len(ev) == 1 and ev[0][3] == "h", ev)
gap = [x * 2.0 for x in range(0, 40)] + [x * 2.0 for x in range(80, 200)]      # no polls between 78 s and 160 s; the first payload after the restart (160 s) is the one that must clear the baseline
ev = events([(70, 0.50), (160, 0.56)], gap)
chk("outage rule: a 6c move across a 90 s poll gap is NOT an event (baseline cleared)", ev == [], ev)
ev = events([(70, 0.50), (160, 0.56)], cont)
chk("same move with continuous polls IS an event (the rule can say yes)", len(ev) == 1, ev)
print("ALL PASS" if not F else "FAILED: " + "; ".join(F)); sys.exit(1 if F else 0)
