"""Event-level bootstrap 90% interval of pre-fee trade P&L by sport x role. Usage: boot.py act7d meta trades7d_dir"""
import gzip,json,glob,sys,collections,random
A=json.load(gzip.open(sys.argv[1])); meta=json.load(gzip.open(sys.argv[2]))
taker=set()
for f in glob.glob(sys.argv[3]+'/true_*.json'):
  for r in json.load(open(f))['rows']: taker.add((r['transactionHash'],r['asset'],r['size'],r['price'],r['timestamp']))
pay={}
for c,m in meta.items():
  if not m.get('closed'): continue
  try: op=[float(x) for x in json.loads(m['outcomePrices'])]; tk=json.loads(m['clobTokenIds'])
  except Exception: continue
  for t,o in zip(tk,op): pay[t]=o
def sport(s):
  s=s.split('-')[0]
  return 'tennis' if s in('wta','atp') else 'cs2' if s=='cs2' else 'us' if s in('nfl','nba','mlb','nhl','cfb','cbb') else 'other_esports' if s in('lol','dota2','val') else 'soccer_other'
ev=collections.defaultdict(lambda:collections.defaultdict(float))
for r in A:
  if r['type']!='TRADE' or r['asset'] not in pay: continue
  role='taker' if (r['transactionHash'],r['asset'],r['size'],r['price'],r['timestamp']) in taker else 'maker'
  k=(sport(r['eventSlug']),role); ev[k][r['eventSlug']]+=float(r['size'])*(pay[r['asset']]-float(r['price']))
random.seed(1); out={}
for k,d in sorted(ev.items()):
  v=list(d.values()); bs=sorted(sum(random.choice(v) for _ in v) for _ in range(2000))
  out[':'.join(k)]=dict(events=len(v),pnl=round(sum(v)),boot90=[round(bs[100]),round(bs[1900])],share_events_positive=round(sum(x>0 for x in v)/len(v),2))
json.dump(out,sys.stdout,indent=1)
