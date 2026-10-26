"""Page public trades (newest first) per event until 2 days before the first market close."""
import json, time, os, urllib.request, datetime as dt
OUT = '/tmp/macro'
H = {'User-Agent': 'curl/8.5.0', 'Accept': 'application/json'}
def get(u, tries=4):
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(u, headers=H), timeout=40) as f:
                return json.load(f)
        except Exception as ex:
            err = ex; time.sleep(2 ** i)
    raise err
meta = json.load(open(OUT + '/meta.json'))
for m in meta:
    fn = '%s/tr_%s.json' % (OUT, m['id'])
    if os.path.exists(fn): continue
    fc = dt.datetime.fromisoformat(m['first_close'].replace('+00', '+00:00').replace(' ', 'T')).timestamp()
    stop = fc - 2 * 86400
    cids = [x['cid'] for x in m['markets']]
    rows, status = [], 'ok'
    for chunk in range(0, len(cids), 20):
        cs = ','.join(cids[chunk:chunk + 20]); off = 0
        while True:
            try:
                d = get('https://data-api.polymarket.com/trades?limit=500&offset=%d&market=%s' % (off, cs))
            except Exception as ex:
                status = 'err offset %d: %s' % (off, ex); break
            if not d: break
            rows += [{k: r[k] for k in ('proxyWallet', 'side', 'conditionId', 'size', 'price', 'timestamp', 'outcomeIndex', 'transactionHash')} for r in d]
            if d[-1]['timestamp'] < stop or len(d) < 500: break
            off += 500
            if off > 10000: status = 'hit offset cap'; break
    json.dump({'status': status, 'rows': rows}, open(fn, 'w'))
    print(m['id'], m['slug'][:40], len(rows), status, flush=True)
print('DONE')
