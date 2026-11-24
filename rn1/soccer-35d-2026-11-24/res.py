import json,gzip,sys,urllib.request,urllib.parse,collections,time
sp=json.load(open('sports.json')); SOC={s['sport'] for s in sp if '100350' in str(s.get('tags','')).split(',')}
def load(f): return [json.loads(l) for l in gzip.open(f,'rt')]
allr=load('all.jsonl.gz'); tk=load('taker.jsonl.gz')
key=lambda r:(r['transaction_hash'],r['token_id'],r['size'],r['price'],r['side'])
seen=set(); A=[]
for r in allr:
    k=key(r)+(r['timestamp'],)
    if k in seen: continue
    seen.add(k); A.append(r)
tc=collections.Counter(key(r) for r in tk)
for r in A:
    k=key(r)
    if tc[k]>0: tc[k]-=1; r['taker']=True
    else: r['taker']=False
mn=min(r['timestamp'] for r in A); mx=max(r['timestamp'] for r in A)
print('fills',len(A),'span days',(mx-mn)/86400, 'sides',collections.Counter(r['side'] for r in A))
S=[r for r in A if (r.get('event_slug') or r.get('slug') or '').split('-')[0] in SOC]
print('soccer fills',len(S),'of',len(A))
conds=sorted({r['condition_id'] for r in S}); print('conditions',len(conds))
import os
cache=json.load(open('mk.json')) if os.path.exists('mk.json') else {}
def gm(batch):
    q=urllib.parse.urlencode([('condition_ids',c) for c in batch]+[('limit',len(batch)),('closed','true')])
    for a in range(5):
        try:
            rq=urllib.request.Request('https://gamma-api.polymarket.com/markets?'+q,headers={'User-Agent':'x','Accept-Encoding':'gzip'})
            b=urllib.request.urlopen(rq,timeout=60).read()
            try: b=gzip.decompress(b)
            except: pass
            return json.loads(b)
        except Exception as e: time.sleep(2*(a+1)); err=e
    raise err
need=[c for c in conds if c not in cache]
from concurrent.futures import ThreadPoolExecutor
batches=[need[i:i+20] for i in range(0,len(need),20)]
def work(b):
    rows=gm(b); got={}
    for m in rows:
        c=m['conditionId'].lower() if m.get('conditionId') else None
        if c not in {x.lower() for x in b}: raise SystemExit('WRONG MARKET returned by gamma: '+str(c))
        got[m['conditionId']]={'closed':m.get('closed'),'tokens':json.loads(m.get('clobTokenIds') or '[]'),'prices':json.loads(m.get('outcomePrices') or '[]'),'umaStatus':m.get('umaResolutionStatus')}
    return got
with ThreadPoolExecutor(8) as ex:
    for g in ex.map(work,batches): cache.update(g)
json.dump(cache,open('mk.json','w'))
print('markets resolved info',len(cache),'of',len(conds))
import statistics as st
by=collections.defaultdict(lambda: dict(n=0,notl=0,mk=0,unres=0,pnl=0,rn=0,games=collections.defaultdict(lambda:[0,0]),pnl_t=0,n_t=0,mk_pnl=0,mk_rn=0))
for r in S:
    lg=(r.get('event_slug') or r['slug']).split('-')[0]; b=by[lg]
    notl=r['size']*(r['price'] if r['side']=='BUY' else 1-r['price'])
    b['n']+=1; b['notl']+=notl
    if not r['taker']: b['mk']+=notl
    m=cache.get(r['condition_id'])
    pay=None
    if m and m['closed'] and r['token_id'] in m['tokens']:
        p=float(m['prices'][m['tokens'].index(r['token_id'])])
        if p in (0.0,1.0): pay=p
    if pay is None: b['unres']+=notl; continue
    pnl=r['size']*((pay-r['price']) if r['side']=='BUY' else (r['price']-pay))
    if not r['taker']:
        b['mk_pnl']+=pnl; b['mk_rn']+=notl
        g=b['games'][r['event_slug']]; g[0]+=pnl; g[1]+=notl
    else: b['pnl_t']+=pnl; b['n_t']+=notl
tot=sum(b['notl'] for b in by.values())
print('league  share% notional maker% | maker resolved notional, P&L, %ret | taker resolved P&L %ret | games, mean game ret%, sd, %pos, t | unresolved$')
out={}
for lg,b in sorted(by.items(),key=lambda x:-x[1]['notl']):
    if b['notl']/tot<0.02: continue
    gr=[g[0]/g[1] for g in b['games'].values() if g[1]>0]
    n=len(gr); mean=st.mean(gr) if n else 0; sd=st.stdev(gr) if n>1 else 0
    t=mean/(sd/n**.5) if sd>0 else 0
    print(f"{lg:5} {100*b['notl']/tot:5.1f} {b['notl']:10.0f} {100*b['mk']/b['notl']:5.1f} | {b['mk_rn']:9.0f} {b['mk_pnl']:8.0f} {100*b['mk_pnl']/max(b['mk_rn'],1):6.2f}% | {b['pnl_t']:7.0f} {100*b['pnl_t']/max(b['n_t'],1):6.2f}% | {n:3d} {100*mean:6.2f} {100*sd:6.1f} {100*sum(x>0 for x in gr)/max(n,1):4.0f} {t:5.2f} | {b['unres']:8.0f}")
    out[lg]=dict(share=b['notl']/tot,notional=b['notl'],maker_pct=b['mk']/b['notl'],mk_resolved=b['mk_rn'],mk_pnl=b['mk_pnl'],games=n,mean=mean,sd=sd,t=t)
json.dump(out,open('league_summary.json','w'))
