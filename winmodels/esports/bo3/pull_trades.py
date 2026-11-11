"""Polymarket v2 trades for linked CS2 events (top N by volume), window = bo3 match start-1h .. end+1h. Parallel."""
import json, gzip, sys, os, datetime as dt
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, '../..'); import common as C
import bo3_pull as b
N = int(sys.argv[1])
L = sorted(json.load(gzip.open(f'{b.RAW}/links.json.gz')), key=lambda o: -o['vol'])[:N]
ms = {m['id']: m for m in json.load(gzip.open(f'{b.RAW}/matches_2026-09-01_2026-11-04.json.gz'))}
def ts(s): return dt.datetime.fromisoformat(s.replace('Z', '+00:00')).timestamp()
jobs = []
for o in L:
    m = ms[o['bo3']]; t0 = ts(m['start_date']) - 3600; t1 = ts(m['end_date'] or m['start_date']) + 3 * 3600
    for mk in o['markets']: jobs.append((mk['conditionId'], t0, t1))
def f(j):
    tr = C.pull_trades(j[0], j[1], j[2], sub='bo3/trades'); return len(tr)
with ThreadPoolExecutor(8) as ex:
    for i, n in enumerate(ex.map(f, jobs)):
        if i % 50 == 0: print(i, len(jobs), n, flush=True)
print('done', len(jobs))
