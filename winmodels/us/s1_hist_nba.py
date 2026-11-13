"""Bigger NBA sample for the delay curve: 2025-26 season games we already have ESPN summaries for (raw/us_hist/nba,
every 2nd day) -> Polymarket gamma event by slug -> moneyline trades (data-api v2) for the game window.
Writes raw/us_nba_hist/gamma_events.json.gz, match.json, trades/<cond>.json.gz. All games are out of sample
for the rule (rule params were frozen on 22-27 Oct 2026 games)."""
import sys, os, json, gzip, glob, datetime as dt
from concurrent.futures import ThreadPoolExecutor
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))
from common import jget, RAW, pull_trades
AB = {'gs': ['gsw'], 'ny': ['nyk'], 'sa': ['sas'], 'no': ['nop'], 'utah': ['uta'], 'wsh': ['was'], 'phx': ['phx', 'pho'], 'bkn': ['bkn', 'bro']}
def ts(s): return dt.datetime.fromisoformat(s.replace('Z', '+00:00')).timestamp()
def find(g):
    t = ts(g['date']); a = g['comp']['away']['abbr'].lower(); h = g['comp']['home']['abbr'].lower()
    for off in (8, 0, 24):
        d = (dt.datetime.fromtimestamp(t, dt.timezone.utc) - dt.timedelta(hours=off)).strftime('%Y-%m-%d')
        for aa in AB.get(a, [a]):
            for hh in AB.get(h, [h]):
                c, e = jget('https://gamma-api.polymarket.com/events', {'slug': f'nba-{aa}-{hh}-{d}'})
                if c == 200 and e: return g, e[0]
    return g, None
OUT = f'{RAW}/us_nba_hist'; os.makedirs(OUT, exist_ok=True)
fs = sorted(glob.glob(f'{RAW}/us_hist/nba/*.json.gz'))
GS = [json.load(gzip.open(f)) for f in fs]; GS = [g for g in GS if g.get('completed') and len(g['tl']) > 50]
fn = f'{OUT}/gamma_events.json.gz'
if os.path.exists(fn):
    G = json.load(gzip.open(fn)); match = json.load(open(f'{OUT}/match.json'))
else:
    with ThreadPoolExecutor(12) as ex: R = list(ex.map(find, GS))
    G = [e for g, e in R if e]; match = {e['slug']: dict(sport='nba', espn_id=g['id']) for g, e in R if e}
    json.dump(G, gzip.open(fn, 'wt')); json.dump(match, open(f'{OUT}/match.json', 'w'), indent=0)
print('espn games', len(GS), 'matched PM events', len(G), flush=True)
jobs = []
for e in G:
    for m in e['markets']:
        if m.get('sportsMarketType') == 'moneyline' and e.get('startTime'):
            t = ts(e['startTime']); jobs.append((m['conditionId'], t))
print('moneyline markets', len(jobs), flush=True)
done = [0]
def job(j):
    pull_trades(j[0], j[1] - 1800, j[1] + 4 * 3600, 'us_nba_hist/trades'); done[0] += 1
    if done[0] % 25 == 0: print('trades pulled', done[0], flush=True)
with ThreadPoolExecutor(16) as ex: list(ex.map(job, jobs))
print('done')
