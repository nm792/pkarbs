import json,glob,bisect,collections as C,statistics as S
P=json.load(open('positions.json'))
fin={}
for r in P:
    if r['status'] in('CLOSED','REDEEMABLE') or r['current_price'] in(0,1): fin[r['token_id']]=r['current_price']
mk=json.load(open('mk3.json'));lgvol=C.Counter();
for x in mk: lgvol[x[0]]+=x[3]
H=[10,30,60,300]
res={}
for lg in('cs2','sea','fl1'):
    st=C.defaultdict(float);mo={k:C.defaultdict(list) for k in('M','T')};pre={'M':[],'T':[]};gap={'M':[],'T':[]};cov=0;nmk=0;unres=0
    for f in glob.glob(f'tapes/{lg}-*.json'):
        d=json.load(open(f));nmk+=1;cov+=d['vol']
        # price series in outcome-0 terms
        ser=[]
        for r in d['tape']:
            p=r['price'] if r['outcome_index']==0 else 1-r['price']
            ser.append((r['timestamp'],p))
        ser.sort();ts=[s[0] for s in ser]
        def px(t,strict=False):
            i=(bisect.bisect_left(ts,t) if strict else bisect.bisect_right(ts,t))-1
            return ser[i][1] if i>=0 else None
        tk=C.Counter((r['transaction_hash'],r['token_id'],r['size'],r['price']) for r in d['tk'])
        for r in d['all']:
            k=(r['transaction_hash'],r['token_id'],r['size'],r['price'])
            if tk[k]>0: role='T';tk[k]-=1
            else: role='M'
            usd=r['size']*r['price'];sg=1 if r['side']=='BUY' else -1
            st[role+'$']+=usd
            fp=fin.get(r['token_id'])
            if fp is None: unres+=usd
            else: st[role+'pnl']+=sg*(fp-r['price'])*r['size']
            # convert to outcome-0 view
            p0=r['price'] if r['outcome_index']==0 else 1-r['price']; s0=sg if r['outcome_index']==0 else -sg
            t=r['timestamp']
            lp=px(t,strict=True)
            if lp is not None: gap[role].append((s0*(lp-p0),usd))
            b=px(t-30,strict=True)
            if b is not None and lp is not None: pre[role].append((s0*(lp-b),usd))
            for h in H:
                a=px(t+h)
                if a is not None: mo[role][h].append((s0*(a-p0),usd))
    def w(L): 
        tw=sum(u for _,u in L); return round(100*sum(x*u for x,u in L)/tw,2) if tw else None
    res[lg]=dict(markets_sampled=nmk,cover=round(cov/lgvol[lg],2),maker_usd=round(st['M$']),taker_usd=round(st['T$']),maker_share=round(st['M$']/(st['M$']+st['T$']),3),
      maker_pnl=round(st['Mpnl']),taker_pnl=round(st['Tpnl']),maker_ret=round(100*st['Mpnl']/st['M$'],2) if st['M$'] else None,taker_ret=round(100*st['Tpnl']/st['T$'],2) if st['T$'] else None,unresolved_usd=round(unres),
      edge_vs_last_print_c={k:w(gap[k]) for k in gap},move_30s_before_c={k:w(pre[k]) for k in pre},
      markout_c={k:{h:w(mo[k][h]) for h in H} for k in mo},nfills={k:len(gap[k]) for k in gap})
print(json.dumps(res,indent=1))
json.dump(res,open('probe_result.json','w'),indent=1)
