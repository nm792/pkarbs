#!/usr/bin/env python3
"""Self test of feeds/ps_cs2_daily_look.py: end-to-end through synthetic raw files (PandaScore hour files, capture event log, Polymarket markets/books).
Run: python3 -I feeds/test_ps_cs2_daily_look.py   (prints ALL PASS as the last line only if every check passed)"""
import calendar, gzip, json, os, random, shutil, subprocess, sys, tempfile, time

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(HERE, "ps_cs2_daily_look.py")
sys.path.insert(0, HERE)
import ps_cs2_daily_look as S

D19 = 1795046400.0            # 2026-11-19T00:00Z
FAILS = []


def ok(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        FAILS.append(msg)


def iso(t):
    return time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(t)) + ".000+00:00"


def build(root, n=30, lead=8.0, lat=lambda r: 0, seed=1, day=0, extra=None, evlog_extra=(), pm_markets_extra=()):
    """n CS2 matches on UTC day `day` (0 = 19 Nov), 40 min apart from 01:00Z, one map each, 14 rounds. PM moves lead seconds after the feed receive time.
    extra(msgs, mk, bk, evl) may add cases."""
    rnd = random.Random(seed)
    ps, pm = os.path.join(root, "ps"), os.path.join(root, "pm")
    os.makedirs(ps, exist_ok=True)
    os.makedirs(pm, exist_ok=True)
    msgs, mk, bk, evl = [], [], [], [dict(t=iso(D19 - 7200), kind="start")]
    for i in range(n):
        mid, A, B = 1000 + i + 100 * day, "Alpha %d" % (i + 100 * day), "Bravo %d" % (i + 100 * day)
        tkA, tkB, mtA, mtB = "a%d_%d" % (i, day), "b%d_%d" % (i, day), "ma%d_%d" % (i, day), "mb%d_%d" % (i, day)
        mk.append(dict(cond="c%d_%d" % (i, day), q="Counter-Strike: %s vs %s - Map 1 Winner" % (A, B), smt="moneyline", outcomes=[A, B], tokens=[tkA, tkB]))
        mk.append(dict(cond="m%d_%d" % (i, day), q="Counter-Strike: %s vs %s" % (A, B), smt="moneyline", outcomes=[A, B], tokens=[mtA, mtB]))
        t = D19 + day * 86400 + 3600 + i * 2400.0
        sa = sb = 0
        pa = 0.5
        evl.append(dict(t=iso(t), kind="connected", match_id=mid, slug="cs-go"))
        for tk in (tkA, tkB, mtA, mtB):
            bk.append(dict(tk=tk, ms=int((t - 200) * 1000), bids=[dict(price="0.49")], asks=[dict(price="0.51")]))

        def msg(tt, la, kind="update"):
            return dict(recv_ns=int(tt * 1e9), match_id=mid, slug="cs-go", kind=kind, payload=dict(
                game_id=77 + i + 100 * day, available_fields=["round_score"], home_team=dict(team_id=1, team_name=A, score=sa),
                away_team=dict(team_id=2, team_name=B, score=sb), latency=[dict(field="round_score", delay=la)]))
        msgs.append(dict(recv_ns=int(t * 1e9), match_id=mid, slug="cs-go", kind="hello", payload={}))
        msgs.append(msg(t + 1, 0))
        acts = []
        for r in range(14):
            t += 130 + rnd.uniform(0, 60)
            up = +1 if rnd.random() < .5 else -1
            if up > 0:
                sa += 1
            else:
                sb += 1
            msgs.append(msg(t, lat(r)))
            acts.append((t + lead + rnd.uniform(-.2, .2), "ev", up))
        tn = D19 + day * 86400 + 3600 + i * 2400.0
        while tn < t + 120:
            tn += rnd.uniform(8, 25)
            acts.append((tn, "noise", rnd.choice((-1, 1))))
        w = 0.0
        for (tm, kind_, s_) in sorted(acts):
            if kind_ == "ev":
                pa = min(.9, max(.1, pa + .04 * s_))
                bk.append(dict(tk=mtA, ms=int(tm * 1000), bids=[dict(price="%.3f" % (.49 + .005 * s_))], asks=[dict(price="%.3f" % (.51 + .005 * s_))]))
            else:
                w = max(-.03, min(.03, w + .01 * s_))
            mid = pa + w
            bk.append(dict(tk=tkA, ms=int(tm * 1000), bids=[dict(price="%.3f" % (mid - .01))], asks=[dict(price="%.3f" % (mid + .01))]))
            bk.append(dict(tk=tkB, ms=int(tm * 1000), bids=[dict(price="%.3f" % (1 - mid - .01))], asks=[dict(price="%.3f" % (1 - mid + .01))]))
    # closing row in the last hour of the day so the day counts as complete (a non-CS2 match)
    msgs.append(dict(recv_ns=int((D19 + day * 86400 + 86400 - 600) * 1e9), match_id=999, slug="dota-2", kind="update", payload=dict(game_id=1)))
    if extra:
        extra(msgs, mk, bk, evl)
    msgs.sort(key=lambda r: r["recv_ns"])
    bk.sort(key=lambda r: r["ms"])
    byh = {}
    for m in msgs:
        h = time.strftime("%Y%m%d%H", time.gmtime(m["recv_ns"] / 1e9))
        byh.setdefault(h, []).append(m)
    for h, L in byh.items():
        with gzip.open(os.path.join(ps, "pandascore_%s.jsonl.gz" % h), "at") as f:
            for m in L:
                f.write(json.dumps(m) + "\n")
    with open(os.path.join(pm, "markets.jsonl"), "a") as f:
        for m in mk:
            f.write(json.dumps(m) + "\n")
    with open(os.path.join(pm, "books.jsonl"), "a") as f:
        for b in bk:
            f.write(json.dumps(b) + "\n")
    with gzip.open(os.path.join(root, "events.jsonl.gz"), "at") as f:
        for e in evl + list(evlog_extra):
            f.write(json.dumps(e) + "\n")
    return root


def run(root, script=SCRIPT, copied=None, extra_args=(), expect_fail=False):
    out = os.path.join(root, "result.json")
    if os.path.exists(out):
        os.remove(out)
    K = 1
    cmd = [sys.executable, "-I", script, "--ps", os.path.join(root, "ps"), "--pm", os.path.join(root, "pm"), "--evlog", os.path.join(root, "events.jsonl.gz"),
           "--copied-at-utc", str(copied if copied is not None else D19 + 3 * 86400), "--clock-note", "test", "--out", out] + list(extra_args)
    p = subprocess.run(cmd, capture_output=True, text=True)
    if expect_fail:
        return p
    if p.returncode != 0:
        print(p.stdout[-800:], p.stderr[-1500:])
        raise SystemExit("run failed")
    return json.load(open(out))


def prim(res):
    return res["cells"][S.PRIMARY]


def oracle_onset(rows, t0, sign):
    base = None
    for ts, m in rows:
        if ts <= t0 - 60.0:
            base = m
    if base is None:
        return None, False
    for ts, m in rows:
        if t0 - 60.0 <= ts <= t0 + 60.0 and sign * (m - base) >= 0.02:
            return ts - t0, True
    return None, True


def main():
    tmp = tempfile.mkdtemp(prefix="pscs2_")
    try:
        # 1. onset function against an independent brute-force oracle (the ps_lead_test.onset rule)
        rnd = random.Random(5)
        bad = 0
        for _ in range(3000):
            rows, t = [], 0.0
            for _k in range(rnd.randint(1, 25)):
                t += rnd.uniform(0, 12)
                rows.append((t, round(rnd.uniform(0.2, 0.8), 2)))
            t0, sg = rnd.uniform(30, 150), rnd.choice((-1, 1))
            bad += S.onset_from(rows, t0, sg) != oracle_onset(rows, t0, sg)
        ok(bad == 0, "onset_from equals the brute-force ps_lead_test rule on 3000 random book/time/sign cases (%d differences)" % bad)
        ok(abs(S.boundary(20) - 2.60 / (20 / 60) ** 0.5) < 1e-12 and S.boundary(60) == 2.60 and S.boundary(100) == 2.60 and S.boundary(6) > S.boundary(30), "boundary = 2.60/sqrt(n/60), falling in n, capped at 2.60 (not 2.60*sqrt)")

        # 2. a +8 s feed lead is found end to end
        a = build(os.path.join(tmp, "lead8"), lead=8.0)
        r = run(a)
        c = prim(r)
        ok(c["n_matches_used"] == 30 and r["look"] == 1 and not r["smoke_not_a_result"], "lead8: 30 matches, look 1, not marked smoke (%s)" % c["n_matches_used"])
        ok(c["z_eq"] > c["boundary_z"] and c["verdict"].startswith("meets bar"), "lead8: z_eq %.1f > boundary %.2f and verdict '%s'" % (c["z_eq"], c["boundary_z"], c["verdict"]))
        ok(c["median_real_lead_s"] > 3.0 and c["pct_price_after_feed"] >= 60, "lead8: median real lead positive, price after feed >= 60 pct (%.2f s)" % c["median_real_lead_s"])
        ok(r["plant"]["events_checked"] > 250 and not r["plant"]["violations"], "lead8: plant identities hold on every event (+10 s step, -10 s step, team-to-token map): %d events, violations %s" % (r["plant"]["events_checked"], r["plant"]["violations"]))
        ok(r["cells"]["cs2|match|lat0"]["verdict"].startswith("(informational)") and r["cells"]["cs2|match|lat0"]["n_events_with_onset"] == 0, "lead8: match-winner market (1c moves) gives no onset and is informational only")

        # 3. PM first by 30 s is never a pass
        b = build(os.path.join(tmp, "pm30"), lead=-30.0)
        cb = prim(run(b))
        ok(cb["z_eq"] < -cb["boundary_z"] and not cb["verdict"].startswith("meets"), "pm_first: z_eq %.1f below -boundary %.2f, never 'meets bar' (%s)" % (cb["z_eq"], cb["boundary_z"], cb["verdict"]))

        # 4. no lead (PM moves at the feed time): not a pass
        z = build(os.path.join(tmp, "lead0"), lead=0.0)
        cz = prim(run(z))
        ok(not cz["verdict"].startswith("meets"), "lead0: no pass (%s, z_eq %s)" % (cz["verdict"], cz["z_eq"]))

        # 5. latency strata: only round_score delay == 0 events are in the primary cell
        l = build(os.path.join(tmp, "lat"), lead=8.0, lat=lambda r: 0 if r % 2 == 0 else 500)
        rl = run(l)
        n0, n1 = rl["cells"]["cs2|map|lat0"]["n_events"], rl["cells"]["cs2|map|lat>0"]["n_events"]
        ok(n0 == n1 == 30 * 7, "latency strata: lat0 %d and lat>0 %d events split by the producing message's round_score delay" % (n0, n1))
        ok(rl["cells"]["cs2|map|all"]["n_events"] == n0 + n1 + rl["cells"]["cs2|map|lat_unknown"]["n_events"], "latency strata partition the 'all' cell")

        # 6. exclusions are counted: score jump of 2, straddling match, match in progress at the cut, rematch
        def extra(msgs, mk, bk, evl):
            def m(mid, tt, sa, sb, gid, nm=("Zeta", "Yoyo"), kind="update"):
                return dict(recv_ns=int(tt * 1e9), match_id=mid, slug="cs-go", kind=kind, payload=dict(game_id=gid, available_fields=["round_score"], home_team=dict(team_id=1, team_name=nm[0], score=sa), away_team=dict(team_id=2, team_name=nm[1], score=sb), latency=[dict(field="round_score", delay=0)]))
            # straddler: first message 18 Nov 23:50Z, continues on 19 Nov
            msgs += [m(5001, D19 - 600, 0, 0, 501), m(5001, D19 + 600, 1, 0, 501), m(5001, D19 + 700, 2, 0, 501)]
            mk.append(dict(cond="s1", q="Counter-Strike: Zeta vs Yoyo - Map 1 Winner", smt="moneyline", outcomes=["Zeta", "Yoyo"], tokens=["zs", "ys"]))
            # in progress at the cut: last message 23:50Z
            msgs += [m(5002, D19 + 86400 - 3000, 0, 0, 502, ("Eta", "Theta")), m(5002, D19 + 86400 - 2900, 1, 0, 502, ("Eta", "Theta")), m(5002, D19 + 86400 - 600, 2, 0, 502, ("Eta", "Theta"))]
            mk.append(dict(cond="p1", q="Counter-Strike: Eta vs Theta - Map 1 Winner", smt="moneyline", outcomes=["Eta", "Theta"], tokens=["et", "tt"]))
            # score jump of 2 in a fresh complete match
            msgs += [m(5003, D19 + 7200, 0, 0, 503, ("Iota", "Kappa")), m(5003, D19 + 7260, 2, 0, 503, ("Iota", "Kappa")), m(5003, D19 + 7320, 3, 0, 503, ("Iota", "Kappa"))]
            mk.append(dict(cond="j1", q="Counter-Strike: Iota vs Kappa - Map 1 Winner", smt="moneyline", outcomes=["Iota", "Kappa"], tokens=["it", "kt"]))
            for tk in ("it", "kt"):
                bk.append(dict(tk=tk, ms=int((D19 + 7000) * 1000), bids=[dict(price="0.49")], asks=[dict(price="0.51")]))
            # rematch: two PM markets with the same names
            msgs += [m(5004, D19 + 9000, 0, 0, 504, ("Lam", "Mu")), m(5004, D19 + 9060, 1, 0, 504, ("Lam", "Mu"))]
            for j in (1, 2):
                mk.append(dict(cond="r%d" % j, q="Counter-Strike: Lam vs Mu - Map 1 Winner", smt="moneyline", outcomes=["Lam", "Mu"], tokens=["l%d" % j, "u%d" % j]))
                for tk in ("l%d" % j, "u%d" % j):
                    bk.append(dict(tk=tk, ms=int((D19 + 8800) * 1000), bids=[dict(price="0.49")], asks=[dict(price="0.51")]))
        e = build(os.path.join(tmp, "excl"), lead=8.0, extra=extra)
        re_ = run(e)
        ex = re_["match_exclusions"]
        ok(ex.get("match_straddles_start_excluded") == 1, "straddling match excluded and counted (%s)" % ex)
        ok(ex.get("match_in_progress_at_cut_not_counted_yet") == 1, "match with a message in the last 30 min before the cut is not counted yet, and counted (%s)" % ex)
        ok(re_["drops"].get("events_score_jump_not_1_excluded") == 1, "score jump of 2 excluded and counted (%s)" % re_["drops"].get("events_score_jump_not_1_excluded"))
        ok(re_["drops"].get("market_ambiguous_rematch_excluded", 0) >= 1, "rematch (two PM markets, same names) excluded and counted")
        ok(prim(re_)["n_matches_used"] == 30, "exclusions do not change the 30 clean matches (%d)" % prim(re_)["n_matches_used"])

        # 7. earlier matches never change at the next look (per-match d identical; in-progress match appears once complete)
        d2 = os.path.join(tmp, "two")
        build(d2, lead=8.0, extra=extra)
        r1 = run(d2)
        build(d2, n=3, lead=8.0, day=1, seed=9)
        r2 = run(d2)
        d1_, d2_ = prim(r1)["per_match_d"], prim(r2)["per_match_d"]
        same = all(d2_.get(k) == v for k, v in d1_.items())
        ok(r2["look"] == 2 and same and len(d2_) > len(d1_), "look 2 keeps every look-1 per-match d bit-identical (%d matches) and adds the new ones (%d)" % (len(d1_), len(d2_)))
        ok(r2["match_exclusions"].get("match_in_progress_at_cut_not_counted_yet", 0) == 0 and "5002" not in {str(k) for k in d1_} and r2["cells"]["cs2|map|all"]["n_matches_seen"] > r1["cells"]["cs2|map|all"]["n_matches_seen"], "the match in progress at the cut is counted at look 2 when complete")

        # 8. completeness refusals and range
        p = run(a, copied=D19 + 86400 + 100, expect_fail=True)
        ok(p.returncode != 0 and "copied" in (p.stderr + p.stdout), "refuses when the files were copied before the end of the day + 10 min")
        s1 = build(os.path.join(tmp, "stopped"), lead=8.0, evlog_extra=[dict(t=iso(D19 + 5000), kind="stopped", reason="free space")])
        p = run(s1, expect_fail=True)
        ok(p.returncode != 0 and "stopped" in (p.stderr + p.stdout), "refuses when the capture logged 'stopped' inside the window")
        s2 = build(os.path.join(tmp, "lost"), lead=8.0, evlog_extra=[dict(t=iso(D19 + 6000), kind="connected", match_id=777777, slug="cs-go")])
        p = run(s2, expect_fail=True)
        ok(p.returncode != 0 and "lost or unshipped" in (p.stderr + p.stdout), "refuses when the capture log shows a connected CS2 match that has no messages in the copied files")
        s3 = build(os.path.join(tmp, "silent"), lead=8.0, evlog_extra=[dict(t=iso(D19 + 6000), kind="silent", match_id=1003, gap_s=400)])
        r3 = run(s3)
        ok(r3["match_exclusions"].get("match_had_silent_gap_gt_300s_excluded") == 1 and prim(r3)["n_matches_used"] == 29, "a match with a silent gap > 300 s is excluded and counted (29 left)")
        t1 = os.path.join(tmp, "trunc")
        build(t1, lead=8.0)
        fz = sorted(os.listdir(os.path.join(t1, "ps")))[1]
        raw = open(os.path.join(t1, "ps", fz), "rb").read()
        open(os.path.join(t1, "ps", fz), "wb").write(raw[: len(raw) // 2])
        p = run(t1, expect_fail=True)
        ok(p.returncode != 0 and "truncated" in (p.stderr + p.stdout), "refuses on a truncated hour file")
        p = run(a, extra_args=("--t-start", "1"), expect_fail=True)
        ok(p.returncode != 0, "--t-start is refused without --smoke")
        rs = run(a, extra_args=("--smoke",))
        ok(rs["smoke_not_a_result"] is True, "--smoke runs and marks the output smoke_not_a_result")

        # 9. mutants: a broken plant path must be caught by the identity checks (verdict unknown, never a pass)
        src = open(SCRIPT).read()
        mut = src.replace("(e[\"t\"] + PLANT_DT, PLANT_C)), e[\"t\"], +1)\n            pl_m", "(e[\"t\"] + PLANT_DT, -PLANT_C)), e[\"t\"], +1)\n            pl_m", 1)
        ok(mut != src, "mutant 1 built (plus step with the wrong sign)")
        mp = os.path.join(HERE, "_mut_ps_cs2.py")
        open(mp, "w").write(mut)
        try:
            rm = run(a, script=mp)
            ok(rm["plant"]["violations"].get("plus_step_not_recovered", 0) > 0 and prim(rm)["verdict"].startswith("unknown (plant"), "mutant 1 (plant step wrong sign): identity check fires and no verdict is given (%s)" % prim(rm)["verdict"][:60])
        finally:
            os.remove(mp)
        mut2 = src.replace("real, has_base = onset_from(window_rows(tk, e[\"t\"]), e[\"t\"], +1)", "real, has_base = onset_from(window_rows(otk, e[\"t\"]), e[\"t\"], +1)", 1)
        ok(mut2 != src, "mutant 2 built (real leads read from the OTHER token)")
        open(mp, "w").write(mut2)
        try:
            rm2 = run(a, script=mp)
            ok(not prim(rm2)["verdict"].startswith("meets"), "mutant 2: the true +8 s lead is NOT reported when the wrong token is read")
        finally:
            os.remove(mp)

        # 10. null behaviour: shuffled-sign fixtures never pass (40 independent seeds, no-lead fixture with random PM reaction -30..+30 s symmetric)
        passes = 0
        for sd in range(12):
            nd = build(os.path.join(tmp, "null%d" % sd), n=14, lead=random.Random(sd).uniform(-30, 30) if False else 0.0, seed=100 + sd)
            passes += prim(run(nd))["verdict"].startswith("meets")
        ok(passes == 0, "12 no-lead fixtures (14 matches each): %d passes" % passes)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("ALL PASS" if not FAILS else "FAILURES: %d" % len(FAILS))
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
