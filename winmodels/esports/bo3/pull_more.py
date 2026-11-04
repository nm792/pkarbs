"""bo3 games+rounds and Polymarket v2 trades for linked CS2 events ranked lo..hi by volume (smaller tournaments)."""
import json, gzip, sys, datetime as dt
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, '../..'); import common as C
import bo3_pull as b
lo, hi = int(sys.argv[1]), int(sys.argv[2])
L = sorted(json.load(gzip.open(f'{b.RAW}/links.json.gz')), key=lambda o: -o['vol'])[lo:hi]
ms = {m['id']: m for m in json.load(gzip.open(f'{b.RAW}/matches_2026-09-01_2026-11-04.json.gz'))}
def ts(s): return dt.datetime.fromisoformat(s.replace('Z', '+00:00')).timestamp()
def g(o):
    try: b.games(o['bo3'])
    except Exception as e: print('games err', o['bo3'], e)
with ThreadPoolExecutor(6) as ex: list(ex.map(g, L))
print('games done', flush=True)
jobs = []
for o in L:
    m = ms[o['bo3']]; t0 = ts(m['start_date']) - 3600; t1 = ts(m['end_date'] or m['start_date']) + 3 * 3600
    for mk in o['markets']: jobs.append((mk['conditionId'], t0, t1))
with ThreadPoolExecutor(8) as ex:
    for i, n in enumerate(ex.map(lambda j: len(C.pull_trades(j[0], j[1], j[2], sub='bo3/trades')), jobs)):
        if i % 200 == 0: print(i, len(jobs), flush=True)
print('done', len(jobs))
