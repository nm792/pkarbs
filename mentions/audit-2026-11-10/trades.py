import json,urllib.request,time,sys,datetime as dt,concurrent.futures as cf
B='https://api.elections.kalshi.com/trade-api/v2/'
def g(u):
    for a in range(5):
        try:return json.load(urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'x'}),timeout=60))
        except Exception as e:
            if hasattr(e,'code') and e.code in(400,404):return None
            time.sleep(1+a)
def ts(s):return int(dt.datetime.fromisoformat(s.replace('Z','+00:00')).timestamp())
s=sys.argv[1]
M=[m for m in json.load(open(f'm_{s}.json')) if m['result'] in('yes','no')]
def tp(m):
    o=ts(m['open_time']);out=[]
    for base in('historical/trades','markets/trades'):
        cur=None
        for _ in range(10):
            r=g(f"{B}{base}?ticker={m['ticker']}&min_ts={o}&max_ts={o+7200}&limit=1000"+(f'&cursor={cur}' if cur else ''))
            if not r:break
            out+=[(x['created_time'],x['taker_side'],float(x['yes_price_dollars']),float(x['no_price_dollars']),float(x['count_fp'])) for x in r.get('trades',[])]
            cur=r.get('cursor')
            if not cur:break
        if out:break
    return m['ticker'],out
res={}
with cf.ThreadPoolExecutor(10) as ex:
    for i,(t,o) in enumerate(ex.map(tp,M)):
        res[t]=o
        if i%2000==0:print(s,i,len(M),flush=True)
json.dump(res,open(f't_{s}.json','w'));print('done',s,sum(len(v) for v in res.values()))
