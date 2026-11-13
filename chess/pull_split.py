"""Chess sizing (8 Nov 2026): every resolved per-game chess event in gamma series 11480; all data-api v2 trades per market;
split pre-match / in-play by market gameStartTime (in-play = start..start+7h or closedTime if earlier); notional = size x price."""
import sys, os, json, gzip, time, datetime as dt, urllib.request, urllib.parse, collections
from concurrent.futures import ThreadPoolExecutor
HERE = os.path.dirname(os.path.abspath(__file__)); TD = f'{HERE}/raw/trades'; os.makedirs(TD, exist_ok=True)
def jget(url, p=None):
    if p: url += '?' + urllib.parse.urlencode(p)
    for k in range(4):
        try: return json.load(urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'pkarbs-research/1.0'}), timeout=40))
        except Exception: time.sleep(2 ** k)
def ts(s):
    if not s: return None
    s = s.replace(' ', 'T'); s = s.replace('+00', '+00:00') if s.endswith('+00') else s
    return int(dt.datetime.fromisoformat(s.replace('Z', '+00:00')).timestamp())
ev = []; off = 0
while True:
    d = jget('https://gamma-api.polymarket.com/events', {'series_id': 11480, 'closed': 'true', 'limit': 100, 'offset': off})
    if not d: break
    ev += d; off += 100
json.dump(ev, gzip.open(f'{HERE}/raw/events_series11480.json.gz', 'wt'))
def trades(c):
    fn = f'{TD}/{c}.json.gz'
    if os.path.exists(fn): return json.load(gzip.open(fn))
    p = {'condition': c, 'limit': 500}; out = []; cur = None
    for _ in range(300):
        if cur: p['cursor'] = cur
        d = jget('https://data-api.polymarket.com/v2/trades', p)
        if not d: break
        out += [(z['timestamp'], z['price'], z['size'], z['outcome_index'], z['side']) for z in d['data']]
        cur = d['pagination'].get('next_cursor')
        if not d['pagination'].get('has_more') or not cur: break
    json.dump(out, gzip.open(fn, 'wt')); return out
def one(e):
    r = collections.Counter(); mk = e['markets']
    for m in mk:
        t0 = ts(m.get('gameStartTime')) or ts(e.get('startTime')); 
        if not t0: continue
        t1 = min(t0 + 7 * 3600, ts(m.get('closedTime')) or 10**12)
        for t, p, s, oi, sd in trades(m['conditionId']):
            x = p * s
            if t < t0: r['pre'] += x
            elif t <= t1:
                r['inplay'] += x
                if 0.05 <= p <= 0.95: r['inplay_mid'] += x
            else: r['post'] += x
            r['n'] += 1
    return dict(r)
with ThreadPoolExecutor(8) as ex: res = list(ex.map(one, ev))
rows = []
for e, r in zip(ev, res):
    rows.append(dict(title=e['title'], start=(e['markets'][0].get('gameStartTime') or ''), gamma_vol=e.get('volume'), **r))
json.dump(rows, open(f'{HERE}/chess_events_split.json', 'w'), indent=1)
print(len(rows), sum(r.get('pre', 0) for r in rows), sum(r.get('inplay', 0) for r in rows))
