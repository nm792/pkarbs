# Match closed Polymarket LoL "Game N Winner" markets to lolesports games (team names + date).
import json, re, datetime as dt
def norm(s): return re.sub(r'[^a-z0-9]', '', s.lower().replace('esports', '').replace('gaming', '').replace('team', ''))
def ts(s): return dt.datetime.fromisoformat(s.replace('Z', '+00:00').replace(' ', 'T').replace('+00', '+00:00') if s.endswith('+00') else s.replace('Z', '+00:00')).timestamp()
import gzip; E = json.load(gzip.open('raw/pm/gamma_lol_events_closed.json.gz'))
L = json.load(open('raw/matches_since2026-04_names.json'))
idx = {}
for m in L:
    if 'names' not in m or not m.get('games'): continue
    idx.setdefault(frozenset(norm(n) for n in m['names']), []).append(m)
out = []; nomatch = 0
for e in E:
    if not e['slug'].startswith('lol-'): continue
    for mk in e['markets']:
        g = re.match(r'Game (\d) Winner', mk.get('groupItemTitle') or '')
        if not g or not mk.get('gameStartTime'): continue
        oc = json.loads(mk['outcomes']); op = json.loads(mk['outcomePrices'])
        if len(oc) != 2 or sorted(op) != ['0', '1']: continue
        key = frozenset(norm(n) for n in oc)
        t = ts(mk['gameStartTime'])
        cands = [m for m in idx.get(key, []) if abs(ts(m['start']) - t) < 36 * 3600]
        if len(cands) != 1: nomatch += 1; continue
        m = cands[0]; gg = [x for x in m['games'] if x['number'] == int(g.group(1))]
        if not gg: nomatch += 1; continue
        name_by_id = {tid: m['names'][[c for c, _ in m['teams']].index(code)] for tid, code in m['team_ids'].items() if code in [c for c, _ in m['teams']]}
        out.append(dict(match_id=m['match_id'], league=m['league'], gid=gg[0]['id'], game=int(g.group(1)), start=m['start'],
                        condition=mk['conditionId'], outcomes=oc, winner=oc[op.index('1')], tokens=json.loads(mk['clobTokenIds']),
                        blue_name=name_by_id.get(gg[0]['sides'].get('blue')), volume=float(mk.get('volumeNum') or mk.get('volume') or 0), title=e['title']))
json.dump(out, open('raw/pm/pm_game_markets_matched.json', 'w'), indent=0)
import collections
print('matched', len(out), 'unmatched', nomatch)
print(collections.Counter(o['league'] for o in out))
v = sorted(o['volume'] for o in out); print('volume median', v[len(v)//2] if v else None, 'total', round(sum(v)))
