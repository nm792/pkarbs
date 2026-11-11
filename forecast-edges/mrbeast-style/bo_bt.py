import json,re,math,random,statistics as S
from datetime import datetime as DT,timezone as TZ
D=json.load(open('bo_events.json')); TR=json.load(open('bo_trades.json')); B=json.load(open('bom_weekends.json'))
ORD={'2nd':2,'second':2,'3rd':3,'third':3,'4th':4,'5th':5,'6th':6,'7th':7,'8th':8}
def nm(s): return re.sub(r'[^a-z0-9]','',s.lower())
# BOM index: film -> {weeks: (week key, gross)}
F={}
for wk in sorted(B):
    for r in B[wk]['rows']:
        if r['gross']: F.setdefault(nm(r['title']),{})[r['weeks']]=(wk,r['gross'],r['theaters'])
def brk(g):
    g=g.replace('$','').replace(' ','').lower(); nums=[float(x) for x in re.findall(r'\d+(?:\.\d+)?',g)]
    if g.startswith('<') or g.startswith('<'): return (0,nums[0])
    if g.startswith('>') or g.endswith('+'): return (nums[0],1e9)
    if len(nums)==2: return (nums[0],nums[1])
    return None
evs=[]
for e in D.values():
    t=e['title']; m=re.search(r'["\'“](.+?)["\'”] (?:(\w+) )?weekend',t,re.I) or re.search(r'["“\'](.+?)["”\'] (\d+(?:st|nd|rd|th)|second|third) ',t,re.I)
    mm=re.search(r'["“\'](.+?)["”\']\s+(\d+(?:st|nd|rd|th)|Second|Third)',t)
    if not mm: continue
    n=ORD.get(mm.group(2).lower())
    if not n: continue
    film=nm(mm.group(1))
    if film not in F or n not in F[film] or (n-1) not in F[film]: continue
    bs=[brk(m.get('groupItemTitle') or '') for m in e['markets']]
    if any(b is None for b in bs): continue
    ws=[]
    for m in e['markets']:
        op=json.loads(m['outcomePrices']) if m.get('outcomePrices') else None
        if not op or float(op[0]) not in (0.0,1.0): ws=None;break
        ws.append(float(op[0]))
    if ws is None or sum(ws)!=1: continue
    st=DT.fromisoformat(e['startDate'].replace('Z','+00:00')).timestamp()
    evs.append(dict(id=e['id'],t=t,n=n,film=film,prev=F[film][n-1][1],act=F[film][n][1],pgross_wk=F[film][n-1][0],st=st,ms=e['markets'],bs=bs,ws=ws))
import datetime as _d
def sun(wk): y,w=int(wk[:4]),int(wk[5:]); return DT.combine(_d.date.fromisocalendar(y,w,7),_d.time(),tzinfo=TZ.utc).timestamp()
n0=len(evs); evs=[r for r in evs if r['st']+3600>=sun(r['pgross_wk'])+3*86400]; print('dropped for availability (T before Wed after prior weekend):',n0-len(evs))
evs.sort(key=lambda r:r['st']); print('events',len(evs),'with BOM prior+actual')
# sanity: does actual fall in winning bracket?
bad=0
for r in evs:
    for b,w in zip(r['bs'],r['ws']):
        if w and not (b[0]*1e6<=r['act']<=b[1]*1e6): bad+=1
print('BOM actual outside winning bracket (rounding/est)',bad,'of',len(evs))
h=len(evs)//2
def fit(es,n_):
    lr=[math.log(r['act']/r['prev']) for r in es if r['n']==n_]
    return (S.mean(lr),max(S.pstdev(lr),.08),len(lr)) if len(lr)>=4 else None
def Phi(x): return .5*(1+math.erf(x/2**.5))
def probs(r,mu,sd):
    out=[]
    for lo,hi in r['bs']:
        a=Phi((math.log(max(lo*1e6,1))-math.log(r['prev'])-mu)/sd) if lo>0 else 0
        b=Phi((math.log(hi*1e6)-math.log(r['prev'])-mu)/sd) if hi<1e8 else 1
        out.append(max(b-a,1e-4))
    s=sum(out); return [x/s for x in out]
# fit on first half (all n pooled by n>=2 buckets 2,3,4+)
def bucket(n): return min(n,4)
fits={}
for k in (2,3,4):
    lr=[math.log(r['act']/r['prev']) for r in evs[:h] if bucket(r['n'])==k]
    fits[k]=(S.mean(lr),max(S.pstdev(lr),.08),len(lr)); print('fit weekend',k,'mu %.2f sd %.2f n %d'%fits[k])
def sim(thr,win,sdmult=1.0):
    units=[]
    for r in evs:
        mu,sd,_=fits[bucket(r['n'])]; p=probs(r,mu,sd*sdmult)
        T0=r['st']+3600; bet=None; fills=[]
        cand=[]
        for q,m,w in zip(p,r['ms'],r['ws']):
            cid=m['conditionId']
            for ts,side,pr,sz,oi in TR.get(cid,[]):
                if side!='BUY' or not(T0<=ts<=T0+win): continue
                fills.append((oi,pr,sz,w,r['id']))
                e=(q-pr) if oi==0 else ((1-q)-pr)
                cand.append((ts,e,oi,pr,sz,w))
        cand.sort()
        for ts,e,oi,pr,sz,w in cand:
            if e>=thr and .02<=pr<=.98: bet=dict(oi=oi,p=pr,sz=sz,w=w);break
        units.append(dict(id=r['id'],bet=bet,fills=fills,n=r['n']))
    return units
def pnl(b): return ((b['w'] if b['oi']==0 else 1-b['w'])-b['p'])*b['sz']
def placebo(us,units,rng,N=400):
    bets=[u for u in us if u['bet']]
    pools=[[(oi,p,sz,w) for v in units if v['id']!=u['id'] for oi,p,sz,w,_ in v['fills'] if oi==u['bet']['oi'] and abs(p-u['bet']['p'])<=.05] for u in bets]
    res=[]
    for _ in range(N):
        t=0
        for u,pool in zip(bets,pools):
            if pool: oi,p,sz,w=rng.choice(pool); t+=((w if oi==0 else 1-w)-p)*min(sz,u['bet']['sz'])
        res.append(t)
    return S.mean(res),S.pstdev(res) or 1
def boot(us,rng):
    pn=[pnl(u['bet']) if u['bet'] else 0 for u in us]; m=[]
    for _ in range(2000): m.append(S.mean(rng.choice(pn) for _ in pn))
    m.sort(); return S.mean(pn),m[50],m[1949]
def report(units,label):
    rng=random.Random(3)
    for nm_,us in (('all',units),('test half',units[h:])):
        bets=[u for u in us if u['bet']]
        tot=sum(pnl(u['bet']) for u in bets); pm,ps=placebo(us,units,rng); mu,lo,hi=boot(us,rng)
        cost=sum(u['bet']['p']*u['bet']['sz'] for u in bets)
        print(label,nm_,'bets %d/%d'%(len(bets),len(us)),'pnl $%.0f on $%.0f'%(tot,cost),'placebo $%.0f sd %.0f z %.1f'%(pm,ps,(tot-pm)/ps),'per-event %.2f CI [%.2f,%.2f]'%(mu,lo,hi))
if __name__=='__main__':
    for win in (7200,21600):
        for thr in (.05,.10):
            report(sim(thr,win),'win%dh thr%.2f'%(win//3600,thr))
    # oracle check
    u=sim(.05,7200)
    for x in u:
        if x['bet']: pass
    # oracle / anti-oracle: bet on truth-informed side at same first prints
    import copy
    def orc(sign):
        us=sim(.05,7200)
        out=[]
        for r,u in zip(evs,us):
            b=None
            for oi,pr,sz,w,_ in sorted(u['fills'],key=lambda x:0):
                pass
            fl=u['fills']
            for oi,pr,sz,w,_ in fl:
                win=(w if oi==0 else 1-w)
                if (win==1)==(sign>0) and .02<=pr<=.98: b=dict(oi=oi,p=pr,sz=sz,w=w);break
            out.append(dict(id=u['id'],bet=b,fills=fl,n=u['n']))
        return out
    report(orc(1),'ORACLE'); report(orc(-1),'ANTI-ORACLE')
