import json,time,datetime as dt,collections as C
P=json.load(open('positions.json.gz' if False else 'positions.json'))
seen=set();rows=[]
for r in P:
    k=(r['token_id'])
    if k in seen: continue
    seen.add(k);rows.append(r)
now=int(time.time())
def sport(s):
    p=s.split('-')[0]
    return p
def agg(lo,hi,filt):
    pnl=0;vol=0;mk=set();days=C.defaultdict(float);opn=0
    for r in rows:
        t=r['last_event_at']
        if not(lo<=t<hi) or not filt(r): continue
        pnl+=r['total_pnl'];vol+=r['avg_price']*r['total_size'];mk.add(r['condition_id'])
        days[dt.datetime.utcfromtimestamp(t).strftime('%m-%d')]+=r['total_pnl']
        if r['status']=='OPEN': opn+=r['unrealized_pnl']
    return pnl,vol,len(mk),days,opn
W=30*86400
for name,f in [('ALL',lambda r:True),('NBA',lambda r:r['slug'].startswith('nba-'))]:
    for lab,lo,hi in [('last30',now-W,now),('prior30',now-2*W,now-W)]:
        pnl,vol,n,days,opn=agg(lo,hi,f)
        print(name,lab,f'pnl {pnl:,.0f} buy$ {vol:,.0f} ret {100*pnl/vol if vol else 0:.2f}% markets {n} open-unrealized {opn:,.0f} posdays {sum(v>0 for v in days.values())}/{len(days)}')
        if name=='NBA' and lab=='last30': print(' daily',{k:round(v) for k,v in sorted(days.items())})
# by sport last30
s=C.defaultdict(lambda:[0,0])
for r in rows:
    if now-W<=r['last_event_at']<now:
        s[sport(r['slug'])][0]+=r['total_pnl'];s[sport(r['slug'])][1]+=r['avg_price']*r['total_size']
for k,v in sorted(s.items(),key=lambda x:-x[1][1])[:15]: print(k,f'{v[0]:,.0f}',f'{v[1]:,.0f}',f'{100*v[0]/v[1]:.2f}%')
