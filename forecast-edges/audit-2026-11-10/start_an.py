import json,re,math,random,collections,statistics as st
random.seed(9)
D=json.load(open('elon_tr_start.json'))
Phi=lambda x:.5*(1+math.erf(x/math.sqrt(2)))
def bucket(t):
    m=re.match(r'<(\d+)',t)
    if m: return (0,int(m.group(1))-1)
    m=re.match(r'(\d+)\+',t)
    if m: return (int(m.group(1)),int(m.group(1))+20)
    m=re.match(r'(\d+)[-–](\d+)',t)
    if m: return (int(m.group(1)),int(m.group(2)))
TR=collections.defaultdict(dict)
for r in D['tr']: TR[r['eid']][r['t']]=r['tr']
EV=[]
for e in D['evs']:
    bk=[]
    for t,c,op in e['markets']:
        b=bucket(t); o=json.loads(op)
        if not b: bk=None;break
        bk.append((b,float(o[0])==1.0,TR[e['id']].get(t,[])))
    if not bk or sum(x[1] for x in bk)!=1: continue
    real=[(x[0][0]+x[0][1])/2 for x in bk if x[1]][0]
    EV.append(dict(title=e['title'],T=e['start'],real=real,bk=bk))
EV.sort(key=lambda e:e['T'])
for i,e in enumerate(EV): e['mu']=st.mean(x['real'] for x in EV[i-3:i]) if i>=3 else None
EV=[e for e in EV if e['mu']]; cut=len(EV)//2
ratios=[(e['real']-e['mu'])/e['mu'] for e in EV[:cut]]; k=st.pstdev(ratios); b0=st.mean(ratios); print('n',len(EV),'k',round(k,3),'b0',round(b0,3))
def cands(e,th=.05,win=600):
    m_=e['mu']*(1+b0); sd=k*e['mu']; out=[];pool=[]
    for (lo,hi),w,trs in e['bk']:
        pm=Phi((hi+.5-m_)/sd)-Phi((lo-.5-m_)/sd)
        for ts,side,p,sz,oi in trs:
            if side!='BUY' or not(e['T']<=ts<=e['T']+win) or p<=.02 or p>=.98: continue
            pay=(((1 if w else 0) if oi==0 else (0 if w else 1))-p)*sz
            pool.append((ts,sz*p,pay,p,oi)); edge=(pm-p) if oi==0 else ((1-pm)-p)
            if edge>th: out.append((ts,edge,sz*p,pay,p,oi))
    return out,pool
def summ(sel,mode,name,cap=None):
    pn=[];dets=[];stk=0
    for e in sel:
        out,pool=cands(e)
        if out:
            c=max(out,key=lambda x:x[1]) if mode=='best' else min(out,key=lambda x:x[0])
            ts,edge,stake,pnl,p,oi=c
            if cap and stake>cap: pnl*=cap/stake; stake=cap
            pn.append(pnl);stk+=stake;dets.append((c,pool))
        else: pn.append(0.)
    tot=sum(pn);m=st.mean(pn);sd=st.pstdev(pn)
    sims=[]
    for _ in range(2000):
        t=0
        for c,pool in dets:
            mp=[x for x in pool if x[4]==c[5] and abs(x[3]-c[4])<=.1] or pool; t+=random.choice(mp)[2]
        sims.append(t)
    bs=sorted(sum(random.choices(pn,k=len(pn))) for _ in range(4000))
    print(f'{name}: windows={len(pn)} bets={len(dets)} stake=${stk:.0f} pnl=${tot:.0f} roi={tot/stk*100 if stk else 0:+.0f}% t={m/(sd/math.sqrt(len(pn))) if sd else 0:.2f} boot95=[${bs[100]:.0f},${bs[3900]:.0f}] placebo=${st.mean(sims):.0f}±{st.pstdev(sims):.0f} z={(tot-st.mean(sims))/st.pstdev(sims):+.2f} median stake=${st.median([d[0][2] for d in dets]) if dets else 0:.0f}')
for mode in ('best','first'):
    print('--',mode)
    for nm,sel in (('all',EV),('train',EV[:cut]),('test',EV[cut:])): summ(sel,mode,nm)
    summ(EV,mode,'all cap$50',cap=50)
