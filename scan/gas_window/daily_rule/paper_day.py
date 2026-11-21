#!/usr/bin/env python3
"""Daily scorer for the gas paper run (cron after 15:05Z, when the Polymarket event has resolved). One JSON row per event day appended to paper_days.jsonl, then the cell table.
usage: paper_day.py --date 2026-11-21 --books B.jsonl --page P.jsonl --out-dir DIR [--gamma-json FILE] [--nowcast mean,sd]
Row: page change time and value, counted `post` decisions, markouts at +1/+5/+30 min and 10:00 ET (own best bid), capacity row at the decision moment, settlement P&L (Gamma resolution), Kalshi cross-check is left to the reporter (A6: analysis only).
`aggregate()` reads paper_days.jsonl and gives, per cell, the always-valid interval, status against the registered boundaries and the A9 reachability flag. No orders are ever sent."""
import argparse, datetime as dt, gzip, json, os, sys, urllib.request
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import paper_post as P, paper_score as S, rule as R
SIGMA = {"post": 7.06 * 1.5, "yes_fav": 44.93 * 1.5, "no_out": 5.36 * 1.5}      # registered: backtest SD per day (35 events, print-as-ask upper bound, fee 0.05, v2 caps) x 1.5
def slug_for(D): return f"us-gas-price-on-{D.strftime('%B').lower()}-{D.day}-{D.year}"
def fetch_gamma(slug):
    req = urllib.request.Request(f"https://gamma-api.polymarket.com/events?slug={slug}", headers={"User-Agent": "curl/8.5.0", "Accept-Encoding": "gzip"})
    with urllib.request.urlopen(req, timeout=30) as r:
        b = r.read()
        if r.headers.get("Content-Encoding") == "gzip": b = gzip.decompress(b)
    return json.loads(b)[0]["markets"]
def day_row(D, books, page, prm, gamma_markets, nowcast=None):
    end = dt.datetime(D.year, D.month, D.day, 10, 0, tzinfo=P.ET).timestamp() * 1e9
    dec = P.run(books, page, D, prm, nowcast, end)
    chg = P.page_change(page, D)
    marked = S.markouts(dec, books, end_ns=end)
    settled, unresolved = P.settle(marked, gamma_markets)
    counted = [r for r in settled if not r["shadow"]]
    cap = None
    if chg:
        first = next((b for b in books if b["recv_ns"] >= chg[0]), None)
        if first:
            tb = P.token_buckets(first); bounds = {i: b for i, o, b in tb.values()}
            win = next((i for i, (lo, hi) in bounds.items() if lo <= chg[1] < hi), None)
            if win is not None: cap = S.capacity_row(first, {tid: ((i == win) == (o == "Yes")) for tid, (i, o, b) in tb.items()}, prm)
    row = dict(date=D.isoformat(), page_change_ns=chg[0] if chg else None, page_value=chg[1] if chg else None, n_books=len(books), n_page_rows=len(page),
               n_page_200=sum(1 for r in page if r.get("status") == 200), counted_fills=len(counted), unfilled_hold=sum(1 for r in settled if r['kind'] == 'post_unfilled_hold'), unresolved=unresolved,
               post_pnl=P.day_pnl(settled), shadow_pnl={k: sum(r["pnl"] for r in settled if r["shadow"] and r["kind"] == k and r["pnl"] is not None) for k in ("yes_fav", "no_out")},
               cost=sum(r["cost"] for r in counted), markouts=S.markout_summary(counted), capacity=cap,
               fee_rate=prm.fee_rate, page_log_ok=chg is not None)
    return row, settled
def aggregate(rows):
    """Cells: post (counted) and the two shadow cells. Days without a page change are reported, not scored (the day has no sourced page time)."""
    scored = [r for r in rows if r["page_log_ok"] and r["unresolved"] == 0]
    out = dict(days_logged=len(rows), days_scored=len(scored), days_unsourced=len(rows) - len([r for r in rows if r["page_log_ok"]]))
    cells = {"post": [r["post_pnl"] for r in scored], "yes_fav": [r["shadow_pnl"]["yes_fav"] for r in scored], "no_out": [r["shadow_pnl"]["no_out"] for r in scored]}
    out["cells"] = {k: S.cell_status(v, SIGMA[k]) for k, v in cells.items() if v}
    ests = {k: (sum(v) / len(v), SIGMA[k] / len(v) ** 0.5) for k, v in cells.items() if len(v) >= 2}
    if len(ests) >= 2: out["shrunk"] = S.shrink(ests)
    out["power_days_post_backtest_edge"] = S.power_days(2.60, 7.06)
    return out
def main(argv=None):
    ap = argparse.ArgumentParser(); ap.add_argument("--date", required=True); ap.add_argument("--books", required=True); ap.add_argument("--page", required=True)
    ap.add_argument("--out-dir", required=True); ap.add_argument("--gamma-json"); ap.add_argument("--nowcast"); ap.add_argument("--fee-rate", type=float, default=0.05)
    a = ap.parse_args(argv); D = dt.date.fromisoformat(a.date)
    prm = R.Params(fee_rate=a.fee_rate, rule_caps=(("yes_fav", 0.10), ("no_out", 0.05), ("post", 0.10)))
    gm = json.load(open(a.gamma_json)) if a.gamma_json else fetch_gamma(slug_for(D))
    nc = tuple(float(x) for x in a.nowcast.split(",")) if a.nowcast else None
    row, settled = day_row(D, P.read_jsonl(a.books), P.read_jsonl(a.page), prm, gm, nc)
    os.makedirs(a.out_dir, exist_ok=True)
    with open(os.path.join(a.out_dir, f"paper_decisions_{a.date}.jsonl"), "w") as f:
        for r in settled: f.write(json.dumps(r) + "\n")
    path = os.path.join(a.out_dir, "paper_days.jsonl"); rows = [r for r in P.read_jsonl(path) if r["date"] != a.date] if os.path.exists(path) else []
    rows.append(row)
    with open(path, "w") as f:
        for r in rows: f.write(json.dumps(r) + "\n")
    agg = aggregate(rows); print(json.dumps(row)); print(json.dumps(agg, default=str)); return row, agg
if __name__ == "__main__": main()
