"""NFL 2026 season to date (10 Sep - 3 Nov 2026): ESPN summaries -> raw/us_hist26/nfl; Polymarket series 12185 (nfl-2026)
gamma events -> raw/us_nfl26_hist/gamma_events.json.gz, match.json; moneyline trades -> raw/us_nfl26_hist/trades/.
Same layout as us/s1_hist_nfl.py so us/us_delay_hist.py runs on it with YEAR=26. (5 Nov 2026, thread "Measure NFL feed speed and value".)"""
import sys, os, json, gzip, glob, datetime as dt
from concurrent.futures import ThreadPoolExecutor
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, os.path.join(os.path.dirname(HERE), 'us'))
from common import jget, RAW, pull_trades
from espn import scoreboard, summary
AB = {'wsh': 'was', 'lar': 'la'}
def ts(s): return dt.datetime.fromisoformat(s.replace('Z', '+00:00')).timestamp()
a, b = dt.date(2026, 9, 9), dt.date(2026, 11, 3)
days = [(a + dt.timedelta(days=k)).strftime('%Y%m%d') for k in range((b - a).days + 1)]
with ThreadPoolExecutor(8) as ex: evs = [e for L in ex.map(lambda d: scoreboard('nfl', d), days) for e in L]
ids = sorted({e['id'] for e in evs if e['competitions'][0]['status']['type'].get('completed')})
print('espn games', len(ids), flush=True)
with ThreadPoolExecutor(12) as ex: list(ex.map(lambda i: summary('nfl', i, 'us_hist26'), ids))
OUT = f'{RAW}/us_nfl26_hist'; os.makedirs(OUT, exist_ok=True)
S = []; off = 0
while True:
    c, d = jget('https://gamma-api.polymarket.com/events', {'series_id': 12185, 'closed': 'true', 'limit': 100, 'offset': off})
    if c != 200 or not d: break
    S += d; off += 100
    if len(d) < 100: break
json.dump(S, gzip.open(f'{OUT}/gamma_series_12185.json.gz', 'wt'))
bys = {e['slug']: e for e in S}
GS = [json.load(gzip.open(f)) for f in sorted(glob.glob(f'{RAW}/us_hist26/nfl/*.json.gz'))]
GS = [g for g in GS if g.get('completed') and len(g['tl']) > 50]
G = []; match = {}
for g in GS:
    aa = g['comp']['away']['abbr'].lower(); h = g['comp']['home']['abbr'].lower(); aa, h = AB.get(aa, aa), AB.get(h, h)
    t = ts(g['date'])
    for o in (5, 0, 24, -19):
        d = (dt.datetime.fromtimestamp(t, dt.timezone.utc) - dt.timedelta(hours=o)).strftime('%Y-%m-%d')
        e = bys.get(f'nfl-{aa}-{h}-{d}')
        if e: G.append(e); match[e['slug']] = dict(sport='nfl', espn_id=g['id']); break
    else: print('no PM match', aa, h, g['date'])
json.dump(G, gzip.open(f'{OUT}/gamma_events.json.gz', 'wt')); json.dump(match, open(f'{OUT}/match.json', 'w'), indent=0)
print('series events', len(S), 'espn games', len(GS), 'matched', len(G), flush=True)
jobs = [(m['conditionId'], ts(e['startTime'])) for e in G if e.get('startTime') for m in e['markets'] if m.get('sportsMarketType') == 'moneyline']
print('moneyline markets', len(jobs), flush=True)
with ThreadPoolExecutor(16) as ex: list(ex.map(lambda j: pull_trades(j[0], j[1] - 1800, j[1] + 4.5 * 3600, 'us_nfl26_hist/trades'), jobs))
print('done')
