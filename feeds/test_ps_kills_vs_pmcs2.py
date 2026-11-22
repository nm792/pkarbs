#!/usr/bin/env python3
"""Tests for ps_kills_vs_pmcs2.py on synthetic data; every check can fail (mutant mode: pass a mutated module path as argv[1]).
usage: python3 -I feeds/test_ps_kills_vs_pmcs2.py [MODULE_PATH]"""
import sys, os, json, gzip, random, tempfile, time, io, contextlib, importlib.util
here = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, here)
path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(here, "ps_kills_vs_pmcs2.py")
spec = importlib.util.spec_from_file_location("k", path); k = importlib.util.module_from_spec(spec); spec.loader.exec_module(k)
fails = []
def chk(name, ok, extra=""):
    print(("PASS " if ok else "FAIL ") + name + " " + str(extra))
    if not ok: fails.append(name)
T0 = 1_800_000_000.0

def make(d, lead, gaps=(120,), startround=0, nkills=20):
    """one game, kills favouring home/away alternately; gaps cycles for the spacing; books for moneyline (H,A), Map 1 (H2,A2), Map 2 (H3,A3);
    a lead = cents the favoured token rises 3 s after a kill (kept 20 s). startround>0 makes the capture start mid-game."""
    t = T0; msgs = []; kills = []
    def pl(h, a, rr): return dict(game_id=77, current_round=dict(round_number=rr, home_team=dict(players=[dict(alive=j < h) for j in range(5)]), away_team=dict(players=[dict(alive=j < a) for j in range(5)])), home_team=dict(team_name="Alpha", score=0), away_team=dict(team_name="Beta", score=0))
    for i in range(nkills):
        t += gaps[i % len(gaps)]; fav = "home_team" if i % 2 == 0 else "away_team"; kills.append((t, fav))
        hp, ap = (5, 4) if fav == "home_team" else (4, 5)
        msgs.append(dict(match_id=1, recv_ns=int((t - 5) * 1e9), payload=pl(5, 5, i + 1 + startround)))
        msgs.append(dict(match_id=1, recv_ns=int(t * 1e9), payload=pl(hp, ap, i + 1 + startround)))
    with gzip.open(os.path.join(d, "ps_sample_1.jsonl.gz"), "wt") as f:
        for m in msgs: f.write(json.dumps(m) + "\n")
    rows = []
    for s in range(0, int(t - T0) + 600):
        ts = T0 + s; adj = 0.0
        for kt, fav in kills:
            if kt + 3 <= ts < kt + 23: adj += lead if fav == "home_team" else -lead
        h = 0.5 + adj
        for ha, aa in (("H", "A"), ("H2", "A2"), ("H3", "A3")):
            rows.append((ts, ha, h - .01, h + .01, 50)); rows.append((ts, aa, (1 - h) - .01, (1 - h) + .01, 50))
    with open(os.path.join(d, "markets.jsonl"), "w") as f:
        for c, q, a, b in (("c", "Counter-Strike: Alpha vs Beta (BO3)", "H", "A"), ("c1", "Counter-Strike: Alpha vs Beta - Map 1 Winner", "H2", "A2"), ("c2", "Counter-Strike: Alpha vs Beta - Map 2 Winner", "H3", "A3")):
            f.write(json.dumps(dict(cond=c, q=q, outcomes=["Alpha", "Beta"], tokens=[a, b], start="x")) + "\n")
    with open(os.path.join(d, "books-" + time.strftime("%Y%m%d%H", time.gmtime(T0)) + ".jsonl"), "w") as f:
        for ts, tk, b, a, sz in rows: f.write(json.dumps(dict(recv_ms=int(ts * 1000), asset=tk, bid=round(b, 4), ask=round(a, 4), asks=[dict(price=round(a, 4), size=sz)])) + "\n")

def load(d):
    mk, books = k.load_books(d, T0, T0 + 1e5)
    return [m for m in (k.load_match(os.path.join(d, "ps_sample_1.jsonl.gz"), mk, books) for _ in [0]) if m]
def gross(R, **kw): return k.summ(R, "row", 15.0, "gross", **kw)
def quiet(fn, *a, **kw):
    with contextlib.redirect_stdout(io.StringIO()): return fn(*a, **kw)

# ---- lead / no-lead at 120 s spacing
d0 = tempfile.mkdtemp(); make(d0, 0.0); M0 = load(d0)
chk("match loaded with 3 markets with both token books", len(M0) == 1 and len(M0[0]["mk"]) == 3, len(M0[0]["mk"]) if M0 else 0)
R0 = k.run(M0, 0.5)
chk("ONE row per event (20 events, not 20 x markets)", len(R0[1]) == 20, len(R0[1]))
chk("Map N rule: moneyline + Map 1 get the events, Map 2 gets none (2 results per event)", all(len(ev["rs"]) == 2 for ev in R0[1]))
chk("nolead: real gross = -spread (-2c +-0.1)", abs(gross(R0)["mean_c"] + 2) < 0.1, gross(R0)["mean_c"])
base = gross(k.run(M0, 0.5, only_isolated=True)); pr = gross(k.run(M0, 0.5, plant=0.03, only_isolated=True))
rec = (pr["mean_c"] - base["mean_c"]) / 3.0
chk("plant +3c at 120 s spacing recovered 95-105%", 0.95 <= rec <= 1.05, rec)
snap = lambda: {(mk_["q"], t): list(b.r) for mk_ in M0[0]["mk"] for t, b in mk_["tok"].items()}
bf = snap(); k.run(M0, 0.5, plant=0.03)
chk("plant does not mutate the original rows (all markets)", bf == snap())
rnd = random.Random(3); pl = [gross(k.run(M0, 0.5, "placebo", rnd=rnd)).get("mean_c") for _ in range(20)]
pl = [x for x in pl if x is not None]
chk("placebo = -spread on no-lead book", len(pl) > 0 and abs(sum(pl) / len(pl) + 2) < 0.1, pl[:1])
sh = gross(k.run(M0, 0.5, "shift"))
chk("shift +300 s control runs and reads -spread on no-lead book", sh.get("used", 0) > 0 and abs(sh["mean_c"] + 2) < 0.1, sh.get("mean_c"))

d1 = tempfile.mkdtemp(); make(d1, 0.03); M1 = load(d1); R1 = k.run(M1, 0.5)
chk("lead3c: real gross = +3c - 2c spread (0.5..1.5)", 0.5 < gross(R1)["mean_c"] < 1.5, gross(R1)["mean_c"])
n3 = k.summ(R1, "row", 15.0, "net03"); chk("lead3c: net03 = gross - 0.75c fee (about +0.25c)", 0.0 < n3["mean_c"] < 0.5, n3["mean_c"])
chk("lead3c: label swap NEGATIVE (<-4c)", gross(k.run(M1, 0.5, "swap"))["mean_c"] < -4)
chk("summary reports row gap, markout age and ask size", n3["median_row_gap_s"] is not None and n3["median_markout_age_s"] is not None and n3["median_ask_size"] == 50, (n3["median_row_gap_s"], n3["median_markout_age_s"], n3["median_ask_size"]))
c99 = k.summ(R1, "row", 15.0, "net03", ci=0.99); chk("99% interval is wider or equal to 95%", c99["boot_c"][1] - c99["boot_c"][0] >= n3["boot_c"][1] - n3["boot_c"][0] - 1e-9, (c99["boot_c"], n3["boot_c"]))
sp = k.shuffle_p(M1, 0.5, nperm=300); chk("within-match shuffle p is small for a real 3c lead", sp is not None and sp < 0.05, sp)
chk("mid-game start: Map N markets skipped (1 result per event)", all(len(ev["rs"]) == 1 for ev in k.run((lambda dd: (make(dd, 0.0, startround=6), load(dd))[1])(tempfile.mkdtemp()), 0.5)[1]))

# ---- spacing: the checker's failing case (20 s) must not give 195%
d2 = tempfile.mkdtemp(); make(d2, 0.0, gaps=(20,), nkills=30); M2 = load(d2)
rec_all = (gross(k.run(M2, 0.5, plant=0.03))["mean_c"] - gross(k.run(M2, 0.5))["mean_c"]) / 3.0
chk("20 s spacing, plant on ALL events is outside the band (documents the checker's 195% case)", not (0.95 <= rec_all <= 1.05), rec_all)
chk("20 s spacing: fewer than 5 isolated events (plant 'not measurable')", gross(k.run(M2, 0.5, only_isolated=True)).get("used", 0) < 5, gross(k.run(M2, 0.5, only_isolated=True)).get("used"))
d3 = tempfile.mkdtemp(); make(d3, 0.0, gaps=(120, 20), nkills=30); M3 = load(d3)
iso = k.run(M3, 0.5, only_isolated=True); b3 = gross(iso); p3 = gross(k.run(M3, 0.5, plant=0.03, only_isolated=True))
r3 = (p3["mean_c"] - b3["mean_c"]) / 3.0
chk("mixed spacing 120/20 s: plant on isolated events recovered 95-105%", b3.get("used", 0) >= 5 and 0.95 <= r3 <= 1.05, (b3.get("used"), r3))

# ---- gate through main()
sd1 = tempfile.mkdtemp(); os.rename(os.path.join(d1, "ps_sample_1.jsonl.gz"), os.path.join(sd1, "ps_sample_1.jsonl.gz"))
g1 = quiet(k.main, sd1, d1, 0.5, 0.03, 20)
chk("gate passes on the 120 s lead fixture and real numbers are printed", g1["gate_pass"] and isinstance(g1["real"], dict), (g1["gate_pass"], g1["controls"].get("plant")))
sd2 = tempfile.mkdtemp(); os.rename(os.path.join(d2, "ps_sample_1.jsonl.gz"), os.path.join(sd2, "ps_sample_1.jsonl.gz"))
g2 = quiet(k.main, sd2, d2, 0.5, 0.03, 20)
chk("gate FAILS and withholds the real number at 20 s spacing", (not g2["gate_pass"]) and isinstance(g2["real"], str) and g2["real"].startswith("WITHHELD"), g2["real"][:40] if isinstance(g2["real"], str) else g2["real"])

# ---- book helpers
b = k.Book([(1.0, .4, .5), (3.0, .41, .51)])
chk("first_at_or_after respects 5 s wait", b.first_at_or_after(3.5) is None and b.first_at_or_after(2.0)[0] == 3.0)
chk("state = last row at/before t", b.state(2.9)[0] == 1.0 and b.state(0.5) is None)
d4 = tempfile.mkdtemp(); make(d4, 0.0); os.rename(os.path.join(d4, [x for x in os.listdir(d4) if x.startswith("books-")][0]), os.path.join(d4, "books-2020010100.jsonl"))
chk("hour filter skips a books file far outside the window", len(k.load_books(d4, T0, T0 + 1e5)[1]) == 0)
print("ALL PASS" if not fails else "FAILED: %s" % fails); sys.exit(1 if fails else 0)
