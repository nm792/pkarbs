"""All closed Polymarket events ending 22 Oct - 2 Nov 2026 (gamma), for volume by sport/league."""
import sys, os, json, gzip
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common import jget, RAW
out = []; off = 0
while True:
    c, d = jget('https://gamma-api.polymarket.com/events', {'closed': 'true', 'end_date_min': '2026-10-22T02:00:00Z', 'end_date_max': '2026-11-02T06:00:00Z', 'limit': 100, 'offset': off})
    if c != 200 or not d: break
    out += [{k: e.get(k) for k in ('slug', 'volume', 'startTime', 'endDate', 'gameId', 'seriesSlug', 'sport')} for e in d]
    off += 100
    if len(d) < 100: break
os.makedirs(f'{RAW}/rank', exist_ok=True); json.dump(out, gzip.open(f'{RAW}/rank/gamma_closed_events_2026-10-22_11-02.json.gz', 'wt'))
print(len(out))
