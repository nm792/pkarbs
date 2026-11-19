#!/usr/bin/env python3
"""Filter PMXT Archive hourly Polymarket order-book Parquet files down to the US gas events' tokens.
Read-only: downloads each hourly file, keeps only rows whose token id is a Yes/No token of a Gamma event with slug
us-gas-price-on-<month>-<d>-2026, writes them to --out as one Parquet per hour, deletes the download.
Usage: pmxt_gas_filter.py --url 'https://archive.pmxt.dev/.../polymarket_orderbook_{Y}-{m}-{d}T{H}.parquet' \
   --days 2026-10-22:2026-11-19 --hours 6,7,8 --out DIR [--min-free-gb 15] [--tokens tokens.json] [--list-only]
{Y} {m} {d} {H} are zero-padded UTC. Hours with HTTP 404 are logged as MISSING (never skipped silently).
Stops when free space on --out would fall below --min-free-gb."""
import argparse, json, os, shutil, sys, urllib.request, urllib.error, datetime as dt
import pyarrow.parquet as pq, pyarrow as pa, pyarrow.compute as pc
ID_COLS = ("token_id", "asset_id", "asset", "outcome_token_id", "token")
MONTHS = ["january","february","march","april","may","june","july","august","september","october","november","december"]
def slug_for(day): return f"us-gas-price-on-{MONTHS[day.month-1]}-{day.day}-2026"
def resolve_tokens(days, fetch=None):
    fetch = fetch or (lambda u: json.loads(urllib.request.urlopen(urllib.request.Request(u, headers={"Accept-Encoding": "identity"}), timeout=30).read()))
    toks = {}
    for d in days:
        ev = fetch("https://gamma-api.polymarket.com/events?slug=" + slug_for(d))
        for e in ev:
            for m in e.get("markets", []):
                for t in json.loads(m["clobTokenIds"]): toks[t] = (slug_for(d), m.get("question", ""))
    return toks
def filter_table(tbl, tokens):
    col = next((c for c in ID_COLS if c in tbl.column_names), None)
    if col is None: raise SystemExit(f"no token column among {ID_COLS}; columns are {tbl.column_names}")
    mask = pc.is_in(pc.cast(tbl[col], pa.string()), value_set=pa.array(sorted(tokens), pa.string()))
    return tbl.filter(mask), col
def free_gb(p): return shutil.disk_usage(p).free / 1e9
def process_hour(url, out_dir, tokens, min_free_gb, opener=None):
    name = os.path.basename(url.split("?")[0])
    tmp = os.path.join(out_dir, name + ".part"); dest = os.path.join(out_dir, "gas_" + name)
    if free_gb(out_dir) < min_free_gb: raise SystemExit(f"STOP: free space {free_gb(out_dir):.1f} GB below floor {min_free_gb}")
    try:
        with (opener or urllib.request.urlopen)(url) as r, open(tmp, "wb") as f: shutil.copyfileobj(r, f)
    except urllib.error.HTTPError as e:
        if os.path.exists(tmp): os.remove(tmp)
        return ("MISSING" if e.code == 404 else f"HTTP{e.code}", 0, 0)
    try:
        tbl = pq.read_table(tmp); sub, col = filter_table(tbl, tokens)
        pq.write_table(sub, dest); return ("OK", tbl.num_rows, sub.num_rows)
    finally:
        os.remove(tmp)
def main(a=None):
    p = argparse.ArgumentParser(); p.add_argument("--url"); p.add_argument("--days"); p.add_argument("--hours", default="6,7,8")
    p.add_argument("--out"); p.add_argument("--min-free-gb", type=float, default=15); p.add_argument("--tokens"); p.add_argument("--list-only", action="store_true")
    a = p.parse_args(a); s, e = [dt.date.fromisoformat(x) for x in a.days.split(":")]
    days = [s + dt.timedelta(n) for n in range((e - s).days + 1)]
    tokens = json.load(open(a.tokens)) if a.tokens else resolve_tokens(days + [days[-1] + dt.timedelta(1)])
    os.makedirs(a.out, exist_ok=True); json.dump(tokens, open(os.path.join(a.out, "tokens.json"), "w"))
    print(f"tokens {len(tokens)}", flush=True)
    for d in days:
        for h in [int(x) for x in a.hours.split(",")]:
            url = a.url.format(Y=f"{d.year:04d}", m=f"{d.month:02d}", d=f"{d.day:02d}", H=f"{h:02d}")
            if a.list_only: print(url); continue
            print(url, *process_hour(url, a.out, tokens, a.min_free_gb), flush=True)
if __name__ == "__main__": main()
