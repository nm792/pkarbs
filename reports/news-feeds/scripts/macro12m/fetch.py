"""Pull 12 months of US macro release events (CPI, jobs, FOMC, PPI) and their public trades."""
import json, re, time, os, urllib.request, urllib.parse, datetime as dt
OUT = '/tmp/macro'; os.makedirs(OUT, exist_ok=True)
H = {'User-Agent': 'curl/8.5.0', 'Accept': 'application/json'}
def get(u, tries=4):
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(u, headers=H), timeout=40) as f:
                return json.load(f)
        except Exception as ex:
            err = ex; time.sleep(2 ** i)
    raise err
G = 'https://gamma-api.polymarket.com/'
D = 'https://data-api.polymarket.com/trades?'
LO, HI = '2025-10-20', '2026-10-26'
FOREIGN = r'argentin|china|uk-|eurozone|japan|brazil|mexico|india|korea|south-africa|canada|turkey|germany|australia|egg|how-high|bls-delay|combo|dissent|decisions|cut-by|prints-negative|shutdown|higher-than|will-the-next'
CATS = [('FOMC', r'^fed-decision-in-'), ('PPI', r'ppi|producer-price'), ('CORE_CPI', r'core-cpi'),
        ('CPI', r'inflation'), ('PAYROLLS', r'jobs-added'), ('UNEMP', r'unemployment-rate')]
def cat(slug):
    if re.search(FOREIGN, slug): return None
    for c, rx in CATS:
        if re.search(rx, slug): return c
evs = {}
for q in ['CPI', 'inflation US', 'core CPI', 'jobs added', 'unemployment rate', 'Fed decision', 'PPI', 'producer price index', 'inflation monthly', 'inflation annual']:
    for page in range(1, 6):
        d = get(G + 'public-search?' + urllib.parse.urlencode({'q': q, 'events_status': 'closed', 'limit_per_type': 50, 'page': page}))
        for e in d.get('events') or []:
            c = cat(e['slug'])
            if c: evs[e['id']] = (c, e['slug'])
        if not (d.get('pagination') or {}).get('hasMore'): break
print('candidate events', len(evs))
meta = []
for eid, (c, slug) in sorted(evs.items()):
    e = get(G + 'events?id=' + str(eid))[0]
    mk = []
    for m in e.get('markets') or []:
        try: op = json.loads(m.get('outcomePrices') or '[]')
        except Exception: op = []
        mk.append({'cid': m['conditionId'], 'item': m.get('groupItemTitle') or m.get('question'),
                   'outcomes': json.loads(m.get('outcomes') or '[]'), 'prices': op,
                   'closed': m.get('closedTime'), 'vol': float(m.get('volume') or 0)})
    closed = sorted(x['closed'] for x in mk if x['closed'])
    first_close = closed[0][:10] if closed else None
    if not first_close or not (LO <= first_close <= HI):
        continue
    meta.append({'id': eid, 'cat': c, 'slug': slug, 'title': e['title'], 'first_close': closed[0],
                 'vol': float(e.get('volume') or 0), 'markets': mk})
json.dump(meta, open(OUT + '/meta.json', 'w'))
print('events in window', len(meta))
for m in sorted(meta, key=lambda x: x['first_close']):
    print(m['first_close'][:16], m['cat'], m['slug'], round(m['vol']), len(m['markets']))
