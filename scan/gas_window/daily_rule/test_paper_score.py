"""Can-fail tests for paper_score.py: positive control, null control, later-book rejection, markouts, boundaries, power."""
import datetime as dt, math, os, random, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import paper_post as P, paper_score as S, rule as R
from test_helpers_paper import snap, page, ns, D, PRM
_run = P.run
P.run = lambda *a, **k: _run(*a, **{"hold_s": None, **k})
fails = 0
def check(n, c):
    global fails; print(("ok   " if c else "FAIL ") + n); fails += 0 if c else 1
def with_bids(sn, tok, bids):
    sn["tok"][tok]["bids"] = bids; return sn
# POSITIVE CONTROL: stale ask 0.90 at the page change, market catches up by +60 s (bid 0.97) and +5 min (bid 0.99): markout must be positive through the same code
b0 = snap(ns(3, 15, 2), {(1, "Yes"): [[0.90, 100]], (0, "No"): [[0.90, 100]]})
b1 = with_bids(with_bids(snap(ns(3, 16, 2), {}), "t1Yes", [[0.97, 50]]), "t0No", [[0.97, 50]])
b5 = with_bids(with_bids(snap(ns(3, 20, 2), {}), "t1Yes", [[0.99, 50]]), "t0No", [[0.99, 50]])
b30 = with_bids(with_bids(snap(ns(3, 45, 2), {}), "t1Yes", [[0.99, 50]]), "t0No", [[0.99, 50]])
b10 = with_bids(with_bids(snap(ns(9, 59, 59), {}), "t1Yes", [[0.995, 50]]), "t0No", [[0.995, 50]])
books = [b0, b1, b5, b30, b10]
dec = P.run(books, [page(ns(3, 15))], D, PRM)
rows = S.markouts(dec, books, end_ns=ns(10, 0))
check("control: decisions exist (stale ask lifted at the page change)", len(dec) == 2)
check("control: markout positive at +1, +5, +30 min and 10:00 ET", all(r["mark"][l][1] > 0 for r in rows for l in ("+1min", "+5min", "+30min", "10:00ET")))
check("control: +1min markout equals shares*(0.97-0.90)-fee", all(abs(r["mark"]["+1min"][1] - (r["shares"] * 0.07 - r["fee"])) < 1e-9 for r in rows))
sm = S.markout_summary(rows); check("control: summary counts both fills at every horizon, none missing", all(sm[l]["n"] == 2 and sm[l]["missing"] == 0 for l in sm))
# NULL CONTROL: ask already at the rule's no-trade level -> no decisions, zero markout
nul = [snap(ns(3, 15, 2), {(1, "Yes"): [[0.995, 100]], (0, "No"): [[0.995, 100]]}), b1]
check("null: no decision when the market already shows the price", P.run(nul, [page(ns(3, 15))], D, PRM) == [])
# LATER-BOOK REJECTION (planted): cheap ask appears 2 minutes after the change
lat = [snap(ns(3, 15, 2), {(1, "Yes"): [[0.995, 100]]}), snap(ns(3, 17, 0), {(1, "Yes"): [[0.90, 100]]})]
check("later cheap book is rejected", P.run(lat, [page(ns(3, 15))], D, PRM) == [])
# markout gaps and no-bid
rows2 = S.markouts(dec, [b0], end_ns=ns(10, 0))
check("missing later books -> None, not zero", all(r["mark"]["+5min"] is None and r["mark"]["10:00ET"] is None for r in rows2))
b1n = snap(ns(3, 16, 2), {}); rows3 = S.markouts(dec, [b0, b1n])
check("no bid at the horizon marks at 0.0 (nothing realisable)", all(r["mark"]["+1min"][0] == 0.0 and r["mark"]["+1min"][1] < 0 for r in rows3))
# capacity row: depth passing the rule
cap = S.capacity_row(b0, {"t1Yes": True, "t0No": True, "t2No": False}, PRM)
check("capacity: 200 shares at 0.90 pass, edge = 200*(0.995-0.90-fee)", cap["eligible_shares"] == 200 and abs(cap["edge_usd_at_depth"] - 200 * (0.995 - 0.90 - R.fee_per_share(0.9, 0.05))) < 1e-6)
cap0 = S.capacity_row(nul[0], {"t1Yes": True, "t0No": True}, PRM)
check("capacity: nothing at 0.995 passes", cap0["eligible_shares"] == 0)
# sequential boundaries: planted effects
rnd = random.Random(7)
def sim(mu, n, sd): return [rnd.gauss(mu, sd) for _ in range(n)]
sig = 7.06 * 1.5
st = S.cell_status(sim(8.0, 40, 7.06), sig); check("boundary: planted +8/day at sd 7 reaches SUCCESS within 40 days", st["status"].startswith("SUCCESS"))
st = S.cell_status(sim(-8.0, 40, 7.06), sig); check("boundary: planted -8/day hits FUTILE", st["status"].startswith("FUTILE"))
st = S.cell_status(sim(0.0, 40, 7.06), sig); check("boundary: planted 0/day is NOT called success or futile at 40 days", st["status"] == "continue")
st = S.cell_status(sim(2.6, 60, 7.06), sig, max_days=60); check("boundary: the backtest edge +2.6/day at 60 days is not yet decided -> inconclusive/continue, never 'dead'", not st["status"].startswith("FUTILE"))
check("boundary: gas-like cell cannot reach $200/day", S.cell_status(sim(2.6, 30, 7.06), sig)["can_reach_target"] is False)
check("boundary: a planted +300/day cell can reach $200/day", S.cell_status(sim(300, 10, 50), 75)["can_reach_target"] is True)
# always-valid: under the null, peeking every day for 60 days crosses the SUCCESS boundary in far fewer than 5% of runs
cross = 0
for k in range(400):
    xs = []; hit = False
    for i in range(60):
        xs.append(rnd.gauss(0, 7.06)); lo, hi = S.cs_bounds(xs, sig)
        if lo > 0: hit = True; break
    cross += hit
check("always-valid: false SUCCESS under a zero edge with daily peeking <= 5%% (got %.1f%%)" % (cross / 4), cross / 400 <= 0.05)
# power count
check("power: backtest post +2.60/day sd 7.06 needs about 45 days", 40 <= S.power_days(2.60, 7.06) <= 50)
check("power: $200/day edge is visible in 1 day at sd 7", S.power_days(200, 7.06) < 1)
check("power: zero edge -> infinite", S.power_days(0, 7) == float("inf"))
# shrinkage
sh = S.shrink({"post": (2.6, 1.2), "yes_fav": (8.8, 7.6), "no_out": (0.3, 0.9)})
check("shrink: the noisy high estimate moves toward the group mean more than the precise one", abs(sh["yes_fav"]["shrunk"] - sh["yes_fav"]["raw"]) > abs(sh["post"]["shrunk"] - sh["post"]["raw"]))
print("FAILED" if fails else "ALL PASS", fails); sys.exit(1 if fails else 0)
