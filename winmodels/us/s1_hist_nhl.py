"""NHL history for the event-only delay curve at true event time (5 Nov 2026, thread "Time NHL feed against the price").
ESPN summaries: raw/us_hist/nhl (2025-26, every 2nd day, from pull_hist.py) + every day 1 Oct-4 Nov 2026 (pulled here).
Polymarket: gamma series 10346 (closed), matched to ESPN by start time (+-3 h) and team nicknames; moneyline trades
(data-api v2) for each matched game. Writes raw/us_nhl_hist/gamma_events.json.gz, match.json, trades/<cond>.json.gz."""
import sys, os, json, gzip, glob, re, datetime as dt
from concurrent.futures import ThreadPoolExecutor
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
from common import jget, RAW, pull_trades
from espn import scoreboard, summary
def ts(s): return dt.datetime.fromisoformat(s.replace('Z', '+00:00')).timestamp()
def nz(s): return re.sub(r'[^a-z0-9]', '', (s or '').lower())
OUT = f'{RAW}/us_nhl_hist'; os.makedirs(OUT, exist_ok=True)
# 1) current season ESPN summaries, every day
a = dt.date(2026, 10, 1); days = [(a + dt.timedelta(days=k)).strftime('%Y%m%d') for k in range((dt.date(2026, 11, 4) - a).days + 1)]
with ThreadPoolExecutor(8) as ex: evs = [e for L in ex.map(lambda d: scoreboard('nhl', d), days) for e in L]
ids = sorted({e['id'] for e in evs if e['competitions'][0]['status']['type'].get('completed')})
with ThreadPoolExecutor(12) as ex: n = sum(1 for s in ex.map(lambda i: summary('nhl', i, 'us_hist'), ids) if s)
print('2026-27 espn games', len(ids), 'summaries', n, flush=True)
# 2) gamma series
fn = f'{OUT}/gamma_series_10346.json.gz'
if os.path.exists(fn): S = json.load(gzip.open(fn))
else:
    S = []; off = 0
    while True:
        c, d = jget('https://gamma-api.polymarket.com/events', {'series_id': 10346, 'closed': 'true', 'limit': 100, 'offset': off})
        if c != 200 or not d: break
        S += d; off += 100
        if len(d) < 100: break
    json.dump(S, gzip.open(fn, 'wt'))
S = [e for e in S if e.get('startTime') and e.get('teams') and len(e['teams']) == 2]
print('series events with teams', len(S), flush=True)
# 3) match
GS = [json.load(gzip.open(f)) for f in sorted(glob.glob(f'{RAW}/us_hist/nhl/*.json.gz'))]
GS = [g for g in GS if g.get('completed') and len(g['tl']) > 20]
G = []; match = {}
for g in GS:
    t = ts(g['date']); hn, an = nz(g['comp']['home']['name']), nz(g['comp']['away']['name'])
    for e in S:
        if abs(ts(e['startTime']) - t) > 3 * 3600: continue
        tm = {x['ordering']: nz(x['name']) for x in e['teams']}
        if tm.get('home') and tm.get('away') and tm['home'] in hn and tm['away'] in an:
            G.append(e); match[e['slug']] = dict(sport='nhl', espn_id=g['id']); break
json.dump(G, gzip.open(f'{OUT}/gamma_events.json.gz', 'wt')); json.dump(match, open(f'{OUT}/match.json', 'w'), indent=0)
print('espn games', len(GS), 'matched', len(G), flush=True)
jobs = [(m['conditionId'], ts(e['startTime'])) for e in G for m in e['markets'] if m.get('sportsMarketType') == 'moneyline']
print('moneyline markets', len(jobs), flush=True)
done = [0]
def job(j):
    pull_trades(j[0], j[1] - 1800, j[1] + 4.5 * 3600, 'us_nhl_hist/trades'); done[0] += 1
    if done[0] % 50 == 0: print('trades pulled', done[0], flush=True)
with ThreadPoolExecutor(16) as ex: list(ex.map(job, jobs))
print('done')
