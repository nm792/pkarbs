import json,gzip,collections,statistics as st,re
RN1='0x2005d16a84ceefa912d4e380cd32e7ff827875ea'
rows=[json.loads(l) for l in gzip.open('comp.jsonl.gz','rt')]
F=collections.defaultdict(list); T=collections.defaultdict(collections.Counter)
seen=set()
for r in rows:
    if r['m']=='false':
        k=(r['c'],r['h'],r['t'],r['z'],r['p'],r['s'],r['w'],r['ts'])
        if k in seen: continue
        seen.add(k); F[r['c']].append(r)
    else: T[r['c']][(r['h'],r['t'],r['z'],r['p'],r['s'],r['w'])]+=1  # taker rows (wallet is taker)
# maker rows = false-mode rows not matched by a taker row with same wallet.
M=[]
for c,lst in F.items():
    tc=T[c]
    for r in lst:
        k=(r['h'],r['t'],r['z'],r['p'],r['s'],r['w'])
        if tc[k]>0: tc[k]-=1
        else: M.append(r)
print('rows',len(rows),'unique false-mode',sum(len(v) for v in F.values()),'maker rows',len(M))
byg=collections.defaultdict(lambda: collections.defaultdict(float))
for r in M:
    lg=r['e'].split('-')[0]; byg[(lg,r['e'])][r['w']]+=r['z']*r['p']
res={}
for lg in ('fl1','sea'):
    gs={e:w for (l,e),w in byg.items() if l==lg}
    nw=[len(w) for w in gs.values()]; 
    tot=collections.Counter()
    sh=[];top5=[];rn=[];
    for e,w in gs.items():
        t=sum(w.values()); tot.update(w)
        if t<=0: continue
        sh.append(w.get(RN1,0)/t); top5.append(sum(sorted(w.values(),reverse=True)[:5])/t); rn.append(w.get(RN1,0))
    T_=sum(tot.values())
    print(lg,'games',len(gs),'distinct maker wallets league',len(tot),'per game median',st.median(nw),'mean',round(st.mean(nw),1),
          '| RN1 share of maker notional (league) %.1f%%'%(100*tot[RN1]/T_),'per-game median %.1f%%'%(100*st.median(sh)),
          '| top5 makers share league %.1f%%'%(100*sum(v for _,v in tot.most_common(5))/T_),'per-game median top5 %.1f%%'%(100*st.median(top5)),
          '| maker notional total $%.0f'%T_)
    print('  top makers by notional:',[(w[:8],round(v)) for w,v in tot.most_common(6)])
    res[lg]=dict(games=len(gs),wallets=len(tot),med_wallets=st.median(nw),rn1_share=tot[RN1]/T_,top5=sum(v for _,v in tot.most_common(5))/T_,notl=T_)
json.dump(res,open('comp_summary.json','w'))
print('--- material makers (>= $1,000 maker notional in the game)')
pg=json.load(open('pergame.json'))
for lg in ('fl1','sea'):
    gs={e:w for (l,e),w in byg.items() if l==lg}
    mm=[sum(1 for v in w.values() if v>=1000) for w in gs.values()]
    mm2=[sum(1 for v in w.values() if v>=5000) for w in gs.values()]
    pn=[g['pnl'] for g in pg[lg].values()]
    print(lg,'median material makers (>=$1k)',st.median(mm),'(>=$5k)',st.median(mm2),'| RN1 mean P&L/game $%.0f'%st.mean(pn),'| per >=$1k maker $%.0f'%(st.mean(pn)/st.mean(mm)),'| per >=$5k maker $%.0f'%(st.mean(pn)/max(st.mean(mm2),1)))
sn=json.load(open('snap.json'))
import statistics
for lg in ('fl1','sea','epl','lal'):
    s=[x for x in sn if x['lg']==lg and x.get('bb') is not None and x.get('ba') is not None]
    if not s: print(lg,'no books'); continue
    sp=[x['ba']-x['bb'] for x in s]
    print(lg,'SNAPSHOT tokens',len(s),'games',len({x['slug'] for x in s}),'spread median %.3f'%statistics.median(sp),'best-bid size median %.0f sh'%statistics.median(x['bb_sz'] for x in s),'bid depth top3 $ median %.0f'%statistics.median(x['bid_depth_usd_top3'] for x in s),'within 5c $ median %.0f'%statistics.median(x['bid_depth_usd_5c'] for x in s),'t_utc',s[0]['t_utc'][:16],'..',s[-1]['t_utc'][:16])
