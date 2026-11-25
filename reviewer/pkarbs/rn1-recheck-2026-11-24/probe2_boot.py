import json,glob,random,re,os,collections as C
P=json.load(open('positions.json'));fin={r['token_id']:r['current_price'] for r in P if r['status'] in('CLOSED','REDEEMABLE') or r['current_price'] in(0,1)}
random.seed(1);res={}
for lg in ['cs2','sea','fl1']:
    files={os.path.basename(f):f for f in glob.glob(f'rn/{lg}-*.json')}
    files.update({os.path.basename(f):f for f in glob.glob(f'tapes/{lg}-*.json')})
    ev=C.defaultdict(lambda:[0,0]);mk=C.defaultdict(lambda:[0,0]);tf=[]
    for f in files.values():
        d=json.load(open(f));e=re.match(r'(.*?\d{4}-\d{2}-\d{2})',d['slug']).group(1)
        tk=C.Counter((r['transaction_hash'],r['token_id'],r['size'],r['price']) for r in d['tk'])
        for r in d['all']:
            k=(r['transaction_hash'],r['token_id'],r['size'],r['price']);T=tk[k]>0
            if T: tk[k]-=1
            fp=fin.get(r['token_id'])
            if fp is None: continue
            x=(1 if r['side']=='BUY' else -1)*(fp-r['price'])*r['size']
            ev[e][T]+=x;mk[d['slug']][T]+=x
            if T: tf.append(x)
    E=list(ev.values());n=len(E)
    for i,nm in [(0,'maker'),(1,'taker')]:
        x=[v[i] for v in E];bs=sorted(sum(random.choice(x) for _ in range(n)) for _ in range(4000))
        ms=sorted((v[i] for v in mk.values()),reverse=True)
        res[f'{lg}_{nm}']=dict(events=n,pnl=round(sum(x)),ci95=(round(bs[100]),round(bs[3900])),events_pos=round(sum(1 for v in x if v>0)/n,2),top5_markets=round(sum(ms[:5])),ex_top5=round(sum(ms[5:])))
    tf.sort(reverse=True);res[f'{lg}_taker']['top20_fills']=round(sum(tf[:20]));res[f'{lg}_taker']['n_fills']=len(tf)
for k,v in res.items(): print(k,v)
json.dump(res,open('bootstrap.json','w'),indent=1)
