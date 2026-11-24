import json,glob,re,bisect,datetime as dt,collections as C,os
P=json.load(open('positions.json'))
fin={}
for r in P:
    if r['status'] in('CLOSED','REDEEMABLE') or r['current_price'] in(0,1): fin[r['token_id']]=r['current_price']
starts=json.load(open('starts.json')) if os.path.exists('starts.json') else {}
mk=json.load(open('mk3.json'));tot=C.Counter()
for x in mk: tot[x[0]]+=x[3]
def mtype(slug):
    m=re.search(r'\d{4}-\d{2}-\d{2}(.*)$',slug);s=m.group(1).strip('-') if m else ''
    if s=='' : return 'match'
    for k in ['halftime','spread','total','btts','map-handicap','game','first','corner','exact','both','handicap','o-u']:
        if k in s: return k
    if s=='draw': return 'draw'
    if len(s)<=5: return 'moneyline'
    return 'other'
def tbin(t,st):
    if st is None: return 'nostart'
    m=(t-st)/60
    if m< -60: return 'pre>60m'
    if m< -10: return 'pre10-60m'
    if m< 0: return 'pre0-10m'
    if m< 45: return 'ip0-45'
    if m< 120: return 'ip45-120'
    return 'post120+'
out={}
for lg in ('cs2','sea','fl1'):
    files={}
    for f in glob.glob(f'rn/{lg}-*.json')+glob.glob(f'tapes/{lg}-*.json'): files[os.path.basename(f)]=f if 'tapes' in f else files.get(os.path.basename(f),f)
    agg=C.defaultdict(lambda:[0.0,0.0]);mkt={};tb=C.defaultdict(lambda:[0.0,0.0]);ty=C.defaultdict(lambda:[0.0,0.0]);sizes=[];band=C.defaultdict(lambda:[0.0,0.0]);cov=0;unres=0
    for name,f in files.items():
        d=json.load(open(f));cov+=d['vol']
        stx=starts.get(d['slug']);st=None
        if stx:
            try: st=dt.datetime.fromisoformat(stx.replace(' ','T').replace('+00','+00:00')).timestamp()
            except: st=None
        tk=C.Counter((r['transaction_hash'],r['token_id'],r['size'],r['price']) for r in d['tk'])
        mp=0
        for r in d['all']:
            k=(r['transaction_hash'],r['token_id'],r['size'],r['price'])
            role='T' if tk[k]>0 else 'M'
            if role=='T': tk[k]-=1
            usd=r['size']*r['price'];sg=1 if r['side']=='BUY' else -1
            fp=fin.get(r['token_id'])
            if fp is None: unres+=usd;continue
            pnl=sg*(fp-r['price'])*r['size']
            agg[role][0]+=usd;agg[role][1]+=pnl
            if role=='M':
                mp+=pnl;sizes.append(usd)
                b=tbin(r['timestamp'],st);tb[b][0]+=usd;tb[b][1]+=pnl
                t=mtype(d['slug']);ty[t][0]+=usd;ty[t][1]+=pnl
                pb='<.2' if r['price']<.2 else '.2-.5' if r['price']<.5 else '.5-.8' if r['price']<.8 else '.8-.95' if r['price']<.95 else '>=.95'
                band[pb][0]+=usd;band[pb][1]+=pnl
        mkt[d['slug']]=mp
    pct=lambda v:(round(v[0]),round(v[1]),round(100*v[1]/v[0],2) if v[0] else None)
    srt=sorted(mkt.values(),reverse=True);n=len(srt)
    sizes.sort()
    out[lg]=dict(markets=n,cover=round(cov/tot[lg],3),unresolved_usd=round(unres),maker=pct(agg['M']),taker=pct(agg['T']),
        maker_share=round(agg['M'][0]/(agg['M'][0]+agg['T'][0]),3),
        markets_maker_positive=round(sum(1 for v in srt if v>0)/n,3),top5_maker_pnl=round(sum(srt[:5])),bottom5=round(sum(srt[-5:])),maker_pnl_ex_top5=round(sum(srt[5:])),
        timing={k:pct(v) for k,v in sorted(tb.items())},mtype={k:pct(v) for k,v in sorted(ty.items(),key=lambda x:-x[1][0])},band={k:pct(v) for k,v in sorted(band.items())},
        maker_fill_usd_median=round(sizes[len(sizes)//2]) if sizes else None,maker_fill_usd_p90=round(sizes[int(len(sizes)*.9)]) if sizes else None)
print(json.dumps(out,indent=1));json.dump(out,open('probe2_result.json','w'),indent=1)
