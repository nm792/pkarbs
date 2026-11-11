"""Event-only rule: bigger caps and longer bid windows (4 Nov). Same rule as bo3bt.py; cross-fit timing (anchor fitted on odd
rounds, trade even rounds) so no look-ahead. Usage: bo3bt_grid.py lo hi tag  (links ranked lo..hi by volume)."""
import sys, os, json, gzip
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import bo3bt as B
lo, hi, tag = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
B.XFIT = os.environ.get('XFIT', '1') == '1'   # lag >= +20 has no overlap with the fit window, so XFIT=0 is fair there
LAGS = [int(x) for x in os.environ.get('LAGS', '0,20').split(',')]
links = sorted(json.load(gzip.open(f'{B.RAW}/links.json.gz')), key=lambda o: -o['vol'])[lo:hi]
ms = {m['id']: m for m in json.load(gzip.open(f'{B.RAW}/matches_2026-09-01_2026-11-04.json.gz'))}
games, anchors = B.build(links, ms)
games = [g for g in games if g['fit'] > 0.15]
mids = {g['match'] for g in games if g['kind'] != 'match'}; games = [g for g in games if g['match'] in mids]
start = {o['id']: o['startTime'] for o in links}; matches = sorted(mids, key=lambda m: start[m])
days = (np.datetime64(start[matches[-1]][:10]) - np.datetime64(start[matches[0]][:10])).astype(int) + 1
# beta: fixed from the top-250 training half (bo3bt xfit run) so lower tiers are out of sample
bx = json.load(open(os.path.join(HERE, 'out_bo3bt_xfit.json')))['beta']; bm, bM = bx['maps'][0], bx['match'][0]
print(tag, 'matches', len(matches), 'markets', len(games), 'span days', days, flush=True)
res = dict(tag=tag, n_matches=len(matches), span_days=int(days), runs=[])
half = matches[len(matches) // 2:]
for lag in LAGS:
    for W in (30, 60, 90, 120):
        for Q in (100, 500, 1000, 2000, 1e9):
            r = {(g['match'], g['kind']): B.per_market(g, bm if g['kind'] != 'match' else bM, lag, W, Q) for g in games}
            t = B.agg(r, matches, 'all'); h = B.agg(r, half, 'all')
            res['runs'].append(dict(lag=lag, W=W, Q=Q, all=t, later_half=h))
            print(f"lag+{lag} W{W} Q{Q:g}: fill/match ${t['usd_per_match']} 1min {t['edge_1min_pct']}% {t['ci_1min']} "
                  f"result {t['result_pct']}% $/match {t['per_match']} {t['ci_per_match']} | later half $/m {h['per_match']} 1min {h['edge_1min_pct']}%", flush=True)
json.dump(res, open(os.path.join(HERE, f'out_grid_{tag}.json'), 'w'), indent=1, default=str)
