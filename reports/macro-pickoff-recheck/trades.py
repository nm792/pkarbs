"""Page public taker trades (Data API v2, cursor paging, newest first) per event until 2 days before the first market close.
Per event via event_id (v2 has no offset cap). Output /tmp/macro2/tr_<id>.json, rows keep the v1 field names analyse.py uses."""
import json, time, os, urllib.request, datetime as dt
from concurrent.futures import ThreadPoolExecutor
OUT = '/tmp/macro2'
H = {'User-Agent': 'curl/8.5.0', 'Accept': 'application/json'}
def get(u, tries=5):
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(u, headers=H), timeout=60) as f:
                return json.load(f)
        except Exception as ex:
            err = ex; time.sleep(2 ** i)
    raise err
def one(m):
    fn = '%s/tr_%s.json' % (OUT, m['id'])
    if os.path.exists(fn): return
    fc = dt.datetime.fromisoformat(m['first_close'].replace('+00', '+00:00').replace(' ', 'T')).timestamp()
    stop = fc - 2 * 86400
    rows, status, cur = [], 'ok', None
    while True:
        u = 'https://data-api.polymarket.com/v2/trades?event_id=%s&limit=1000' % m['id'] if cur is None else 'https://data-api.polymarket.com/v2/trades?event_id=%s&cursor=%s' % (m['id'], cur)
        try: d = get(u)
        except Exception as ex: status = 'err: %s' % ex; break
        data = d.get('data') or []
        rows += [{'proxyWallet': r['proxy_wallet'], 'side': r['side'], 'conditionId': r['condition_id'], 'size': r['size'], 'price': r['price'],
                  'timestamp': r['timestamp'], 'outcomeIndex': r['outcome_index'], 'transactionHash': r['transaction_hash']} for r in data]
        cur = (d.get('pagination') or {}).get('next_cursor')
        if not cur or not data or data[-1]['timestamp'] < stop: break
    json.dump({'status': status, 'rows': rows}, open(fn, 'w'))
    print(m['id'], m['slug'][:40], len(rows), status, flush=True)
meta = json.load(open(OUT + '/meta.json'))
with ThreadPoolExecutor(4) as ex: list(ex.map(one, meta))
print('DONE')
