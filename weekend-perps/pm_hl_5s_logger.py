#!/usr/bin/env python3
"""Read-only 5 s logger: Polymarket perp tickers (+ order books when a gap opens) and Hyperliquid xyz/flx/km mark/oracle/mid.
No keys, no orders. Usage: python3 pm_hl_5s_logger.py --out DIR [--interval 5]
Writes DIR/pmhl5s_YYYYMMDD.jsonl.gz. One line per poll: {"t":..,"pm":[...],"books":{sym:{...}},"hl":{dex:[[name,mark,oracle,mid],...]}}"""
import argparse, gzip, json, time, datetime, urllib.request
PM = "https://api.perpetuals.polymarket.com"; HL = "https://api.hyperliquid.xyz/info"
ALWAYS = {"NVDA-USD", "MU-USD", "AMD-USD", "TSLA-USD", "SP500-USD"}
def get(u, t=10):
    return json.load(urllib.request.urlopen(urllib.request.Request(u, headers={"user-agent": "data-logger"}), timeout=t))
def post(b, t=10):
    return json.load(urllib.request.urlopen(urllib.request.Request(HL, json.dumps(b).encode(), {"content-type": "application/json", "user-agent": "data-logger"}), timeout=t))
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--out", required=True); ap.add_argument("--interval", type=float, default=5); a = ap.parse_args()
    ins = {i["symbol"]: i for i in get(PM + "/v1/info/instruments")["data"] if isinstance(get(PM + "/v1/info/instruments"), dict)} if False else {}
    r = get(PM + "/v1/info/instruments"); r = r["data"] if isinstance(r, dict) else r
    eq = {i["symbol"]: i["instrument_id"] for i in r if i["category"] in ("equity", "index")}
    hot = {}
    while True:
        t0 = time.time(); rec = {"t": t0, "pm": [], "books": {}, "hl": {}}
        try:
            tk = get(PM + "/v1/info/tickers"); tk = tk["data"] if isinstance(tk, dict) else tk
            for x in tk:
                if x["symbol"] in eq:
                    rec["pm"].append([x["symbol"], x["index_price"], x["mark_price"], x["mid_price"], x["last_price"]])
                    try: g = abs(float(x["mid_price"]) / float(x["index_price"]) - 1) * 1e4
                    except Exception: g = 0
                    if g >= 20: hot[x["symbol"]] = t0 + 360
                    if g >= 20 or x["symbol"] in ALWAYS or hot.get(x["symbol"], 0) > t0:
                        try:
                            b = get(PM + "/v1/info/book?instrument_id=%d" % eq[x["symbol"]]); rec["books"][x["symbol"]] = b.get("data", b)
                        except Exception as e: rec["books"][x["symbol"]] = {"err": str(e)[:60]}
        except Exception as e: rec["pm_err"] = str(e)[:80]
        for d in ("xyz", "flx", "km"):
            try:
                m, c = post({"type": "metaAndAssetCtxs", "dex": d})
                rec["hl"][d] = [[u["name"], x.get("markPx"), x.get("oraclePx"), x.get("midPx")] for u, x in zip(m["universe"], c)]
            except Exception as e: rec["hl"][d] = {"err": str(e)[:80]}
        fn = "%s/pmhl5s_%s.jsonl.gz" % (a.out, datetime.datetime.fromtimestamp(t0, datetime.timezone.utc).strftime("%Y%m%d"))
        with gzip.open(fn, "at") as f: f.write(json.dumps(rec) + "\n")
        time.sleep(max(0, a.interval - (time.time() - t0)))
if __name__ == "__main__": main()
