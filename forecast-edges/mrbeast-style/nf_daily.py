import sys,json,math,random,statistics as st,datetime,collections,re
sys.argv=sys.argv[:1]; sys.path.insert(0,'/tmp/w')
import nf_full as N
random.seed(21)
S=json.load(open('/tmp/w/wn_daily.json')); TR=N.TR
norm=N.norm
AVAIL_H=24  # hours after the start of day d at which d's list counts as published (24 = day fully over, strict)
CC=['US','UK','AU','BR','CA','FR','DE','IN','MX','NL','NZ','ES']
def week_days(r):
    cl=datetime.datetime.fromtimestamp(r['close'],datetime.timezone.utc)
    sun=(cl-datetime.timedelta(days=(cl.weekday()+1)%7)).date(); mon=sun-datetime.timedelta(days=6)
    return [(mon+datetime.timedelta(days=k)).isoformat() for k in range(7)]
def feats(r,maxday):  # maxday: 0=Mon.. e.g. 1 = through Tuesday
    typ='movie' if r['k'][1]=='movie' else 'tv'
    days=week_days(r)[:maxday+1]
    days=[d for d in days if d in S and datetime.datetime.fromisoformat(d).replace(tzinfo=datetime.timezone.utc).timestamp()+AVAIL_H*3600<=r['T']]
    if not days: return None
    u=collections.defaultdict(float); g=collections.defaultdict(float)
    for d in days:
        for cc in CC:
            lst=S[d]['country'].get(cc,{}).get(typ,[])
            for rk,t in lst:
                k=norm(t); g[k]+=(11-rk)/ (12*len(days))
                if cc=='US': u[k]+=(11-rk)/len(days)
    return u,g,days
def mt(name,keys):
    n=norm(name); best=None
    for k in keys:
        if len(n)>=4 and (n==k or n in k or k in n and len(k)>=4):
            if best is None or abs(len(k)-len(n))<abs(len(best)-len(n)): best=k
    return best
def softmax_rank(scores,rank):
    ex=[math.exp(s) for s in scores]; Z=sum(ex); p1=[e/Z for e in ex]
    if rank==1: return p1
    out=[]
    for i in range(len(ex)):
        s=0
        for j in range(len(ex)):
            if j==i: continue
            s+=p1[j]*ex[i]/(Z-ex[j])
        out.append(s)
    return out
def price_at(r,c,WIN=21600):
    pr=sorted((t,(p if oi==0 else 1-p)) for t,s,p,sz,oi in TR.get(c,[]) if r['T']<=t<=r['T']+WIN)
    return pr[0][1] if pr else None
def build(r,maxday):
    f=feats(r,maxday)
    if f is None: return None
    u,g,days=f; keys=list(set(u)|set(g))
    cands=[]
    for name,c,won in r['mk']:
        k=mt(name,keys)
        if k: cands.append(dict(name=name,c=c,won=won,k=k,u=u.get(k,0.0),g=g.get(k,0.0)))
    return cands
def fit(events,rankfilter=1):
    best=None
    for b1 in [x*0.2 for x in range(0,21)]:
        for b2 in [x*0.4 for x in range(0,21)]:
            ll=0;n=0
            for r,cands in events:
                if r['k'][2]!=rankfilter: continue
                w=[i for i,c in enumerate(cands) if c['won']]
                if not w: continue
                sc=[b1*c['u']+b2*c['g'] for c in cands]; p=softmax_rank(sc,1)
                ll+=math.log(max(p[w[0]],1e-9)); n+=1
            if n and (best is None or ll>best[0]): best=(ll,b1,b2,n)
    return best
UNITS_CACHE={}
def run(reg,TH=.05,WIN=7200,maxday=1,label='',verbose=True):
    evs=[r for r in N.EV if r['k'][0]==reg]
    cutl=sorted(r['start'] for r in evs); cut=cutl[len(cutl)//2]
    built={}
    for r in evs:
        r['T']=r['start']+3600
        cs=build(r,maxday)
        if cs: built[r['id']]=(r,cs)
    params={}
    for typ in('movie','show'):
        tr=[v for v in built.values() if v[0]['k'][1]==typ and v[0]['start']<cut]
        params[typ]=fit(tr)
    # calibration on test: Brier vs market
    br=[];bm=[];hit=0;nh=0
    units=[]
    for r,cs in built.values():
        prm=params[r['k'][1]]
        if not prm: continue
        _,b1,b2,_n=prm
        sc=[b1*c['u']+b2*c['g'] for c in cs]
        pm=softmax_rank(sc,r['k'][2])
        # market mass on matched set
        prices=[price_at(r,c['c']) for c in cs]
        S_m=sum((x if x is not None else .02) for x in prices)
        S_m=min(max(S_m,.05),.98)
        q={c['c']:S_m*p for c,p in zip(cs,pm)}
        half='test' if r['start']>=cut else 'train'
        if half=='test':
            for c,x in zip(cs,prices):
                if x is None: continue
                y=1.0 if c['won'] else 0.0
                br.append((min(max(q[c['c']],.02),.98)-y)**2); bm.append((min(max(x,.02),.98)-y)**2)
        fills=[]
        for name,c,won in r['mk']:
            for t,s,p,sz,oi in TR.get(c,[]):
                if s=='BUY' and r['T']<=t<=r['T']+WIN and .02<p<.98: fills.append((t,c,p,sz,oi,won))
        if not fills: continue
        fills.sort(); bet=None
        for t,c,p,sz,oi,won in fills:
            if c not in q: continue
            qq=min(max(q[c],.02),.98); w=1.0 if won else 0.0
            e=(qq-p) if oi==0 else ((1-qq)-p)
            if e>TH: bet=dict(oi=oi,p=p,sz=sz,stake=sz*p,pnl=((w if oi==0 else 1-w)-p)*sz); break
        units.append(dict(half=half,bet=bet,id=r['id'],fills=[(oi,p,sz,(1.0 if won else 0.0)) for t,c,p,sz,oi,won in fills],k=r['k']))
    def placebo(bets,universe,reps=2000):
        pools={id(u):[(oi,p,sz,w) for v in universe if v['id']!=u['id'] for oi,p,sz,w in v['fills'] if oi==u['bet']['oi'] and abs(p-u['bet']['p'])<=.05] for u in bets}
        tot=[]
        for _ in range(reps):
            s=0
            for u in bets:
                c=pools[id(u)]
                if c: oi,p,sz,w=random.choice(c); s+=((w if oi==0 else 1-w)-p)*min(sz,u['bet']['sz'])
            tot.append(s)
        return st.mean(tot),st.pstdev(tot)
    out=[]
    def summ(sel,name):
        us=[u for u in units if sel(u)]; b=[u for u in us if u['bet']]
        if not us: out.append(f'{label} {name}: no units'); return
        stake=sum(u['bet']['stake'] for u in b); pnl=sum(u['bet']['pnl'] for u in b)
        mp,sp=placebo(b,us) if b else (0,0)
        per=[(u['bet']['pnl'] if u['bet'] else 0.0) for u in us]; n=len(us); sd=st.pstdev(per) if n>1 else 0
        t=(st.mean(per)/(sd/math.sqrt(n))) if sd else 0
        out.append(f"{label} {name}: event-units={n} bets={len(b)} stake=${stake:.0f} pnl=${pnl:.0f} | placebo(v2)=${mp:.0f}±{sp:.0f} excess={(pnl-mp)/sp if sp else 0:+.1f} sd | t/event={t:.2f} | w/l={sum(1 for u in b if u['bet']['pnl']>0)}/{sum(1 for u in b if u['bet']['pnl']<0)}")
    summ(lambda u:True,'ALL'); summ(lambda u:u['half']=='train','train'); summ(lambda u:u['half']=='test','TEST')
    for rk in(1,2): summ(lambda u,rk=rk:u['k'][2]==rk and u['half']=='test',f'TEST rank{rk}')
    out.append(f"   params={ {k:(round(v[1],1),round(v[2],1),v[3]) if v else None for k,v in params.items()} } events_with_lists={len(built)}/{len(evs)}; test candidate Brier model {st.mean(br) if br else float('nan'):.4f} vs market first print {st.mean(bm) if bm else float('nan'):.4f} (n={len(br)})")
    run.units=units
    return out
if __name__=='__main__':
    for reg in('US','global'):
        for maxday,tag in((2,'strict:lists published before T (day fully over)'),):
            for TH in(.05,.03,.10):
                for WIN in(7200,21600):
                    print('\n'.join(run(reg,TH,WIN,maxday,label=f'[{reg} TH={TH} WIN={WIN//3600}h {tag}]')),flush=True)
