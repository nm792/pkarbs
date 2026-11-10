from pmaudit import *
D=data();rows=[]
for f,evs in D.items():
    n=len(evs);byK=sorted(range(n),key=lambda i:evs[i]['K']);hist=collections.defaultdict(lambda:[0,0]);ptr=0
    for i,e in enumerate(evs):
        while ptr<n and evs[byK[ptr]]['K']<e['t0']:
            for m in evs[byK[ptr]]['mk']:
                h=hist[m['word']];h[0]+=1;h[1]+=m['w']
            ptr+=1
        if e['burn']:continue
        gp=sum(h[1] for h in hist.values())/max(1,sum(h[0] for h in hist.values()));tot=0;k=0
        for m in e['mk']:
            pr=[x for x in m['pr'] if x[0]<=e['t0']+3600]
            if not pr:continue
            h=hist[m['word']];q=(h[1]+2*gp)/(h[0]+2);w=m['w'];x=pr[0];mk=x[2] if x[4]==0 else 1-x[2]
            mk=min(max(mk,.01),.99);qq=min(max(q,.01),.99)
            tot+=(w*log(qq)+(1-w)*log(1-qq))-(w*log(mk)+(1-w)*log(1-mk));k+=1
        if k:rows.append((f,e['t0'],tot/k,k))
v=[r[2] for r in rows];print('events',len(v),'mean',round(S.mean(v),4),'event t',round(tstat(v),2))
wk=collections.defaultdict(float)
for f,t,m,k in rows:wk[dt.datetime.fromtimestamp(t).strftime('%G-%V')]+=m
print('week-cluster t',round(tstat(list(wk.values())),2),len(wk))
med=sorted(r[1] for r in rows)[len(rows)//2]
for nm,sel in (('earlier',lambda r:r[1]<med),('later',lambda r:r[1]>=med)):
    vv=[r[2] for r in rows if sel(r)];print(nm,len(vv),round(S.mean(vv),4),round(tstat(vv),2))
for f in D:
    vv=[r[2] for r in rows if r[0]==f];print(f,len(vv),round(S.mean(vv),4),round(tstat(vv),2))
# dropped events
E=json.load(open('pm_mm_events.json'));print('events file',len(E),'ok',sum(1 for e in E if ok(e)))
drop=[e for e in E if not ok(e)];c=collections.Counter(('lt3' if len(e['markets'])<3 else 'unresolved/void') for e in drop);print(dict(c))
