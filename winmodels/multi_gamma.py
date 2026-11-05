"""Pull closed Polymarket game events (moneyline markets) for 8 sports, 16 Oct - 5 Nov 2026, by gamma series.
-> winmodels/raw/multi/gamma_<sport>.json.gz"""
import os, sys, json, gzip, time, urllib.parse, urllib.request
from concurrent.futures import ThreadPoolExecutor
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, 'raw', 'multi')
def get(url, p={}):
    req = urllib.request.Request(url + ('?' + urllib.parse.urlencode(p) if p else ''), headers={'User-Agent': 'pkarbs-research/1.0'})
    for a in range(3):
        try:
            with urllib.request.urlopen(req, timeout=60) as r: return json.loads(r.read())
        except Exception as e: time.sleep(3 * (a + 1))
    return []
S = get('https://gamma-api.polymarket.com/sports'); json.dump(S, gzip.open(f'{OUT}/gamma_sports.json.gz', 'wt'))
def group(s):
    k = s.get('sport', '')
    if k in ('nba', 'nhl', 'nfl', 'lol', 'cs2'): return k
    if k == 'dota2': return 'dota'
    if k.startswith('cr'): return 'cricket'
    if k.startswith('ru'): return 'rugby'
SER = {}
for s in S:
    g = group(s)
    if g:
        for ser in str(s.get('series') or '').split(','):
            if ser: SER.setdefault(g, set()).add(ser)
def pull(ser):
    out, off = [], 0
    while off < 3000:
        ev = get('https://gamma-api.polymarket.com/events', dict(series_id=ser, closed='true', limit=100, offset=off,
                 end_date_min='2026-10-16T00:00:00Z', end_date_max='2026-11-06T00:00:00Z'))
        if not ev: break
        for e in ev:
            ms = [m for m in e.get('markets', []) if m.get('sportsMarketType') == 'moneyline']
            if ms: out.append(dict(slug=e['slug'], title=e.get('title'), startTime=e.get('startTime') or e.get('startDate'), volume=e.get('volume'),
                                   markets=[{k: m.get(k) for k in ('conditionId', 'outcomes', 'outcomePrices', 'sportsMarketType', 'question', 'volume', 'feeSchedule', 'gameStartTime')} for m in ms]))
        if len(ev) < 100: break
        off += 100
    return out
for g, sers in SER.items():
    with ThreadPoolExecutor(8) as ex: E = [e for L in ex.map(pull, sorted(sers)) for e in L]
    E = list({e['slug']: e for e in E}.values())
    json.dump(E, gzip.open(f'{OUT}/gamma_{g}.json.gz', 'wt')); print(g, len(sers), 'series', len(E), 'events', flush=True)
