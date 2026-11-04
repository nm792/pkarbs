"""Pull closed Polymarket CS2 events (series 10310) with startTime Sep 1 - Nov 4 2026 from gamma (4 Nov)."""
import json, gzip, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import common as C
out = []; off = 0
while True:
    c, d = C.jget('https://gamma-api.polymarket.com/events', {'series_id': 10310, 'closed': 'true', 'limit': 100, 'offset': off,
                  'start_date_min': '2026-08-15', 'order': 'startTime', 'ascending': 'false'})
    if c != 200 or not d: break
    out += d; off += 100
    if len(d) < 100: break
out = [e for e in out if '2026-09-01' <= (e.get('startTime') or '') <= '2026-11-04T06']
os.makedirs(f'{C.RAW}/bo3', exist_ok=True)
json.dump(out, gzip.open(f'{C.RAW}/bo3/gamma_cs2_closed_2026-09-01_11-04.json.gz', 'wt'))
print(len(out), 'events', sum(e.get('volume') or 0 for e in out))
