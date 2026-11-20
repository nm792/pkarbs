"""Planted tests for backtest.run_event (each can fail): window edges, which side and bucket may fill, settlement P&L, 03:00-03:30 ET skipped."""
import os, sys, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import backtest as b, rule as R
from zoneinfo import ZoneInfo
ET = ZoneInfo("America/New_York"); D = dt.date(2026, 11, 20)
def ts(h, m, day=D): return dt.datetime(day.year, day.month, day.day, h, m, tzinfo=ET).timestamp()
CR = ts(10, 0, dt.date(2026, 11, 19))
Q = ["Will the US national average gas price be less than $3.7000 on November 20?", "Will the US national average gas price be between $3.7000 and $3.7099 on November 20?",
     "Will the US national average gas price be between $3.7100 and $3.7199 on November 20?", "Will the US national average gas price be $3.7200+ on November 20?"]
def mk(prints_by_bucket):
    return [dict(date="2026-11-20", q=q, cid=str(i), created="2026-11-19T15:00:11Z", tokens=["y", "n"], tr=prints_by_bucket.get(i, [])) for i, q in enumerate(Q)]
NH = dict(mean=3.6955, sd=0.005)        # q(bucket0)=0.82 favourite; bucket 1 q=0.18 (not ruled out); buckets 2 and 3 q<0.01 (ruled out)
def P(actual): return {D: actual}
def t1_yes_fav_gap_and_settlement():
    ms = mk({0: [(CR + 100, "Yes", "BUY", 0.30, 100.0), (CR + 200, "Yes", "BUY", 0.79, 100.0)]})
    r = b.run_event("2026-11-20", ms, NH, P(3.69), R.Params(bank=10000))
    assert r["fav"] == 0 and r["win"] == 0 and [round(f["p"], 2) for f in r["fills"]] == [0.30], r["fills"]    # 0.79 is within 0.05 of q=0.82: not taken
    assert r["fills"][0]["pnl"] > 0
    r = b.run_event("2026-11-20", ms, NH, P(3.7050), R.Params(bank=10000)); assert r["fills"][0]["pnl"] < 0 and not r["fills"][0]["win"]    # favourite loses: P&L is the cost
def t2_no_out_only_for_ruled_out_buckets():
    ms = mk({2: [(CR + 100, "No", "BUY", 0.98, 100.0)], 1: [(CR + 100, "No", "BUY", 0.98, 100.0)], 3: [(CR + 100, "Yes", "BUY", 0.02, 100.0)]})
    r = b.run_event("2026-11-20", ms, NH, P(3.69), R.Params(bank=10000)); assert [(f["j"], f["out"]) for f in r["fills"]] == [(2, "No")], r["fills"]   # bucket 1 not ruled out; YES of a ruled-out bucket is never bought
def t3_windows():
    ms = mk({0: [(CR - 50, "Yes", "BUY", 0.30, 100.0), (ts(2, 59), "Yes", "BUY", 0.30, 100.0), (ts(3, 10), "Yes", "BUY", 0.30, 100.0), (ts(3, 29), "Yes", "BUY", 0.30, 100.0)]})
    r = b.run_event("2026-11-20", ms, NH, P(3.69), R.Params()); assert len(r["fills"]) == 1 and r["fills"][0]["ts"] == ts(2, 59)     # before listing and 03:00-03:30 ET are skipped; 03:30+ only the 'post' rule
def t4_post_rule_uses_page_bucket_only():
    ms = mk({0: [(ts(3, 40), "Yes", "BUY", 0.93, 100.0)], 1: [(ts(3, 40), "Yes", "BUY", 0.93, 100.0), (ts(3, 41), "No", "BUY", 0.93, 100.0)], 2: [(ts(3, 41), "No", "BUY", 0.93, 100.0)]})
    r = b.run_event("2026-11-20", ms, NH, P(3.69), R.Params(bank=10000))
    assert sorted((f["j"], f["out"]) for f in r["fills"]) == [(0, "Yes"), (1, "No"), (2, "No")] and all(f["win"] for f in r["fills"]), r["fills"]
    r = b.run_event("2026-11-20", ms, NH, P(3.69), R.Params(), rules=("yes_fav", "no_out")); assert r["fills"] == []                   # post disabled: nothing fills at 03:40
TESTS = [t1_yes_fav_gap_and_settlement, t2_no_out_only_for_ruled_out_buckets, t3_windows, t4_post_rule_uses_page_bucket_only]
if __name__ == "__main__":
    ok = 0
    for t in TESTS:
        try: t(); ok += 1; print("PASS", t.__name__)
        except AssertionError as e: print("FAIL", t.__name__, e)
    print(f"{ok} of {len(TESTS)} tests pass"); sys.exit(0 if ok == len(TESTS) else 1)
