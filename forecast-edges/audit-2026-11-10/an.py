import json,re,math,random,bisect,collections,statistics as st,sys
random.seed(5)
TS=json.load(open('elon_ts.json')); D=json.load(open('elon_tr.json'))
Phi=lambda x:.5*(1+math.erf(x/math.sqrt(2)))
cnt=lambda a,b:bisect.bisect_left(TS,b)-bisect.bisect_left(TS,a)
def bucket(t):
    m=re.match(r'<(\d+)',t)
    if m: return (0,int(m.group(1))-1)
    m=re.match(r'(\d+)\+',t)
    if m: return (int(m.group(1)),10**9)
    m=re.match(r'(\d+)[-–](\d+)',t)
    if m: return (int(m.group(1)),int(m.group(2)))
def profile(t,days=21):
    a=t-days*86400;c=[0]*24;i=bisect.bisect_left(TS,a);j=bisect.bisect_left(TS,t)
    for x in TS[i:j]: c[int((x%86400)//3600)]+=1
    return [v/days for v in c]
def rem(t,end,prof):
    s=0;x=t
    while x<end:
        nx=min(end,(x//3600+1)*3600); s+=prof[int((x%86400)//3600)]*(nx-x)/3600; x=nx
    return s
TR=collections.defaultdict(dict)
for r in D['tr']: TR[r['eid']][r['t']]=r['tr']
H=int(sys.argv[1]) if len(sys.argv)>1 else 24
EV=[];chk=[]
for e in D['evs']:
    bk=[]
    for t,c,op in e['markets']:
        b=bucket(t); o=json.loads(op)
        if not b: bk=None;break
        bk.append((b,float(o[0])==1.0,TR[e['id']].get(t,[])))
    if not bk or sum(x[1] for x in bk)!=1: continue
    fin=cnt(e['start'],e['end']); wb=[x for x in bk if x[1]][0][0]; chk.append(wb[0]<=fin<=wb[1])
    T=e['end']-H*3600; so=cnt(e['start'],T); rp=rem(T,e['end'],profile(T))
    EV.append(dict(id=e['id'],title=e['title'],start=e['start'],T=T,so=so,rp=rp,final=fin,bk=bk))
EV.sort(key=lambda e:e['start'])
print('events',len(EV),'count matches winning bracket',sum(chk),'/',len(chk))
cut=len(EV)//2
tr=EV[:cut]; errs=[(e['final']-e['so']-e['rp'])/max(e['rp'],1) for e in tr]; k=st.pstdev(errs); b=st.mean(errs)
print('k',round(k,3),'b',round(b,3))
def cands(e,k,b,th=.05,win=600,causal_pick='best'):
    mu=e['so']+e['rp']*(1+b); sd=max(k*e['rp'],math.sqrt(max(e['rp'],1)))
    out=[];pool=[]
    for (lo,hi),w,trs in e['bk']:
        pm=Phi((hi+.5-mu)/sd)-Phi((lo-.5-mu)/sd)
        for ts,side,p,sz,oi in trs:
            if side!='BUY' or not(e['T']<=ts<=e['T']+win) or p<=.02 or p>=.98: continue
            pay=((1 if w else 0) if oi==0 else (0 if w else 1))-p
            pool.append((ts,sz*p,pay*sz,p,oi))
            edge=(pm-p) if oi==0 else ((1-pm)-p)
            if edge>th: out.append((ts,edge,sz*p,pay*sz,p,oi))
    return out,pool
def pick(out,mode):
    if not out: return None
    if mode=='best': return max(out,key=lambda x:x[1])          # original: hindsight max edge in 10 min
    if mode=='first': return min(out,key=lambda x:x[0])         # first qualifying print after T
def summarize(sel,mode,name,th=.05,win=600,cap=None):
    pn=[];stk=0;n=0;pls=[];dets=[]
    for e in sel:
        out,pool=cands(e,k,b,th,win); c=pick(out,mode)
        if c:
            ts,edge,stake,pnl,p,oi=c
            if cap and stake>cap: pnl*=cap/stake; stake=cap
            pn.append(pnl);stk+=stake;n+=1;dets.append((e,c,pool))
        else: pn.append(0.0)
    tot=sum(pn); m=st.mean(pn); sd=st.pstdev(pn)
    # matched placebo: same event, random BUY print of same side and within +-0.1 price
    sims=[]
    for _ in range(2000):
        t=0
        for e,c,pool in dets:
            ts,edge,stake,pnl,p,oi=c
            mp=[x for x in pool if x[4]==oi and abs(x[3]-p)<=.1] or pool
            t+=random.choice(mp)[2]
        sims.append(t)
    # bootstrap over windows
    bs=sorted(sum(random.choices(pn,k=len(pn)))for _ in range(4000))
    print(f'{name}: windows={len(pn)} bets={n} stake=${stk:.0f} pnl=${tot:.0f} roi={tot/stk*100 if stk else 0:+.0f}% mean/win=${m:.1f} t={m/(sd/math.sqrt(len(pn))) if sd else 0:.2f} boot95=[${bs[100]:.0f},${bs[3900]:.0f}] | matched-placebo ${st.mean(sims):.0f}±{st.pstdev(sims):.0f} z={(tot-st.mean(sims))/st.pstdev(sims):+.2f} | wins/losses={sum(1 for x in pn if x>0)}/{sum(1 for x in pn if x<0)} median stake=${st.median([d[1][2] for d in dets]) if dets else 0:.0f}')
    return pn
for mode in ('best','first'):
  for cap in (None,50):
    print('--- pick',mode,'cap',cap)
    for nm,sel in (('all',EV),('train',EV[:cut]),('test',EV[cut:])):
        summarize(sel,mode,nm,cap=cap)
print('--- concentration (best pick, no cap, all)')
bets=[]
for e in EV:
    out,pool=cands(e,k,b); c=pick(out,'best')
    if c: bets.append((c[3],c[2],e['title'][-30:],c[4],c[5]))
bets.sort(reverse=True); print('top5 pnl',[(round(x[0]),round(x[1])) for x in bets[:5]],'sum top5',round(sum(x[0] for x in bets[:5])),'of total',round(sum(x[0] for x in bets)))
print('total excluding top1', round(sum(x[0] for x in bets[1:])),'excl top3',round(sum(x[0] for x in bets[3:])))
allp=[]
for e in EV:
    out,pool=cands(e,k,b); allp+=pool
print('pool of all BUY prints: n',len(allp),'stake',round(sum(x[1] for x in allp)),'pnl',round(sum(x[2] for x in allp)),'roi %.1f%%'%(sum(x[2] for x in allp)/sum(x[1] for x in allp)*100))
for oi in (0,1):
    q=[x for x in allp if x[4]==oi]; print(' side',oi,'n',len(q),'roi %.1f%%'%(sum(x[2] for x in q)/sum(x[1] for x in q)*100))
