#!/usr/bin/env python3
"""Read-only logger of Hyperliquid HIP-3 perp data (public info API). No keys, no orders.
UNTESTED against the live API when written (12 Nov 2026, container had no route to it): first run must be a smoke test.
Usage: python3 hl_weekend_logger.py --out DIR [--interval 60] [--match HSI,HK,JP,NIKKEI,SPX,US500,XYZ100,SAMSUNG,HYNIX]
Writes DIR/hl_YYYYMMDD.jsonl.gz, one line per symbol per poll.
"""
import argparse, gzip, json, time, datetime, urllib.request
URL = "https://api.hyperliquid.xyz/info"

def post(body, timeout=15):
    req = urllib.request.Request(URL, json.dumps(body).encode(), {"content-type": "application/json", "user-agent": "data-logger"})
    return json.load(urllib.request.urlopen(req, timeout=timeout))

def dexes():
    out = [""]  # "" = main dex
    try:
        for d in post({"type": "perpDexs"}):
            if d and d.get("name"):
                out.append(d["name"])
    except Exception as e:
        print("perpDexs error", e, flush=True)
    return out

def poll(dex, wanted):
    rows = []
    meta, ctxs = post({"type": "metaAndAssetCtxs", "dex": dex})
    for u, c in zip(meta["universe"], ctxs):
        name = u["name"]
        if wanted and not any(w in name.upper() for w in wanted):
            continue
        row = {"dex": dex, "coin": name, "mark": c.get("markPx"), "oracle": c.get("oraclePx"), "mid": c.get("midPx"),
               "funding": c.get("funding"), "oi": c.get("openInterest"), "vol24": c.get("dayNtlVlm"), "maxlev": u.get("maxLeverage")}
        try:
            book = post({"type": "l2Book", "coin": name})
            row["bids"] = book["levels"][0][:5]; row["asks"] = book["levels"][1][:5]
        except Exception as e:
            row["book_err"] = str(e)
        rows.append(row)
    return rows

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--interval", type=int, default=60)
    ap.add_argument("--match", default="")
    a = ap.parse_args()
    wanted = [w.strip().upper() for w in a.match.split(",") if w.strip()]
    ds = dexes(); last = 0
    while True:
        t = time.time()
        if t - last > 3600:
            ds = dexes(); last = t
        ts = datetime.datetime.utcfromtimestamp(t)
        fn = f"{a.out}/hl_{ts:%Y%m%d}.jsonl.gz"
        with gzip.open(fn, "at") as f:
            for d in ds:
                try:
                    for r in poll(d, wanted):
                        r["ts"] = t; f.write(json.dumps(r) + "\n")
                except Exception as e:
                    f.write(json.dumps({"ts": t, "dex": d, "err": str(e)}) + "\n")
        time.sleep(max(1, a.interval - (time.time() - t)))

if __name__ == "__main__":
    main()
