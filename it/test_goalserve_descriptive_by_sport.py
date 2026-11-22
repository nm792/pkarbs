#!/usr/bin/env python3
"""Self test for goalserve_descriptive_by_sport.py. Plants a known PM step and known ask depth and checks the table recovers them;
a positive, a flat control, a reversed-outcome-order case, a sign-flip case and a no-market case. Ends with 'ALL PASS' only if every check passes.
Usage: FEEDS_DIR=<exported feeds dir> python3 -I test_goalserve_descriptive_by_sport.py"""
import gzip, json, os, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(HERE, "goalserve_descriptive_by_sport.py")
T0 = 1795000000.0
FAILS = []


def check(name, ok, info=""):
    print(("PASS " if ok else "FAIL ") + name, info)
    if not ok:
        FAILS.append(name)


def part(name, v):
    return {"name": name, "value_eu": str(v), "suspend": 0}


def body(mname, home, away, oh, oa):
    return json.dumps({"bm": "", "events": {"1": {"info": {"league": "ATP - x"}, "team_info": {"home": {"name": home}, "away": {"name": away}},
                       "odds": {"9": {"name": mname, "suspend": 0, "participants": {"0": part(home, oh), "1": part(away, oa)}}}}}})


def make(d, sport, mname, outcomes, tokens, ta_up=True, flat=False, pm_markets=True):
    os.makedirs(d, exist_ok=True)
    polls, rows = [], []
    t = T0
    while t < T0 + 600:
        polls.append({sport: {"recv_ns": int(t * 1e9)}})
        tt = t + 0.5
        o = (2.0, 2.0) if tt < T0 + 300 else (1.6, 2.6)      # home 'alpha' becomes the favourite at T0+300: ph 0.50 -> 0.619
        rows.append({"recv_ns": int(tt * 1e9), "body": body(mname, "alpha", "beta", *o)})
        t += 1.8
    with gzip.open(os.path.join(d, "%s_2026110000.jsonl.gz" % sport), "wt") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    with open(os.path.join(d, "poll.jsonl"), "w") as f:
        for p in polls:
            f.write(json.dumps(p) + "\n")
    pm = os.path.join(d, "pm")
    os.makedirs(pm, exist_ok=True)
    with open(os.path.join(pm, "markets.jsonl"), "w") as f:
        if pm_markets:
            f.write(json.dumps({"cond": "c1", "q": "alpha vs beta", "smt": "moneyline", "outcomes": outcomes, "tokens": tokens}) + "\n")
    tokA, tokB = tokens[outcomes.index("alpha")], tokens[outcomes.index("beta")]
    with open(os.path.join(pm, "books.jsonl"), "w") as f:
        x = T0
        while x < T0 + 600:
            moved = (not flat) and x >= T0 + 310
            up = 0.03 if ta_up else -0.03
            a = 0.50 + (up if moved else 0)
            b = 0.50 - (up if moved else 0)
            asksA = [{"price": "%.2f" % (a + .01), "size": "40"}, {"price": "%.2f" % (a + .02), "size": "60"}, {"price": "%.2f" % (a + .10), "size": "500"}]
            asksB = [{"price": "%.2f" % (b + .01), "size": "10"}]
            f.write(json.dumps({"tk": tokA, "ms": x * 1000, "bids": [{"price": "%.2f" % (a - .01), "size": "5"}], "asks": asksA}) + "\n")
            f.write(json.dumps({"tk": tokB, "ms": x * 1000, "bids": [{"price": "%.2f" % (b - .01), "size": "5"}], "asks": asksB}) + "\n")
            x += 5
    return d


def run(d, sport):
    out = os.path.join(d, "out.json")
    env = dict(os.environ)
    p = subprocess.run([sys.executable, "-I", SCRIPT, "--sport", sport, "--files", os.path.join(d, "%s_*.jsonl.gz" % sport), "--poll-log", os.path.join(d, "poll.jsonl"),
                        "--pm", os.path.join(d, "pm"), "--out", out], capture_output=True, text=True, env=env)
    if p.returncode:
        print(p.stdout[-800:], p.stderr[-1500:])
        return None
    return json.load(open(out))


def near(x, y, tol=1e-6):
    return x is not None and abs(x - y) < tol


with tempfile.TemporaryDirectory() as tmp:
    # 1 planted +3c step 10 s after the odds move; depth 40 at best, 100 within 2c, usd 0.51*40+0.52*60
    j = run(make(os.path.join(tmp, "a"), "tennis", "To Win", ["alpha", "beta"], ["TA", "TB"]), "tennis")
    c = (j or {}).get("cells", {}).get("tennis|Match Winner", {})
    check("planted: one event used", c.get("events_usable") == 1, str(c.get("events_usable")))
    check("planted: pm_before 0c", near(c.get("mean_pm_before_c"), 0.0), str(c.get("mean_pm_before_c")))
    check("planted: pm_after +3c", near(c.get("mean_pm_after_c"), 3.0), str(c.get("mean_pm_after_c")))
    check("planted: net +3c", near(c.get("mean_net_c"), 3.0), str(c.get("mean_net_c")))
    check("planted: depth at best 40", near(c.get("median_ask_shares_at_best"), 40), str(c.get("median_ask_shares_at_best")))
    check("planted: depth within 2c 100", near(c.get("median_ask_shares_within_2c"), 100), str(c.get("median_ask_shares_within_2c")))
    check("planted: usd within 2c 51.6", near(c.get("median_ask_usd_within_2c"), 51.6, 1e-6), str(c.get("median_ask_usd_within_2c")))
    check("planted: wording tennis note present", bool(j and j.get("tennis_note")))
    check("planted: no verdict key", "verdict" not in (j or {}) and all("verdict" not in v for v in (j or {}).get("cells", {}).values()))
    # 2 flat control
    j = run(make(os.path.join(tmp, "b"), "tennis", "To Win", ["alpha", "beta"], ["TA", "TB"], flat=True), "tennis")
    c = (j or {}).get("cells", {}).get("tennis|Match Winner", {})
    check("flat control: net 0c", near(c.get("mean_net_c"), 0.0), str(c.get("mean_net_c")))
    # 3 reversed outcome order must not change the answer (token read by name, not by position)
    j = run(make(os.path.join(tmp, "c"), "tennis", "To Win", ["beta", "alpha"], ["TB", "TA"]), "tennis")
    c = (j or {}).get("cells", {}).get("tennis|Match Winner", {})
    check("reversed outcome order: net still +3c", near(c.get("mean_net_c"), 3.0), str(c.get("mean_net_c")))
    # 4 sign: PM moves the other way -> net -3c (a script reading the wrong token or sign would give +3)
    j = run(make(os.path.join(tmp, "d"), "tennis", "To Win", ["alpha", "beta"], ["TA", "TB"], ta_up=False), "tennis")
    c = (j or {}).get("cells", {}).get("tennis|Match Winner", {})
    check("sign: net -3c", near(c.get("mean_net_c"), -3.0), str(c.get("mean_net_c")))
    # 5 no PM market (hockey_nhl with no recorded book): events counted, nothing invented
    j = run(make(os.path.join(tmp, "e"), "hockey_nhl", "Home/Away", ["alpha", "beta"], ["TA", "TB"], pm_markets=False), "hockey_nhl")
    cells = (j or {}).get("cells", {})
    c = next(iter(cells.values()), {})
    check("no PM market: events counted, none usable", bool(j) and j["goalserve_events_total"] == 1 and c.get("events_usable") == 0 and j["unmatched_markets"] == 1, json.dumps(j and {k: j[k] for k in ("goalserve_events_total", "unmatched_markets")}))
print("ALL PASS" if not FAILS else "FAILED: " + ", ".join(FAILS))
sys.exit(1 if FAILS else 0)
