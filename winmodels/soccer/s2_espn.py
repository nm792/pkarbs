"""Step 2: ESPN 'all soccer' scoreboards for the window, match to Polymarket base events, pull summaries."""
import sys, os, json, gzip, re, datetime as dt, difflib, collections
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common import jget, RAW
from concurrent.futures import ThreadPoolExecutor
E = json.load(gzip.open(f'{RAW}/soccer/gamma_events.json.gz'))
base = {e['slug']: e for e in E if sum(m.get('sportsMarketType') == 'moneyline' for m in e['markets']) == 3}
def ts(s): return dt.datetime.fromisoformat(s.replace('Z', '+00:00')).timestamp()
days = sorted({(dt.datetime.fromtimestamp(ts(e['startTime']), dt.timezone.utc) + dt.timedelta(days=k)).strftime('%Y%m%d') for e in base.values() for k in (-1, 0)})
def sb(day):
    c, d = jget('https://site.api.espn.com/apis/site/v2/sports/soccer/all/scoreboard', {'dates': day, 'limit': 1000})
    return d['events'] if d else []
with ThreadPoolExecutor(8) as ex: espn = [e for L in ex.map(sb, days) for e in L]
espn = list({e['id']: e for e in espn}.values())
json.dump(espn, gzip.open(f'{RAW}/soccer/espn_scoreboards.json.gz', 'wt'))
STOP = {'fc', 'cf', 'sc', 'ac', 'afc', 'cd', 'club', 'de', 'the', 'fk', 'sk', 'if', 'bk', 'ss', 'us', 'as', 'sv', 'vfl', 'vfb', 'rc', 'cr', 'ca', 'se', 'ec', 'real', 'united', 'city', 'sporting', 'atletico', 'deportivo'}
def norm(s):
    s = re.sub(r'[^a-z0-9 ]', ' ', s.lower().replace('&', ' '))
    import unicodedata
    return ' '.join(w for w in unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode().split() if w not in STOP)
def sim(a, b):
    a, b = norm(a), norm(b)
    if not a or not b: return 0
    if a in b or b in a: return 1.0
    return difflib.SequenceMatcher(None, a, b).ratio()
byt = collections.defaultdict(list)
for e in espn: byt[round(ts(e['date']) / 300)].append(e)
match = {}
for s, e in base.items():
    t = ts(e['startTime']); hm = [x['name'] for x in e['teams'] if x.get('ordering') == 'home']; aw = [x['name'] for x in e['teams'] if x.get('ordering') == 'away']
    if not hm or not aw: continue
    best = None
    for k in range(round(t / 300) - 4, round(t / 300) + 5):
        for x in byt.get(k, []):
            cs = x['competitions'][0]['competitors']
            H = [c['team']['displayName'] for c in cs if c['homeAway'] == 'home'][0]; A = [c['team']['displayName'] for c in cs if c['homeAway'] == 'away'][0]
            sc = sim(hm[0], H) + sim(aw[0], A); sw = sim(hm[0], A) + sim(aw[0], H)
            if max(sc, sw) >= 1.3 and (best is None or max(sc, sw) > best[0]): best = (max(sc, sw), x, sw > sc)
    if best: match[s] = dict(espn_id=best[1]['id'], swapped=best[2], score=round(best[0], 2), espn_name=best[1]['name'])
print('base events', len(base), 'matched', len(match), 'swapped', sum(v['swapped'] for v in match.values()))
def summ(eid):
    fn = f'{RAW}/soccer/summary/{eid}.json.gz'
    if os.path.exists(fn): return eid, True
    c, d = jget('https://site.api.espn.com/apis/site/v2/sports/soccer/all/summary', {'event': eid})
    if not d: return eid, False
    keep = {k: d.get(k) for k in ('keyEvents', 'header')}
    json.dump(keep, gzip.open(fn, 'wt')); return eid, True
os.makedirs(f'{RAW}/soccer/summary', exist_ok=True)
with ThreadPoolExecutor(12) as ex: ok = dict(ex.map(summ, [v['espn_id'] for v in match.values()]))
print('summaries ok', sum(ok.values()))
json.dump(match, open(f'{RAW}/soccer/match_pm_espn.json', 'w'), indent=0)
