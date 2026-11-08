"""CS2 detail: per role x market type: fills, $, win rate vs avg price, P&L, distinct events,
minutes from fill to the token's last price point (proxy for market end), and an event-level
bootstrap 90% interval for P&L. Usage: cs2detail.py act7d.json.gz meta.json.gz trades7d_dir clobdir..."""
import gzip,json,glob,os,sys,collections,random,bisect,re
A=json.load(gzip.open(sys.argv[1])); meta=json.load(gzip.open(sys.argv[2])); tdir=sys.argv[3]
taker=set()
for f in glob.glob(tdir+'/true_*.json'):
  for r in json.load(open(f))['rows']: taker.add((r['transactionHash'],r['asset'],r['size'],r['price'],r['timestamp']))
pay={}
for c,m in meta.items():
  if not m.get('closed'): continue
  try: op=[float(x) for x in json.loads(m['outcomePrices'])]; tk=json.loads(m['clobTokenIds'])
  except Exception: continue
  for t,o in zip(tk,op): pay[t]=o
last={}; hist={}
for d in sys.argv[4:]:
  for f in glob.glob(d+'/*.json'):
    tok=os.path.basename(f).split('_',1)[1][:-5]
    try: h=json.load(open(f))['history']
    except Exception: continue
    if h: last[tok]=h[-1]['t']; hist[tok]=([x['t'] for x in h],[x['p'] for x in h])
def mtype(r):
  suf=r['slug'][len(r['eventSlug']):]
  return 'match' if suf=='' else 'map_winner' if re.fullmatch(r'-game\d',suf) else 'other'
rows=[]
for r in A:
  if r['type']!='TRADE' or not r['eventSlug'].startswith('cs2'): continue
  tok=r['asset']
  if tok not in pay: continue
  s=float(r['size']);p=float(r['price']);t=int(r['timestamp'])
  role='taker' if (r['transactionHash'],tok,r['size'],r['price'],t) in taker else 'maker'
  m0=None
  if tok in hist:
    ts,ps=hist[tok]; i=bisect.bisect_right(ts,t)-1; m0=ps[i] if i>=0 else None
  rows.append(dict(ev=r['eventSlug'],mk=r['slug'],role=role,mt=mtype(r),s=s,p=p,P=pay[tok],t=t,
    tend=(last.get(tok,t)-t)/60,m0=m0))
out={}
for key in sorted(set((x['role'],x['mt']) for x in rows)):
  g=[x for x in rows if (x['role'],x['mt'])==key]
  usd=sum(x['s']*x['p'] for x in g); pnl=sum(x['s']*(x['P']-x['p']) for x in g)
  sh=sum(x['s'] for x in g)
  evs=collections.defaultdict(float)
  for x in g: evs[x['ev']]+=x['s']*(x['P']-x['p'])
  ev=list(evs.values()); bs=[]
  for _ in range(2000): bs.append(sum(random.choice(ev) for _ in ev))
  bs.sort()
  te=sorted(x['tend'] for x in g)
  top=sorted(evs.items(),key=lambda kv:-abs(kv[1]))[:5]
  out[f'{key[0]}:{key[1]}']=dict(fills=len(g),usd=round(usd),pnl=round(pnl),pnl_pct=round(100*pnl/usd,2),
    avg_price_per_share=round(usd/sh,4),payout_per_share=round(sum(x['s']*x['P'] for x in g)/sh,4),
    events=len(ev),events_positive=sum(1 for v in ev if v>0),boot90=[round(bs[100]),round(bs[1900])],
    min_fill_to_last_price_point_median=round(te[len(te)//2],1),top5_events=[(k,round(v)) for k,v in top])
json.dump(out,sys.stdout,indent=1)
