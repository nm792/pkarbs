import json, collections, datetime as dt
OUT = '/tmp/macro'
meta = {m['id']: m for m in json.load(open(OUT + '/meta.json'))}
def load(eid):
    m = meta[eid]; rows = json.load(open('%s/tr_%s.json' % (OUT, eid)))['rows']
    win = {x['cid']: x['prices'].index('1') for x in m['markets'] if x['prices'] and sorted(x['prices']) == ['0', '1']}
    item = {x['cid']: x['item'] for x in m['markets']}
    return m, rows, win, item
def prof(eid, R, lo=-20, hi=30, show=True):
    m, rows, win, item = load(eid)
    sec = collections.defaultdict(lambda: [0, 0.0, 0.0])
    big = []
    for r in rows:
        d = r['timestamp'] - R
        if not lo <= d <= hi or r['conditionId'] not in win: continue
        v = 1.0 if r['outcomeIndex'] == win[r['conditionId']] else 0.0
        p, s = float(r['price']), float(r['size'])
        e = (v - p) * s if r['side'] == 'BUY' else (p - v) * s
        sec[d][0] += 1; sec[d][1] += s * p; sec[d][2] += max(e, 0)
        if e > 300: big.append((d, item[r['conditionId']], r['side'], r['outcomeIndex'], p, round(s), round(e), r['proxyWallet'][:8]))
    if show:
        print(m['slug'])
        print(' '.join('%d:%d/%.0f' % (d, sec[d][0], sec[d][2]) for d in sorted(sec)))
        for b in sorted(big)[:25]: print('   ', b)
    return sec
# 1) FOMC Jul, FOMC Sep, CPI Jul, CPI Oct core
def ts(s): return int(dt.datetime.fromisoformat(s).replace(tzinfo=dt.timezone.utc).timestamp())
prof('287395', ts('2026-07-29 18:00'))
prof('481717', ts('2026-09-16 18:00'))
prof('35090', ts('2025-12-10 19:00'))
prof('580294', ts('2026-07-14 12:30'))
# 2) zero-n60 events: where are their trades?
for eid in ('462457', '462423', '42245', '42244', '80638'):
    if eid not in meta: print('missing', eid); continue
    m, rows, win, item = load(eid)
    t = sorted(r['timestamp'] for r in rows)
    print(m['slug'], 'rows', len(rows), 'first', dt.datetime.utcfromtimestamp(t[0]) if t else None, 'last', dt.datetime.utcfromtimestamp(t[-1]) if t else None, 'close', m['first_close'])
    c = collections.Counter(dt.datetime.utcfromtimestamp(x).strftime('%m-%d %H:%M') for x in t)
    print('   busiest minutes', c.most_common(5))
