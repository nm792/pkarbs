import json,re,math,datetime as dt,collections,statistics as st,random
random.seed(2)
D=json.load(open('early_h.json')); E=D['E']; jobs=D['jobs']; H=D['H']
Phi=lambda x:.5*(1+math.erf(x/math.sqrt(2)))
def bucket(t):
    m=re.match(r'<(\d+)',t)
    if m: return (0,int(m.group(1))-1)
    m=re.match(r'(\d+)\+',t)
    if m: return (int(m.group(1)),int(m.group(1))+20)
    m=re.match(r'(\d+)[-–](\d+)',t)
    if m: return (int(m.group(1)),int(m.group(2)))
by=collections.defaultdict(list)
for j,h in zip(jobs,H): by[j[0]].append((j,h))
rows=[]
for i,rs in by.items():
    s=dt.date.fromisoformat(E[i][2]); s=dt.date.fromisoformat(E[i][2]) # placeholder
    st_=dt.date.fromisoformat(E[i][2]); 
    t0=int(dt.datetime(st_.year,st_.month,st_.day,17,tzinfo=dt.timezone.utc).timestamp())
    bk=[];ok=True
    for j,h in rs:
        b=bucket(j[1] or '')
        if not b or not h: ok=False;break
        hh=[p for p in h if p['t']<=t0]
        if not hh: ok=False;break
        bk.append((b,hh[-1]['p'],j[3],(t0-hh[-1]['t'])/3600))
    if not ok or len(bk)<5 or sum(x[2] for x in bk)!=1: continue
    sm=sum(x[1] for x in bk)
    if not .6<sm<1.5: continue
    real=[(x[0][0]+x[0][1])/2 for x in bk if x[2]][0]
    rows.append(dict(start=st_,bk=bk,real=real,eid=E[i][0]))
rows.sort(key=lambda r:r['start']); print(len(rows),'events')
R=rows
for i,r in enumerate(R): r['mu']=st.mean(x['real'] for x in R[max(0,i-3):i]) if i>=3 else None
R=[r for r in R if r['mu']]; cut=len(R)//2; tr,te=R[:cut],R[cut:]
ratios=[(r['real']-r['mu'])/r['mu'] for r in tr]; k=st.pstdev(ratios); b0=st.mean(ratios); print('n',len(R),'k',round(k,3),'b0',round(b0,3))
def run(rs,th=.05):
    ev=[];stake=0;pnl=0;n=0;stale=[]
    for r in rs:
        m_=r['mu']*(1+b0); sd=k*r['mu']; ep=0
        for (lo,hi),p,w,gap in r['bk']:
            pm=Phi((hi+.5-m_)/sd)-Phi((lo-.5-m_)/sd)
            if .02<p<.98 and pm-p>th: g=(1 if w else 0)-p; c=p
            elif .02<p<.98 and p-pm>th: g=((0 if w else 1))-(1-p); c=1-p
            else: continue
            ep+=g; stake+=c; n+=1; stale.append(gap)
        ev.append(ep)
    return ev,stake,n,stale
for nm,rs in (('train',tr),('test',te),('all',R)):
    ev,stake,n,stale=run(rs); pnl=sum(ev)
    # their se: sd of per-bet pnl * sqrt(n) -> need per-bet; recompute
    bets=[]
    for r in rs:
        m_=r['mu']*(1+b0); sd=k*r['mu']
        for (lo,hi),p,w,gap in r['bk']:
            pm=Phi((hi+.5-m_)/sd)-Phi((lo-.5-m_)/sd)
            if .02<p<.98 and pm-p>.05: bets.append((1 if w else 0)-p)
            elif .02<p<.98 and p-pm>.05: bets.append((0 if w else 1)-(1-p))
    se_bet=st.pstdev(bets)*math.sqrt(len(bets)); se_ev=st.pstdev(ev)*math.sqrt(len(ev))
    print(f'{nm}: events={len(rs)} bets={n} pnl={pnl:.1f} stake={stake:.1f} roi={pnl/stake*100:+.1f}% | t(per-bet iid)={pnl/se_bet:.2f} t(event-clustered)={pnl/se_ev:.2f} | median price age at t0={st.median(stale):.1f}h, >6h old: {sum(1 for x in stale if x>6)/len(stale)*100:.0f}%')
