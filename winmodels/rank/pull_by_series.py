"""Closed events per sports league (gamma /sports series), ending 22 Oct 02Z - 2 Nov 06Z 2026: volume per league."""
import sys, os, json, gzip
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common import jget, RAW
from concurrent.futures import ThreadPoolExecutor
c, S = jget('https://gamma-api.polymarket.com/sports')
json.dump(S, gzip.open(f'{RAW}/rank/gamma_sports.json.gz', 'wt'))
def pull(sp):
    out = []
    for ser in str(sp.get('series') or '').split(','):
        if not ser: continue
        off = 0
        while off < 3000:
            c, d = jget('https://gamma-api.polymarket.com/events', {'series_id': ser, 'closed': 'true', 'end_date_min': '2026-10-22T02:00:00Z',
                                                                    'end_date_max': '2026-11-02T06:00:00Z', 'limit': 100, 'offset': off})
            if c != 200 or not d: break
            out += [dict(league=sp['sport'], slug=e.get('slug'), volume=float(e.get('volume') or 0), startTime=e.get('startTime'), gameId=e.get('gameId'),
                         nmk=len(e.get('markets') or [])) for e in d]
            if len(d) < 100: break
            off += 100
    return out
with ThreadPoolExecutor(12) as ex: E = [e for L in ex.map(pull, S) for e in L]
E = list({e['slug']: e for e in E}.values())
json.dump(E, gzip.open(f'{RAW}/rank/gamma_events_by_league_2026-10-22_11-02.json.gz', 'wt'))
print(len(S), 'leagues', len(E), 'events')
