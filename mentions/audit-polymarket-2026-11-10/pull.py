import json,urllib.request,time,sys,re,datetime as dt,collections,concurrent.futures as cf
E=json.load(open('pm_mm_events.json'))
def fam(e):
    t=(e.get('title') or '').lower()
    if 'trump' in t and 'week' in t:return 'trump-weekly'
    if 'trump' in t:return 'trump-event'
    if 'earnings' in t:return 'earnings-call'
    if 'nfl' in t or 'announcer' in t or 'nba' in t or 'game' in t:return 'sports-announcers'
    return 'other'
def start(e):return min((m.get('startDate') or e.get('startDate') or '') for m in e['markets'])
def ok(e):
    for m in e['markets']:
        try:p=json.loads(m['outcomePrices'])
        except Exception:return False
        if max(float(x) for x in p)<.99:return False
    return len(e['markets'])>=3
def ts(s):
    s=s.replace(' ','T').replace('Z','+00:00')
    if re.search(r'[+-]\d\d$',s):s+=':00'
    return dt.datetime.fromisoformat(s).timestamp()
E=[e for e in E if ok(e)]
fams=collections.defaultdict(list)
for e in E:fams[fam(e)].append(e)
post=[]
for f,L in fams.items():
    L.sort(key=start);b=max(10,int(.3*len(L)));post+=L[b:]
def g(u):
    for a in range(6):
        try:return json.load(urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'x'}),timeout=60))
        except Exception as e:
            if hasattr(e,'code') and e.code in(400,404):return None
            time.sleep(1+a)
def pt(m,t0):
    c=m['conditionId'];out=[];cur=None;first=None
    for _ in range(600):
        r=g(f"https://data-api.polymarket.com/v2/trades?condition={c}&limit=500"+(f'&cursor={cur}' if cur else ''))
        if not r:break
        for x in r['data']:
            t=x['timestamp'];first=t if first is None else min(first,t)
            if t<=t0+86400:out.append((t,x['side'],x['price'],x['size'],x['outcome_index']))
        p=r['pagination']
        if not p.get('has_more') or not p.get('next_cursor'):break
        cur=p['next_cursor']
    return c,(first,out)
jobs=[(m,ts(start(e))) for e in post for m in e['markets']]
print(len(post),len(jobs),flush=True)
res={}
with cf.ThreadPoolExecutor(14) as ex:
    futs=[ex.submit(pt,m,t0) for m,t0 in jobs]
    for i,f in enumerate(futs):
        c,v=f.result();res[c]=v
        if i%1000==0:print(i,flush=True)
json.dump(res,open('pm_trades.json','w'));print('done',sum(len(v[1]) for v in res.values()))
