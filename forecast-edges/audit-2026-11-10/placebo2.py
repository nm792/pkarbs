import io,contextlib,sys,random,statistics as st
sys.argv=['x','24']
g={}
with contextlib.redirect_stdout(io.StringIO()): exec(open('an.py').read().split("for mode in ('best','first')")[0],g)
EV=g['EV'];cands=g['cands'];pick=g['pick'];k=g['k'];b=g['b']
random.seed(3)
P=[];allpools=[]
for e in EV:
    out,pool=cands(e,k,b); allpools.append(pool)
    c=pick(out,'best')
    # oracle: best-payoff print in same pool (knows outcome), same stake rule: pick max pnl/stake
    orc=max(pool,key=lambda x:x[2]/x[1]) if pool else None
    P.append((c,pool,orc))
def test(bets_sel,name):
    real=sum(c[3] for c,_,_ in bets_sel if c)
    same=[];other=[]
    for _ in range(2000):
        t1=t2=0
        for i,(c,pool,_) in enumerate(P):
            if not c: continue
            mp=[x for x in pool if x[4]==c[5] and abs(x[3]-c[4])<=.1] or pool; t1+=random.choice(mp)[2]
            j=random.choice([x for x in range(len(P)) if x!=i and allpools[x]]); op=allpools[j]
            mo=[x for x in op if x[4]==c[5] and abs(x[3]-c[4])<=.1] or op; t2+=random.choice(mo)[2]
        same.append(t1);other.append(t2)
    print(f'{name}: pnl ${real:.0f} | same-event placebo ${st.mean(same):.0f}±{st.pstdev(same):.0f} z={(real-st.mean(same))/st.pstdev(same):+.2f} | other-event placebo ${st.mean(other):.0f}±{st.pstdev(other):.0f} z={(real-st.mean(other))/st.pstdev(other):+.2f}')
test(P,'real model')
# oracle: replace each bet by the oracle print (same count of bets: events where model bet)
O=[((orc[0],0,orc[1],orc[2],orc[3],orc[4]) if c and orc else None,pool,orc) for c,pool,orc in P]
test(O,'ORACLE (knows winner)')
