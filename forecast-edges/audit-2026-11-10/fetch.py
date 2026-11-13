import json,re,requests,time,datetime as dt,concurrent.futures as cf
from zoneinfo import ZoneInfo
NY=ZoneInfo('America/New_York')
MO={m:i+1 for i,m in enumerate('January February March April May June July August September October November December'.split())}
ev=json.load(open('events_all.json')); ts=json.load(open('elon_ts.json'))
jobs=[];evs=[]
for e in ev:
    m=re.match(r'Elon Musk # tweets (\w+) (\d+) - (?:(\w+) )?(\d+), (\d{4})',e['title'])
    if not m: continue
    y=int(m.group(5)); m1=MO[m.group(1)]; d1=int(m.group(2)); m2=MO[m.group(3)] if m.group(3) else m1; d2=int(m.group(4))
    y1=y if m1<=m2 else y-1
    s=dt.datetime(y1,m1,d1,12,tzinfo=NY).timestamp(); en=dt.datetime(y,m2,d2,12,tzinfo=NY).timestamp()
    if round((en-s)/86400)!=7 or s<ts[0]+21*86400: continue
    evs.append(dict(id=e['id'],title=e['title'],start=s,end=en,markets=[(mk.get('groupItemTitle'),mk['conditionId'],mk['outcomePrices']) for mk in e['markets']]))
print(len(evs),'weekly events')
S=requests.Session()
def fetch(job):
    eid,t,c,end=job; out=[];cur=None
    for _ in range(200):
        u="https://data-api.polymarket.com/v2/trades"; p=dict(condition=c,limit=500)
        if cur: p['cursor']=cur
        j=None
        for a in range(5):
            try: j=S.get(u,params=p,timeout=40).json(); 
            except Exception: j=None
            if j and 'data' in j: break
            time.sleep(1+a); j=None
        if j is None: return dict(eid=eid,t=t,err=1,tr=out)
        d=j['data']; out+=[(x['timestamp'],x['side'],x['price'],x['size'],x['outcome_index']) for x in d if x['timestamp']>=end-25*3600]
        if not d or d[-1]['timestamp']<end-25*3600 or not j['pagination'].get('has_more'): break
        cur=j['pagination'].get('next_cursor')
    return dict(eid=eid,t=t,tr=out)
for e in evs:
    for t,c,_ in e['markets']: jobs.append((e['id'],t,c,e['end']))
print(len(jobs),'markets',flush=True)
res=[]
with cf.ThreadPoolExecutor(16) as ex:
    for i,r in enumerate(ex.map(fetch,jobs)):
        res.append(r)
        if i%100==0: print(i,flush=True)
json.dump(dict(evs=evs,tr=res),open('elon_tr.json','w'))
print('done',sum(len(r['tr']) for r in res),sum(1 for r in res if r.get('err')))
