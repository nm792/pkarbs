import json,collections,datetime as dt,statistics as S,random,sys
from math import sqrt
from pmaudit import ts,norm,fam,start,ok,res,tstat
TRF=sys.argv[1] if len(sys.argv)>1 else 'pm_trades_full.json'
E=[e for e in json.load(open('pm_mm_events.json')) if ok(e)]
TR=json.load(open(TRF))
byf=collections.defaultdict(list)
for e in E:byf[fam(e)].append(e)
D={}
for f,L in byf.items():
    L.sort(key=start);b=max(10,int(.3*len(L)));evs=[]
    for i,e in enumerate(L):
        t0=ts(start(e));K=max(ts(m.get('closedTime') or m.get('umaEndDate') or e.get('endDate')) for m in e['markets'])
        mk=[]
        for m in e['markets']:
            first,pr=TR.get(m['conditionId']) or (None,[])
            pr=sorted(pr,key=lambda z:z[0])
            mk.append(dict(word=norm(m.get('groupItemTitle') or m['question']),w=res(m),all=pr,close=ts(m.get('closedTime') or m.get('umaEndDate') or e.get('endDate'))))
        evs.append(dict(id=e['id'],fam=f,t0=t0,K=K,mk=mk,burn=i<b))
    D[f]=evs
EXITS=['V0','V1','V2','V3','V1c','V2c','V3c','V1c15','V2c15','V3c15','V1b15','V1c60','V1sw15']
H={'V1':3600,'V2':6*3600,'V3':86400}
def exit_val(v,t,oi,p,sz,resv,allt,close,pre=None):
    """returns (token exit value per share averaged over sz, info) ; resv token payoff at resolution."""
    if v=='V0':return resv,None
    base=v[:2];te=t+H[base]
    capped='c' in v[2:];maxd=None
    rest=v[2:]
    if '15' in rest:maxd=900
    if '60' in rest:maxd=3600
    if 'b' in rest:
        # backward-looking: last SELL print on same token in (te-900, te]; cap by its size
        cand=[x for x in allt if x[4]==oi and x[1]=='SELL' and x[3]>0 and te-900<x[0]<=te]
        if not cand:return resv,None
        x=cand[-1];f=min(1.0,x[3]/sz);return f*x[2]+(1-f)*resv,(x[0]-te,x[0]>close)
    if 'sw' in rest:
        # sweep: accumulate SELL prints on same token within [te, te+maxd] until sz filled; remainder held
        left=sz;val=0.0
        for x in allt:
            if x[0]<te:continue
            if x[0]>te+900:break
            if x[4]==oi and x[1]=='SELL' and x[3]>0:
                q=min(left,x[3]);val+=q*x[2];left-=q
                if left<=1e-9:break
        val+=left*resv;return val/sz,None
    s=None
    for x in allt:
        if x[0]<te:continue
        if maxd is not None and x[0]>te+maxd:break
        if x[4]==oi and x[1]=='SELL' and x[3]>0:s=x;break
    if not s:return resv,None
    if capped:
        f=min(1.0,s[3]/sz);return f*s[2]+(1-f)*resv,(s[0]-te,s[0]>close)
    return s[2],(s[0]-te,s[0]>close)
def run(thr=.10,alpha=2.0,pmin=.05,pmax=.95,win=3600,causal=True,variants=EXITS):
    out={v:[] for v in variants};info=[]
    for f,evs in D.items():
        n=len(evs);byK=sorted(range(n),key=lambda i:evs[i]['K']);hist=collections.defaultdict(lambda:[0,0]);ptr=0
        for i,e in enumerate(evs):
            while ptr<n and evs[byK[ptr]]['K']<e['t0']:
                for m in evs[byK[ptr]]['mk']:
                    h=hist[m['word']];h[0]+=1;h[1]+=m['w']
                ptr+=1
            if e['burn']:continue
            t0=e['t0'];gp=sum(h[1] for h in hist.values())/max(1,sum(h[0] for h in hist.values()))
            fills={v:[] for v in variants};cand={v:[] for v in variants}
            for m in e['mk']:
                w=m['w'];h=hist[m['word']];q=(h[1]+alpha*gp)/(h[0]+alpha);allt=m['all']
                for (t,side,p,sz,oi) in allt:
                    if side!='BUY' or sz<=0 or not(t0<=t<=t0+win) or not(pmin<=p<=pmax):continue
                    tok=q if oi==0 else 1-q;edge=tok-p;resv=w if oi==0 else 1-w
                    for v in variants:
                        ex,inf=exit_val(v,t,oi,p,sz,resv,allt,m['close'])
                        if inf:info.append((v,inf[0],inf[1],edge>=thr))
                        wadj=ex if oi==0 else 1-ex
                        fills[v].append((oi,p,sz,wadj))
                        if edge>=thr:cand[v].append((t,oi,p,sz,wadj))
            for v in variants:
                bet=None
                if cand[v]:
                    tt,oi,p,sz,wa=min(cand[v]);bet=dict(oi=oi,p=p,sz=sz,w=wa)
                out[v].append(dict(id=e['id'],bet=bet,fills=fills[v],t0=t0,fam=f,wk=dt.datetime.fromtimestamp(t0).strftime('%G-%V'),mo=dt.datetime.fromtimestamp(t0).strftime('%Y-%m')))
    return out,info
def pnl(b):return ((b['w'] if b['oi']==0 else 1-b['w'])-b['p'])*b['sz']
def stats(U,label,nvar=5,quiet=False):
    bets=[u for u in U if u['bet']];real=[pnl(u['bet']) for u in bets];tot=sum(real);cost=sum(u['bet']['p']*u['bet']['sz'] for u in bets)
    def pe(u,mode):
        b=u['bet'];f=[x for x in u['fills'] if (mode=='any' or x[0]==b['oi'])]
        if not f:return None
        return S.mean(((x[3] if x[0]==0 else 1-x[3])-x[1])*b['sz'] for x in f)
    res={}
    for mode in ('same','any'):
        d=[(u,pnl(u['bet'])-pe(u,mode)) for u in bets if pe(u,mode) is not None]
        res[mode]=(tstat([x for _,x in d]),sum(pe(u,mode) for u,_ in d))
    cl=collections.defaultdict(float)
    for u in U:cl[u['mo']]+=pnl(u['bet']) if u['bet'] else 0
    srt=sorted(real,reverse=True)
    from math import erf
    t=res['same'][0];p=2*(1-.5*(1+erf(abs(t)/sqrt(2))))
    if not quiet:print(f"{label}: bets {len(bets)} pnl ${tot:.0f} on ${cost:.0f} | placebo(same side,bet size) ${res['same'][1]:.0f} paired t={t:.2f} (Bonf x{nvar} p={min(1,p*nvar):.3f}) | any-side paired t={res['any'][0]:.2f} | cluster-month t={tstat(list(cl.values())):.2f} | top3 ${sum(srt[:3]):.0f} exTop10 ${tot-sum(srt[:10]):.0f}")
    return dict(tot=tot,t=t)
if __name__=='__main__':
    out,info=run()
    for v in EXITS:
        U=sorted(out[v],key=lambda u:u['t0']);h=len(U)//2
        stats(U,f'{v} all');stats(U[h:],f'{v} later-half')
    import pickle;pickle.dump(info,open('exit_info.pkl','wb'))
    for v in ('V1','V2','V3','V1c','V2c','V3c'):
        a=[x for x in info if x[0]==v and x[3]]
        if a:
            ds=sorted(x[1] for x in a);n=len(ds)
            print(v,'bets exited',n,'delay after te pctiles(s) 25/50/75/90',[round(ds[int(n*q)]) for q in (.25,.5,.75,.9)],'share exit print AFTER market close',round(sum(1 for x in a if x[2])/n,2))
