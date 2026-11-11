import json,collections,datetime as dt,statistics as S,re,math,random,sys,os
from math import log,sqrt
SER=['KXVANCEMENTION','KXNFLMENTION','KXNBAMENTION','KXWCMENTION','KXMAMDANIMENTION','KXBERNIEMENTION','KXSECPRESSMENTION','KXTRUMPMENTIONB','KXTRUMPSAY']
def ts(s):return dt.datetime.fromisoformat(s.replace('Z','+00:00')).timestamp()
def norm(s):return re.sub(r'[^a-z]','',s.lower())
_cache={}
def load(s):
    if s in _cache:return _cache[s]
    M=json.load(open(f'm_{s}.json'));TR=json.load(open(f't_{s}.json'))
    ev=collections.defaultdict(list)
    for m in M:
        if m['result'] in('yes','no'):ev[m['event_ticker']].append(m)
    E=[]
    for et,ms in ev.items():
        t0=min(ts(x['open_time']) for x in ms)
        # knowledge time: when every market in the event is known to have settled (conservative: later of close_time/settlement_ts capped by the earlier of the two per market)
        K=max(min(ts(x['close_time']),ts(x['settlement_ts']) if x.get('settlement_ts') else 9e18) for x in ms)
        mk=[]
        for m in ms:
            pr=[]
            for c in TR.get(m['ticker'],[]):
                t=ts(c[0])
                if c[4]>0 and t0<=t<=t0+3600:
                    oi,p=(0,c[2]) if c[1]=='yes' else (1,c[3])
                    pr.append((t,oi,p,c[4],c[2]))
            pr.sort()
            mk.append(dict(word=norm(m['yes_sub_title']),w=1 if m['result']=='yes' else 0,pr=pr))
        E.append(dict(et=et,t0=t0,K=K,mk=mk,series=s))
    E.sort(key=lambda e:e['t0'])
    _cache[s]=E;return E
def run(s,thr,causal=False,delay=0,alpha=2.0,pmin=.05,pmax=.95,cap=None):
    E=load(s);n=len(E);burn=max(10,int(.3*n))
    U=[];LS=[]
    byK=sorted(range(n),key=lambda i:E[i]['K'])
    hist=collections.defaultdict(lambda:[0,0]);ptr=0
    for i,e in enumerate(E):
        if causal:
            while ptr<n and E[byK[ptr]]['K']<e['t0']:
                for m in E[byK[ptr]]['mk']:
                    h=hist[m['word']];h[0]+=1;h[1]+=m['w']
                ptr+=1
        if i>=burn:
            gp=sum(h[1] for h in hist.values())/max(1,sum(h[0] for h in hist.values()))
            fills=[];cand=[]
            for m in e['mk']:
                w=m['w'];h=hist[m['word']];q=(h[1]+alpha*gp)/(h[0]+alpha)
                if m['pr']:
                    mkp=min(max(m['pr'][0][4],.01),.99);qq=min(max(q,.01),.99)
                    LS.append((w*log(qq)+(1-w)*log(1-qq))-(w*log(mkp)+(1-w)*log(1-mkp)))
                for (t,oi,p,sz,_) in m['pr']:
                    if not(pmin<=p<=pmax):continue
                    fills.append((oi,p,sz,w,m['word'],t-e['t0']))
                    edge=(q-p) if oi==0 else ((1-q)-p)
                    if edge>=thr and t-e['t0']>=delay:cand.append((t,oi,p,sz,w,m['word']))
            bet=None
            if cand:
                t,oi,p,sz,w,wd=min(cand[:])
                if cap:sz=min(sz,cap)
                bet=dict(oi=oi,p=p,sz=sz,w=w,word=wd,lag=t-e['t0'])
            U.append(dict(id=s+e['et'],bet=bet,fills=fills,t0=e['t0'],series=s,cluster=dt.datetime.utcfromtimestamp(e['t0']).strftime('%Y-%m')))
        if not causal:
            for m in e['mk']:
                h=hist[m['word']];h[0]+=1;h[1]+=m['w']
    return U,LS
def pnl(b):return ((b['w'] if b['oi']==0 else 1-b['w'])-b['p'])*b['sz']
def fee(b):return math.ceil(100*0.07*b['sz']*b['p']*(1-b['p'])-1e-9)/100
def tstat(v):
    n=len(v)
    if n<3:return 0.0
    sd=S.stdev(v)
    return 0 if sd==0 else S.mean(v)/sd*sqrt(n)
def pval(t):return 2*(1-.5*(1+math.erf(abs(t)/sqrt(2))))
def report(U,label,LS=None,nsim=3000,seed=1):
    rnd=random.Random(seed)
    bets=[u for u in U if u['bet']];real=[pnl(u['bet']) for u in bets];tot=sum(real);cost=sum(u['bet']['p']*u['bet']['sz'] for u in bets)
    fe=sum(fee(u['bet']) for u in bets)
    # P1 same-event random BUY print (any side/word), bet size
    def draw1(u):
        f=u['fills'];x=rnd.choice(f);return ((x[3] if x[0]==0 else 1-x[3])-x[1])*u['bet']['sz']
    ok=[u for u in bets if u['fills']]
    sims1=[sum(draw1(u) for u in ok) for _ in range(nsim)]
    realok=sum(pnl(u['bet']) for u in ok)
    z1=(realok-S.mean(sims1))/S.stdev(sims1)
    # P2 price-matched, same series, same side, +-3c, other events
    pool=collections.defaultdict(list)
    for u in U:
        for (oi,p,sz,w,wd,lag) in u['fills']:
            pool[(u['series'],oi,round(p*100))].append(((w if oi==0 else 1-w)-p,u['id']))
    def pm(u):
        b=u['bet'];c=round(b['p']*100);v=[]
        for d in range(-3,4):v+=[x for x,i in pool.get((u['series'],b['oi'],c+d),[]) if i!=u['id']]
        return v
    pms=[(u,pm(u)) for u in bets];pms=[(u,v) for u,v in pms if v]
    exp2=sum(S.mean(v)*u['bet']['sz'] for u,v in pms)
    sims2=[sum(rnd.choice(v)*u['bet']['sz'] for u,v in pms) for _ in range(nsim)]
    real2=sum(pnl(u['bet']) for u,v in pms);z2=(real2-S.mean(sims2))/S.stdev(sims2)
    # cluster t
    cl=collections.defaultdict(float)
    for u in U:
        if u['bet']:cl[u['cluster']]+=pnl(u['bet'])
        else:cl[u['cluster']]+=0
    tc=tstat(list(cl.values()))
    # per-event paired t vs placebo exp
    d=[pnl(u['bet'])-S.mean(((x[3] if x[0]==0 else 1-x[3])-x[1])*u['bet']['sz'] for x in u['fills']) for u in ok]
    tpair=tstat(d)
    srt=sorted(real,reverse=True)
    out=dict(label=label,n=len(bets),events=len(U),pnl=tot,cost=cost,fees=fe,net=tot-fe,pl1=S.mean(sims1),sd1=S.stdev(sims1),z1=z1,pl2=exp2,sd2=S.stdev(sims2),z2=z2,
      tpair=tpair,tclu=tc,ncl=len(cl),top3=sum(srt[:3]),wins=sum(1 for r in real if r>0),
      ex_top10=tot-sum(srt[:10]))
    if LS:out['ls']=(S.mean(LS),S.mean(LS)/S.stdev(LS)*len(LS)**.5,len(LS))
    print(f"{label}: bets {out['n']}/{out['events']} pnl ${tot:.0f} on ${cost:.0f} fees ${fe:.0f} net ${tot-fe:.0f} | P1 same-event placebo ${out['pl1']:.0f}±{out['sd1']:.0f} z={z1:.2f} | P2 price-matched ${exp2:.0f}±{out['sd2']:.0f} z={z2:.2f} (real on same bets ${real2:.0f}) | paired t={tpair:.2f} cluster t={tc:.2f} ({len(cl)}) | top3 ${out['top3']:.0f} ex-top10 ${out['ex_top10']:.0f} | wins {out['wins']}/{len(real)}"+(f" | LS {out['ls'][0]:.4f} t={out['ls'][1]:.1f} n={out['ls'][2]}" if LS else ''))
    return out
if __name__=='__main__':
    pass
