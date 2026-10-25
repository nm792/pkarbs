import json,copy
B=json.load(open('books_senate.json')); L=json.load(open('senate_legs.json'))
def tok(ev,name,side='yes'):
    for l in L:
        if l['ev'].startswith(ev) and l['name']==name: return (l[side] if side=='yes' else l['yes']+':NO')
    raise KeyError(ev+name)
# NO ladders from YES bids (buy NO at 1-bid); valid on neg-risk markets via the NO token book mirror
for l in L:
    b=B[l['yes']]; B[l['yes']+':NO']=dict(asks=[(round(1-p,4),s) for p,s in b['bids']])
S='which-party-will-win-the-senate'; P='balance-of-power'; O85='who-wins-the-senate-pending-oil-below-85'; O80='who-wins-the-senate-pending-oil-above-or-below-80'
H1='who-wins-the-senate-pending-hormuz-agreement-by-oct-23'; H2='who-wins-the-senate-pending-hormuz-agreement-and-oil'
def inst(side):
    p='Republican' if side=='R' else 'Democratic'; o='D' if side=='R' else 'R'
    out={f'main {side} YES':[tok(S,p+' Party')], f'main {o} NO (+Other)':[tok(S,('Democratic' if side=='R' else 'Republican')+' Party','no')]}
    if side=='R': out['BoP R']=[tok(P,'R Senate, D House'),tok(P,'Republicans Sweep')]
    else: out['BoP D']=[tok(P,'Democrats Sweep'),tok(P,'D Senate, R House')]
    out['oil85']=[tok(O85,f'Oil < $85; {side} Senate'),tok(O85,f'Oil ≥ $85; {side} Senate')]
    out['oil80']=[tok(O80,f'Oil < $80; {side} Senate'),tok(O80,f'Oil ≥ $80; {side} Senate')]
    out['HO80-oct23']=[tok(H1,f'Agreement + Oil < $80; {side} Senate'),tok(H1,f'No Agreement or Oil ≥ $80; {side} Senate')]
    out['HO80']=[tok(H2,f'Agreement + Oil < $80; {side} Senate'),tok(H2,f'No Agreement or Oil ≥ $80; {side} Senate')]
    return out
def top(bk,t): 
    a=bk[t]['asks']; return a[0] if a else (9,0)
def take(bk,t,q):
    a=bk[t]['asks']; a[0]=(a[0][0],a[0][1]-q)
    if a[0][1]<=1e-9: a.pop(0)
def run(maxq=1e6, step_print=(1000,5000,10000,20000,50000,100000)):
    bk=copy.deepcopy(B); I={'R':inst('R'),'D':inst('D')}
    tot=0; cost=0; used={}
    rows=[]
    while tot<maxq:
        best={}
        for side in 'RD':
            c=[(sum(top(bk,t)[0] for t in ts), min(top(bk,t)[1] for t in ts), k) for k,ts in I[side].items()]
            best[side]=min(c)
        px=best['R'][0]+best['D'][0]
        if px>=1: break
        q=min(best['R'][1],best['D'][1],maxq-tot)
        for side in 'RD':
            for t in I[side][best[side][2]]: take(bk,t,q)
            used[best[side][2]]=used.get(best[side][2],0)+q
        tot+=q; cost+=q*px; rows.append((round(px,4),round(q,1),best['R'][2],best['D'][2]))
    return tot,cost,used,rows
tot,cost,used,rows=run()
print('sets',round(tot),'cost',round(cost,2),'profit',round(tot-cost,2),'avg',round(cost/tot,4) if tot else None)
print('used',{k:round(v) for k,v in used.items()})
for r in rows[:40]: print(r)
