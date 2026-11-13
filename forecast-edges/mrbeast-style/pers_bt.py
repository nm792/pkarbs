import json,math,random,statistics as st,collections
random.seed(5)
R=json.load(open('/tmp/w/pers_rows.json')); TR=json.load(open('/tmp/w/pers_trades.json'))
WIN=7200
R.sort(key=lambda r:r['start'])
def grp(k): return k.split('|')[0]+'|'+k.split('|')[1]  # family + rank
def run(label,fam_sel,TH=0.05,verbose=True):
    rows=[r for r in R if fam_sel(r['key'])]
    cut=len(rows)//2; train=rows[:cut]; test=rows[cut:]
    q={}
    for g in set(grp(r['key']) for r in rows):
        tr=[r for r in train if grp(r['key'])==g]
        q[g]=((sum(r['won'] for r in tr)+1)/(len(tr)+2)) if tr else .5
    res=[]
    for half,es in (('train',train),('test',test)):
        for r in es:
            fills=[(t,s,p,sz,oi) for t,s,p,sz,oi in TR.get(r['cid'],[]) if s=='BUY' and r['T']<=t<=r['T']+WIN and .02<p<.98]
            if not fills: continue
            qq=q[grp(r['key'])]; w=1.0 if r['won'] else 0.0
            pool=[(sz*p,((w if oi==0 else 1-w)-p)*sz) for t,s,p,sz,oi in fills]
            out=[]
            for t,s,p,sz,oi in fills:
                e=(qq-p) if oi==0 else ((1-qq)-p)
                if e>TH: out.append((e,sz*p,((w if oi==0 else 1-w)-p)*sz))
            res.append(dict(half=half,bet=max(out) if out else None,pool=pool,key=r['key']))
    def summ(sel,name):
        rs=[d for d in res if sel(d)]; bets=[d for d in rs if d['bet']]; n=len(rs)
        stake=sum(d['bet'][1] for d in bets); pnl=sum(d['bet'][2] for d in bets)
        sims=[sum(random.choice(d['pool'])[1] for d in bets) for _ in range(2000)]
        per=[(d['bet'][2] if d['bet'] else 0.0) for d in rs]
        m=st.mean(per) if per else 0; sdv=st.pstdev(per) if n>1 else 0; sdp=st.pstdev(sims) if bets else 0
        mp=st.mean(sims) if bets else 0
        print(f"{label} {name}: windows(with fills)={n} bets={len(bets)} stake=${stake:.0f} pnl=${pnl:.0f} roi={pnl/stake*100 if stake else 0:+.0f}% | placebo=${mp:.0f}±{sdp:.0f} excess=${pnl-mp:.0f} ({(pnl-mp)/sdp if sdp else 0:+.1f} sd) | t={m/(sdv/math.sqrt(n)) if sdv else 0:.2f} | w/l={sum(1 for d in bets if d['bet'][2]>0)}/{sum(1 for d in bets if d['bet'][2]<0)}")
    print(f"-- {label}: rows={len(rows)} q={ {g:round(v,2) for g,v in q.items()} }")
    summ(lambda d:True,'ALL'); summ(lambda d:d['half']=='train','train'); summ(lambda d:d['half']=='test','TEST')
    return res
for name,sel in [('Netflix',lambda k:k.startswith('netflix')),('Spotify',lambda k:k.startswith('spotify')),('Billboard',lambda k:k.startswith('billboard')),('AppStore',lambda k:k.startswith('appstore')),('OpenRouter',lambda k:k.startswith('openrouter')),('ALL families',lambda k:True)]:
    run(name,sel)
