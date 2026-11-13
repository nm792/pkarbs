"""Backtest set: Polymarket NBA/NFL/CFB/NHL events in rn1's 22 Oct - 2 Nov universe -> gamma events, ESPN match, summaries, trades."""
import sys, os, json, gzip, pickle, collections, datetime as dt, re, difflib
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common import jget, RAW, pull_trades
from espn import scoreboard, summary
from concurrent.futures import ThreadPoolExecutor
SP = ('nba', 'nfl', 'cfb', 'nhl')
M = pickle.load(open(f'{RAW}/M.pkl', 'rb'))
slugs = sorted({m['events'][0]['slug'] for m in M.values() if m['slug'].split('-')[0] in SP})
print(len(slugs), flush=True)
def get(s):
    c, d = jget('https://gamma-api.polymarket.com/events', {'slug': s}); return d[0] if c == 200 and d else None
fn = f'{RAW}/us/gamma_events.json.gz'
if os.path.exists(fn): G = json.load(gzip.open(fn))
else:
    with ThreadPoolExecutor(16) as ex: G = [e for e in ex.map(get, slugs) if e]
    os.makedirs(f'{RAW}/us', exist_ok=True); json.dump(G, gzip.open(fn, 'wt'))
base = [e for e in G if any(m.get('sportsMarketType') == 'moneyline' for m in e['markets']) and e.get('startTime')]
print('events with moneyline', len(base), collections.Counter(e['slug'].split('-')[0] for e in base))
def ts(s): return dt.datetime.fromisoformat(s.replace('Z', '+00:00')).timestamp()
def norm(s): return re.sub(r'[^a-z0-9]', '', (s or '').lower())
match = {}
for sp in SP:
    B = [e for e in base if e['slug'].startswith(sp + '-')]
    days = sorted({(dt.datetime.fromtimestamp(ts(e['startTime']), dt.timezone.utc) + dt.timedelta(hours=h)).strftime('%Y%m%d') for e in B for h in (-12, 0)})
    with ThreadPoolExecutor(8) as ex: ES = [x for L in ex.map(lambda d: scoreboard(sp, d), days) for x in L]
    ES = list({x['id']: x for x in ES}.values())
    for e in B:
        t = ts(e['startTime']); tm = {x.get('ordering'): x for x in e.get('teams', [])}
        if 'home' not in tm or 'away' not in tm: continue
        best = None
        for x in ES:
            if abs(ts(x['date']) - t) > 3 * 3600: continue
            cs = {c['homeAway']: c['team'] for c in x['competitions'][0]['competitors']}
            sc = 0
            for ha in ('home', 'away'):
                a = norm(tm[ha].get('name')); b = norm(cs[ha].get('displayName')); ab = norm(tm[ha].get('abbreviation')) == norm(cs[ha].get('abbreviation'))
                sc += 1 if (ab or (a and b and (a in b or b in a))) else difflib.SequenceMatcher(None, a, b).ratio()
            if sc >= 1.5 and (best is None or sc > best[0]): best = (sc, x)
        if best: match[e['slug']] = dict(sport=sp, espn_id=best[1]['id'], espn_name=best[1]['name'])
print('matched', len(match), collections.Counter(v['sport'] for v in match.values()), flush=True)
json.dump(match, open(f'{RAW}/us/match_pm_espn.json', 'w'), indent=0)
with ThreadPoolExecutor(12) as ex: list(ex.map(lambda v: summary(v['sport'], v['espn_id'], 'us_bt'), match.values()))
jobs = []
for e in base:
    if e['slug'] not in match: continue
    t = ts(e['startTime'])
    for m in e['markets']:
        if m.get('sportsMarketType') in ('moneyline', 'spreads', 'totals'): jobs.append((m['conditionId'], t))
print('markets', len(jobs), flush=True)
with ThreadPoolExecutor(24) as ex: list(ex.map(lambda j: pull_trades(j[0], j[1] - 1800, j[1] + 4.5 * 3600, 'us/trades'), jobs))
print('done')
