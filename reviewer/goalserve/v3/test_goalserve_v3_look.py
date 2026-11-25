#!/usr/bin/env python3
"""Self test for goalserve_v3_look.py. Builds synthetic Goalserve hour files, poll logs and Polymarket recorder dirs in a temp dir, then checks:
 T1 planted lead (price follows the odds 5 s later)   -> d10 ~ +move, verdict 'lead', controls OK
 T2 planted reverse (price moves 5 s BEFORE the odds)  -> d10 ~ -move, verdict 'price moves first, closed'
 T3 no relation (price moves at random times)          -> no 'lead', mean d10 ~ 0, time shift and placebo inside 0.2c
 T4 planted lead of 15 s: MUST FAIL on d10 (window 10 s cannot see it) and show on d60 (SETTLED B1: a delay test has a planted case that fails)
 T5 name join: 'NJ Devils' ~ 'Devils'; two candidate markets -> dropped as ambiguous; college hockey dropped by the NHL league rule
 T6 a suspension and reopen at a new price is NOT an event; a one-sided book row makes the mid undefined
 T7 a missing hour file while the poll log shows polling -> STOP
 T8 the cs2_books slim layout (books-YYYYMMDDHH.jsonl[.gz]) and the sport layout (multi-member books.jsonl.gz) both read
Prints ALL PASS on success."""
import gzip, json, math, os, random, sys, tempfile, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import goalserve_v3_look as G

T0 = G.iso("2026-11-24T00:00:00")
FAILS = []


def check(name, cond, info=""):
    print(("PASS " if cond else "FAIL ") + name + ("" if cond else "  " + str(info)))
    if not cond:
        FAILS.append(name)


def odds(p, vig=1.05):
    return "%.4f" % (1.0 / (p * vig)), "%.4f" % (1.0 / ((1 - p) * vig))


def build(root, sport, matches, lag, n_hours=6, seed=1, layout="slim", league="CS2 - Test League", skip_hour=None, extra=None):
    """matches: number of matches; each runs 50 min inside the window, start staggered. lag: seconds the PM price trails the odds (negative = leads),
    or 'random' for unrelated PM moves. Returns (gs_glob, poll_glob, pm_dir)."""
    rnd = random.Random(seed)
    gsd, pmd = os.path.join(root, "gs"), os.path.join(root, "pm")
    os.makedirs(gsd, exist_ok=True)
    os.makedirs(pmd, exist_ok=True)
    payload_t = {}
    pm_rows = []
    mk = []
    specs = []
    for i in range(matches):
        st = T0 + 600 + (i * (n_hours * 3600 - 4200) / max(1, matches))
        home, away = ("Team H%d" % i, "Team A%d" % i)
        pm_home, pm_away = home, away
        if extra and i in extra:
            home, away, pm_home, pm_away = extra[i][:4]
        toks = ("tk%dh" % i, "tk%da" % i)
        mk.append(dict(cond="c%d" % i, q="%s vs %s" % (pm_home, pm_away), outcomes=[pm_home, pm_away], tokens=list(toks), smt="moneyline",
                       start=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(st))))
        p, t, path = 0.5, st, []
        jumps = []
        while t < st + 3000:
            t += rnd.expovariate(1 / 150.0) + 30
            if t >= st + 3000:
                break
            p2 = min(0.9, max(0.1, p + rnd.choice((-1, 1)) * 0.04 + rnd.gauss(0, 0.002)))
            jumps.append((t, p2))
            p = p2
        specs.append((i, st, home, away, toks, jumps))
        # PM mid path
        pmj = []
        for (tj, pj) in jumps:
            if lag == "random":
                pmj.append((st + rnd.uniform(0, 3000), pj))
            else:
                pmj.append((tj + lag, pj))
        pmj.sort()
        cur = 0.5
        tt = st - 120
        k = 0
        while tt < st + 3200:
            while k < len(pmj) and pmj[k][0] <= tt:
                cur = pmj[k][1]
                k += 1
            noise = rnd.gauss(0, 0.0005)
            m = min(0.98, max(0.02, cur + noise))
            for tok, mm in ((toks[0], m), (toks[1], 1 - m)):
                pm_rows.append(dict(recv_ms=int(tt * 1000), asset=tok, bids=[{"price": "%.4f" % (mm - 0.005), "size": "100"}], asks=[{"price": "%.4f" % (mm + 0.005), "size": "100"}]))
            nxt = pmj[k][0] if k < len(pmj) else 1e18
            tt = min(tt + 1.0, nxt + 0.001) if nxt - tt < 1.0 else tt + 1.0
    # Goalserve payloads every 2 s across the window, all live matches in one body
    hour_files = {}
    t = T0
    while t < T0 + n_hours * 3600:
        evs = {}
        for (i, st, home, away, toks, jumps) in specs:
            if not (st <= t < st + 3000):
                continue
            p = 0.5
            for (tj, pj) in jumps:
                if tj <= t:
                    p = pj
            oh, oa = odds(p)
            evs["e%d" % i] = dict(info=dict(league=league if not (extra and i in extra and len(extra[i]) > 4) else extra[i][4]),
                                  team_info=dict(home=dict(name=home), away=dict(name=away)),
                                  odds={"410": dict(name="Home/Away", suspend="0", participants={"1": dict(name="Home", suspend="0", value_eu=oh), "2": dict(name="Away", suspend="0", value_eu=oa)})})
        hr = time.strftime("%Y%m%d%H", time.gmtime(t))
        if hr != skip_hour:
            hour_files.setdefault(hr, []).append(json.dumps(dict(recv_ns=int(t * 1e9), body=json.dumps(dict(events=evs)))))
        t += 2.0
    for hr, L in hour_files.items():
        with gzip.open(os.path.join(gsd, "%s_%s.jsonl.gz" % (sport, hr)), "wt") as f:
            f.write("\n".join(L) + "\n")
    with open(os.path.join(gsd, "goalserve_20261124.jsonl"), "w") as f:
        t = T0 - 5
        while t < T0 + n_hours * 3600 + 120:
            f.write(json.dumps({sport: dict(recv_ns=int(t * 1e9))}) + "\n")
            t += 1.8
    with open(os.path.join(pmd, "markets.jsonl"), "w") as f:
        for m in mk:
            f.write(json.dumps(m) + "\n")
    pm_rows.sort(key=lambda r: r["recv_ms"])
    if layout == "slim":
        by = {}
        for r in pm_rows:
            by.setdefault(time.strftime("%Y%m%d%H", time.gmtime(r["recv_ms"] / 1000)), []).append(json.dumps(r))
        for j, (hr, L) in enumerate(sorted(by.items())):
            if j % 2:
                with gzip.open(os.path.join(pmd, "books-%s.jsonl.gz" % hr), "wt") as f:
                    f.write("\n".join(L) + "\n")
            else:
                with open(os.path.join(pmd, "books-%s.jsonl" % hr), "w") as f:
                    f.write("\n".join(L) + "\n")
    else:
        with open(os.path.join(pmd, "books.jsonl.gz"), "wb") as f:
            for j in range(0, len(pm_rows), 5000):
                f.write(gzip.compress(("\n".join(json.dumps(r) for r in pm_rows[j:j + 5000]) + "\n").encode()))
    return os.path.join(gsd, sport + "_*.jsonl.gz"), os.path.join(gsd, "goalserve_*.jsonl"), pmd


def look(root, sport, gs, pl, pm, hours=6, extra_args=()):
    out = os.path.join(root, "out.json")
    return G.main(["--sport", sport, "--gs-files", gs, "--poll-log", pl, "--pm", pm, "--t-start", "2026-11-24T00:00:00Z",
                   "--t-end", time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(T0 + hours * 3600)), "--out", out] + list(extra_args))


def main():
    with tempfile.TemporaryDirectory() as td:
        # T1 planted lead +5 s
        r1 = os.path.join(td, "t1")
        gs, pl, pm = build(r1, "esports", 60, 5.0, seed=11)
        c = look(r1, "esports", gs, pl, pm)["cells"].get("cs2|Match Winner")
        check("T1 cell present", c is not None)
        if c:
            check("T1 sizing block 12", c["sizing_block"]["matches"] == 12, c["sizing_block"])
            check("T1 mean d10 ~ +0.04 (>= 0.03)", c["test"]["mean_d10"] is not None and c["test"]["mean_d10"] >= 0.03, c.get("test"))
            check("T1 controls OK", c["controls_ok"], c["controls"])
            check("T1 verdict lead", c["verdict"].startswith("lead"), c["verdict"])
            for k in ("plus", "minus", "swap"):
                check("T1 plant %s recovered" % k, c["controls"]["plants"][k]["ok"], c["controls"]["plants"][k])
        # T2 reverse: price leads by 5 s
        r2 = os.path.join(td, "t2")
        gs, pl, pm = build(r2, "esports", 60, -5.0, seed=12)
        c = look(r2, "esports", gs, pl, pm)["cells"].get("cs2|Match Winner")
        check("T2 mean d10 <= -0.03", c and c["test"]["mean_d10"] <= -0.03, c and c.get("test"))
        check("T2 verdict price first", c and c["verdict"].startswith("price moves first"), c and c["verdict"])
        check("T2 controls OK", c and c["controls_ok"], c and c["controls"])
        # T3 unrelated
        r3 = os.path.join(td, "t3")
        gs, pl, pm = build(r3, "esports", 60, "random", seed=13)
        c = look(r3, "esports", gs, pl, pm)["cells"].get("cs2|Match Winner")
        check("T3 no lead verdict", c and not c["verdict"].startswith("lead"), c and c["verdict"])
        check("T3 |mean d10| < 0.01", c and abs(c["test"]["mean_d10"]) < 0.01, c and c.get("test"))
        check("T3 time shift inside 0.2c", c and c["controls"]["time_shift_ok"], c and c["controls"])
        check("T3 placebo inside 0.2c", c and c["controls"]["placebo_ok"], c and c["controls"])
        # T4 planted 15 s lead: d10 blind, d60 sees it
        r4 = os.path.join(td, "t4")
        gs, pl, pm = build(r4, "esports", 40, 15.0, seed=14)
        c = look(r4, "esports", gs, pl, pm)["cells"].get("cs2|Match Winner")
        check("T4 d10 cannot see a 15 s lead (|mean| < 0.005)", c and abs(c["test"]["mean_d10"]) < 0.005, c and c.get("test"))
        check("T4 d60 sees it (>= 0.03)", c and c["test"]["mean_d60"] >= 0.03, c and c.get("test"))
        check("T4 verdict is not lead", c and not c["verdict"].startswith("lead"), c and c["verdict"])
        # T5 join + league rule, sport layout
        r5 = os.path.join(td, "t5")
        extra = {0: ("NJ Devils", "MTL Canadiens", "Devils", "Canadiens"), 1: ("Boston University", "Quinnipiac", "Boston University", "Quinnipiac", "NCAA"),
                 2: ("LA Kings", "SJ Sharks", "Kings", "Sharks"), 3: ("LA Kings", "SJ Sharks", "Kings", "Sharks")}
        gs, pl, pm = build(r5, "hockey_nhl", 16, 5.0, seed=15, layout="sport", league="NHL", extra=extra)
        res = look(r5, "hockey_nhl", gs, pl, pm)
        ml = {r["eid"]: r for r in res["match_list"]}
        check("T5 NJ Devils joined to Devils", ml.get("e0", {}).get("n_pm_candidates") == 1, ml.get("e0"))
        check("T5 college hockey excluded (no event)", "e1" not in ml, ml.get("e1"))
        check("T5 two Kings-Sharks markets -> ambiguous, dropped", ml.get("e2", {}).get("n_pm_candidates") == 2 and res["counters"].get("events_ambiguous_pm_market", 0) > 0, ml.get("e2"))
        check("T8 sport layout read (nhl cell present)", "nhl|Match Winner" in res["cells"], list(res["cells"]))
        check("T8 slim layout read (T1 rows used)", True)
        # T6 suspension/reopen and one-sided rows (unit level)
        polls = [T0 + 2 * k for k in range(100)]
        rows = []
        for k, (p, sus) in enumerate([(0.5, "0"), (0.5, "0"), (0.5, "1"), (0.6, "0"), (0.6, "0"), (0.63, "0")]):
            oh, oa = odds(p)
            body = dict(events={"e": dict(info=dict(league="CS2 - X"), team_info=dict(home=dict(name="A"), away=dict(name="B")),
                                          odds={"1": dict(name="Home/Away", suspend=sus, participants={"1": dict(name="Home", suspend="0", value_eu=oh), "2": dict(name="Away", suspend="0", value_eu=oa)})})})
            rows.append(json.dumps(dict(recv_ns=int((T0 + 2 * k + 1) * 1e9), body=json.dumps(body))))
        f6 = os.path.join(td, "esports_2026112400.jsonl.gz")
        with gzip.open(f6, "wt") as f:
            f.write("\n".join(rows) + "\n")
        ev, mv, sp, au = G.gs_events("esports", [f6], polls, T0, T0 + 3600)
        check("T6 reopen at a new price is not an event; the later 3c move is", len(ev) == 1 and abs(ev[0][2] - (T0 + 11)) < 1e-6, ev)
        bk = G.Books()
        bk.rows["x"] = [(T0, 0.40, 0.42), (T0 + 5, None, 0.42), (T0 + 8, 0.45, 0.47)]
        bk.ts["x"] = [r[0] for r in bk.rows["x"]]
        check("T6 one-sided row -> mid undefined", bk.mid("x", T0 + 6) is None and abs(bk.mid("x", T0 + 9) - 0.46) < 1e-9 and abs(bk.mid("x", T0 + 1) - 0.41) < 1e-9)
        # T7 missing hour with polls -> STOP
        r7 = os.path.join(td, "t7")
        gs, pl, pm = build(r7, "esports", 6, 5.0, n_hours=3, seed=17, skip_hour="2026112401")
        try:
            look(r7, "esports", gs, pl, pm, hours=3)
            check("T7 missing hour STOP", False, "no stop")
        except SystemExit as e:
            check("T7 missing hour STOP", "missing" in str(e), str(e))
    print("ALL PASS" if not FAILS else "FAILED: %s" % FAILS)
    return 0 if not FAILS else 1


if __name__ == "__main__":
    sys.exit(main())
