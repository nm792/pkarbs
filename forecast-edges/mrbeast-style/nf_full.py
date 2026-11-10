import json,math,random,statistics as st,datetime,collections,re,sys
random.seed(11)
W=json.load(open('/tmp/w/nf_weeks.json')); EVS=json.load(open('/tmp/w/nf_events.json')); TR=json.load(open('/tmp/w/nf_trades.json'))
def ts(s): return datetime.datetime.fromisoformat(s.replace('Z','+00:00')).timestamp()
def wts(w): return datetime.datetime.fromisoformat(w).replace(tzinfo=datetime.timezone.utc).timestamp()
def norm(s): return re.sub(r'[^a-z0-9]','',s.lower())
weeks=sorted(W)
def lst(week,typ):
    rows=[x for x in W[week] if x['cat'].startswith('Films' if typ=='movie' else 'TV')]
    rows.sort(key=lambda x:-x['hours']); return rows
# ---- train regression on TSV: log ratio by age bucket (age = cum weeks of prev week row)
def bucket(c): return min(c,4)
def fit_decay(upto):
    d={('movie',b):[] for b in range(1,5)}; d.update({('show',b):[] for b in range(1,5)})
    newrate={}
    for typ in('movie','show'):
        n=0;tot=0;n2=0
        for i in range(len(weeks)-1):
            if wts(weeks[i+1])>upto: break
            a=lst(weeks[i],typ); b=lst(weeks[i+1],typ)
            if len(a)<2 or len(b)<2: continue
            pa={x['title']:x for x in a}
            for x in b:
                if x['title'] in pa: d[(typ,bucket(pa[x['title']]['cum']))].append(math.log(x['hours']/pa[x['title']]['hours']))
            tot+=1; n+= (b[0]['title'] not in pa); n2+=(b[1]['title'] not in pa)
        newrate[typ]=(n/tot if tot else .5, n2/tot if tot else .5)
    par={k:(st.mean(v),max(st.pstdev(v),.1)) for k,v in d.items() if len(v)>=5}
    return par,newrate
# ---- events
SER=[]
def sk(t):
    if not re.search(r'Netflix',t) or not re.search(r'this week',t): return None
    if re.search(r'How many|say',t): return None
    rk=2 if '#2' in t else 1; reg='US' if re.search(r'\bUS\b',t) else 'global'; typ='movie' if re.search(r'[Mm]ovie',t) else 'show'
    return (reg,typ,rk)
EV=[]
for e in EVS.values():
    k=sk(e['title'])
    if not k or not e.get('closedTime'): continue
    mk=[m for m in e['markets'] if m.get('outcomePrices')]
    w=[m for m in mk if json.loads(m['outcomePrices'])[0]=='1']
    if len(w)!=1: continue
    EV.append(dict(id=e['id'],k=k,start=ts(e['startDate']),close=ts(e['closedTime']),
      mk=[(m['groupItemTitle'],m['conditionId'],json.loads(m['outcomePrices'])[0]=='1') for m in mk],title=e['title']))
EV.sort(key=lambda r:r['start'])
print('resolved events',len(EV),collections.Counter(r['k'] for r in EV))
def match(name,rows):
    n=norm(name); best=None
    for x in rows:
        m=norm(x['title'])
        if len(n)>=4 and (n==m or n in m or m.startswith(n)):
            if best is None or len(m)<len(norm(best['title'])): best=x
    return best
def predict(r,upto,par,newrate,N=3000):
    reg,typ,rk=r['k']
    if reg!='global': return None
    cand=[w for w in weeks if wts(w)+2*86400+16*3600<=r['T']]
    if not cand: return None
    w=cand[-1]
    if r['T']-wts(w)>12*86400: return None
    rows=lst(w,typ)[:10]
    if len(rows)<4: return None
    sims=collections.Counter()
    pr=[par.get((typ,bucket(x['cum'])),(0,.5)) for x in rows]
    for _ in range(N):
        v=[(math.log(x['hours'])+random.gauss(*pr[i]),i) for i,x in enumerate(rows)]
        v.sort(reverse=True); sims[v[rk-1][1]]+=1
    u=newrate[typ][rk-1]
    out={}
    for i,x in enumerate(rows): out[x['title']]=(1-u)*sims[i]/N
    return rows,out
def run(TH=.05,WIN=7200,LEADMODE='start',split=True,verbose=True,label=''):
    cutm=sorted(r['start'] for r in EV if r['k'][0]=='global')
    cut=cutm[len(cutm)//2]
    par,newrate=fit_decay(cut)
    units=[]
    skipped=collections.Counter()
    for r in EV:
        r['T']=r['start']+3600 if LEADMODE=='start' else max(r['start'],r['close']-72*3600)
        if r['k'][0]!='global': continue
        pq=predict(r,cut,par,newrate)
        if pq is None: skipped['nopred']+=1; continue
        rows,P=pq
        prob={}
        for name,c,won in r['mk']:
            mt=match(name,rows)
            if mt: prob[c]=(P[mt['title']],won)
        if not prob: skipped['nomatch']+=1; continue
        fills=[]
        for name,c,won in r['mk']:
            for t,s,p,sz,oi in TR.get(c,[]):
                if s=='BUY' and r['T']<=t<=r['T']+WIN and .02<p<.98: fills.append((t,c,p,sz,oi,won))
        if not fills: skipped['nofills']+=1; continue
        fills.sort()
        bet=None
        for t,c,p,sz,oi,won in fills:
            if c not in prob: continue
            q=prob[c][0]; w=1.0 if won else 0.0
            e=(q-p) if oi==0 else ((1-q)-p)
            if e>TH: bet=dict(oi=oi,p=p,sz=sz,stake=sz*p,pnl=((w if oi==0 else 1-w)-p)*sz); break   # FIRST qualifying print
        units.append(dict(half='test' if r['start']>=cut else 'train',bet=bet,fills=[(oi,p,sz,(1.0 if won else 0.0)) for t,c,p,sz,oi,won in fills],id=r['id'],start=r['start'],k=r['k']))
    def placebo(bets,reps=2000):
        # matched on side (oi) and price within +-5c, drawn from the same event's fills
        tot=[];dropped=0
        for _ in range(reps):
            s=0
            for u in bets:
                b=u['bet']; c=[(oi,p,sz,w) for oi,p,sz,w in u['fills'] if oi==b['oi'] and abs(p-b['p'])<=.05]
                if not c: dropped+=1; c=[(oi,p,sz,w) for oi,p,sz,w in u['fills'] if oi==b['oi']] or u['fills']
                oi,p,sz,w=random.choice(c); s+=((w if oi==0 else 1-w)-p)*sz
            tot.append(s)
        return st.mean(tot),st.pstdev(tot),dropped/reps
    def summ(sel,name):
        us=[u for u in units if sel(u)]; b=[u for u in us if u['bet']]
        if not us: print(label,name,'no units'); return
        stake=sum(u['bet']['stake'] for u in b); pnl=sum(u['bet']['pnl'] for u in b)
        mp,sp,dr=placebo(b) if b else (0,0,0)
        per=[(u['bet']['pnl'] if u['bet'] else 0.0) for u in us]; n=len(us)
        sd=st.pstdev(per) if n>1 else 0; t=(st.mean(per)/(sd/math.sqrt(n))) if sd else 0
        print(f"{label} {name}: event-units={n} bets={len(b)} stake=${stake:.0f} pnl=${pnl:.0f} | matched placebo=${mp:.0f}±{sp:.0f} excess={(pnl-mp)/sp if sp else 0:+.1f} sd (unmatched draws {dr:.1f}/bet-set) | t per event={t:.2f} | w/l={sum(1 for u in b if u['bet']['pnl']>0)}/{sum(1 for u in b if u['bet']['pnl']<0)}")
    summ(lambda u:True,'ALL'); summ(lambda u:u['half']=='train','train'); summ(lambda u:u['half']=='test','TEST')
    for rk in(1,2): summ(lambda u,rk=rk:u['k'][2]==rk and u['half']=='test',f'TEST rank{rk}')
    print(f'   skipped {dict(skipped)}; cut={datetime.datetime.fromtimestamp(cut)}; newrate={newrate}')
    return units
if __name__=='__main__':
    for TH in(.05,.03,.10):
        for WIN in(7200,21600):
            for lm in('start','close72'):
                run(TH,WIN,lm,label=f'[TH={TH} WIN={WIN//3600}h T={lm}]')
