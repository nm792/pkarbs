#!/usr/bin/env python3
"""Rerun of the stale-ask pickoff scan (Reviewer, 26 Nov), ON PRIME (R-039). Changes vs run.py; scan.py is reused unchanged:
  1. NEWS-TIME anchor for ONSET families: R = the time the deciding news first became public (webb T113 news_times.csv:
     tweet/post time, wire, official call, or the rule deadline for NO-by-date). This replaces R = price jump, which is defined from the price itself.
     An onset event without a T113 row is SKIPPED and listed, never anchored on the price.
  2. FEES: each market's own feeSchedule (rate x p x (1-p) per share, exponent 1) is deducted. A market with no schedule gets fee 0 and is counted in `no_fee_schedule`.
  3. COMPLETENESS: a market whose fetched prints do not reach back to R-60 s (page cap or stop heuristic) is flagged `incomplete` and excluded, never read as "no prints".
  4. A T113 row whose source_type is rule_deadline (NO on a 'by <date>' market) is a known time, so its anchor is 'deadline', reported apart and kept out of the news group.
  5. STALE WINDOW per event (Nick 26 Nov 05:23Z hypothesis: unscheduled news leaves asks up longer because makers cannot pull ahead of an unknown time):
     W_ub = first winner BUY print at >= 0.95 after R (no cheap ask left then); W_lb = last winner BUY print < 0.95 before W_ub (cheap asks lasted at least that long), within 300 s.
     compare() tests, pre-registered: H = news group has a larger median edge_after_fee per event at L=5 AND a longer median W_lb than calendar (one-sided rank-sum permutation p < 0.05 on both, 10,000 draws, MC type 1).
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
        try: out[str(r['event_id'])] = (int(dt.datetime.fromisoformat(r['news_utc'].replace('Z', '+00:00')).timestamp()), (r.get('source_type') or '').strip())
        except (KeyError, ValueError): pass
    return out

def window(rows, wtok, R, horizon=300):
    b = sorted((r['ts'], r['p']) for r in rows if r['tok'] == wtok and r['side'] == 'BUY' and R < r['ts'] <= R + horizon)
    ub = next((t - R for t, p in b if p >= scan.PMAX), None)
    hi = R + (ub if ub is not None else horizon)
    c = [t for t, p in b if p < scan.PMAX and t <= hi]
    return (max(c) - R) if c else 0, ub

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
        lb, ub = window(rows, w, R); res.setdefault('W', []).append((lb, ub))
        for L in scan.LS: allp[L] += [(t, p, s, rate) for t, p, s in o[L]]
    for L in scan.LS:
        paid = edge = 0.0
        for rate in set(x[3] for x in allp[L]):
            pe = edge_after_fee([(t, p, s) for t, p, s, r in allp[L] if r == rate], rate)
            paid += pe[0]; edge += pe[1]
        res['stats'][L] = dict(n=len(allp[L]), paid=round(paid, 2), edge_after_fee=round(edge, 2))
    ws = res.get('W', [])
    res['W_lb_max'] = max((x[0] for x in ws), default=0)
    res['W_ub_min'] = min((x[1] for x in ws if x[1] is not None), default=None)
    return res

def compare(rows, L=5, draws=10000, seed=7):
    import random, statistics
    g = {a: [r for r in rows if r['anchor'] == a] for a in ('news', 'calendar')}
    if not g['news'] or not g['calendar']:
        return dict(verdict='n/a (a group is empty)', n_news=len(g['news']), n_calendar=len(g['calendar']))
    def stat(rs, k): return statistics.median([r['stats'][L]['edge_after_fee'] if k == 'edge' else r['W_lb_max'] for r in rs])
    out = dict(n_news=len(g['news']), n_calendar=len(g['calendar']))
    rng = random.Random(seed)
    def val(r, k): return r['stats'][L]['edge_after_fee'] if k == 'edge' else r['W_lb_max']
    def ranksum(vals, nn):   # mean rank of the first nn values minus mean rank of the rest (ties get average ranks)
        order = sorted(range(len(vals)), key=lambda i: vals[i]); rk = [0.0] * len(vals); i = 0
        while i < len(order):
            j = i
            while j + 1 < len(order) and vals[order[j + 1]] == vals[order[i]]: j += 1
            for q in range(i, j + 1): rk[order[q]] = (i + j) / 2 + 1
            i = j + 1
        return sum(rk[:nn]) / nn - sum(rk[nn:]) / (len(vals) - nn)
    for k in ('edge', 'W_lb'):
        vals = [val(r, k) for r in g['news']] + [val(r, k) for r in g['calendar']]; nn = len(g['news'])
        obs = ranksum(vals, nn); hits = 0
        for _ in range(draws):
            rng.shuffle(vals)
            if ranksum(vals, nn) >= obs - 1e-12: hits += 1
        out[k] = dict(median_news=stat(g['news'], k), median_calendar=stat(g['calendar'], k), diff=stat(g['news'], k) - stat(g['calendar'], k), rank_diff=obs, p_one_sided=(hits + 1) / (draws + 1))
    sup = all(out[k]['diff'] > 0 and out[k]['p_one_sided'] < 0.05 for k in ('edge', 'W_lb'))
    out['verdict'] = 'SUPPORTS H' if sup else ('AGAINST H' if all(out[k]['diff'] <= 0 for k in ('edge', 'W_lb')) else 'NOT SHOWN')
    out['note'] = 'per-event medians; W from prints (1 s resolution), a floor on how long asks stayed; MC type 1 permutation of group labels on the rank-sum (Mann-Whitney) statistic'
    return out

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
            tR, st = nr[str(b['id'])]
            r = event_result(e, b, tR)
            r['anchor'] = 'deadline' if st == 'rule_deadline' else 'news'   # a rule deadline is a KNOWN time: kept out of the unscheduled group
            r['price_jump_R'] = b['R']; r['news_minus_jump_s'] = tR - b['R']
        r['family'] = b['family']; out['rows'].append(r)
    out['compare_L5'] = compare(out['rows'])
    json.dump(out, sys.stdout, indent=1)

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
