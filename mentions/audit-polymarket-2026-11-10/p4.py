from pmaudit import *
D=data()
print('== robustness: alpha, burn (robustness only, not selection)')
for a in (1.0,5.0):
    U,LS=run(.10,alpha=a);report(U,f'thr .10 alpha {a}',nsim=1000)
for frac in (.15,.5):
    for f,evs in D.items():
        b=max(10,int(frac*len(evs)))
        for i,e in enumerate(evs):e['burn']=i<b
    U,LS=run(.10);report(U,f'thr .10 burn {frac}',nsim=1000);U,_=run(.03);report(U,f'thr .03 burn {frac}',nsim=1000)
for f,evs in D.items():
    b=max(10,int(.3*len(evs)))
    for i,e in enumerate(evs):e['burn']=i<b
print('== p range')
for lo,hi in ((.02,.98),(.10,.90)):
    U,_=run(.10,pmin=lo,pmax=hi);report(U,f'thr .10 p in [{lo},{hi}]',nsim=1000)
print('== price bucket of 10c bets')
U,_=run(.10);bk=collections.defaultdict(list)
for u in U:
    if u['bet']:
        b=u['bet'];bk[('YES' if b['oi']==0 else 'NO',min(int(b['p']*100)//20*20,80))].append(b)
for k in sorted(bk):
    v=bk[k];print(k,'n',len(v),'stake',round(sum(b['p']*b['sz'] for b in v)),'pnl',round(sum(pnl(b) for b in v)),'win%',round(100*S.mean((b['w'] if b['oi']==0 else 1-b['w']) for b in v)),'avg p',round(100*S.mean(b['p'] for b in v)))
bets=[u['bet'] for u in U if u['bet']];print('avg stake $',round(S.mean(b['p']*b['sz'] for b in bets),1),'median shares',S.median(b['sz'] for b in bets))
# per-day
first=min(u['t0'] for u in U);last=max(u['t0'] for u in U);days=(last-first)/86400
print('span days',round(days),'pnl/day',round(sum(pnl(b) for b in bets)/days,2))
# log score event level
LS=[];EV=collections.defaultdict(list)
U,LS=run(.10)
# recompute per event
for f,evs in D.items():
    pass
