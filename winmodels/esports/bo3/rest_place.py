"""Resting bids with rn1-like placement (4 Nov 2026). rn1's real CS2 maker fills sit ~1c under the trade-derived mid at every
price level (out_rn1_vs_sim.json), not 2.5% under. Here: bid on both tokens at mid - off (cents) or mid x (1 - pct), maker only,
never at/above mid; optional pull for `pull` s after each round (rn1 does not pull). Fill rules:
  'through' = a sell print strictly below our bid, at most 1% below (current corrected rule; we're last in queue)
  'touch'   = a sell print at or below our bid, at most 1% below (we're first in queue at our level; optimistic)
Hold to result, + estimated rebate. Usage: rest_place.py lo hi tag [rn1]  (links ranked lo..hi; rn1 = only rn1's 42 matches)"""
import sys, os, json, gzip, bisect
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import bo3bt as B
C = B.C
def run(g, off=None, pct=None, rule='through', pull=0, Q=100, max_gap=0.01):
    s = g['s']; M = s['M']; et = sorted(t for t, _ in g['ev']); t0, t1 = et[0] - 120, et[-1]
    reb = C.reb_rate(s['m']); tot = np.zeros(4)
    for (T, _, ph, sell0, sz) in s['pr']:
        if not (t0 <= T <= t1): continue
        mk = M.at(T - 1)
        if mk is None or not (0.03 <= mk <= 0.97): continue
        if pull:
            i = bisect.bisect_right(et, T) - 1
            if i >= 0 and T < et[i] + pull: continue
        m = mk if sell0 else 1 - mk; p = ph if sell0 else 1 - ph
        b = round(m - off, 3) if off is not None else m * (1 - pct)
        if b <= 0.005 or b >= m: continue
        hit = (p < b - 1e-9) if rule == 'through' else (p <= b + 1e-9)
        if not hit or (b - p) / b > max_gap: continue
        q = min(sz, Q); m60 = M.at(T + 60); m60 = m60 if sell0 else 1 - m60
        out = 1.0 if (s['win0'] == sell0) else 0.0
        tot += [q * b, q * (m60 - b), q * (out - b), q * reb * b * (1 - b)]
    return tot.tolist()
if __name__ == '__main__':
    lo, hi, tag = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
    links = sorted(json.load(gzip.open(f'{B.RAW}/links.json.gz')), key=lambda o: -o['vol'])[lo:hi]
    if len(sys.argv) > 4 and sys.argv[4] == 'rn1':
        A = json.load(gzip.open('/mnt/project-files/rn1/raw/act7d.json.gz')); cs = {a['conditionId'] for a in A if a.get('type') == 'TRADE'}
        links = [o for o in links if any(m['conditionId'] in cs for m in o['markets'])]
    ms = {m['id']: m for m in json.load(gzip.open(f'{B.RAW}/matches_2026-09-01_2026-11-04.json.gz'))}
    games, _ = B.build(links, ms)
    games = [g for g in games if g['fit'] > 0.15]
    mids = {g['match'] for g in games if g['kind'] != 'match'}; games = [g for g in games if g['match'] in mids]
    start = {o['id']: o['startTime'] for o in links}; matches = sorted(mids, key=lambda m: start[m]); half = matches[len(matches) // 2:]
    print(tag, 'matches', len(matches), 'markets', len(games), flush=True)
    res = dict(tag=tag, n_matches=len(matches), runs=[])
    cfgs = [dict(pct=0.025), dict(off=0.005), dict(off=0.01), dict(off=0.015), dict(off=0.02)]
    rules, pulls = ('through', 'touch'), (0, 30)
    if os.environ.get('DEEP'):      # deep ladder levels, as rn1's profitable fills (5-15% under mid)
        cfgs = [dict(pct=x) for x in (0.04, 0.05, 0.075, 0.10, 0.15)]; rules, pulls = ('touch', 'through'), (0,)
    for rule in rules:
        for pull in pulls:
            for cf in cfgs:
                for Q in (100, 500):
                    r = {(g['match'], g['kind']): run(g, rule=rule, pull=pull, Q=Q, **cf) for g in games}
                    t = B.agg(r, matches, 'all'); h = B.agg(r, half, 'all')
                    res['runs'].append(dict(rule=rule, pull=pull, Q=Q, **cf, all=t, later_half=h))
                    print(f"{rule} pull{pull} {cf} Q{Q}: fill/match ${t['usd_per_match']} 1min {t['edge_1min_pct']}% {t['ci_1min']} "
                          f"result {t['result_pct']}% $/match {t['per_match']} {t['ci_per_match']} reb/m {t['reb_per_match']} | later half $/m {h['per_match']} 1min {h['edge_1min_pct']}%", flush=True)
    json.dump(res, open(os.path.join(HERE, f'out_rest_place_{tag}.json'), 'w'), indent=1, default=str)
