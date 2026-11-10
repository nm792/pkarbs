import json,collections,datetime as dt,statistics as S,re,math,random,warnings
warnings.filterwarnings('ignore')
from math import log,sqrt
def ts(s):
    s=s.replace(' ','T').replace('Z','+00:00')
    if re.search(r'[+-]\d\d$',s):s+=':00'
    return dt.datetime.fromisoformat(s).timestamp()
def norm(s):return re.sub(r'[^a-z]','',(s or '').lower())
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
def res(m):
    p=json.loads(m['outcomePrices']);return 1 if float(p[0])>.5 else 0
_D={}
def data():
    if _D:return _D
    E=[e for e in json.load(open('pm_mm_events.json')) if ok(e)]
    TR=json.load(open('pm_trades.json'))
    byf=collections.defaultdict(list)
    for e in E:byf[fam(e)].append(e)
    out={}
    for f,L in byf.items():
        L.sort(key=start);b=max(10,int(.3*len(L)))
        evs=[]
        for i,e in enumerate(L):
            t0=ts(start(e))
            K=max(ts(m.get('closedTime') or m.get('umaEndDate') or e.get('endDate')) for m in e['markets'])
            mk=[]
            for m in e['markets']:
                fs=m.get('feeSchedule') or {}
                rate=fs.get('rate',0) if m.get('feesEnabled') else 0
                tr=TR.get(m['conditionId'])
                first,pr=(tr if tr else (None,[]))
                if m['outcomes'] and json.loads(m['outcomes'])[0].lower()!='yes':flip=True
                else:flip=False
                mk.append(dict(word=norm(m.get('groupItemTitle') or m['question']),w=res(m),rate=rate,exp=fs.get('exponent',1),first=first,
                    pr=sorted([x for x in pr if x[1]=='BUY' and x[3]>0 and t0<=x[0]],key=lambda z:z[0]),flip=flip))
            evs.append(dict(id=e['id'],fam=f,t0=t0,K=K,mk=mk,burn=i<b,idx=i,title=e['title']))
        out[f]=evs
    _D.update(out);return _D
def run(thr,causal=True,delay=0,win=3600,alpha=2.0,pmin=.05,pmax=.95,cap=None,subset=None,fam_only=None,anchor='start'):
    D=data();U=[];LS=[]
    for f,evs in D.items():
        if fam_only and f not in fam_only:continue
        n=len(evs);byK=sorted(range(n),key=lambda i:evs[i]['K'])
        hist=collections.defaultdict(lambda:[0,0]);ptr=0
        for i,e in enumerate(evs):
            if causal:
                while ptr<n and evs[byK[ptr]]['K']<e['t0']:
                    for m in evs[byK[ptr]]['mk']:
                        h=hist[m['word']];h[0]+=1;h[1]+=m['w']
                    ptr+=1
            if not e['burn'] and (subset is None or e['id'] in subset):
                t0=e['t0']
                if anchor=='firsttrade':
                    ft=[m['first'] for m in e['mk'] if m['first']];
                    if not ft:continue
                    t0=min(ft)
                t1=t0+win;gp=sum(h[1] for h in hist.values())/max(1,sum(h[0] for h in hist.values()))
                fills=[];cand=[]
                for m in e['mk']:
                    w=m['w'];h=hist[m['word']];q=(h[1]+alpha*gp)/(h[0]+alpha)
                    pr=[x for x in m['pr'] if t0<=x[0]<=t1]
                    if pr:
                        x=pr[0];mkp=x[2] if x[4]==0 else 1-x[2];mkp=min(max(mkp,.01),.99);qq=min(max(q,.01),.99)
                        LS.append((w*log(qq)+(1-w)*log(1-qq))-(w*log(mkp)+(1-w)*log(1-mkp)))
                    for (t,side,p,sz,oi) in pr:
                        if not(pmin<=p<=pmax):continue
                        fills.append((oi,p,sz,w,m['word'],t-t0,m['rate'],m['exp']))
                        edge=(q-p) if oi==0 else ((1-q)-p)
                        if edge>=thr and t-t0>=delay:cand.append((t,oi,p,sz,w,m['word'],m['rate'],m['exp']))
                bet=None
                if cand:
                    t,oi,p,sz,w,wd,rate,ex=min(cand)
                    if cap:sz=min(sz,cap)
                    bet=dict(oi=oi,p=p,sz=sz,w=w,word=wd,lag=t-t0,rate=rate,exp=ex)
                U.append(dict(id=e['id'],bet=bet,fills=fills,t0=e['t0'],series=f,cluster=dt.datetime.fromtimestamp(e['t0']).strftime('%Y-%m'),wk=dt.datetime.fromtimestamp(e['t0']).strftime('%G-%V')))
            if not causal:
                for m in e['mk']:
                    h=hist[m['word']];h[0]+=1;h[1]+=m['w']
    return U,LS
def pnl(b):return ((b['w'] if b['oi']==0 else 1-b['w'])-b['p'])*b['sz']
def fee(b,allrate=None):
    r=b['rate'] if allrate is None else allrate
    return round(r*b['sz']*(b['p']*(1-b['p']))**b['exp'],5)
def tstat(v):
    n=len(v)
    if n<3:return 0.0
    sd=S.stdev(v);return 0 if sd==0 else S.mean(v)/sd*sqrt(n)
def report(U,label,LS=None,nsim=2000,seed=1,quiet=False):
    rnd=random.Random(seed)
    bets=[u for u in U if u['bet']];real=[pnl(u['bet']) for u in bets];tot=sum(real);cost=sum(u['bet']['p']*u['bet']['sz'] for u in bets)
    fe=sum(fee(u['bet']) for u in bets);fe_all=sum(fee(u['bet'],.04) for u in bets)
    ok_=[u for u in bets if u['fills']]
    def d1(u):
        x=rnd.choice(u['fills']);return ((x[3] if x[0]==0 else 1-x[3])-x[1])*u['bet']['sz']
    if not ok_:
        print(label,'no bets');return {}
    sims1=[sum(d1(u) for u in ok_) for _ in range(nsim)];realok=sum(pnl(u['bet']) for u in ok_)
    z1=(realok-S.mean(sims1))/S.stdev(sims1)
    pool=collections.defaultdict(list)
    for u in U:
        for (oi,p,sz,w,wd,lag,rate,ex) in u['fills']:
            pool[(u['series'],oi,round(p*100))].append(((w if oi==0 else 1-w)-p,u['id']))
    def pm(u):
        b=u['bet'];c=round(b['p']*100);v=[]
        for dd in range(-3,4):v+=[x for x,i in pool.get((u['series'],b['oi'],c+dd),[]) if i!=u['id']]
        return v
    pms=[(u,pm(u)) for u in bets];pms=[(u,v) for u,v in pms if v]
    exp2=sum(S.mean(v)*u['bet']['sz'] for u,v in pms)
    sims2=[sum(rnd.choice(v)*u['bet']['sz'] for u,v in pms) for _ in range(nsim)]
    real2=sum(pnl(u['bet']) for u,v in pms);z2=(real2-S.mean(sims2))/S.stdev(sims2) if S.stdev(sims2)>0 else 0
    clm=collections.defaultdict(float);clw=collections.defaultdict(float)
    for u in U:
        v=pnl(u['bet']) if u['bet'] else 0;clm[u['cluster']]+=v;clw[u['wk']]+=v
    pe=lambda u:S.mean(((x[3] if x[0]==0 else 1-x[3])-x[1])*u['bet']['sz'] for x in u['fills'])
    d=[pnl(u['bet'])-pe(u) for u in ok_]
    cw=collections.defaultdict(float)
    for u,dd in zip(ok_,d):cw[u['wk']]+=dd
    srt=sorted(real,reverse=True)
    out=dict(n=len(bets),pnl=tot,cost=cost,fee=fe,fee_all=fe_all,z1=z1,z2=z2,tpair=tstat(d),tclu_m=tstat(list(clm.values())),tclu_w_pair=tstat(list(cw.values())),top3=sum(srt[:3]),pl1=S.mean(sims1),pl2=exp2)
    if not quiet:
        print(f"{label}: bets {len(bets)}/{len(U)} pnl ${tot:.0f} on ${cost:.0f} fees(listed) ${fe:.0f} fees(all@4%) ${fe_all:.0f} net ${tot-fe:.0f}/${tot-fe_all:.0f} | P1 ${out['pl1']:.0f}±{S.stdev(sims1):.0f} z={z1:.2f} | P2 ${exp2:.0f}±{S.stdev(sims2):.0f} z={z2:.2f} | paired t={out['tpair']:.2f} clusterM t={out['tclu_m']:.2f}({len(clm)}) clusterW(real-pl) t={out['tclu_w_pair']:.2f}({len(cw)}) | top3 ${out['top3']:.0f} exTop10 ${tot-sum(srt[:10]):.0f} | wins {sum(1 for r in real if r>0)}/{len(real)}"+(f" | LS {S.mean(LS):.4f} t={S.mean(LS)/S.stdev(LS)*len(LS)**.5:.1f} n={len(LS)}" if LS else ''))
    return out
