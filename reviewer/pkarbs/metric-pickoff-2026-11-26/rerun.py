#!/usr/bin/env python3
"""Rerun of the stale-ask pickoff scan (Reviewer, 26 Nov), ON PRIME (R-039). Changes vs run.py; scan.py is reused unchanged:
  1. NEWS-TIME anchor for ONSET families: R = the time the deciding news first became public (webb T113 news_times.csv:
     tweet/post time, wire, official call, or the rule deadline for NO-by-date). This replaces R = price jump, which is defined from the price itself.
     An onset event without a T113 row is SKIPPED and listed, never anchored on the price.
  2. FEES: each market's own feeSchedule (rate x p x (1-p) per share, exponent 1) is deducted. A market with no schedule gets fee 0 and is counted in `no_fee_schedule`.
  3. COMPLETENESS: a market whose fetched prints do not reach back to R-60 s (page cap or stop heuristic) is flagged `incomplete` and excluded, never read as "no prints".
Calendar rows keep the scheduled-clock R from scan_out.json. The old price-jump figure is printed beside the news-time figure, for comparison only.
Usage: python3 -I rerun.py <dir with events_*.json, scan_out.json, cache/> [news_times.csv] > rerun.json"""
import csv, datetime as dt, glob, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import scan

def fee_rate(m):
    f = m.get('fee')
    if isinstance(f, str):
        try: f = json.loads(f)
        except ValueError: f = None
    if isinstance(f, dict) and f.get('rate') is not None:
        return float(f['rate']), True
    return 0.0, False

def edge_after_fee(prints, rate):
    """prints [(ts,p,sz)] -> (paid, edge) under the scan's $200/trade, $2,000/day caps, fee rate*p*(1-p)/share deducted."""
    by, paid, edge = {}, 0.0, 0.0
    for ts, p, sz in sorted(prints):
        d = ts // 86400
        n = min(p * sz, scan.CAP_TRADE, scan.CAP_DAY - by.get(d, 0.0))
        if n <= 0: continue
        sh = n / p
        by[d] = by.get(d, 0.0) + n; paid += n; edge += sh * (1 - p) - sh * rate * p * (1 - p)
    return paid, edge

def complete(rows, R):
    return bool(rows) and min(r['ts'] for r in rows) <= R - 60

def news_R(path):
    out = {}
    if not path: return out
    for r in csv.DictReader(open(path)):
        try: out[str(r['event_id'])] = int(dt.datetime.fromisoformat(r['news_utc'].replace('Z', '+00:00')).timestamp())
        except (KeyError, ValueError): pass
    return out

def event_result(e, base, R, fetch=scan.fetch_trades):
    res = dict(id=e['id'], R=R, markets=0, incomplete=0, no_fee_schedule=0, stats={})
    allp = {L: [] for L in scan.LS}
    for m in sorted(e['markets'], key=lambda m: -float(m.get('vol') or 0))[:20]:
        w = scan.winner_token(m)
        if not w or not m.get('cid'): continue
        rows = fetch(m['cid'])
        if not complete(rows, R): res['incomplete'] += 1; continue
        rate, has = fee_rate(m); res['no_fee_schedule'] += (not has); res['markets'] += 1
        o = scan.scan_market(rows, w, R)
        for L in scan.LS: allp[L] += [(t, p, s, rate) for t, p, s in o[L]]
    for L in scan.LS:
        paid = edge = 0.0
        for rate in set(x[3] for x in allp[L]):
            pe = edge_after_fee([(t, p, s) for t, p, s, r in allp[L] if r == rate], rate)
            paid += pe[0]; edge += pe[1]
        res['stats'][L] = dict(n=len(allp[L]), paid=round(paid, 2), edge_after_fee=round(edge, 2))
    return res

def main(d, news_csv=None):
    os.chdir(d)
    ev = {}
    for f in glob.glob('events_*.json'):
        for e in json.load(open(f)): ev[str(e['id'])] = e
    nr = news_R(news_csv); out = dict(rows=[], skipped_no_news=[])
    for b in json.load(open('scan_out.json')):
        if not b.get('R'): continue
        e = ev.get(str(b['id']))
        if e is None: continue
        if b.get('anchor') == 'calendar':
            r = event_result(e, b, b['R']); r['anchor'] = 'calendar'
        else:
            if str(b['id']) not in nr: out['skipped_no_news'].append(b['id']); continue
            r = event_result(e, b, nr[str(b['id'])]); r['anchor'] = 'news'
            r['price_jump_R'] = b['R']; r['news_minus_jump_s'] = nr[str(b['id'])] - b['R']
        r['family'] = b['family']; out['rows'].append(r)
    json.dump(out, sys.stdout, indent=1)

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
