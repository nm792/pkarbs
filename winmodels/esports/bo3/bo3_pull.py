"""Pull bo3.gg CS2 matches, games (maps) and per-round data (4 Nov 2026). Raw JSON saved under winmodels/raw/bo3/.
bo3.gg rounds carry round_number, winner/score and round_duration (ns), NOT absolute timestamps; map begin_at is absolute."""
import os, sys, json, gzip, time, urllib.request, urllib.parse
B = 'https://api.bo3.gg/api/v1'; UA = 'Mozilla/5.0 (X11; Linux x86_64) Chrome/124 pkarbs-research'
RAW = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'raw', 'bo3')
os.makedirs(RAW, exist_ok=True)
def get(path, params=None):
    url = f'{B}/{path}' + ('?' + urllib.parse.urlencode(params) if params else '')
    for k in range(5):
        try:
            return json.load(urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': UA}), timeout=40))
        except urllib.error.HTTPError as e:
            if e.code == 404: return None
            time.sleep(2 ** k)
        except Exception: time.sleep(2 ** k)
    return None
def matches(since, until):
    out = []; off = 0
    while True:
        d = get('matches', {'filter[matches.status][eq]': 'finished', 'filter[matches.discipline_id][eq]': 1,
                            'filter[matches.start_date][gt]': since, 'filter[matches.start_date][lt]': until,
                            'sort': '-start_date', 'page[limit]': 100, 'page[offset]': off})
        if not d or not d['results']: break
        out += d['results']; off += 100
        if off >= d['total']['count']: break
    return out
def games(mid):
    fn = f'{RAW}/games/{mid}.json.gz'
    if os.path.exists(fn): return json.load(gzip.open(fn))
    d = get('games', {'filter[games.match_id][eq]': mid, 'page[limit]': 10}) or {'results': []}
    gs = []
    for g in d['results']:
        r = get(f"games/{g['id']}/rounds") or {}
        g['game_rounds'] = r.get('game_rounds') or []
        gs.append(g)
    if all(g['game_rounds'] for g in gs if g.get('status') == 'finished'):
        os.makedirs(f'{RAW}/games', exist_ok=True); json.dump(gs, gzip.open(fn, 'wt'))
    return gs
if __name__ == '__main__':
    since, until = sys.argv[1], sys.argv[2]
    ms = matches(since, until)
    json.dump(ms, gzip.open(f'{RAW}/matches_{since[:10]}_{until[:10]}.json.gz', 'wt'))
    print(len(ms), 'matches')
