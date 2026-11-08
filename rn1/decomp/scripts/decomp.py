"""Exact per-fill decomposition of rn1 trade P&L (22-29 Oct 2026 fills).
Per fill (shares s, price p, token mid m(t) from CLOB prices-history, 1-min points, last point <= t):
  entry = s*(m0 - p)        bought below/above the market price at the moment of fill
  move1 = s*(m60 - m0)      price move in the first minute after the fill (adverse selection if <0)
  move10= s*(m600 - m60)    move 1-10 min after
  hold  = s*(payout - m600) what holding to the result earned vs the 10-min price
  sum   = s*(payout - p)    = trade P&L of the fill (exact identity)
Usage: decomp.py act7d.json.gz meta.json.gz trades7d_dir clob_dir1 [clob_dir2 ...] > out.json"""
import gzip,json,glob,os,sys,bisect,collections
act,metaf,tdir=sys.argv[1:4]; cdirs=sys.argv[4:]
A=json.load(gzip.open(act)); meta=json.load(gzip.open(metaf))
tr=[r for r in A if r['type']=='TRADE']
def K5(r): return (r['transactionHash'],r['asset'],round(float(r['size']),4),round(float(r['price']),6),int(r['timestamp']))
taker=set()
for f in glob.glob(tdir+'/true_*.json'):
  for r in json.load(open(f))['rows']: taker.add(K5(r))
hist={}
for d in cdirs:
  for f in glob.glob(d+'/*.json'):
    tok=os.path.basename(f).split('_',1)[1][:-5]
    try: h=json.load(open(f))['history']
    except Exception: continue
    if h: hist[tok]=([x['t'] for x in h],[x['p'] for x in h])
pay={}; 
for c,m in meta.items():
  if not m.get('closed'): continue
  try:
    op=[float(x) for x in json.loads(m['outcomePrices'])]; tk=json.loads(m['clobTokenIds'])
  except Exception: continue
  if sorted(op) not in ([0.0,1.0],[0.5,0.5]): continue
  for t,o in zip(tk,op): pay[t]=o
def mid(tok,t):
  ts,ps=hist[tok]; i=bisect.bisect_right(ts,t)-1
  return ps[i] if i>=0 else None
def sport(slug):
  s=slug.split('-')[0]
  if s in('wta','atp'):return 'tennis'
  if s=='cs2':return 'cs2'
  if s in('nfl','nba','mlb','nhl','cfb','cbb'):return 'us'
  if s in('lol','dota2','val'):return 'other_esports'
  return 'soccer_other'
K=['usd','pnl','entry','move1','move10','hold','n']
agg=collections.defaultdict(lambda:dict.fromkeys(K,0.0)); skip=collections.Counter()
def add(key,v):
  a=agg[key]
  for k in K: a[k]+=v[k]
for r in tr:
  tok=r['asset']; s=float(r['size']); p=float(r['price']); t=int(r['timestamp'])
  if tok not in pay: skip['unresolved_usd']+=s*p; continue
  if tok not in hist: skip['no_hist_usd']+=s*p; skip['no_hist_pnl']+=s*(pay[tok]-p); continue
  m0,m60,m600=mid(tok,t),mid(tok,t+60),mid(tok,t+600)
  if m0 is None: skip['no_mid_usd']+=s*p; skip['no_mid_pnl']+=s*(pay[tok]-p); continue
  P=pay[tok]
  v=dict(usd=s*p,pnl=s*(P-p),entry=s*(m0-p),move1=s*(m60-m0),move10=s*(m600-m60),hold=s*(P-m600),n=1)
  role='taker' if K5(r) in taker else 'maker'
  sp=sport(r.get('eventSlug') or r.get('slug') or '')
  pb='p<0.2' if p<0.2 else 'p0.2-0.4' if p<0.4 else 'p0.4-0.6' if p<0.6 else 'p0.6-0.8' if p<0.8 else 'p>=0.8'
  for key in ['ALL','role:'+role,'sport:'+sp,f'sport_role:{sp}:{role}',f'price:{pb}',f'cs2_price:{pb}' if sp=='cs2' else None]:
    if key: add(key,v)
out={'skip':dict(skip),'agg':{k:{kk:round(vv,2) for kk,vv in v.items()} for k,v in sorted(agg.items())}}
json.dump(out,sys.stdout,indent=1)
