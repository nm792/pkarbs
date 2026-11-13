"""Out-of-sample check, fills 29 Oct 02Z - 2 Nov 06Z: pre-fee trade P&L by sport x role, CS2 taker by market type,
event bootstrap 90%. Fetches gamma results for traded markets. Usage: oos.py activity.jsonl.gz taker.jsonl.gz meta_out.json.gz"""
import gzip,json,sys,collections,random,re,urllib.request
act=[json.loads(l) for l in gzip.open(sys.argv[1],'rt')]; tk=[json.loads(l) for l in gzip.open(sys.argv[2],'rt')]
tr=[x for x in act if x['type']=='TRADE']
tkey=collections.Counter((x['token_id'],round(float(x['size']),4),round(float(x['price']),6),x['timestamp']) for x in tk)
cids=sorted(set(x['condition_id'] for x in tr)); meta={}
for i in range(0,len(cids),40):
  q='&'.join('condition_ids='+c for c in cids[i:i+40])
  for cl in ('true','false'):
    for m in json.load(urllib.request.urlopen(urllib.request.Request(f'https://gamma-api.polymarket.com/markets?limit=100&closed={cl}&{q}',headers={'User-Agent':'Mozilla/5.0'}),timeout=60)): meta[m['conditionId']]=m
json.dump(meta,gzip.open(sys.argv[3],'wt'))
pay={}
for m in meta.values():
  if not m.get('closed'): continue
  try:
    for t,o in zip(json.loads(m['clobTokenIds']),[float(x) for x in json.loads(m['outcomePrices'])]): pay[t]=o
  except Exception: pass
def sport(s):
  s=s.split('-')[0]
  return 'tennis' if s in('wta','atp') else 'cs2' if s=='cs2' else 'us' if s in('nfl','nba','mlb','nhl','cfb','cbb') else 'other_esports' if s in('lol','dota2','val') else 'soccer_other'
ev=collections.defaultdict(lambda:collections.defaultdict(float)); usd=collections.Counter(); ntk=0; unres=0
for x in tr:
  tok=x['token_id']
  if tok not in pay: unres+=x['usdc_size']; continue
  k=(tok,round(float(x['size']),4),round(float(x['price']),6),x['timestamp'])
  role='maker'
  if tkey[k]>0: role='taker'; tkey[k]-=1; ntk+=1
  sp=sport(x['event_slug']); pnl=float(x['size'])*(pay[tok]-float(x['price']))
  keys=[f'{sp}:{role}','ALL:'+role]
  if sp=='cs2':
    suf=x['slug'][len(x['event_slug']):]
    keys.append('cs2_'+role+':'+('match' if suf=='' else 'map_winner' if re.fullmatch(r'-game\d',suf) else 'other'))
  for kk in keys: ev[kk][x['event_slug']]+=pnl; usd[kk]+=x['usdc_size']
random.seed(1); out={'unresolved_usd':round(unres),'taker_matched':ntk,'taker_rows':len(tk)}
for k,d in sorted(ev.items()):
  v=list(d.values()); bs=sorted(sum(random.choice(v) for _ in v) for _ in range(2000))
  out[k]=dict(usd=round(usd[k]),pnl=round(sum(v)),pct=round(100*sum(v)/usd[k],2),events=len(v),boot90=[round(bs[100]),round(bs[1900])])
json.dump(out,sys.stdout,indent=1)
