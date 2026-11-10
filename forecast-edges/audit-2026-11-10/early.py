import json,re,math,datetime as dt,collections,statistics as st,requests,concurrent.futures as cf,time,random
MO={m:i+1 for i,m in enumerate('January February March April May June July August September October November December'.split())}
ev=json.load(open('events_all.json'))
E=[]
for e in ev:
    m=re.match(r'Elon Musk # tweets (\w+) (\d+) - (?:(\w+) )?(\d+), (\d{4})',e['title'])
    if not m: continue
    y=int(m.group(5)); m1=MO[m.group(1)]; m2=MO[m.group(3)] if m.group(3) else m1
    y1=y if m1<=m2 else y-1
    s=dt.date(y1,m1,int(m.group(2))); en=dt.date(y,m2,int(m.group(4)))
    if (en-s).days!=7: continue
    E.append((e,s,en))
print(len(E),'weekly events')
S=requests.Session()
def hist(job):
    tok,s0,e0=job
    for a in range(4):
        try:
            j=S.get('https://clob.polymarket.com/prices-history',params=dict(market=tok,startTs=s0,endTs=e0,fidelity=60),timeout=40).json()
            return j.get('history',[])
        except Exception: time.sleep(1+a)
    return None
jobs=[]
for i,(e,s,en) in enumerate(E):
    for mk in e['markets']: jobs.append((i,mk.get('groupItemTitle'),json.loads(mk['clobTokenIds'])[0],float(json.loads(mk['outcomePrices'])[0])==1.0,int(dt.datetime(s.year,s.month,s.day,tzinfo=dt.timezone.utc).timestamp())-86400,int(dt.datetime(en.year,en.month,en.day,tzinfo=dt.timezone.utc).timestamp())+86400))
with cf.ThreadPoolExecutor(16) as ex: H=list(ex.map(lambda j:hist((j[2],j[4],j[5])),jobs))
json.dump(dict(E=[(e['id'],e['title'],str(s),str(en)) for e,s,en in E],jobs=jobs,H=H),open('early_h.json','w'))
print('done',sum(1 for h in H if h is None),'failed',sum(1 for h in H if h==[]),'empty')
