import json,sys
evs=json.load(open(sys.argv[1]))
out=[]
for e in evs:
    if not e.get('negRisk'): continue
    ms=[m for m in e.get('markets',[]) if not m.get('closed') and m.get('active') and m.get('acceptingOrders')]
    live=[m for m in ms if not (float(m.get('bestAsk') or 1)>=0.999 and float(m.get('bestBid') or 0)<=0.001)]
    if len(live)<2: continue
    sa=sum(float(m.get('bestAsk') or 1) for m in live); sb=sum(float(m.get('bestBid') or 0) for m in live)
    rate=max(((m.get('feeSchedule') or {}).get('rate') or 0) for m in live)
    other=[m for m in ms if m.get('negRiskOther')]
    dead=len(ms)-len(live)
    out.append((round(sa,3),round(sb,3),len(live),dead,rate,e['slug'][:70],round(float(e.get('liquidity') or 0)),e.get('endDate','')[:10]))
out.sort()
print('events',len(out))
print('--- lowest ask sums (buy all YES; but dead/placeholder legs uncovered!)')
for r in out[:25]: print(r)
print('--- highest bid sums (buy all NO)')
for r in sorted(out,key=lambda r:-r[1])[:15]: print(r)
