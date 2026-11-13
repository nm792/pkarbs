"""CS2 / Dota 2 / NBA events that ended after the server logger started (2 Nov 06:49Z): gamma events (with gameId,
which matches the Polymarket sports-websocket gameId in the logger) and all their trades."""
import sys, os, json, gzip
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common import jget, RAW, pull_trades
from concurrent.futures import ThreadPoolExecutor
SER = {'cs2': '10310', 'dota2': '10309', 'nba': '10345'}
out = {}
for sp, ser in SER.items():
    ev = []; off = 0
    while off < 2000:
        c, d = jget('https://gamma-api.polymarket.com/events', {'series_id': ser, 'end_date_min': '2026-11-02T06:00:00Z', 'end_date_max': '2026-11-04T00:00:00Z', 'limit': 100, 'offset': off})
        if c != 200 or not d: break
        ev += d; off += 100
        if len(d) < 100: break
    out[sp] = ev; print(sp, len(ev), 'events,', sum(1 for e in ev if e.get('gameId')), 'with gameId', flush=True)
os.makedirs(f'{RAW}/esports', exist_ok=True); json.dump(out, gzip.open(f'{RAW}/esports/gamma_events_2026-11-02_03.json.gz', 'wt'))
jobs = [(m['conditionId'],) for sp in out for e in out[sp] for m in e.get('markets', []) if m.get('closed')]
print('closed markets', len(jobs), flush=True)
with ThreadPoolExecutor(24) as ex: list(ex.map(lambda j: pull_trades(j[0], 0, 2e9, 'esports/trades'), jobs))
print('done')
