"""Link closed Polymarket CS2 events (Sep 1 - Nov 4) to bo3.gg matches by team names + start time; pull bo3 games+rounds
for linked matches. Output: raw/bo3/links.json.gz [{event fields subset, bo3 match id}]"""
import json, gzip, re, sys, datetime as dt
import bo3_pull as b
def ts(s): return dt.datetime.fromisoformat(s.replace('Z', '+00:00')).timestamp()
def norm(s): return re.sub(r'[^a-z0-9]', '', (s or '').lower().replace('esports', '').replace('team', '').replace('gaming', '').replace('cs2', '').replace('csgo', ''))
E = json.load(gzip.open(f'{b.RAW}/gamma_cs2_closed_2026-09-01_11-04.json.gz'))
ms = json.load(gzip.open(f'{b.RAW}/matches_2026-09-01_2026-11-04.json.gz'))
ms = [m for m in ms if m['parsed_status'] == 'done']
def hit(name, slug):
    n = norm(name)
    return len(n) >= 2 and (n[:6] in slug or slug.find(n[:4]) >= 0 and len(n) <= 5)
out = []
for e in E:
    if not e.get('teams') or len(e['teams']) != 2 or not e.get('startTime'): continue
    mk = [m for m in e['markets'] if m.get('closed') and (m.get('groupItemTitle') or '') in ('Match Winner', 'Map 1 Winner', 'Map 2 Winner', 'Map 3 Winner')]
    vol = sum(float(m.get('volumeNum') or m.get('volume') or 0) for m in mk)
    if vol < 2000: continue
    st = ts(e['startTime'])
    c = [m for m in ms if abs(ts(m['start_date']) - st) < 8 * 3600 and all(hit(t['name'], norm(m['slug'])) for t in e['teams'])]
    if len(c) != 1: continue
    out.append(dict(id=e['id'], title=e['title'], startTime=e['startTime'], gameId=e.get('gameId'), teams=[t['name'] for t in e['teams']],
                    vol=vol, bo3=c[0]['id'], bo3_slug=c[0]['slug'], tier=c[0]['tier'],
                    markets=[{k: v for k, v in m.items() if k not in ('description', 'image', 'icon')} for m in mk]))
print(len(out), 'linked events; vol', round(sum(o['vol'] for o in out)))
json.dump(out, gzip.open(f'{b.RAW}/links.json.gz', 'wt'))
for i, o in enumerate(sorted(out, key=lambda o: -o['vol'])):
    b.games(o['bo3'])
    if i % 50 == 0: print(i, flush=True)
