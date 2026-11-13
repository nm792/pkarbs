import warnings;warnings.filterwarnings('ignore')
from audit import *
import collections
def pool(thr,causal=True,**kw):
    U=[];LS=[]
    for s in SER:
        u,l=run(s,thr,causal=causal,**kw);U+=u;LS+=l
    return U,LS
print('== void / non-binary results')
for s in SER+['KXTRUMPMENTION']:
    M=json.load(open(f'm_{s}.json'));c=collections.Counter((m['result'],m['status']) for m in M);print(s,dict(c))
U3,_=pool(.03);med=sorted(u['t0'] for u in U3)[len(U3)//2]
print('== thresholds, causal, all / later half')
for thr in (.03,.05,.10):
    U,LS=pool(thr);report(U,f'thr {thr} all',LS=LS,nsim=1500);report([u for u in U if u['t0']>=med],f'thr {thr} later half',nsim=1500)
print('== delay in later (held-out) half, 3c')
for d in (0,5,15,30,60,300):
    U,_=pool(.03,delay=d);report([u for u in U if u['t0']>=med],f'later half delay {d}s',nsim=1500)
print('== event-level log score vs first print')
# recompute per-event LS sums, causal
import statistics
def evls(causal=True):
    out=[]
    for s in SER:
        E=load(s);n=len(E);burn=max(10,int(.3*n));byK=sorted(range(n),key=lambda i:E[i]['K']);hist=collections.defaultdict(lambda:[0,0]);ptr=0
        for i,e in enumerate(E):
            while ptr<n and E[byK[ptr]]['K']<e['t0']:
                for m in E[byK[ptr]]['mk']:
                    h=hist[m['word']];h[0]+=1;h[1]+=m['w']
                ptr+=1
            if i<burn:continue
            gp=sum(h[1] for h in hist.values())/max(1,sum(h[0] for h in hist.values()))
            tot=0;k=0
            for m in e['mk']:
                if not m['pr']:continue
                h=hist[m['word']];q=(h[1]+2*gp)/(h[0]+2);w=m['w']
                mk=min(max(m['pr'][0][4],.01),.99);qq=min(max(q,.01),.99)
                tot+=(w*log(qq)+(1-w)*log(1-qq))-(w*log(mk)+(1-w)*log(1-mk));k+=1
            if k:out.append((s,e['t0'],tot/k,tot,k))
    return out
o=evls()
v=[x[2] for x in o];print('events',len(o),'mean nats/market-event',round(S.mean(v),4),'event-level t',round(tstat(v),2))
wk=collections.defaultdict(float)
for s,t,m,tot,k in o:wk[dt.datetime.fromtimestamp(t).strftime('%G-%V')]+=m
print('week-cluster t',round(tstat(list(wk.values())),2),len(wk))
for s in SER:
    vv=[x[2] for x in o if x[0]==s];print(s,len(vv),round(S.mean(vv),4),round(tstat(vv),2))
# also later half only
vv=[x[2] for x in o if x[1]>=med];print('later half',len(vv),round(S.mean(vv),4),round(tstat(vv),2))
