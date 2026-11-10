import json,urllib.request,time,concurrent.futures as cf
E=json.load(open('/mnt/project-files/mrbeast-markets/mentions/pm_mm_events.json'))
er=[e for e in E if 'earnings' in (e.get('title') or '').lower()]
def g(u):
    for a in range(5):
        try:return json.load(urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'research'}),timeout=40))
        except Exception as e:
            if getattr(e,'code',0) in(400,404):return None
            time.sleep(1+a)
def one(m):
    out=[];url='https://data-api.polymarket.com/v2/trades?condition=%s&limit=500'%m['conditionId'];flag=None
    r=g(url)
    if not r:return m['conditionId'],[],None
    out+=r['data'];pg=r.get('pagination');flag=pg if len(r['data'])>=500 else None
    return m['conditionId'],[(x['timestamp'],x['side'],x['outcome_index'],x['price'],x['size']) for x in out],flag
ms=[m for e in er for m in e['markets']]
res={};fl=0
with cf.ThreadPoolExecutor(16) as ex:
    for i,(c,t,f) in enumerate(ex.map(one,ms)):
        res[c]=t
        if f:fl+=1;print('FULLPAGE',c,f,flush=True)
        if i%300==0:print(i,flush=True)
json.dump(res,open('pm_trades.json','w'));print('done',len(res),sum(map(len,res.values())),'fullpages',fl)
