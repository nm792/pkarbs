"""What-if: a feed that arrives BEFORE the Polymarket WS (event time = WS receipt + lag, lag < 0). Same rule as cs2_maps.py."""
import json, numpy as np, cs2_maps as X
games = X.build(); games.sort(key=lambda g: g['t0'])
matches = sorted({g['title'] for g in games}, key=lambda t: min(g['t0'] for g in games if g['title'] == t))
half = set(matches[:len(matches) // 2]); tr = [g for g in games if g['title'] in half]; te = [g for g in games if g['title'] not in half]
bm = X.fit_beta([g for g in tr if g['kind'] != 'match'])[0]; bM = X.fit_beta([g for g in tr if g['kind'] == 'match'])[0]
res = []
for Q in (100, 500):
    for lag in (-30, -20, -15, -10, -5, 0):
        for nm, gs in (('holdout', te), ('all', games)):
            for kind, b in (('maps', bm), ('match', bM)):
                s, _ = X.run([g for g in gs if (g['kind'] == 'match') == (kind == 'match')], b, lag, 30, Q=Q)
                res.append(dict(Q=Q, lag=lag, set=nm, kind=kind, **s))
                print(f"Q{Q} lag{lag:+d} W30 {nm} {kind}: mkts {s['events']} $fill {s['usd']} 1min {s.get('net_1min_pct')}% {s.get('ci_1min')} result {s.get('net_result_pct')}% ${s.get('net_result_usd')} {s.get('ci_result_usd')}", flush=True)
json.dump(res, open('out_cs2_maps_fast.json', 'w'), indent=1, default=str)
