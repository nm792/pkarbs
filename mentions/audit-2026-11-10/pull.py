import json,urllib.request,time,sys
B='https://api.elections.kalshi.com/trade-api/v2/'
def g(u):
    for a in range(5):
        try:return json.load(urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'x'}),timeout=60))
        except Exception as e:
            if hasattr(e,'code') and e.code in(400,404):return None
            time.sleep(1+a)
s=sys.argv[1];out=[];cur=None
for base in ('markets','historical/markets'):
    cur=None
    while True:
        r=g(f"{B}{base}?series_ticker={s}&limit=1000"+(f'&cursor={cur}' if cur else ''))
        if not r:break
        out+=r.get('markets',[]);cur=r.get('cursor')
        if not cur:break
    print(base,len(out))
d={m['ticker']:m for m in out}
json.dump(list(d.values()),open(f'm_{s}.json','w'));print(s,len(d))
