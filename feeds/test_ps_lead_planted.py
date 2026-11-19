#!/usr/bin/env python3
"""Planted-case test of feeds/ps_lead_test.py (checker, 18 Nov 2026). Synthetic PandaScore hour files + Polymarket markets/books with a KNOWN feed lead.
(a) PM moves +10 s after the feed message -> lead ~ +10 s, bar met; (b) PM moves 10 s BEFORE -> lead ~ -10 s, no lead; (c) PM never reacts to events (background noise only) -> no pass.
Dota (kills) and CS2 (round score), map and match series. Prints ALL PASS as the last line only if every check passed.  Run: python3 -I feeds/test_ps_lead_planted.py"""
import gzip, json, os, random, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
T0 = 1795046400.0
FAILS = []


def ok(c, m):
    print(("PASS " if c else "FAIL ") + m)
    if not c:
        FAILS.append(m)


def build(root, title, shift, n=40, seed=3, react=True):
    rnd = random.Random(seed)
    ps, pm = os.path.join(root, "ps"), os.path.join(root, "pm")
    os.makedirs(ps), os.makedirs(pm)
    msgs, mk, bk = [], [], []
    for i in range(n):
        mid, A, B = 100 + i, "Alpha%d" % i, "Bravo%d" % i
        tA, tB, mA, mB = "a%d" % i, "b%d" % i, "ma%d" % i, "mb%d" % i
        mk.append(dict(cond="c%d" % i, q="X: %s vs %s - Game 1 Winner" % (A, B), smt="moneyline", outcomes=[A, B], tokens=[tA, tB]))
        mk.append(dict(cond="m%d" % i, q="X: %s vs %s" % (A, B), smt="moneyline", outcomes=[A, B], tokens=[mA, mB]))
        t = T0 + 3600 + i * 3000.0
        sa = sb = 0
        slug = "cs-go" if title == "cs2" else "dota-2"

        def msg(tt):
            if title == "cs2":
                p = dict(game_id=7 + i, available_fields=["round_score"], home_team=dict(team_id=1, team_name=A, score=sa), away_team=dict(team_id=2, team_name=B, score=sb))
            else:
                p = dict(game_id=7 + i, available_fields=["kills"], radiant=dict(team_id=1, team_name=A, kills=sa), dire=dict(team_id=2, team_name=B, kills=sb))
            return dict(recv_ns=int(tt * 1e9), match_id=mid, slug=slug, kind="update", payload=p)
        msgs.append(dict(recv_ns=int(t * 1e9), match_id=mid, slug=slug, kind="hello", payload={}))
        msgs.append(msg(t + 1))
        acts, pa = [], 0.5
        for r in range(16):
            t += 130 + rnd.uniform(0, 60)
            up = 1 if rnd.random() < .5 else -1
            sa, sb = (sa + 1, sb) if up > 0 else (sa, sb + 1)
            msgs.append(msg(t))
            if react:
                acts.append((t + shift + rnd.uniform(-.2, .2), "ev", up))
        tn = T0 + 3600 + i * 3000.0
        while tn < t + 120:
            tn += rnd.uniform(8, 25)
            acts.append((tn, "noise", rnd.choice((-1, 1))))
        w = 0.0
        for (tm, k, s) in sorted(acts):
            if k == "ev":
                pa = min(.9, max(.1, pa + .04 * s))
            else:
                w = max(-.03, min(.03, w + .01 * s))
            mid_ = pa + w
            for tk, v in ((tA, mid_), (tB, 1 - mid_)):
                bk.append(dict(tk=tk, ms=int(tm * 1000), bids=[dict(price="%.3f" % (v - .01))], asks=[dict(price="%.3f" % (v + .01))]))
            if k == "ev":
                bk.append(dict(tk=mA, ms=int(tm * 1000), bids=[dict(price="%.3f" % (.49 + .005 * s))], asks=[dict(price="%.3f" % (.51 + .005 * s))]))
    msgs.sort(key=lambda r: r["recv_ns"])
    bk.sort(key=lambda r: r["ms"])
    with gzip.open(os.path.join(ps, "pandascore_2026111901.jsonl.gz"), "wt") as f:
        for m in msgs:
            f.write(json.dumps(m) + "\n")
    open(os.path.join(pm, "markets.jsonl"), "w").write("".join(json.dumps(m) + "\n" for m in mk))
    open(os.path.join(pm, "books.jsonl"), "w").write("".join(json.dumps(b) + "\n" for b in bk))


def run(root):
    out = os.path.join(root, "o.json")
    p = subprocess.run([sys.executable, "-I", os.path.join(HERE, "ps_lead_test.py"), "--ps", root + "/ps", "--pm", root + "/pm", "--out", out], capture_output=True, text=True)
    if p.returncode:
        print(p.stderr[-1500:])
        raise SystemExit("ps_lead_test.py failed")
    return json.load(open(out))["cells"]


def main():
    tmp = tempfile.mkdtemp(prefix="pslead_")
    try:
        for title in ("cs2", "dota2"):
            for name, shift, react in (("a_pm_10s_after", 10.0, True), ("b_pm_10s_before", -10.0, True), ("c_pm_never_moves", 0.0, False)):
                d = os.path.join(tmp, title + name)
                build(d, title, shift, react=react)
                c = run(d)["%s|map|all" % title]
                if name.startswith("a"):
                    ok(c["n_events"] >= 30 and 9.0 <= c["median_real_lead_s"] <= 11.0 and c["verdict"].startswith("meets bar"),
                       "%s (a) PM +10 s after the feed: n %d, median real lead %.2f s, verdict %s" % (title, c["n_events"], c["median_real_lead_s"], c["verdict"]))
                elif name.startswith("b"):
                    ok(-11.0 <= c["median_real_lead_s"] <= -9.0 and c["verdict"].startswith("no lead"),
                       "%s (b) PM 10 s BEFORE the feed: median real lead %.2f s, verdict %s" % (title, c["median_real_lead_s"], c["verdict"]))
                else:
                    ok(not c["verdict"].startswith("meets"),
                       "%s (c) PM never reacts to events (only background noise): events %d, with onset %d, verdict %s" % (title, c["n_events"], c["n_with_onset"], c["verdict"]))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("ALL PASS" if not FAILS else "FAILURES: %d" % len(FAILS))
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
