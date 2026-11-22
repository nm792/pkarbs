#!/usr/bin/env python3
"""Tests for ps_kills_vs_pmcs2.py on synthetic data. Each check can fail (a mutant in MUTANT mode must fail test 4 and 3).
usage: python3 -I feeds/test_ps_kills_vs_pmcs2.py [MODULE_PATH]"""
import sys, os, json, gzip, random, tempfile, importlib.util
here = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, here)
path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(here, "ps_kills_vs_pmcs2.py")
spec = importlib.util.spec_from_file_location("k", path); k = importlib.util.module_from_spec(spec); spec.loader.exec_module(k)
fails = []
def chk(name, ok, extra=""):
    print(("PASS " if ok else "FAIL ") + name + " " + str(extra)); 
    if not ok: fails.append(name)

def make(d, lead):
    """40 s-spaced kills alternating home/away over 20 rounds in one game; books: random walk with 1 s rows; lead = cents the favoured token rises 3 s after a kill (kept 20 s)."""
    rnd = random.Random(1); t0 = 1_800_000_000.0; msgs = []; kills = []
    hp = ap = 5; rn = 1; t = t0
    for i in range(20):
        t += 120; fav = "home_team" if i % 2 == 0 else "away_team"
        if fav == "home_team": ap = max(1, ap - 1)
        else: hp = max(1, hp - 1)
        kills.append((t, fav))
        def pl(h, a, rr): return dict(game_id=77, current_round=dict(round_number=rr, home_team=dict(players=[dict(alive=j < h) for j in range(5)]), away_team=dict(players=[dict(alive=j < a) for j in range(5)])), home_team=dict(team_name="Alpha", score=0), away_team=dict(team_name="Beta", score=0))
        msgs.append(dict(match_id=1, recv_ns=int((t - 20) * 1e9), payload=pl(hp + (1 if fav == "away_team" else 0), ap + (1 if fav == "home_team" else 0), i + 1)))
        msgs.append(dict(match_id=1, recv_ns=int(t * 1e9), payload=pl(hp, ap, i + 1)))
        hp = ap = 5
    with gzip.open(os.path.join(d, "ps_sample_1.jsonl.gz"), "wt") as f:
        for m in msgs: f.write(json.dumps(m) + "\n")
    mid = 0.5; rows = []
    for s in range(0, int(t - t0) + 200):
        ts = t0 + s; mid += rnd.uniform(-.002, .002) * 0
        adj = 0.0
        for kt, fav in kills:
            if kt + 3 <= ts < kt + 23: adj += lead if fav == "home_team" else -lead
        h = 0.5 + adj; rows.append((ts, h - .01, h + .01, "H")); rows.append((ts, (1 - h) - .01, (1 - h) + .01, "A"))
    os.makedirs(d, exist_ok=True)
    json.dump(dict(cond="c", q="Counter-Strike: Alpha vs Beta (BO3)", outcomes=["Alpha", "Beta"], tokens=["H", "A"], start="x"), open(os.path.join(d, "markets.jsonl"), "w"))
    with open(os.path.join(d, "markets.jsonl"), "a") as f: f.write("\n")
    with open(os.path.join(d, "books-2027010100.jsonl"), "w") as f:
        for ts, b, a, tk in rows: f.write(json.dumps(dict(recv_ms=int(ts * 1000), asset=tk, bid=round(b, 4), ask=round(a, 4))) + "\n")

def load(d):
    fs = [os.path.join(d, "ps_sample_1.jsonl.gz")]
    mk, books = k.load_books(d, 1_800_000_000.0, 1_800_000_000.0 + 1e5)
    return [m for m in (k.load_match(f, mk, books) for f in fs) if m]

for lead, name in ((0.0, "nolead"), (0.03, "lead3c")):
    d = tempfile.mkdtemp(); make(d, lead); M = load(d)
    chk("%s: match loaded with both token books" % name, len(M) == 1 and len(M[0]["mk"]) == 1)
    R = k.run(M, 0.5); g = k.summ(R, "row", 15.0, "gross")
    if lead == 0: chk("nolead: real gross = -spread (-2c +-0.1)", abs(g["mean_c"] + 2) < 0.1, g.get("mean_c"))
    else:
        chk("lead3c: real gross = +3c - 2c spread (0.5..1.5)", 0.5 < g["mean_c"] < 1.5, g.get("mean_c"))
        n = k.summ(R, "row", 15.0, "net03"); chk("lead3c: net03 = gross - 0.75c fee (about +0.25c)", 0.0 < n["mean_c"] < 0.5, n.get("mean_c"))
        sw = k.summ(k.run(M, 0.5, "swap"), "row", 15.0, "gross"); chk("lead3c: label swap is NEGATIVE (<-4c)", sw["mean_c"] < -4, sw.get("mean_c"))
    if lead == 0:
        base = k.summ(R, "row", 15.0, "gross")
        books_before = {mk_["q"]: {t: list(b.r) for t, b in mk_["tok"].items()} for m_ in M for mk_ in m_["mk"]}
        pr = k.summ(k.run(M, 0.5, plant=0.03), "row", 15.0, "gross")
        rec = (pr["mean_c"] - base["mean_c"]) / 3.0
        chk("plant +3c on no-lead book recovered 95-105%", 0.95 <= rec <= 1.05, rec)
        books_after = {mk_["q"]: {t: list(b.r) for t, b in mk_["tok"].items()} for m_ in M for mk_ in m_["mk"]}
        chk("plant does not mutate the original rows", books_before == books_after)
        pl = []; rnd = random.Random(3)
        for _ in range(30):
            s = k.summ(k.run(M, 0.5, "placebo", rnd=rnd), "row", 15.0, "gross")
            if s.get("used"): pl.append(s["mean_c"])
        chk("placebo = -spread on no-lead book", abs(sum(pl) / len(pl) + 2) < 0.1, sum(pl) / len(pl))
d = tempfile.mkdtemp(); make(d, 0.03); M = load(d)
pl = []; rnd = random.Random(4)
for _ in range(30):
    s_ = k.summ(k.run(M, 0.5, "placebo", rnd=rnd), "row", 15.0, "gross")
    if s_.get("used"): pl.append(s_["mean_c"])
chk("placebo on LEAD book is below the real event gross (event-free times do not catch the lead)", sum(pl) / len(pl) < k.summ(k.run(M, 0.5), "row", 15.0, "gross")["mean_c"], sum(pl) / len(pl))
b = k.Book([(1.0, .4, .5), (3.0, .41, .51)])
chk("first_at_or_after respects 5 s wait", b.first_at_or_after(3.5) is None and b.first_at_or_after(2.0)[0] == 3.0)
chk("state = last row at/before t", b.state(2.9)[0] == 1.0 and b.state(0.5) is None)
print("ALL PASS" if not fails else "FAILED: %s" % fails); sys.exit(1 if fails else 0)
