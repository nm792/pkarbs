#!/usr/bin/env python3
"""Pull per-game player stats (player_rating, adr, kast, kills/deaths, equipment value) from bo3.gg for every match played by the teams in our paired maps
between WINDOW_START and 10 Nov 2026.  Endpoints: games?filter[games.match_id][eq]=ID  and  games/{game_id}/players_stats.  Output bo3_pstats.json: list of rows
{game, match, date, team_id, nick, rating, adr, kast, kills, deaths, eqv}."""
import sys, json, time, datetime as dt, urllib.request, urllib.parse, concurrent.futures as cf, re, unicodedata, difflib
B = 'https://api.bo3.gg/api/v1'; UA = 'Mozilla/5.0 (X11; Linux x86_64) Chrome/124 pkarbs-research'
def get(path, params=None):
    url = f'{B}/{path}' + ('?' + urllib.parse.urlencode(params) if params else '')
    for k in range(5):
        try: return json.load(urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': UA}), timeout=40))
        except urllib.error.HTTPError as e:
            if e.code == 404: return None
            time.sleep(1.5 ** k)
        except Exception: time.sleep(1.5 ** k)
    return None
M = json.load(open(sys.argv[1])); E = json.load(open(sys.argv[2])); TM = {t['id']: t for t in json.load(open(sys.argv[3]))}
START = dt.datetime.fromisoformat(sys.argv[5]).timestamp()
def norm(x):
    x = unicodedata.normalize('NFKD', x or '').encode('ascii', 'ignore').decode().lower(); return re.sub(r'[^a-z0-9]', '', x)
byname = {}
for t in TM.values(): byname.setdefault(norm(t['name']), []).append(t['id'])
names = set()
for v in E.values(): names.add(v['name_h']); names.add(v['name_a'])
tids = set()
for n in names:
    for tid in byname.get(norm(n), []): tids.add(tid)
ms = [m for m in M if (m['t1'] in tids or m['t2'] in tids) and START <= dt.datetime.fromisoformat(m['d']).timestamp() <= dt.datetime(2026, 11, 10, 12).timestamp()]
print('teams', len(tids), 'matches', len(ms), flush=True)
def one(m):
    out = []
    g = get('games', {'filter[games.match_id][eq]': m['id'], 'page[limit]': 10})
    for gm in (g or {}).get('results', []):
        if gm.get('state') != 'done': continue
        ps = get(f"games/{gm['id']}/players_stats") or []
        for p in ps:
            sp = p.get('steam_profile') or {}
            out.append(dict(game=gm['id'], match=m['id'], date=m['d'], team_id=(p.get('team_clan') or {}).get('team_id'), nick=sp.get('nickname'), pid=sp.get('player_id'),
                            rating=p.get('player_rating'), adr=p.get('adr'), kast=p.get('kast'), kills=p.get('kills'), deaths=p.get('death'), eqv=p.get('total_equipment_value'), map=gm.get('map_name')))
    return out
rows = []
with cf.ThreadPoolExecutor(10) as ex:
    for i, r in enumerate(ex.map(one, ms)):
        rows += r
        if i % 200 == 0: print(i, len(rows), flush=True)
json.dump(rows, open(sys.argv[4], 'w'))
print('player-game rows', len(rows))
