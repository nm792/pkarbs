# Trades (data-api v2) for "Match Winner" markets of matched events, from 30 min before game 1 to 10 min after the last game.
import json, gzip, os, re, datetime as dt
from concurrent.futures import ThreadPoolExecutor
from pull_frames import jget
E = json.load(gzip.open('raw/pm/gamma_lol_events_closed.json.gz'))
X = json.load(open('raw/pm/pm_game_markets_matched.json'))
by = {}
for x in X: by.setdefault(x['title'], []).append(x)
ts = lambda z: int(dt.datetime.fromisoformat(z[:19] + '+00:00').timestamp())
jobs = []
for e in E:
    if e['title'] not in by: continue
    mw = [m for m in e['markets'] if (m.get('groupItemTitle') or '') == 'Match Winner']
    if not mw: continue
    gs = by[e['title']]; tt = []
    for g in gs:
        f = f"raw/bt/{g['gid']}/frames.json.gz"
        if os.path.exists(f):
            fr = json.load(gzip.open(f)); tt += [ts(fr[0]['t']), ts(fr[-1]['t'])]
    if not tt: continue
    m = mw[0]; jobs.append(dict(title=e['title'], match_id=gs[0]['match_id'], condition=m['conditionId'], outcomes=json.loads(m['outcomes']),
                                prices=json.loads(m['outcomePrices']), start=min(tt) - 1800, end=max(tt) + 600))
os.makedirs('raw/series', exist_ok=True); json.dump(jobs, open('raw/series/series_markets.json', 'w'))
def pull(j):
    out = f"raw/series/{j['match_id']}_trades.json.gz"
    if os.path.exists(out): return 'cached'
    p = {'condition': j['condition'], 'limit': 500, 'start': j['start'], 'end': j['end']}; allt = []; cur = None
    for _ in range(600):
        if cur: p['cursor'] = cur
        c, d = jget('https://data-api.polymarket.com/v2/trades', p)
        if c != 200 or not d: break
        allt += [{k: z[k] for k in ('timestamp', 'outcome', 'side', 'price', 'size')} for z in d['data']]
        cur = d['pagination'].get('next_cursor')
        if not d['pagination'].get('has_more') or not cur: break
    json.dump(allt, gzip.open(out, 'wt')); return len(allt)
with ThreadPoolExecutor(16) as ex:
    for i, r in enumerate(ex.map(pull, jobs)): print(i, r, flush=True)
