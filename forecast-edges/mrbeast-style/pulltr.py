import json,urllib.request,time,sys,concurrent.futures as cf,os
evf,outf=sys.argv[1],sys.argv[2]
D=json.load(open(evf))
cache=json.load(open(outf)) if os.path.exists(outf) else {}
jobs=[]
for e in D.values():
    for m in e['markets']:
        if m['conditionId'] not in cache: jobs.append(m['conditionId'])
print(len(jobs),'todo',flush=True)
def fetch(c):
    out=[];cur=None
    for _ in range(150):
        u=f"https://data-api.polymarket.com/v2/trades?condition={c}&limit=500"+(f"&cursor={cur}" if cur else "")
        j=None
        for a in range(5):
            try: j=json.load(urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'x'}),timeout=40));break
            except Exception: time.sleep(1+a)
        if j is None: return c,None
        out+=[(x['timestamp'],x['side'],x['price'],x['size'],x['outcome_index']) for x in j['data']]
        p=j['pagination']
        if not p.get('has_more'): break
        cur=p.get('next_cursor')
        if not cur: break
    return c,out
n=0
with cf.ThreadPoolExecutor(12) as ex:
    for c,o in ex.map(fetch,jobs):
        if o is not None: cache[c]=o
        n+=1
        if n%100==0:
            json.dump(cache,open(outf,'w')); print(n,flush=True)
json.dump(cache,open(outf,'w')); print('done',len(cache),sum(len(v) for v in cache.values()))
