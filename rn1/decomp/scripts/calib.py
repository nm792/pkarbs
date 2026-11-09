"""Is Polymarket's own price unbiased in the markets rn1 trades? For every 1-min price point of every
resolved token, average (payout - price) by price bucket and sport. ~0 = price is a fair forecast,
so any rn1 'hold' profit is selection, not a generic market bias. Usage: calib.py meta.json.gz act7d.json.gz clobdir..."""
import gzip,json,glob,os,sys,collections
meta=json.load(gzip.open(sys.argv[1])); act=json.load(gzip.open(sys.argv[2]))
slug={r['asset']:(r.get('eventSlug') or '') for r in act if r['type']=='TRADE'}
pay={}
for c,m in meta.items():
  if not m.get('closed'): continue
  try: op=[float(x) for x in json.loads(m['outcomePrices'])]; tk=json.loads(m['clobTokenIds'])
  except Exception: continue
  if sorted(op)!=[0.0,1.0]: continue
  for t,o in zip(tk,op): pay[t]=(o,m['events'][0]['slug'] if m.get('events') else '')
def sport(s):
  s=s.split('-')[0]
  return 'tennis' if s in('wta','atp') else 'cs2' if s=='cs2' else 'us' if s in('nfl','nba','mlb','nhl','cfb','cbb') else 'soccer_other'
agg=collections.defaultdict(lambda:[0,0.0,0.0])
for d in sys.argv[3:]:
  for f in glob.glob(d+'/*.json'):
    tok=os.path.basename(f).split('_',1)[1][:-5]
    if tok not in pay: continue
    P,sl=pay[tok]
    try: h=json.load(open(f))['history']
    except Exception: continue
    for x in h:
      p=x['p']
      if p<=0.01 or p>=0.99: continue
      pb='p<0.2' if p<0.2 else 'p0.2-0.4' if p<0.4 else 'p0.4-0.6' if p<0.6 else 'p0.6-0.8' if p<0.8 else 'p>=0.8'
      for k in ('ALL:'+pb,sport(sl)+':'+pb,'ALL',sport(sl)):
        a=agg[k]; a[0]+=1; a[1]+=P-p; a[2]+=p
print(json.dumps({k:{'points':v[0],'mean_payout_minus_price_c':round(100*v[1]/v[0],3),'mean_price':round(v[2]/v[0],3)} for k,v in sorted(agg.items())},indent=1))
