"""Step 1: soccer events in rn1's 22 Oct - 2 Nov universe -> full gamma event objects (all markets)."""
import sys, os, json, gzip, pickle, collections
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common import jget, RAW
from concurrent.futures import ThreadPoolExecutor
NOT = {'atp','wta','itf','cs2','lol','dota2','val','cricket','ufc','boxing','mlbb','nhl','nba','mlb','nfl','cfb','cbb','wnba'}
M = pickle.load(open(f'{RAW}/M.pkl', 'rb'))
slugs = sorted({m['events'][0]['slug'] for m in M.values() if (m.get('feeSchedule') or {}).get('rate') == 0.05
                and m['slug'].split('-')[0] not in NOT and m.get('sportsMarketType') in ('moneyline','totals','soccer_exact_score','spreads','both_teams_to_score')})
print(len(slugs))
def get(s):
    c, d = jget('https://gamma-api.polymarket.com/events', {'slug': s})
    return d[0] if c == 200 and d else None
with ThreadPoolExecutor(16) as ex: evs = [e for e in ex.map(get, slugs) if e]
os.makedirs(f'{RAW}/soccer', exist_ok=True)
json.dump(evs, gzip.open(f'{RAW}/soccer/gamma_events.json.gz', 'wt'))
print(len(evs), collections.Counter(m.get('sportsMarketType') for e in evs for m in e['markets']).most_common())
