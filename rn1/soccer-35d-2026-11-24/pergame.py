import json,gzip,collections,random,csv,re
exec(open('res.py').read().split("tot=sum(")[0].replace("print(","(lambda *a,**k:None)("))  # reuse loading/classification quietly
cache=json.load(open('mk.json'))
def pay(r):
    m=cache.get(r['condition_id'])
    if m and m['closed'] and r['token_id'] in m['tokens']:
        p=float(m['prices'][m['tokens'].index(r['token_id'])])
        if p in (0.0,1.0): return p
    return None
G=collections.defaultdict(lambda: collections.defaultdict(lambda: dict(notl=0,fills=0,pnl=0,unres=0,tk_notl=0,tk_pnl=0)))
for r in S:
    ev=r['event_slug']; lg=ev.split('-')[0]; g=G[lg][ev]
    notl=r['size']*r['price']; p=pay(r)
    if r['taker']:
        g['tk_notl']+=notl
        if p is not None: g['tk_pnl']+=r['size']*(p-r['price'])
        continue
    g['fills']+=1
    if p is None: g['unres']+=notl; continue
    g['notl']+=notl; g['pnl']+=r['size']*(p-r['price'])
random.seed(7)
def boot(games,B=4000):
    gl=[(g['pnl'],g['notl']) for g in games if g['notl']>0]
    if len(gl)<5: return None
    pt=sum(a for a,b in gl)/sum(b for a,b in gl); xs=[]
    for _ in range(B):
        s=[random.choice(gl) for _ in gl]; d=sum(b for a,b in s); xs.append(sum(a for a,b in s)/d)
    xs.sort(); return pt,xs[int(.025*B)],xs[int(.975*B)],len(gl)
print('league: games, maker resolved notional, P&L, weighted %ret [game-cluster bootstrap 95% CI], share of games with +P&L')
for lg in ['fl1','sea','epl','lal','ucl','bun','uel','unl','bra']:
    gs=list(G[lg].values()); b=boot(gs)
    if not b: continue
    tn=sum(g['notl'] for g in gs); tp=sum(g['pnl'] for g in gs)
    print(f"{lg:4} games {b[3]:4d} notl {tn:9.0f} pnl {tp:8.0f} ret {100*b[0]:6.2f}% CI [{100*b[1]:6.2f}, {100*b[2]:6.2f}] pos {100*sum(g['pnl']>0 for g in gs if g['notl']>0)/b[3]:3.0f}%")
for lg in ['fl1','sea']:
    with open(f'pergame_{lg}.csv','w',newline='') as f:
        w=csv.writer(f); w.writerow(['event_slug','date','maker_resolved_notional','maker_fills','pnl_before_rebate','pct_return','maker_unresolved_notional','taker_notional','taker_pnl'])
        for ev,g in sorted(G[lg].items(),key=lambda x:x[0].split('-')[-3:]):
            d='-'.join(ev.split('-')[3:6]) if len(ev.split('-'))>=6 else ''
            m=re.search(r'(\d{4}-\d\d-\d\d)',ev); d=m.group(1) if m else ''
            w.writerow([ev,d,round(g['notl']),g['fills'],round(g['pnl'],1),round(100*g['pnl']/g['notl'],2) if g['notl'] else '',round(g['unres']),round(g['tk_notl']),round(g['tk_pnl'],1)])
    # concentration: share of league P&L from top 5 games, and by-week
    gs=sorted(G[lg].items(),key=lambda x:-x[1]['pnl']); tp=sum(g['pnl'] for _,g in gs)
    print(lg,'total pnl',round(tp),'top5 games pnl',round(sum(g['pnl'] for _,g in gs[:5])),'bottom5',round(sum(g['pnl'] for _,g in gs[-5:])))
    wk=collections.defaultdict(lambda:[0,0])
    for ev,g in G[lg].items():
        m=re.search(r'(\d{4})-(\d\d)-(\d\d)',ev)
        if m:
            import datetime; d=datetime.date(*map(int,m.groups())); k=d.isocalendar()[:2]; wk[k][0]+=g['pnl']; wk[k][1]+=g['notl']
    print(lg,'by ISO week (pnl, notl, %):',[(k,round(v[0]),round(v[1]),round(100*v[0]/v[1],1) if v[1] else None) for k,v in sorted(wk.items())])
json.dump({lg:{ev:g for ev,g in d.items()} for lg,d in G.items() if lg in('fl1','sea')},open('pergame.json','w'))
