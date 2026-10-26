"""Re-pull events that hit the 10.5k-row cap: one market at a time, trades >= $MIN notional only."""
import json, sys, time, urllib.request, datetime as dt
OUT = '/tmp/macro'; MIN = int(sys.argv[1])
H = {'User-Agent': 'curl/8.5.0', 'Accept': 'application/json'}
def get(u):
    for i in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(u, headers=H), timeout=40) as f: return json.load(f)
        except Exception as ex: err = ex; time.sleep(2 ** i)
    raise err
meta = json.load(open(OUT + '/meta.json'))
for m in meta:
    fn = '%s/tr_%s.json' % (OUT, m['id'])
    try: tr = json.load(open(fn))
    except Exception: continue
    if tr['status'] == 'ok' or tr.get('min'): continue
    fc = dt.datetime.fromisoformat(m['first_close'].replace('+00', '+00:00').replace(' ', 'T')).timestamp()
    stop = fc - 86400; rows = []; status = 'ok'
    for x in m['markets']:
        off = 0
        while True:
            d = get('https://data-api.polymarket.com/trades?limit=500&offset=%d&market=%s&filterType=CASH&filterAmount=%d' % (off, x['cid'], MIN))
            if not d: break
            rows += [{k: r[k] for k in ('proxyWallet', 'side', 'conditionId', 'size', 'price', 'timestamp', 'outcomeIndex', 'transactionHash')} for r in d]
            if d[-1]['timestamp'] < stop or len(d) < 500: break
            off += 500
            if off > 10000: status = 'hit offset cap in ' + str(x['item']); break
    json.dump({'status': status, 'rows': rows, 'min': MIN}, open(fn, 'w'))
    print(m['id'], m['slug'][:40], len(rows), status, min(r['timestamp'] for r in rows) if rows else None, flush=True)
print('DONE')
