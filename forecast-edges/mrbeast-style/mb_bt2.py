import json,re,math,random,statistics as st,collections,datetime,sys
random.seed(7)
Phi=lambda x:.5*(1+math.erf(x/math.sqrt(2)))
D=json.load(open('/tmp/w/mb_events.json')); TR=json.load(open('/tmp/w/mb_trades.json'))
def ts(s): return datetime.datetime.fromisoformat(s.replace('Z','+00:00')).timestamp()
def parse(t):
    t=t.replace(' ','').replace('–','-').replace('m','M')
    nums=[float(x) for x in re.findall(r'[\d\.]+',t)]
    if t.startswith('<'): return (0.0,nums[0])
    if t.endswith('+'): return (nums[0],1e9)
    if len(nums)==2: return (nums[0],nums[1])
    return None
EV=[]
for e in D.values():
    t=e['title']
    m=re.search(r'day (\d+)',t); w=re.search(r'week (\d+)',t)
    if m: h=24*int(m.group(1))
    elif w: h=168*int(w.group(1))
    else: continue
    gam='Gaming' in t
    bk=[];win=None
    for mk in e['markets']:
        b=parse(mk['groupItemTitle'])
        if not b: continue
        op=json.loads(mk['outcomePrices']); w1=1.0 if op[0]=='1' else (0.0 if op[1]=='1' else None)
        if w1 is None: bk=None;break
        bk.append((b[0],b[1],w1,mk['conditionId']))
        if w1==1: win=b
    if not bk or win is None or not e.get('closedTime'): continue
    mid=win[0]+0.5*(win[1]-win[0]) if win[1]<1e8 else win[0]*1.03
    if win[0]==0: mid=win[1]*0.97
    EV.append(dict(id=e['id'],gam=gam,h=h,start=ts(e['startDate']),close=ts(e['closedTime']),bk=bk,mid=mid,title=t))
EV.sort(key=lambda r:r['start'])
for r in EV: r['u']=r['close']-r['h']*3600
print('events',len(EV),'gaming',sum(r['gam'] for r in EV))
# video clustering: same channel, u within 10h
for r in EV: r['vid']=None
vids=[]
for r in sorted(EV,key=lambda r:r['u']):
    for v in vids:
        if v['gam']==r['gam'] and abs(v['u']-r['u'])<10*3600: v['ev'].append(r); r['vid']=v; break
    else:
        v=dict(gam=r['gam'],u=r['u'],ev=[r]); vids.append(v); r['vid']=v
print('videos',len(vids),'events/video',st.mean(len(v['ev']) for v in vids))
# decision T and prior info
LEAD=3600;WIN=7200
for r in EV:
    r['T']=r['start']+LEAD
    # M2: latest same-video event closed before T with different (shorter) horizon
    prev=[x for x in r['vid']['ev'] if x is not r and x['h']<r['h'] and x['close']<=r['T']]
    r['prev']=max(prev,key=lambda x:x['h']) if prev else None
    # M1: previous same-channel same-horizon events (different videos) closed before T
    pk=[x for x in EV if x['gam']==r['gam'] and x['h']==r['h'] and x['vid'] is not r['vid'] and x['close']<=r['T']]
    pk.sort(key=lambda x:x['close']); r['lvl']=[x['mid'] for x in pk[-4:]]
def model_params(train):
    # M1 residual sd, M2 ratio mean/sd by (prev h, h)
    res=[];rat=collections.defaultdict(list)
    for r in train:
        if r['prev'] is None and len(r['lvl'])>=3: res.append(math.log(r['mid'])-st.mean(math.log(x) for x in r['lvl']))
        if r['prev'] is not None: rat[(r['prev']['h'],r['h'])].append(math.log(r['mid']/r['prev']['mid']))
    sd1=st.pstdev(res) if len(res)>2 else 0.5
    b1=st.mean(res) if len(res)>2 else 0
    R={}
    for k,v in rat.items():
        if len(v)>=3: R[k]=(st.mean(v),max(st.pstdev(v),0.01))
    return sd1,b1,R
def forecast(r,P):
    sd1,b1,R=P
    if r['prev'] is not None:
        k=(r['prev']['h'],r['h'])
        if k in R: return math.log(r['prev']['mid'])+R[k][0],R[k][1],'M2'
        return None
    if len(r['lvl'])>=3: return st.mean(math.log(x) for x in r['lvl'])+b1,sd1,'M1'
    return None
def decide(r,P,TH=0.05):
    f=forecast(r,P)
    if f is None: return None
    mu,sd,mod=f; out=[];pool=[]
    for lo,hi,w,c in r['bk']:
        a=Phi((math.log(hi)-mu)/sd) if hi<1e8 else 1.0
        b=Phi((math.log(max(lo,1e-6))-mu)/sd) if lo>0 else 0.0
        pm=a-b
        for t,side,p,sz,oi in TR.get(c,[]):
            if side!='BUY' or not(r['T']<=t<=r['T']+WIN) or p<=.02 or p>=.98: continue
            pay=((w if oi==0 else 1-w)-p)*sz; pool.append((sz*p,pay,oi,p,sz))
            edge=(pm-p) if oi==0 else ((1-pm)-p)
            if edge>TH: out.append((edge,sz*p,pay,oi,p,sz))
    return dict(r=r,mod=mod,bet=max(out) if out else None,pool=pool,nfills=len(pool))
def run(TH=0.05,label=''):
    cut=len(EV)//2; train=EV[:cut]; test=EV[cut:]
    P=model_params(train)
    print(f'\n== {label} TH={TH} params sd1={P[0]:.2f} b1={P[1]:+.2f} ratios={ {k:(round(v[0],3),round(v[1],3)) for k,v in P[2].items()} }')
    res=[]
    for half,es in (('train',train),('test',test)):
        for r in es:
            d=decide(r,P,TH)
            if d and d['nfills']>0: d['half']=half; res.append(d)
    def summ(sel,name):
        rs=[d for d in res if sel(d)]
        bets=[d for d in rs if d['bet']]
        n=len(rs)
        stake=sum(d['bet'][1] for d in bets); pnl=sum(d['bet'][2] for d in bets)
        allp=[(x,d['r']['id']) for d in rs for x in d['pool']]
        cand={id(d):[x for x,eid in allp if eid!=d['r']['id'] and x[2]==d['bet'][3] and abs(x[3]-d['bet'][4])<=.05] for d in bets}
        sims=[]
        for _ in range(2000):
            tot=0
            for d in bets:
                c=cand[id(d)]
                if c:
                    x=random.choice(c); tot+=x[1]/x[4]*min(x[4],d['bet'][5])
            sims.append(tot)
        per=[(d['bet'][2] if d['bet'] else 0.0) for d in rs]
        m=st.mean(per) if per else 0; sdv=st.pstdev(per) if n>1 else 0
        sdp=st.pstdev(sims) if sims and bets else 0
        print(f"{name}: windows(with fills)={n} bets={len(bets)} stake=${stake:.0f} pnl=${pnl:.0f} roi={pnl/stake*100 if stake else 0:+.0f}% | placebo=${st.mean(sims) if sims else 0:.0f}±{sdp:.0f} excess=${pnl-(st.mean(sims) if sims else 0):.0f} ({(pnl-st.mean(sims))/sdp if sdp else 0:+.1f} sd) | t(per window)={m/(sdv/math.sqrt(n)) if sdv else 0:.2f} | w/l={sum(1 for d in bets if d['bet'][2]>0)}/{sum(1 for d in bets if d['bet'][2]<0)}")
    summ(lambda d:True,'ALL')
    summ(lambda d:d['half']=='train','train')
    summ(lambda d:d['half']=='test','TEST')
    summ(lambda d:d['mod']=='M1','M1 level (all)')
    summ(lambda d:d['mod']=='M2','M2 continuation (all)')
    summ(lambda d:d['mod']=='M1' and d['half']=='test','M1 test')
    summ(lambda d:d['mod']=='M2' and d['half']=='test','M2 test')
    return res
if __name__=='__main__':
    run(0.05,'primary')
    run(0.10,'robust TH=0.10')
