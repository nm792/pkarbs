"""1-minute Polymarket perp SP500-USD marks for [T-6h-10min, T) of every event date. usage: collect_perp1m.py RUNDIR  -> RUNDIR/perp1m.json {date: [[ts_ms, mark], ...]}"""
import sys, json, time, requests
from oclib import open_ts
R = sys.argv[1]; P = "https://api.perpetuals.polymarket.com"
dates = sorted({m["date"] for m in json.load(open(R + "/markets.json"))["markets"]}); out = {}; bad = 0
for d in dates:
    T = int(open_ts(d) * 1000)
    for k in range(5):
        try:
            r = requests.get(P + "/v1/info/mark-history", params=dict(instrument_id=1, interval="1m", start_timestamp=T - (6 * 3600 + 600) * 1000, end_timestamp=T), timeout=40).json(); break
        except Exception: time.sleep(1.5); r = {}
    pts = [[x[0], float(x[1])] for x in r.get("data", [])]
    if r.get("more"): bad += 1
    out[d] = pts
json.dump(out, open(R + "/perp1m.json", "w")); print("dates", len(out), "points", sum(len(v) for v in out.values()), "dates with 'more' flag", bad, "empty dates", sum(1 for v in out.values() if not v))
