"""Closed sports events per league (gamma series), ending 20 Oct 00Z - 4 Nov 00Z 2026, WITH markets
(conditionId, volume, market type, gameStartTime, closedTime). Raw -> raw/inplay/events_2026-10-20_11-04.json.gz.
Used to rank leagues by IN-PLAY volume (thread "Rank sports by in-play volume", 4 Nov 2026)."""
import sys, os, json, gzip
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common import jget, RAW
from concurrent.futures import ThreadPoolExecutor
T0, T1 = '2026-10-20T00:00:00Z', '2026-11-04T00:00:00Z'
c, S = jget('https://gamma-api.polymarket.com/sports')
os.makedirs(f'{RAW}/inplay', exist_ok=True)
json.dump(S, gzip.open(f'{RAW}/inplay/gamma_sports_2026-11-04.json.gz', 'wt'))
MK = ('conditionId', 'volumeNum', 'sportsMarketType', 'gameStartTime', 'closedTime', 'question')
def pull(sp):
    out = []
    for ser in str(sp.get('series') or '').split(','):
        if not ser: continue
        off = 0
        while off < 5000:
            c, d = jget('https://gamma-api.polymarket.com/events', {'series_id': ser, 'closed': 'true', 'end_date_min': T0,
                                                                    'end_date_max': T1, 'limit': 100, 'offset': off})
            if c != 200 or not d: break
            for e in d:
                out.append(dict(league=sp['sport'], slug=e.get('slug'), volume=float(e.get('volume') or 0), startTime=e.get('startTime'),
                                gameId=e.get('gameId'), markets=[{k: m.get(k) for k in MK} for m in (e.get('markets') or [])]))
            if len(d) < 100: break
            off += 100
    return out
with ThreadPoolExecutor(12) as ex: E = [e for L in ex.map(pull, S) for e in L]
E = list({e['slug']: e for e in E}.values())
json.dump(E, gzip.open(f'{RAW}/inplay/events_2026-10-20_11-04.json.gz', 'wt'))
print(len(S), 'leagues', len(E), 'events')
