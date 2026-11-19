"""Companion trade tape for an elon_listing capture: polls data-api /v2/trades for each bracket condition every INTERVAL s, appends new prints to <event dir>/trades.jsonl.
usage: elon_trades.py EVENT_DIR [--interval 5] [--max-hours 6]. Diagnostic only (Amendment 1): passive-fill credit is NOT part of the pass test."""
import argparse, json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import elon_listing as E
DATA = "https://data-api.polymarket.com"


def poll(meta, seen, path):
    n = 0
    for b in meta["brackets"]:
        try:
            r = E.jget(f"{DATA}/v2/trades?condition={b['cond']}&limit=100")
        except Exception as ex:
            print("trade poll error", ex, flush=True); continue
        for x in r.get("data", []):
            k = (x.get("token_id"), x.get("timestamp"), x.get("price"), x.get("size"), x.get("side"))
            if k in seen: continue
            seen.add(k); open(path, "a").write(json.dumps(dict(t_seen=time.time(), cond=b["cond"], **{kk: x.get(kk) for kk in ("token_id", "side", "price", "size", "timestamp")})) + "\n"); n += 1
    return n


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("dir"); ap.add_argument("--interval", type=float, default=5.0); ap.add_argument("--max-hours", type=float, default=6.0); a = ap.parse_args()
    meta = json.load(open(f"{a.dir}/meta.json")); seen = set(); path = f"{a.dir}/trades.jsonl"; end = time.time() + a.max_hours * 3600
    while time.time() < end:
        n = poll(meta, seen, path); time.sleep(a.interval)
