#!/usr/bin/env python3
"""Pull ALL finished bo3.gg CS2 matches (whole history) and the teams table. Output bo3_matches.json (compact) and bo3_teams.json. Read-only public API."""
import json, sys, time, urllib.request, urllib.parse, concurrent.futures as cf
B = 'https://api.bo3.gg/api/v1'; UA = 'Mozilla/5.0 (X11; Linux x86_64) Chrome/124 pkarbs-research'
def get(path, params):
    url = f'{B}/{path}?' + urllib.parse.urlencode(params)
    for k in range(6):
        try: return json.load(urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': UA}), timeout=60))
        except Exception: time.sleep(1.5 ** k)
    return None
def page(off):
    d = get('matches', {'filter[matches.status][eq]': 'finished', 'filter[matches.discipline_id][eq]': 1, 'sort': 'start_date', 'page[limit]': 100, 'page[offset]': off})
    if not d: return off, None
    return off, [dict(id=m['id'], t1=m['team1_id'], t2=m['team2_id'], w=m['winner_team_id'], s1=m['team1_score'], s2=m['team2_score'], bo=m['bo_type'], d=m['start_date'], tier=m.get('tier'), tour=m.get('tournament_id')) for m in d['results']]
def tpage(off):
    d = get('teams', {'page[limit]': 100, 'page[offset]': off})
    return off, None if not d else [dict(id=t['id'], name=t['name'], rank=t.get('rank'), slug=t['slug']) for t in d['results']]
first = get('matches', {'filter[matches.status][eq]': 'finished', 'filter[matches.discipline_id][eq]': 1, 'page[limit]': 1})
N = first['total']['count']; print('matches', N, flush=True)
out = {}
with cf.ThreadPoolExecutor(8) as ex:
    for i, (off, r) in enumerate(ex.map(page, range(0, N + 100, 100))):
        out[off] = r
        if i % 50 == 0: print(i, flush=True)
bad = [o for o, r in out.items() if r is None]
ms = [m for o in sorted(out) if out[o] for m in out[o]]
json.dump(ms, open(sys.argv[1], 'w')); print('matches saved', len(ms), 'bad pages', len(bad), flush=True)
tn = get('teams', {'page[limit]': 1})['total']['count']; teams = []
with cf.ThreadPoolExecutor(8) as ex:
    for off, r in ex.map(tpage, range(0, tn + 100, 100)):
        if r: teams += r
json.dump(teams, open(sys.argv[2], 'w')); print('teams', len(teams))
