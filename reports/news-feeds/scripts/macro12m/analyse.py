"""Stale-quote pickoff at US macro releases from Polymarket public (taker) trades.

R = official release second, detected as the candidate slot (BLS 12:30Z/13:30Z, FOMC 18:00Z/19:00Z,
on the 45 days up to the first market close) with the most trades in its first 60 s.
Winner per market from gamma outcomePrices after resolution. Edge of a taker trade valued at the
settled outcome: BUY (v - p) * size, SELL (p - v) * size. "Pickoff" = sum of positive edges.
Fee: today's Economics taker fee, 0.05 * p * (1 - p) per share.
Timestamps are Polygon block times (a few seconds after matching).
"""
import json, os, collections, datetime as dt, statistics as st
OUT = '/tmp/macro'
FAM = {'CPI': 'CPI', 'CORE_CPI': 'CPI', 'PAYROLLS': 'JOBS', 'UNEMP': 'JOBS', 'FOMC': 'FOMC', 'PPI': 'PPI'}
SLOTS = {'FOMC': [(18, 0), (19, 0)]}
BINS = (10, 30, 300)
SB = (4, 6, 10, 20, 30)
# release days with no Polymarket trading at the release second
EXCLUDE = {('2025-11-07', 'JOBS'): 'markets closed 7 Nov; Sept 2025 report came out 20 Nov (shutdown)',
           ('2025-11-21', 'CPI'): 'Oct 2025 CPI never published (shutdown)',
           ('2026-06-05', 'JOBS'): 'no trades at 12:30Z; burst at 12:49Z, cause not checked'}
meta = json.load(open(OUT + '/meta.json'))
def ts_of(s): return dt.datetime.fromisoformat(s.replace('+00', '+00:00').replace(' ', 'T')).timestamp()
events = []
for m in meta:
    fn = '%s/tr_%s.json' % (OUT, m['id'])
    if not os.path.exists(fn): continue
    tr = json.load(open(fn))
    rows = tr['rows']
    if not rows: continue
    win = {}
    for x in m['markets']:
        if x['prices'] and sorted(x['prices']) == ['0', '1']:
            win[x['cid']] = x['prices'].index('1')
    fc = ts_of(m['first_close'])
    day0 = dt.datetime.fromtimestamp(fc, dt.timezone.utc).replace(hour=0, minute=0, second=0)
    best = None
    for dd in range(0, 45):
        for h, mi in SLOTS.get(m['cat'], [(12, 30), (13, 30)]):
            c = (day0 - dt.timedelta(days=dd)).replace(hour=h, minute=mi).timestamp()
            if c > fc: continue
            n = sum(1 for r in rows if c <= r['timestamp'] < c + 60)
            pre = sum(1 for r in rows if c - 600 <= r['timestamp'] < c)
            if best is None or n > best[1]: best = (c, n, pre)
    R, n60, pre600 = best
    earliest = min(r['timestamp'] for r in rows)
    ev = {'id': m['id'], 'cat': m['cat'], 'fam': FAM[m['cat']], 'slug': m['slug'], 'R': R, 'n60': n60, 'pre600': pre600,
          'covered': earliest < R - 600, 'status': tr['status'], 'mk': len(m['markets']), 'resolved': len(win),
          'bins': {b: [0, 0.0, 0.0, 0.0] for b in BINS}, 'pre_edge': 0.0, 'wallet': collections.Counter(),
          'cluster': collections.Counter(), 'first': None, 'unres': 0, 'sb': collections.Counter()}
    for r in rows:
        d = r['timestamp'] - R
        if r['conditionId'] not in win:
            if 0 <= d <= 30: ev['unres'] += 1
            continue
        v = 1.0 if r['outcomeIndex'] == win[r['conditionId']] else 0.0
        p, s = float(r['price']), float(r['size'])
        e = (v - p) * s if r['side'] == 'BUY' else (p - v) * s
        fee = 0.05 * p * (1 - p) * s
        if -600 <= d < 0: ev['pre_edge'] += max(e, 0)
        if d < 0 or d > BINS[-1]: continue
        b = next(b for b in BINS if d <= b)
        x = ev['bins'][b]; x[0] += 1; x[1] += s * p; x[2] += max(e, 0); x[3] += max(e - fee, 0)
        if e > 0 and d <= 30:
            ev['wallet'][r['proxyWallet']] += e
            ev['sb'][next(k for k in SB if d <= k)] += e
            ev['cluster'][(r['conditionId'], r['outcomeIndex'], r['side'], round(p, 3))] += e
            ev['first'] = d if ev['first'] is None else min(ev['first'], d)
    events.append(ev)

def iso(t): return dt.datetime.fromtimestamp(t, dt.timezone.utc).strftime('%Y-%m-%d %H:%MZ')
print('event-level')
for ev in sorted(events, key=lambda e: e['R']):
    b = ev['bins']; p30 = b[10][2] + b[30][2]
    top = ev['cluster'].most_common(1)
    print('%s %-8s %-48s n60=%4d pre=%3d cov=%d res=%d/%d unres30=%d first=%s notl30=%7.0f e10=%6.0f e30=%6.0f e300=%5.0f net30=%6.0f pre=%4.0f topcl=%.2f %s' % (
        iso(ev['R']), ev['cat'], ev['slug'][:48], ev['n60'], ev['pre600'], ev['covered'], ev['resolved'], ev['mk'], ev['unres'],
        ev['first'], b[10][1] + b[30][1], b[10][2], b[30][2], b[300][2], b[10][3] + b[30][3], ev['pre_edge'],
        (top[0][1] / p30) if top and p30 else 0, ev['status']))

days = collections.OrderedDict()
for ev in sorted(events, key=lambda e: e['R']):
    k = (iso(ev['R'])[:10], ev['fam'])
    if k in EXCLUDE: continue
    d = days.setdefault(k, {'R': ev['R'], 'ev': [], 'e10': 0, 'e30': 0, 'e300': 0, 'net30': 0, 'notl30': 0, 'wallet': collections.Counter(), 'cluster': collections.Counter(), 'bad': [], 'sb': collections.Counter(), 'first': []})
    d['ev'].append(ev['slug'][:30]); b = ev['bins']
    d['e10'] += b[10][2]; d['e30'] += b[30][2]; d['e300'] += b[300][2]; d['net30'] += b[10][3] + b[30][3]; d['notl30'] += b[10][1] + b[30][1]
    d['wallet'] += ev['wallet']; d['cluster'] += ev['cluster']; d['sb'] += ev['sb']
    if ev['first'] is not None: d['first'].append(ev['first'])
    if not ev['covered'] or ev['status'] != 'ok' or ev['resolved'] < ev['mk'] or ev['n60'] < 5: d['bad'].append(ev['slug'][:25])
print('\nrelease-day level (pool = positive taker edge 0-30 s)')
res = []
allw = collections.Counter(); wdays = collections.Counter()
for (day, fam), d in days.items():
    pool = d['e10'] + d['e30']
    w = d['wallet'].most_common(3)
    top1 = w[0][1] / pool if pool else 0
    top3 = sum(x[1] for x in w) / pool if pool else 0
    cl = d['cluster'].most_common(1)
    lumpy = (cl[0][1] / pool) if cl and pool else 0
    res.append({'day': day, 'fam': fam, 'n_ev': len(d['ev']), 'notl30': d['notl30'], 'pool10': d['e10'], 'pool11_30': d['e30'], 'pool30': pool, 'net30': d['net30'], 'e31_300': d['e300'],
                'top1w': top1, 'top3w': top3, 'lump': lumpy, 'nwal': len(d['wallet']), 'first': min(d['first']) if d['first'] else None, 'sb': {k: d['sb'][k] for k in SB}, 'w': dict(d['wallet'].most_common(5))})
    allw.update(d['wallet']); wdays.update(x for x, v in d['wallet'].items() if v >= 50)
    print('%s %-5s n_ev=%d notl30=%7.0f pool10=%6.0f pool30=%6.0f net30=%6.0f e31_300=%5.0f top1w=%.2f top3w=%.2f nwal=%3d topcluster=%.2f %s' % (
        day, fam, len(d['ev']), d['notl30'], d['e10'], d['e30'], d['net30'], d['e300'], top1, top3, len(d['wallet']), lumpy, ('FLAG ' + ','.join(d['bad'])) if d['bad'] else ''))
json.dump(res, open(OUT + '/days.json', 'w'))
pools = [r['pool30'] for r in res]
print('\nrelease days', len(res), 'total pool 0-30s %.0f net %.0f median %.0f mean %.0f max %.0f' % (sum(pools), sum(r['net30'] for r in res), st.median(pools), st.mean(pools), max(pools)))
for fam in ('CPI', 'JOBS', 'FOMC', 'PPI'):
    p = [r['pool30'] for r in res if r['fam'] == fam]
    if p: print(fam, len(p), 'sum %.0f median %.0f max %.0f' % (sum(p), st.median(p), max(p)))

tot = collections.Counter()
for r in res: tot.update(r['sb'])
T = sum(tot.values())
print('pool by block-time second after release (all days):', ', '.join('<=%ds $%.0f (%.0f%%)' % (k, tot[k], 100 * tot[k] / T) for k in SB))
print('first positive-edge print, s after R:', sorted(r['first'] for r in res if r['first'] is not None))

print('\ntop wallets over the year (pool $ in 0-30 s, days with >= $50):')
Ttot = sum(allw.values())
for w, v in allw.most_common(8): print('  %s $%.0f (%.0f%%) on %d days' % (w[:10], v, 100 * v / Ttot, wdays[w]))
print('days where the year-top-3 wallets took the most:', sum(1 for r in res if r['w'] and max(r['w'], key=r['w'].get) in dict(allw.most_common(3))))
for lab, f in (('Oct25-Apr26', lambda r: r['day'] < '2026-05-01'), ('May26-Oct26', lambda r: r['day'] >= '2026-05-01')):
    rr = [r for r in res if f(r)]; c = collections.Counter()
    for r in rr: c.update(r['sb'])
    t = sum(c.values())
    print(lab, 'days', len(rr), 'pool $%.0f' % t, 'median day $%.0f' % st.median([r['pool30'] for r in rr]), 'share <=6s %.0f%%, 7-10s %.0f%%, 11-30s %.0f%%' % (100 * (c[4] + c[6]) / t, 100 * c[10] / t, 100 * (c[20] + c[30]) / t),
          'first prints', sorted(r['first'] for r in rr if r['first'] is not None))
med = st.median(pools)
lumpy = [r for r in res if r['pool30'] >= 3 * med]
print('lumpy days (>= 3x median $%.0f):' % med, len(lumpy), '$%.0f' % sum(r['pool30'] for r in lumpy), [(r['day'], r['fam'], round(r['pool30'])) for r in lumpy])
print('one resting level > 50%% of day pool: %d of %d days' % (sum(1 for r in res if r['lump'] > 0.5), len(res)))
srt = sorted(pools, reverse=True); print('top1 share %.0f%% top3 %.0f%% top5 %.0f%%' % tuple(100 * sum(srt[:k]) / sum(srt) for k in (1, 3, 5)))
