#!/usr/bin/env python3
"""Build the scorer input from words.json (list of {event, subfam, cond, yes_token, t_w (unix s), t_w_src, res_s}).
Public Data API v2 /trades, taker rows only (default takerOnly=true, checked 25 Nov 18:2xZ: 460 unique-tx rows vs 500 rows with 196 tx when false),
filtered by condition, paged by cursor (offset is rejected), condition asserted on every row. Runs on Prime (R-039).
Usage: python3 -I pull.py words.json fee_rates.json out.json"""
import json, subprocess, sys

API = 'https://data-api.polymarket.com/v2/trades?'


def get(q):
    return json.loads(subprocess.run(['curl', '-s', '--max-time', '30', API + q], capture_output=True, text=True).stdout)


def trades_for(cond, t_min, max_pages=200):
    rows, cur = [], None
    for _ in range(max_pages):
        j = get('condition=%s&limit=500%s' % (cond, '&cursor=' + cur if cur else ''))
        b = j['data']
        assert all(x['condition_id'] == cond for x in b), cond
        rows += b
        cur = (j.get('pagination') or {}).get('next_cursor')
        if not cur or not b or min(x['timestamp'] for x in b) < t_min:
            return rows, True
    return rows, False   # page cap hit before t_min: reported, not silently cut


def main():
    words = json.load(open(sys.argv[1])); rates = json.load(open(sys.argv[2]))
    by = {}
    for w in words:
        by.setdefault(w['cond'], []).append(w)
    trades, report = [], []
    for cond, ws in by.items():
        lo = min(w['t_w'] for w in ws) - 6 * 3600 - 300; hi = max(w['t_w'] for w in ws) + 300
        rows, complete = trades_for(cond, lo)
        keep = [dict(asset=x['token_id'], side=x['side'], price=float(x['price']), size=float(x['size']), ts=float(x['timestamp'])) for x in rows if lo <= x['timestamp'] <= hi]
        trades += keep; report.append(dict(cond=cond, rows=len(rows), kept=len(keep), complete=complete))
    json.dump(dict(trades=trades, words=words, fee_rate=rates, pull_report=report), open(sys.argv[3], 'w'))
    print(json.dumps(report, indent=1))


if __name__ == '__main__':
    main()
