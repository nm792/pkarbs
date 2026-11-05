"""Gamma tennis events (atp, wta, itf, doubles) starting from 3 Nov 2026 and moneyline v2 trades for those matching Cito matches."""
import sys, os, json, gzip, re, unicodedata, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from common import jget, RAW, pull_trades
from concurrent.futures import ThreadPoolExecutor
S = json.load(gzip.open(f'{RAW}/inplay/gamma_sports_2026-11-04.json.gz'))
ser = {s['sport']: s['series'] for s in S if s['sport'] in ('atp', 'wta', 'itf', 'atp-doubles', 'wta-doubles')}
G = []
for sp, ss in ser.items():
    for se in str(ss).split(','):
        off = 0
        while True:
            c, d = jget('https://gamma-api.polymarket.com/events', {'series_id': se, 'start_date_min': '2026-11-02T00:00:00Z', 'limit': 100, 'offset': off})
            if c != 200 or not d: break
            G += [dict(league=sp, slug=e['slug'], title=e.get('title'), gameId=e.get('gameId'), startTime=e.get('startTime'),
                       markets=[{k: m.get(k) for k in ('conditionId', 'sportsMarketType', 'outcomes', 'outcomePrices', 'closed', 'feeSchedule', 'question')} for m in e.get('markets') or []]) for e in d]
            off += 100
            if len(d) < 100 or off > 4000: break
json.dump(G, gzip.open(f'{RAW}/tennis/point/gamma_tennis_2026-11-02_on.json.gz', 'wt'))
def toks(s): return set(w for w in re.sub(r'[^a-z ]', ' ', unicodedata.normalize('NFKD', s or '').encode('ascii', 'ignore').decode().lower()).split() if len(w) > 2)
C = {}
for f in sys.argv[1:]:
    for l in gzip.open(f, 'rt'):
        d = json.loads(l)
        if d['src'] != 'cito_tennis_ws': continue
        try: m = json.loads(d['m'])
        except Exception: continue
        if m.get('type') != 'POINT_UPDATE': continue
        x = m['data']; C.setdefault(x['match_id'], (x['player1']['name'], x['player2']['name'], d['rt']))
match = {}
for mid, (p1, p2, t) in C.items():
    best = None
    for e in G:
        ml = [mk for mk in e['markets'] if mk.get('sportsMarketType') == 'moneyline']
        if not ml or not e.get('startTime'): continue
        st = dt.datetime.fromisoformat(e['startTime'].replace('Z', '+00:00')).timestamp()
        if abs(st - t) > 12 * 3600: continue
        oc = json.loads(ml[0]['outcomes']); a, b = toks(oc[0]), toks(oc[1])
        s1 = len(toks(p1) & a) + len(toks(p2) & b); s2 = len(toks(p1) & b) + len(toks(p2) & a)
        sc, p1is0 = (s1, True) if s1 >= s2 else (s2, False)
        if sc >= 2 and (best is None or sc > best[0]): best = (sc, e, ml[0], p1is0)
    if best: match[mid] = dict(slug=best[1]['slug'], cond=best[2]['conditionId'], p1is0=best[3], outcomes=best[2]['outcomes'], prices=best[2]['outcomePrices'],
                               reb=best[2].get('feeSchedule'), start=best[1]['startTime'])
json.dump(match, open(f'{RAW}/tennis/point/match_cito_pm.json', 'w'), indent=0)
print('gamma events', len(G), 'cito matches', len(C), 'matched', len(match))
with ThreadPoolExecutor(12) as ex:
    list(ex.map(lambda v: pull_trades(v['cond'], dt.datetime.fromisoformat(v['start'].replace('Z', '+00:00')).timestamp() - 3 * 3600,
                                      dt.datetime.fromisoformat(v['start'].replace('Z', '+00:00')).timestamp() + 12 * 3600, 'tennis/point/trades'), match.values()))
print('done')
