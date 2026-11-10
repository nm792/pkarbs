import urllib.request,json,time
B='https://api.elections.kalshi.com/trade-api/v2'
def g(u):
    for a in range(6):
        try:return json.load(urllib.request.urlopen(urllib.request.Request(B+u,headers={'User-Agent':'research'}),timeout=60))
        except Exception as e:time.sleep(2*(a+1))
    raise RuntimeError(u)
S=g('/series?category=Mentions')['series']
ser=[s['ticker'] for s in S if 'EARNINGS' in s['ticker']]
print(len(S),len(ser),ser[:10])
evs=[]
for t in ser:
    cur=''
    while True:
        r=g(f'/events?series_ticker={t}&status=settled&with_nested_markets=true&limit=200'+(f'&cursor={cur}' if cur else ''))
        evs+=r['events']; cur=r.get('cursor')
        if not cur or not r['events']:break
json.dump(evs,open('kal_events.json','w'))
print(len(evs),sum(len(e.get('markets') or []) for e in evs))
