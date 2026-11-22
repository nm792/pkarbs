#!/usr/bin/env python3
"""Tests for feeds/audit_ps_inround.py. No network. Every check can fail: oracles, mutants, planted and null cases.
usage: python3 -I feeds/test_audit_ps_inround.py"""
import os, sys, random, statistics as st
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import audit_ps_inround as A

FAILS = []
def ok(c, msg):
    print(("ok   " if c else "FAIL ") + msg)
    if not c: FAILS.append(msg)

def pl(alive): return [{"alive": a} for a in alive]
def msg(t, gid, rnd, ha, aa, sc=(0, 0), map_id=8):
    return {"recv_ns": int(t * 1e9), "payload": {"game_id": gid, "map_id": map_id, "home_team": {"score": sc[0]}, "away_team": {"score": sc[1]},
            "current_round": {"round_number": rnd, "home_team": {"players": pl(ha)}, "away_team": {"players": pl(aa)}}}}

# ---- events oracle
S = [msg(0, 10, 1, [1] * 5, [1] * 5), msg(5, 10, 1, [1] * 4, [1] * 5),        # home loses a player -> kill FOR away at t=5
     msg(20, 10, 1, [1] * 4, [1] * 4),                                         # away loses one -> kill for home at t=20
     msg(40, 10, 2, [1] * 5, [1] * 5, sc=(1, 0)),                              # new round: alive resets, home score +1 -> round end home (t=40)
     msg(60, 11, 1, [1] * 5, [1] * 5), msg(65, 11, 1, [1] * 5, [1] * 4)]       # next map (game_id 11): kill for home at t=65
ev = A.events(S)
exp = [(5.0, "K", "away_team", 10, 1), (20.0, "K", "home_team", 10, 1), (40.0, "T", "home_team", 10, 2), (65.0, "K", "home_team", 11, 1)]
ok(ev == exp, f"events oracle {ev}")
ok(not any(e[0] == 60 for e in ev), "mutant: alive reset / new game_id is not an event")
S2 = [msg(0, 10, 1, [1] * 5, [1] * 5), msg(5, 10, 2, [1] * 4, [1] * 5)]       # alive drops but the ROUND CHANGED -> not a kill
ok(A.events(S2) == [], "mutant: alive drop across a round change is not a kill")
ok(A.dedup([(0, "K", "a", 1, 1), (10, "K", "a", 1, 1), (16, "K", "a", 1, 1), (17, "T", "a", 1, 1)]) == [(0, "K", "a", 1, 1), (16, "K", "a", 1, 1), (17, "T", "a", 1, 1)], "dedup 15 s per kind")
ok(len(A.first_per_round([(0, "K", "a", 1, 1), (3, "K", "b", 1, 1), (9, "K", "a", 1, 2)])) == 2, "first kill per round")

ev_all = [(10.0, "K", "a", 1, 1), (50.0, "K", "a", 1, 2), (52.0, "T", "a", 1, 2), (200.0, "K", "a", 2, 1), (205.0, "T", "a", 1, 9)]
kept = A.no_round_end_within(ev_all, [e for e in ev_all if e[1] == "K"])
ok([e[0] for e in kept] == [10.0, 200.0], f"round-end contamination filter: kill 2 s before a round end dropped, other-game round end ignored ({[e[0] for e in kept]})")

# ---- A1: map ordinal comes from game_id rank, NOT map_id (map_id here is a pool id 31 / 8)
ok(A.ordinals([238559, 238558, 238558]) == {238558: 1, 238559: 2}, "A1 map ordinal = rank of game_id")

# ---- A2 team mapping
ok(A.team_map(["NIP", "BIG"], "BIG", "NIP") == {0: "away_team", 1: "home_team"}, "A2 two-team market mapped")
ok(A.team_map(["Yes", "No"], "BIG", "NIP") is None, "A2 Yes/No market refused")
ok(A.team_map(["BIG", "BIG Academy"], "BIG", "NIP") is None, "A2 ambiguous outcomes refused (both match home)")

ok(abs(A.fee(0.5) - 0.0125) < 1e-12, "fee at 0.5 = 1.25c")
ok(abs(A.sign_test_p([1] * 11 + [-1] * 4) - 0.11846923828125) < 1e-9, "exact sign test 11/15 = 0.1185")

# ---- synthetic price world: events every 60 s alternate fav home/away; token0 = home. true lead applied to prints after the event
def world(true_lead, print_every, seed, nev=300, anticip=0.0):
    rnd = random.Random(seed); evs = []; prints = []
    t = 100.0
    for i in range(nev):
        evs.append((t, "K", "home_team" if rnd.random() < .5 else "away_team", 1, i)); t += 60
    drift = 0.5; ts = []
    T = 100.0
    price = 0.5
    shifts = {}
    # build a price process: random walk, then a step of +-true_lead at t+3 s that persists 20 s then decays back (net zero long run)
    grid = {}
    x = 0.5
    for sec in range(int(T), int(t) + 40):
        x += rnd.gauss(0, 0.0015); x = min(.9, max(.1, x)); grid[sec] = x
    adj = {sec: 0.0 for sec in grid}
    for (te, k, fav, g, r) in evs:
        s = 1 if fav == "home_team" else -1
        for sec in range(int(te) + 3, int(te) + 23): adj[sec] = adj.get(sec, 0) + s * true_lead
        for sec in range(int(te) - 12, int(te) + 23): adj[sec] = adj.get(sec, 0) + s * anticip
    for sec in sorted(grid):
        if sec % print_every == 0:
            p = min(.99, max(.01, grid[sec] + adj[sec])); prints.append({"timestamp": sec, "price": p, "outcome_index": 0, "side": "BUY" if rnd.random() < .5 else "SELL"})
    return evs, prints

def run(true_lead, print_every, seed=1, plant=0.0, anticip=0.0):
    evs, prints = world(true_lead, print_every, seed, anticip=anticip)
    tok0 = A.Tok(prints); tok1 = A.Tok([dict(x, outcome_index=1, price=1 - x["price"]) for x in prints])
    sof = lambda fav: 1 if fav == "home_team" else -1
    t0 = A.plant_tok(tok0, [(e[0], sof(e[2])) for e in evs], plant) if plant else tok0
    rows = A.rows_for_market(evs, t0, tok1, sof, hs=1)
    # split into 10 pseudo-matches (by event index) for the cluster tools
    by = {}
    for i, r in enumerate(rows): by.setdefault(i % 10, []).append(r)
    return rows, by

rows, by = run(0.0, 1)
S0 = A.summarise(by, "null dense prints")
ok(abs(S0["lead_c"]) < 0.35, f"NULL: lead near 0 ({S0['lead_c']:+.2f}c)")
cover = 0
for sd in range(1, 21):
    _, b_ = run(0.0, 1, seed=sd); lo, hi = A.boot_matches({m: [r["post"] for r in v] for m, v in b_.items()}, nb=500); cover += lo < 0 < hi
ok(cover >= 15, f"NULL calibration: bootstrap 95% CI covers 0 in {cover}/20 seeds (>=15 needed)")
rows, by = run(2.0 / 100, 1)
S1 = A.summarise(by, "true +2c")
ok(1.5 < S1["lead_c"] < 2.5 and S1["boot95_c"][0] > 1.0, f"PLANT in world (+2c at t+3 s, dense prints) is recovered ({S1['lead_c']:+.2f}c, {S1['boot95_c']})")
ok(abs(S1["ant_c"]) < 0.4, f"no anticipation when none built in ({S1['ant_c']:+.2f}c)")
rows, by = run(0.0, 1, anticip=0.02)
S2 = A.summarise(by, "pure anticipation")
ok(S2["ant_c"] > 1.2 and S2["ant_boot95_c"][0] > 0.5, f"anticipation world (+2c before the event) shows ANT ({S2['ant_c']:+.2f}c)")
ok(S2["lead_c"] < 0.5, f"anticipation world is not read as a lead ({S2['lead_c']:+.2f}c)")

# ---- A8 plant: recovery = share of rows with a print in [t+5, t+15]
rows, by = run(0.0, 1, plant=0.03)
S3 = A.summarise(by, "plant dense")
ok(2.5 < S3["lead_c"] < 3.5, f"A8 plant +3c on dense prints reads {S3['lead_c']:+.2f}c (~100%)")
rows, by = run(0.0, 17, plant=0.03)
S4 = A.summarise(by, "plant sparse")
ok(1.2 < S4["lead_c"] < 2.7, f"A8 plant +3c on sparse prints (1 per 17 s) reads {S4['lead_c']:+.2f}c: partial recovery (about 11/17 of rows have a print in the window)")
# mutant: a plant that is NOT applied must read ~0
rows, by = run(0.0, 1, plant=0.0)
ok(abs(A.summarise(by, "no plant")["lead_c"]) < 0.35, "mutant: no plant -> no lead")

# ---- A7 executable proxy: entry uses BUY prints only
tk = A.Tok([{"timestamp": 101, "price": .40, "side": "SELL"}, {"timestamp": 103, "price": .45, "side": "BUY"}, {"timestamp": 120, "price": .50, "side": "SELL"}])
ok(tk.first_buy(101, 115) == (0.45, 103), "A7 first BUY at/after t+1 s skips SELL prints")
ok(tk.first_buy(104, 115) == (None, None), "A7 no BUY in window -> no fill")
# net = mark - entry - fee
rowsx = A.rows_for_market([(100.0, "K", "home_team", 1, 1)],
                          A.Tok([{"timestamp": 80, "price": .5, "side": "BUY"}, {"timestamp": 99, "price": .5, "side": "BUY"}, {"timestamp": 103, "price": .5, "side": "BUY"}, {"timestamp": 114, "price": .54, "side": "SELL"}]),
                          A.Tok([]), lambda f: 1)
ok(len(rowsx) == 1 and abs(rowsx[0]["net"] - (0.54 - 0.5 - 0.0125)) < 1e-9, f"A7 net = mark - entry - fee ({rowsx[0].get('net') if rowsx else None})")

# ---- within-match shuffle detects a real effect and not a null
rows, by = run(0.02, 1)
_, p_real = A.within_match_shuffle_p({m: v for m, v in by.items()}, nperm=400)
rows, by = run(0.0, 1)
_, p_null = A.within_match_shuffle_p({m: v for m, v in by.items()}, nperm=400)
ok(p_real < 0.01 and p_null > 0.01, f"within-match shuffle: real p={p_real:.3f}, null p={p_null:.3f}")

print("\nALL PASS" if not FAILS else f"\n{len(FAILS)} FAILED")
sys.exit(1 if FAILS else 0)
