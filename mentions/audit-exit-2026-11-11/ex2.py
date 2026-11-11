import sys;sys.argv=['x','pm_trades_full.json']
from exitaudit import *
out,info=run(variants=['V0','V1','V2','V3'])
# per bet exit timing stats
def bet_exit_stats(v):
    rows=[]
    H_=H[v]
    for f,evs in D.items():pass
    return rows
# recompute using stored info restricted to bet prints: info rows (v,delay,after_close,is_candidate) - need bet-specific; rebuild
import pickle
res={}
for v in ('V1','V2','V3'):
    U=out[v]
    # identify bet print per event: recompute exit delay for bets
tot=0
rows=collections.defaultdict(list)
for f,evs in D.items():
    n=len(evs);byK=sorted(range(n),key=lambda i:evs[i]['K']);hist=collections.defaultdict(lambda:[0,0]);ptr=0
    for i,e in enumerate(evs):
        while ptr<n and evs[byK[ptr]]['K']<e['t0']:
            for m in evs[byK[ptr]]['mk']:
                h=hist[m['word']];h[0]+=1;h[1]+=m['w']
            ptr+=1
        if e['burn']:continue
        t0=e['t0'];gp=sum(h[1] for h in hist.values())/max(1,sum(h[0] for h in hist.values()));cand=[]
        for m in e['mk']:
            h=hist[m['word']];q=(h[1]+2*gp)/(h[0]+2)
            for (t,side,p,sz,oi) in m['all']:
                if side!='BUY' or sz<=0 or not(t0<=t<=t0+3600) or not(.05<=p<=.95):continue
                tok=q if oi==0 else 1-q
                if tok-p>=.10:cand.append((t,oi,p,sz,m,tok))
        if not cand:continue
        t,oi,p,sz,m,tok=min(cand,key=lambda c:(c[0],c[1]))
        resv=m['w'] if oi==0 else 1-m['w']
        for v in ('V1','V2','V3'):
            te=t+H[v]
            s=next((x for x in m['all'] if x[0]>=te and x[4]==oi and x[1]=='SELL' and x[3]>0),None)
            rows[v].append(dict(delay=(s[0]-te) if s else None,exitp=s[2] if s else None,sz=sz,ssz=s[3] if s else None,resv=resv,p=p,entry_t=t,close=m['close'],sale_t=s[0] if s else None))
for v in ('V1','V2','V3'):
    R=rows[v];n=len(R);ex=[r for r in R if r['delay'] is not None]
    print(v,'bets',n,'have any later SELL print',len(ex))
    for lim in (900,3600,6*3600,86400):
        print('  exit within',lim,'s of planned time:',sum(1 for r in ex if r['delay']<=lim),'=',round(100*sum(1 for r in ex if r['delay']<=lim)/n),'% of bets')
    d=sorted(r['delay'] for r in ex);print('  delay pctiles(h) 25/50/75/90',[round(d[int(len(d)*q)]/3600,1) for q in (.25,.5,.75,.9)])
    rt=[(r['sale_t']-r['entry_t'])/3600 for r in ex];rt.sort();print('  total hold time before sale (h) median',round(rt[len(rt)//2],1))
    big=sum(1 for r in ex if r['ssz']>=r['sz']);print('  exit print size >= our size:',round(100*big/len(ex)),'% ; median ratio',round(S.median(r['ssz']/r['sz'] for r in ex),2))
    gain=[(r['exitp']-r['resv']) for r in ex];print('  mean (exit price - resolution payoff) per share',round(S.mean(gain),3),' stake-weighted $ effect of exiting vs hold',round(sum((r['exitp']-r['resv'])*r['sz'] for r in ex),0))
    # bets sold within 15min
