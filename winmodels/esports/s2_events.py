"""CS2 events 2 Nov 06:00Z - 4 Nov 12:00Z (logger window): gamma events with gameId + all trades of closed markets (v2)."""
import sys, os, json, gzip
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common import jget, RAW, pull_trades
from concurrent.futures import ThreadPoolExecutor
ev = []; off = 0
while off < 3000:
    c, d = jget('https://gamma-api.polymarket.com/events', {'series_id': '10310', 'end_date_min': '2026-11-02T06:00:00Z', 'end_date_max': '2026-11-04T12:00:00Z', 'limit': 100, 'offset': off})
    if c != 200 or not d: break
    ev += d; off += 100
    if len(d) < 100: break
print('cs2', len(ev), 'events,', sum(1 for e in ev if e.get('gameId')), 'with gameId', flush=True)
json.dump({'cs2': ev}, gzip.open(f'{RAW}/esports/gamma_cs2_2026-11-02_04.json.gz', 'wt'))
jobs = [m['conditionId'] for e in ev for m in e.get('markets', []) if m.get('closed')]
print('closed markets', len(jobs), flush=True)
with ThreadPoolExecutor(16) as ex: list(ex.map(lambda j: pull_trades(j, 0, 2e9, 'esports/trades'), jobs))
print('done')
