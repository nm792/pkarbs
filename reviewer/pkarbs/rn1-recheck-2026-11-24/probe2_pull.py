import json,urllib.request,time,os,concurrent.futures as F
U='0x2005d16a84ceefa912d4e380cd32e7ff827875ea'
def get(u):
    for a in range(6):
        try: return json.load(urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'curl/8.5.0'}),timeout=60))
        except Exception as e: time.sleep(2*(a+1))
    return None
def pull(q,cid,cap=100):
    out=[];cur=None
    for i in range(cap):
        d=get('https://data-api.polymarket.com/v2/trades?'+q+'&limit=500'+(f'&cursor={cur}' if cur else ''))
        if d is None: return None
        for r in d['data']: assert r['condition_id']==cid
        out+=d['data'];cur=d['pagination'].get('next_cursor')
        if not d['pagination'].get('has_more'): break
    return out
mk=json.load(open('mk3.json'))
os.makedirs('rn',exist_ok=True);os.makedirs('tapes',exist_ok=True)
rank={}
for x in mk: rank.setdefault(x[0],[]).append(x)
jobs=[]
for lg,L in rank.items():
    for i,x in enumerate(L): jobs.append((lg,i,x))
def work(j):
    lg,i,(s,cid,pnl,vol,slug)=j
    f=f'rn/{slug}.json'
    if not os.path.exists(f) and not os.path.exists(f'tapes/{slug}.json'):
        a=pull(f'user={U}&condition_id={cid}&taker_only=false',cid);t=pull(f'user={U}&condition_id={cid}&taker_only=true',cid)
        if a is None or t is None: return slug,'FAIL'
        json.dump({'slug':slug,'cid':cid,'pnl':pnl,'vol':vol,'all':a,'tk':t},open(f,'w'))
    if i<80 and not os.path.exists(f'tapes/{slug}.json'):
        d=json.load(open(f));tp=pull(f'condition_id={cid}&taker_only=true',cid)
        if tp is not None: d['tape']=tp;json.dump(d,open(f'tapes/{slug}.json','w'))
    return slug,'ok'
with F.ThreadPoolExecutor(6) as ex:
    n=0
    for s,st in ex.map(work,jobs):
        n+=1
        if st!='ok' or n%100==0: print(n,s,st,flush=True)
# gamma start times per event
ev=set()
for x in mk:
    sl=x[4]; parts=sl.split('-')
    ev.add(sl)
starts={}
def g(sl):
    # try progressively shorter slugs
    p=sl.split('-')
    for k in range(len(p),3,-1):
        d=get('https://gamma-api.polymarket.com/markets?closed=true&slug='+'-'.join(p[:k]))
        if d: return sl,(d[0].get('gameStartTime') or d[0].get('eventStartTime'))
    return sl,None
with F.ThreadPoolExecutor(6) as ex:
    for sl,st in ex.map(g,ev): starts[sl]=st
json.dump(starts,open('starts.json','w'));print('starts',sum(1 for v in starts.values() if v),len(starts))
