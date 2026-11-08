"""Step 3: data-api trades for every moneyline/totals/spreads/BTTS market of matched events, kickoff-30 min to +3 h."""
import sys, os, json, gzip, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common import pull_trades, RAW
from concurrent.futures import ThreadPoolExecutor
TYPES = {'moneyline', 'totals', 'spreads', 'both_teams_to_score'}
G = json.load(gzip.open(f'{RAW}/soccer/gamma_events.json.gz')); MT = json.load(open(f'{RAW}/soccer/match_pm_espn.json'))
jobs = []
for e in G:
    b = [s for s in MT if e['slug'] == s or e['slug'].startswith(s + '-')]
    if not b: continue
    t0 = dt.datetime.fromisoformat(e['startTime'].replace('Z', '+00:00')).timestamp() if e.get('startTime') else None
    for m in e['markets']:
        if m.get('sportsMarketType') in TYPES:
            st = m.get('gameStartTime'); t = dt.datetime.fromisoformat(st.replace(' ', 'T').replace('+00', '+00:00')).timestamp() if st else t0
            jobs.append((m['conditionId'], t))
print(len(jobs), flush=True)
def f(j): c, t = j; return len(pull_trades(c, t - 1800, t + 3 * 3600, 'soccer/trades'))
n = 0
with ThreadPoolExecutor(int(sys.argv[1]) if len(sys.argv) > 1 else 24) as ex:
    for k in ex.map(f, jobs):
        n += 1
        if n % 500 == 0: print(n, flush=True)
print('done', n)
