"""Historical tennis moneylines for the trade-only check (5 Nov 2026): gamma ATP + WTA singles events starting
START..END, then all v2 trades from start-1 h to start+8 h -> raw/tennis/hist/trades/<cond>.json.gz."""
import sys, os, json, gzip, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from common import jget, RAW, pull_trades
from concurrent.futures import ThreadPoolExecutor
START, END = os.environ.get('START', '2026-10-05'), os.environ.get('END', '2026-11-02')
G = []
for lg, se in (('atp', 10365), ('wta', 10366)):
    off = 0
    while True:
        c, d = jget('https://gamma-api.polymarket.com/events', {'series_id': se, 'start_date_min': START + 'T00:00:00Z',
                    'start_date_max': END + 'T00:00:00Z', 'closed': 'true', 'limit': 100, 'offset': off})
        if c != 200 or not d: break
        G += [dict(league=lg, slug=e['slug'], title=e.get('title'), startTime=e.get('startTime'), volume=e.get('volume'),
                   markets=[{k: m.get(k) for k in ('conditionId', 'sportsMarketType', 'outcomes', 'outcomePrices', 'feeSchedule', 'question', 'volumeNum')}
                            for m in e.get('markets') or [] if m.get('sportsMarketType') == 'moneyline']) for e in d]
        off += 100
        if len(d) < 100 or off > 6000: break
G = [e for e in G if e['markets'] and e['startTime']]
os.makedirs(f'{RAW}/tennis/hist', exist_ok=True)
json.dump(G, gzip.open(f'{RAW}/tennis/hist/gamma_{START}_{END}.json.gz', 'wt'))
print(len(G), 'events', flush=True)
def job(e):
    t = dt.datetime.fromisoformat(e['startTime'].replace('Z', '+00:00')).timestamp()
    return len(pull_trades(e['markets'][0]['conditionId'], t - 3600, t + 8 * 3600, 'tennis/hist/trades'))
with ThreadPoolExecutor(16) as ex: n = list(ex.map(job, G))
print('trades', sum(n), 'markets with >=30 trades', sum(x >= 30 for x in n))
