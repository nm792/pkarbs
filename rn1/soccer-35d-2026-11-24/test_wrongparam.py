# planted wrong-param test (R-080): 'wallet' and 'user_address' are NOT filters in v2; the wallet assertion used by pull.py must reject the result.
import json,urllib.request,urllib.parse
W='0x2005d16a84ceefa912d4e380cd32e7ff827875ea'
def rows(p):
    return json.load(urllib.request.urlopen(urllib.request.Request('https://data-api.polymarket.com/v2/trades?'+urllib.parse.urlencode(p),headers={'User-Agent':'x'}),timeout=40))['data']
def accepted(rs): return all(r['proxy_wallet'].lower()==W for r in rs)
ok=accepted(rows({'user':W,'limit':50})); print('valid param user= passes assertion:',ok)
for bad in ('wallet','user_address','maker'):
    a=accepted(rows({bad:W,'limit':50})); print(f'wrong param {bad}= passes assertion (must be False):',a)
    assert not a
assert ok; print('PASS')
