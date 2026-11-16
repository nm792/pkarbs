#!/usr/bin/env python3
"""Read-only logger of Polymarket perp public data (api.perpetuals.polymarket.com). No keys, no orders.
Usage: python3 pm_weekend_logger.py --out DIR [--interval 60] [--symbols SP500-USD,NAS100-USD,NVDA-USD,SNDK-USD,MU-USD,AMD-USD,GOOG-USD]
Writes DIR/pm_YYYYMMDD.jsonl.gz: per symbol per poll: tickers row (index/mark/last/mid/OI/...) plus top 5 book levels.
Smoke-tested 16 Nov 2026. Same locked rule as hl_weekend_logger.py (weekend-perps/LOCKED-RULE.md).
"""
import argparse, gzip, json, time, datetime, urllib.request
H = "https://api.perpetuals.polymarket.com"
def get(path, timeout=15):
    req = urllib.request.Request(H + path, headers={"user-agent": "data-logger"})
    return json.load(urllib.request.urlopen(req, timeout=timeout))
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True); ap.add_argument("--interval", type=int, default=60)
    ap.add_argument("--symbols", default="SP500-USD,NAS100-USD,NVDA-USD,SNDK-USD,MU-USD,AMD-USD,GOOG-USD")
    a = ap.parse_args(); want = set(s.strip() for s in a.symbols.split(",") if s.strip())
    while True:
        t = time.time(); ts = datetime.datetime.fromtimestamp(t, datetime.timezone.utc)
        fn = f"{a.out}/pm_{ts:%Y%m%d}.jsonl.gz"
        with gzip.open(fn, "at") as f:
            try:
                tick = [x for x in get("/v1/info/tickers") if x.get("symbol") in want]
            except Exception as e:
                f.write(json.dumps({"ts": t, "err": "tickers " + str(e)}) + "\n"); tick = []
            for x in tick:
                row = dict(x); row["ts"] = t
                try:
                    b = get(f"/v1/info/book?instrument_id={x['instrument_id']}")
                    row["bids"] = b.get("bids", [])[:5]; row["asks"] = b.get("asks", [])[:5]
                except Exception as e:
                    row["book_err"] = str(e)
                f.write(json.dumps(row) + "\n")
        time.sleep(max(1, a.interval - (time.time() - t)))
if __name__ == "__main__":
    main()
