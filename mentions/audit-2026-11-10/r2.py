from audit import *
import collections
thr=.03
def pool(causal=True,**kw):
    U=[];LS=[]
    for s in SER:
        u,l=run(s,thr,causal=causal,**kw);U+=u;LS+=l
    return U,LS
U,LS=pool()
print('== HELD-OUT / TRAIN by pooled calendar time (median event t0)')
ts_=sorted(u['t0'] for u in U);med=ts_[len(ts_)//2]
print('median date',dt.datetime.utcfromtimestamp(med))
report([u for u in U if u['t0']<med],'train (earlier half, calendar)')
report([u for u in U if u['t0']>=med],'HELD-OUT (later half, calendar)')
print('== per-series later half (build style)')
H=[]
for s in SER:
    us=[u for u in U if u['series']==s];us.sort(key=lambda u:u['t0']);H+=us[len(us)//2:]
report(H,'HELD-OUT per-series 2nd half')
print('== excluding NBA'); report([u for u in U if u['series']!='KXNBAMENTION'],'ex-NBA all')
report([u for u in U if u['series']!='KXNBAMENTION' and u['t0']>=med],'ex-NBA later half')
report([u for u in U if u['series']=='KXNBAMENTION' and u['t0']>=med],'NBA later half')
print('== cluster by week/day (all bets)')
for fmt,nm in (('%G-%V','week'),('%Y-%m-%d','day')):
    cl=collections.defaultdict(float)
    for u in U:
        cl[dt.datetime.utcfromtimestamp(u['t0']).strftime(fmt)]+= pnl(u['bet']) if u['bet'] else 0
    print(nm,'clusters',len(cl),'t=',round(tstat(list(cl.values())),2))
# placebo-adjusted cluster t by week
cl=collections.defaultdict(float)
for u in U:
    if u['bet'] and u['fills']:
        pe=S.mean(((x[3] if x[0]==0 else 1-x[3])-x[1])*u['bet']['sz'] for x in u['fills'])
        cl[dt.datetime.utcfromtimestamp(u['t0']).strftime('%G-%V')]+=pnl(u['bet'])-pe
print('real-minus-same-event-placebo, week cluster t',round(tstat(list(cl.values())),2),len(cl))
print('== delay sensitivity (pooled, causal)')
for d in (0,5,30,60,300,900):
    u,_=pool(delay=d);report(u,f'delay {d}s',nsim=800)
print('== size cap sensitivity')
for c in (10,25,100):
    u,_=pool(cap=c);report(u,f'cap {c} contracts',nsim=800)
print('== bet lag after open (s) pctiles')
lags=sorted(u['bet']['lag'] for u in U if u['bet']);n=len(lags)
print([round(lags[int(n*q)]) for q in (.1,.25,.5,.75,.9)],'share<=60s',sum(1 for l in lags if l<=60)/n)
print('== by price bucket of bet')
bk=collections.defaultdict(list)
for u in U:
    if u['bet']:
        b=u['bet'];k=('YES' if b['oi']==0 else 'NO',min(int(b['p']*100)//10*10,90));bk[k].append(b)
for k in sorted(bk):
    v=bk[k];cost=sum(b['p']*b['sz'] for b in v);print(k,'n',len(v),'stake',round(cost),'pnl',round(sum(pnl(b) for b in v)),'win%',round(100*S.mean(((b['w'] if b['oi']==0 else 1-b['w'])) for b in v)),'avg price',round(100*S.mean(b['p'] for b in v)))
