import json,math,random,statistics as st,datetime,collections,re
random.seed(3)
W=json.load(open('/tmp/w/nf_weeks.json')); R=json.load(open('/tmp/w/pers_rows.json')); TR=json.load(open('/tmp/w/pers_trades.json'))
def wts(w): return datetime.datetime.fromisoformat(w).replace(tzinfo=datetime.timezone.utc).timestamp()
def norm(s): return re.sub(r'[^a-z0-9]','',s.lower())
weeks=sorted(W)
def top(week,typ):
    rows=[x for x in W[week] if x['cat'].startswith('Films' if typ=='movie' else 'TV')]
    rows.sort(key=lambda x:-x['hours'])
    return rows
def feat(i,typ):
    # features of the #1 title in week i
    r=top(weeks[i],typ)
    if len(r)<2: return None
    t1=r[0]; lead=math.log(r[0]['hours']/r[1]['hours'])
    prevh=None
    if i>0:
        for x in W[weeks[i-1]]:
            if x['title']==t1['title']: prevh=x['hours']
    trend=math.log(t1['hours']/prevh) if prevh else 0.0   # 0 for new
    new=1.0 if not prevh else 0.0
    return [1.0,lead,trend,new,min(t1['cum'],8)/8]
def label(i,typ):
    if i+1>=len(weeks): return None
    a=top(weeks[i],typ);b=top(weeks[i+1],typ)
    if not a or not b: return None
    return 1.0 if a[0]['title']==b[0]['title'] else 0.0
def fit(X,y,l2=1.0):
    d=len(X[0]); w=[0.0]*d
    for _ in range(50):
        g=[ -l2*w[j] if j else 0 for j in range(d)]; H=[[(l2 if (j==k and j) else 0) for k in range(d)] for j in range(d)]
        for x,t in zip(X,y):
            p=1/(1+math.exp(-sum(a*b for a,b in zip(w,x))))
            for j in range(d):
                g[j]+=(t-p)*x[j]
                for k in range(d): H[j][k]+=p*(1-p)*x[j]*x[k]
        # solve H dw = g
        A=[row[:]+[g[i]] for i,row in enumerate(H)]
        for c in range(d):
            piv=max(range(c,d),key=lambda r:abs(A[r][c])); A[c],A[piv]=A[piv],A[c]
            for r in range(d):
                if r!=c:
                    f=A[r][c]/A[c][c]
                    for k in range(c,d+1): A[r][k]-=f*A[c][k]
        dw=[A[i][d]/A[i][i] for i in range(d)]
        w=[a+b for a,b in zip(w,dw)]
        if max(abs(x) for x in dw)<1e-8: break
    return w
sig=lambda z:1/(1+math.exp(-z))
cut_ts=sorted(r['start'] for r in R if r['key'] in('netflix|top|global|movie','netflix|top|global|show'))
cut=cut_ts[len(cut_ts)//2]
MODEL={}
for typ in ('movie','show'):
    X=[];y=[];Xt=[];yt=[]
    for i in range(len(weeks)-1):
        f=feat(i,typ);l=label(i,typ)
        if f is None or l is None: continue
        (X if wts(weeks[i])+7*86400<cut else Xt).append(f) ; (y if wts(weeks[i])+7*86400<cut else yt).append(l)
    w=fit(X,y); base=sum(y)/len(y)
    ll=lambda ps,ys:-st.mean(t*math.log(p)+(1-t)*math.log(1-p) for p,t in zip(ps,ys))
    pm=[min(max(sig(sum(a*b for a,b in zip(w,x))),.02),.98) for x in Xt]
    print(typ,'train weeks',len(y),'test weeks',len(yt),'stay rate train',round(base,2),'test',round(sum(yt)/len(yt),2),'w',[round(a,2) for a in w],'| TSV test logloss model',round(ll(pm,yt),3),'base',round(ll([base]*len(yt),yt),3))
    MODEL[typ]=w
# trade test
def run(TH=0.05,WIN=7200):
    out=[]
    for r in sorted(R,key=lambda r:r['start']):
        if r['key'] not in('netflix|top|global|movie','netflix|top|global|show'): continue
        typ='movie' if 'movie' in r['key'] else 'show'
        # find TSV week whose #1 matches prevwin, latest published before T
        cand=None
        for i,wk in enumerate(weeks):
            if wts(wk)+7*86400>r['T']: break
            t=top(wk,typ)
            if t and (norm(t[0]['title'])==norm(r['prevwin']) or norm(r['prevwin']) in norm(t[0]['title']) or norm(t[0]['title'].split(': Season')[0])==norm(r['prevwin'].split(': Season')[0])): cand=i
        if cand is None: continue
        f=feat(cand,typ)
        if f is None: continue
        q=min(max(sig(sum(a*b for a,b in zip(MODEL[typ],f))),.02),.98)
        fills=[(t,s,p,sz,oi) for t,s,p,sz,oi in TR.get(r['cid'],[]) if s=='BUY' and r['T']<=t<=r['T']+WIN and .02<p<.98]
        if not fills: continue
        w=1.0 if r['won'] else 0.0
        pool=[(sz*p,((w if oi==0 else 1-w)-p)*sz) for t,s,p,sz,oi in fills]
        bets=[]
        for t,s,p,sz,oi in fills:
            e=(q-p) if oi==0 else ((1-q)-p)
            if e>TH: bets.append((e,sz*p,((w if oi==0 else 1-w)-p)*sz))
        out.append(dict(half='test' if r['start']>=cut else 'train',bet=max(bets) if bets else None,pool=pool))
    def summ(sel,name):
        rs=[d for d in out if sel(d)]; b=[d for d in rs if d['bet']]
        stake=sum(d['bet'][1] for d in b); pnl=sum(d['bet'][2] for d in b)
        sims=[sum(random.choice(d['pool'])[1] for d in b) for _ in range(2000)]
        sdp=st.pstdev(sims) if b else 0; mp=st.mean(sims) if b else 0
        print(f"{name}: windows(with fills)={len(rs)} bets={len(b)} stake=${stake:.0f} pnl=${pnl:.0f} placebo=${mp:.0f}±{sdp:.0f} excess={(pnl-mp)/sdp if sdp else 0:+.1f} sd")
    summ(lambda d:True,'ALL'); summ(lambda d:d['half']=='train','train'); summ(lambda d:d['half']=='test','TEST')
run()
