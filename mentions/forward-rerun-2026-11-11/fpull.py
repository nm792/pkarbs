import json,urllib.request,urllib.error,time,sys,datetime as dt,concurrent.futures as cf
B='https://api.elections.kalshi.com/trade-api/v2/'
FREEZE=dt.datetime(2026,11,10,15,0,tzinfo=dt.timezone.utc).timestamp()
LOG=open('fpull.log','a')
def g(u):
    for a in range(9):
        try:return json.load(urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'x'}),timeout=60))
        except urllib.error.HTTPError as e:
            if e.code in(400,404):return None
            w=min(60,2**a)+(int(e.headers.get('Retry-After',0)) if e.code==429 else 0)
            LOG.write(f'{e.code} retry in {w}s {u[-60:]}\n');LOG.flush();time.sleep(w)
        except Exception as e:
            LOG.write(f'err {e} {u[-60:]}\n');LOG.flush();time.sleep(min(30,2**a))
    LOG.write('GAVE UP '+u+'\n');LOG.flush();raise RuntimeError('gave up '+u)
def ts(s):return dt.datetime.fromisoformat(s.replace('Z','+00:00')).timestamp()
SER=['KXVANCEMENTION','KXNFLMENTION','KXNBAMENTION','KXWCMENTION','KXMAMDANIMENTION','KXBERNIEMENTION','KXSECPRESSMENTION','KXTRUMPMENTIONB','KXTRUMPSAY','KXTRUMPMENTION']
def pullm(s):
    out={}
    for base in('markets','historical/markets'):
        cur=None
        while True:
            r=g(f"{B}{base}?series_ticker={s}&limit=1000"+(f'&cursor={cur}' if cur else ''))
            if not r:break
            for m in r.get('markets',[]):out[m['ticker']]=m
            cur=r.get('cursor')
            if not cur:break
    return s,list(out.values())
def tp(m):
    o=ts(m['open_time']);out=[]
    for base in('markets/trades','historical/trades'):
        cur=None
        for _ in range(10):
            r=g(f"{B}{base}?ticker={m['ticker']}&min_ts={int(o)}&max_ts={int(o)+7200}&limit=1000"+(f'&cursor={cur}' if cur else ''))
            if not r:break
            out+=[(x['created_time'],x['taker_side'],float(x['yes_price_dollars']),float(x['no_price_dollars']),float(x['count_fp'])) for x in r.get('trades',[])]
            cur=r.get('cursor')
            if not cur:break
        if out:break
    return m['ticker'],out
if __name__=='__main__':
    with cf.ThreadPoolExecutor(3) as ex:
        for s,ms in ex.map(pullm,SER):
            json.dump(ms,open(f'm_{s}.json','w'));print(s,len(ms),flush=True)
    now=time.time();summary={}
    for s in SER:
        M=json.load(open(f'm_{s}.json'))
        fw=[m for m in M if ts(m['open_time'])>=FREEZE and ts(m['open_time'])<=now]
        done=[m for m in fw if m['result'] in('yes','no')]
        summary[s]=dict(forward_markets=len(fw),resolved=len(done),events_forward=len({m['event_ticker'] for m in fw}),events_resolved=len({m['event_ticker'] for m in done}))
        res={}
        with cf.ThreadPoolExecutor(4) as ex:
            for t,o in ex.map(tp,done):res[t]=o
        json.dump(res,open(f't_{s}.json','w'));print(s,summary[s],sum(len(v) for v in res.values()),flush=True)
    json.dump(summary,open('summary.json','w'))
    print('DONE')
