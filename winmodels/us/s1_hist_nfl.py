"""NFL 2025 season for the delay curve at TRUE event time (ESPN play wallclock): ESPN summaries already in
raw/us_hist/nfl (every day 4 Sep 2025 - 5 Jan 2026) -> Polymarket gamma event (series 10187, slug nfl-<away>-<home>-<ET date>)
-> moneyline trades (data-api v2) for the game window. Writes raw/us_nfl_hist/gamma_events.json.gz, match.json,
trades/<cond>.json.gz. (4 Nov 2026, thread "Rank sports by in-play volume".)"""
import sys, os, json, gzip, glob, datetime as dt
from concurrent.futures import ThreadPoolExecutor
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))
from common import jget, RAW, pull_trades
AB = {'wsh': 'was', 'lar': 'la'}
def ts(s): return dt.datetime.fromisoformat(s.replace('Z', '+00:00')).timestamp()
OUT = f'{RAW}/us_nfl_hist'; os.makedirs(OUT, exist_ok=True)
fn = f'{OUT}/gamma_series_10187.json.gz'
if os.path.exists(fn): S = json.load(gzip.open(fn))
else:
    S = []; off = 0
    while True:
        c, d = jget('https://gamma-api.polymarket.com/events', {'series_id': 10187, 'closed': 'true', 'limit': 100, 'offset': off})
        if c != 200 or not d: break
        S += d; off += 100
        if len(d) < 100: break
    json.dump(S, gzip.open(fn, 'wt'))
bys = {e['slug']: e for e in S}
GS = [json.load(gzip.open(f)) for f in sorted(glob.glob(f'{RAW}/us_hist/nfl/*.json.gz'))]
GS = [g for g in GS if g.get('completed') and len(g['tl']) > 50]
G = []; match = {}
for g in GS:
    a = g['comp']['away']['abbr'].lower(); h = g['comp']['home']['abbr'].lower(); a, h = AB.get(a, a), AB.get(h, h)
    t = ts(g['date'])
    for off in (5, 0, 24):
        d = (dt.datetime.fromtimestamp(t, dt.timezone.utc) - dt.timedelta(hours=off)).strftime('%Y-%m-%d')
        e = bys.get(f'nfl-{a}-{h}-{d}')
        if e: G.append(e); match[e['slug']] = dict(sport='nfl', espn_id=g['id']); break
json.dump(G, gzip.open(f'{OUT}/gamma_events.json.gz', 'wt')); json.dump(match, open(f'{OUT}/match.json', 'w'), indent=0)
print('series events', len(S), 'espn games', len(GS), 'matched', len(G), flush=True)
jobs = [(m['conditionId'], ts(e['startTime'])) for e in G if e.get('startTime') for m in e['markets'] if m.get('sportsMarketType') == 'moneyline']
print('moneyline markets', len(jobs), flush=True)
done = [0]
def job(j):
    pull_trades(j[0], j[1] - 1800, j[1] + 4.5 * 3600, 'us_nfl_hist/trades'); done[0] += 1
    if done[0] % 25 == 0: print('trades pulled', done[0], flush=True)
with ThreadPoolExecutor(16) as ex: list(ex.map(job, jobs))
print('done')
