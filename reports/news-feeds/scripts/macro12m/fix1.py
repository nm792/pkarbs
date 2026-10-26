import json, time, urllib.request
H = {'User-Agent': 'curl/8.5.0'}
m = [x for x in json.load(open('/tmp/macro/meta.json')) if x['id'] == '80638'][0]
cs = ','.join(x['cid'] for x in m['markets']); rows = []; off = 0; stop = 1766000000  # 2025-12-17 19:33Z
while off <= 10000:
    d = json.load(urllib.request.urlopen(urllib.request.Request('https://data-api.polymarket.com/trades?limit=500&offset=%d&market=%s' % (off, cs), headers=H), timeout=40))
    if not d: break
    rows += [{k: r[k] for k in ('proxyWallet', 'side', 'conditionId', 'size', 'price', 'timestamp', 'outcomeIndex', 'transactionHash')} for r in d]
    if d[-1]['timestamp'] < stop or len(d) < 500: break
    off += 500
json.dump({'status': 'ok', 'rows': rows}, open('/tmp/macro/tr_80638.json', 'w'))
print(len(rows), min(r['timestamp'] for r in rows))
