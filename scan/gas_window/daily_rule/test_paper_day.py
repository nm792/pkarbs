"""Can-fail test for paper_day.py: end to end on a planted day, a day with no page change, and the aggregate."""
import json, os, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import paper_day as PD, paper_post as P, datetime as dt
from test_helpers_paper import snap, page, ns, D, PRM
fails = 0
def check(n, c):
    global fails; print(("ok   " if c else "FAIL ") + n); fails += 0 if c else 1
def bids(sn, tok, b): sn["tok"][tok]["bids"] = b; return sn
GM = [dict(clobTokenIds=json.dumps(["t1Yes", "t1No"]), outcomes='["Yes","No"]', outcomePrices='["1","0"]'),
      dict(clobTokenIds=json.dumps(["t0Yes", "t0No"]), outcomes='["Yes","No"]', outcomePrices='["0","1"]'),
      dict(clobTokenIds=json.dumps(["t2Yes", "t2No"]), outcomes='["Yes","No"]', outcomePrices='["0","1"]'),
      dict(clobTokenIds=json.dumps(["t3Yes", "t3No"]), outcomes='["Yes","No"]', outcomePrices='["0","1"]')]
b0 = snap(ns(3, 15, 2), {(1, "Yes"): [[0.90, 100]], (2, "No"): [[0.92, 100]]})
b1 = bids(bids(snap(ns(3, 16, 2), {}), "t1Yes", [[0.97, 9]]), "t2No", [[0.97, 9]])
b0b = snap(ns(3, 15, 3), {(1, "Yes"): [[0.90, 100]], (2, "No"): [[0.92, 100]]})
rows = [b0, b0b, b1]
row, settled = PD.day_row(D, rows, [page(ns(3, 15))], PRM, GM)
check("planted day: page change time and value logged", row["page_change_ns"] == ns(3, 15) and row["page_value"] == 3.705 and row["page_log_ok"])
check("planted day: two counted fills settle as wins, pnl > 0", row["counted_fills"] == 2 and row["unresolved"] == 0 and row["post_pnl"] > 0)
check("planted day: +1min markout positive", row["markouts"]["+1min"]["pnl"] > 0)
check("planted day: capacity row counts both eligible asks (200 shares)", row["capacity"]["eligible_shares"] == 200)
row3, _ = PD.day_row(D, [b0, b1], [page(ns(3, 15))], PRM, GM)
check("hold: the ask is gone/unseen at the hold check -> 0 counted fills, 2 logged unfilled (hold), P&L 0", row3["counted_fills"] == 0 and row3["unfilled_hold"] == 2 and row3["post_pnl"] == 0 and row3["page_log_ok"])
row2, _ = PD.day_row(D, rows, [page(ns(3, 15), status=403, val=None)], PRM, GM)
check("403-only page log: day is NOT scored (page_log_ok false, no fills)", not row2["page_log_ok"] and row2["counted_fills"] == 0)
agg = PD.aggregate([row, row2])
check("aggregate: unsourced day reported, not scored", agg["days_logged"] == 2 and agg["days_scored"] == 1 and agg["days_unsourced"] == 1)
check("aggregate: post cell has an interval and cannot reach $200/day", agg["cells"]["post"]["ci"] is not None and agg["cells"]["post"]["can_reach_target"] is False)
with tempfile.TemporaryDirectory() as td:
    bk, pg, gj = (os.path.join(td, n) for n in ("b", "p", "g"))
    open(bk, "w").write("\n".join(json.dumps(x) for x in rows) + "\n"); open(pg, "w").write(json.dumps(page(ns(3, 15))) + "\n"); json.dump(GM, open(gj, "w"))
    PD.main(["--date", "2026-11-21", "--books", bk, "--page", pg, "--out-dir", td, "--gamma-json", gj]); PD.main(["--date", "2026-11-21", "--books", bk, "--page", pg, "--out-dir", td, "--gamma-json", gj])
    days = [json.loads(l) for l in open(os.path.join(td, "paper_days.jsonl"))]
    check("main: re-running the same day replaces its row (no double count)", len(days) == 1 and os.path.exists(os.path.join(td, "paper_decisions_2026-11-21.jsonl")))
check("slug for the day", PD.slug_for(dt.date(2026, 12, 1)) == "us-gas-price-on-december-1-2026")
print("FAILED" if fails else "ALL PASS", fails); sys.exit(1 if fails else 0)
