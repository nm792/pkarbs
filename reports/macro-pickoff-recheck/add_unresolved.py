"""Oct 2026 CPI YoY and core YoY (events 1189074, 1189689) were still not formally resolved on 20 Nov (closed=False, no closedTime)
though one bracket sits at 0.99+. Add them to meta with INFERRED winners (Yes price >= 0.99), flagged inferred=True."""
import json, urllib.request
OUT = '/tmp/macro2'; H = {'User-Agent': 'curl/8.5.0'}
def get(u): return json.load(urllib.request.urlopen(urllib.request.Request(u, headers=H), timeout=40))
meta = json.load(open(OUT + '/meta.json'))
have = {m['id'] for m in meta}
for eid, cat in (('1189074', 'CPI'), ('1189689', 'CORE_CPI')):
    if eid in have: continue
    e = get('https://gamma-api.polymarket.com/events?id=' + eid)[0]
    mk = []
    for m in e['markets']:
        op = json.loads(m['outcomePrices']); yes = float(op[0])
        mk.append({'cid': m['conditionId'], 'item': m.get('groupItemTitle'), 'outcomes': json.loads(m['outcomes']),
                   'prices': ['1', '0'] if yes >= 0.99 else (['0', '1'] if yes <= 0.01 else op), 'closed': None, 'vol': float(m.get('volume') or 0)})
    print(eid, e['slug'], [(x['item'], x['prices']) for x in mk if x['prices'][0] == '1'])
    meta.append({'id': eid, 'cat': cat, 'slug': e['slug'] + '-INFERRED', 'title': e['title'], 'first_close': '2026-11-10 15:31:52+00', 'vol': float(e.get('volume') or 0), 'markets': mk})
json.dump(meta, open(OUT + '/meta.json', 'w'))
