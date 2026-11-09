"""rn1's maker fills 22-29 Oct (activity + takerOnly set) in soccer, NBA and LoL markets, and the full market trade
lists WITH transaction hashes (data-api v2 lists one row per taker transaction; maker fills are inside it)."""
import sys, os, json, gzip, glob, collections, pickle
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common import jget, RAW
from concurrent.futures import ThreadPoolExecutor
M = pickle.load(open(f'{RAW}/M.pkl', 'rb'))
NOTSOC = {'atp','wta','itf','cs2','lol','dota2','val','cricket','ufc','boxing','mlbb','nhl','nba','mlb','nfl','cfb','cbb','wnba'}
def sport(slug, m):
    p = slug.split('-')[0]
    if p in ('nba', 'lol'): return p
    if p not in NOTSOC and (m.get('feeSchedule') or {}).get('rate') == 0.05: return 'soccer'
    return None
tk = set()
for f in glob.glob('/tmp/t7/trades7d/true_*.json'):
    for r in json.load(open(f))['rows']: tk.add(r['transactionHash'])
fills = []; seen = set()
for f in glob.glob('/tmp/t7/trades7d/false_*.json'):
    for r in json.load(open(f))['rows']:
        k = (r['transactionHash'], r['asset'], r['size'], r['price'], r['timestamp'])
        if k in seen or r['transactionHash'] in tk: continue
        seen.add(k); m = M.get(r['conditionId'])
        if not m: continue
        sp = sport(r['slug'], m)
        if sp: fills.append(dict(sport=sp, cond=r['conditionId'], oi=r['outcomeIndex'], price=r['price'], size=r['size'], ts=r['timestamp'], tx=r['transactionHash'], slug=r['slug'],
                                 gst=m.get('gameStartTime'), win=json.loads(m['outcomePrices'])))
print('rn1 maker fills', len(fills), collections.Counter(f['sport'] for f in fills))
os.makedirs(f'{RAW}/fillcheck/trades', exist_ok=True)
json.dump(fills, gzip.open(f'{RAW}/fillcheck/rn1_maker_fills_2026-10-22_29.json.gz', 'wt'))
conds = sorted({f['cond'] for f in fills})
def pull(c):
    fn = f'{RAW}/fillcheck/trades/{c}.json.gz'
    if os.path.exists(fn): return
    rows = []; cur = None
    for _ in range(800):
        p = {'condition': c, 'limit': 500}
        if cur: p['cursor'] = cur
        s, d = jget('https://data-api.polymarket.com/v2/trades', p)
        if s != 200 or not d: break
        rows += [{k: z[k] for k in ('timestamp', 'outcome_index', 'side', 'price', 'size', 'transaction_hash', 'proxy_wallet')} for z in d['data']]
        cur = d['pagination'].get('next_cursor')
        if not d['pagination'].get('has_more') or not cur: break
    json.dump(rows, gzip.open(fn, 'wt'))
print('markets', len(conds), flush=True)
with ThreadPoolExecutor(24) as ex: list(ex.map(pull, conds))
print('done')
