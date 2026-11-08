"""rn1's real CS2 maker fills vs our resting-bid sim fills on the same markets (4 Nov 2026).
Same 42 matches / 125 markets as rn1_phase.py (rn1 act7d 22-29 Oct, bo3-timed rounds). For every fill:
  disc   = (mid just before - price) / mid      (trade-derived mid, C.Mid)
  m1     = (mid 60 s later - price) / price     1-min markout, rebate excluded
  fav    = token price >= 0.5;  kind = map / match;  since = s since last round end; size $.
Sim = rn1 resting pattern as in bo3bt.resting (bid mid x 0.975 both sides, pulled 30 s after rounds at lag 0, corrected
fills max_gap 1%, cap 100 shares) but keeping each fill."""
import sys, os, json, gzip, glob, bisect, collections
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import bo3bt as B
C = B.C
SCR = sys.argv[1]
taker = set()
for fn in glob.glob(f'{SCR}/trades7d/true_*.json'):
    for r in json.load(open(fn))['rows']: taker.add(r['transactionHash'])
A = json.load(gzip.open('/mnt/project-files/rn1/raw/act7d.json.gz'))
fills = collections.defaultdict(list)
for a in A:
    if a.get('type') == 'TRADE': fills[a['conditionId']].append(a)
links = sorted(json.load(gzip.open(f'{B.RAW}/links.json.gz')), key=lambda o: -o['vol'])[:250]
links = [o for o in links if any(m['conditionId'] in fills for m in o['markets'])]
ms = {m['id']: m for m in json.load(gzip.open(f'{B.RAW}/matches_2026-09-01_2026-11-04.json.gz'))}
games, _ = B.build(links, ms)
games = [g for g in games if g['fit'] > 0.15 and g['s']['m']['conditionId'] in fills]

def sim_fills(g, d=0.025, Q=100, max_gap=0.01, pull=30):
    s = g['s']; M = s['M']; et = sorted(t for t, _ in g['ev']); t0, t1 = et[0] - 120, et[-1]; out = []
    for (T, _, ph, sell0, sz) in s['pr']:
        if not (t0 <= T <= t1): continue
        mk = M.at(T - 1)
        if mk is None or not (0.05 <= mk <= 0.95): continue
        i = bisect.bisect_right(et, T) - 1
        if i >= 0 and T < et[i] + pull: continue
        if sell0:
            b = mk * (1 - d)
            if ph < b - 1e-9 and (b - ph) / b <= max_gap: out.append((T, 0, b, min(sz, Q)))
        else:
            b = (1 - mk) * (1 - d)
            if (1 - ph) < b - 1e-9 and (b - (1 - ph)) / b <= max_gap: out.append((T, 1, b, min(sz, Q)))
    return out

rows = {'rn1': [], 'sim': []}
for g in games:
    s = g['s']; M = s['M']; et = np.sort(np.array([t for t, _ in g['ev']])); t0, t1 = et[0] - 120, et[-1]
    kind = 'match' if g['kind'] == 'match' else 'map'
    def feat(t, tok, p, usd):
        m = M.at(t - 1); m60 = M.at(t + 60)
        if m is None or m60 is None: return None
        if tok == 1: m, m60 = 1 - m, 1 - m60
        i = bisect.bisect_left(et, t); since = t - (et[i - 1] if i > 0 else t0)
        out = 1.0 if (s['win0'] == (tok == 0)) else 0.0
        return dict(disc=(m - p) / m, m1=(m60 - p) / p, res=(out - p) / p, fav=p >= 0.5, p=p, kind=kind, since=since, usd=usd)
    for a in fills[s['m']['conditionId']]:
        if a['transactionHash'] in taker or not (t0 <= a['timestamp'] <= t1): continue
        f = feat(a['timestamp'], a['outcomeIndex'], a['price'], a['size'] * a['price'])
        if f: rows['rn1'].append(f)
    for (T, tok, b, q) in sim_fills(g):
        f = feat(T, tok, b, q * b)
        if f: rows['sim'].append(f)

def summ(rs):
    if not rs: return dict(n=0)
    w = np.array([r['usd'] for r in rs]); f = lambda k: np.array([r[k] for r in rs], float)
    return dict(n=len(rs), usd=round(w.sum()), disc_wtd=round(100 * np.average(f('disc'), weights=w), 2),
                disc_med=round(100 * np.median(f('disc')), 2), m1=round(100 * np.average(f('m1'), weights=w), 2),
                res=round(100 * np.average(f('res'), weights=w), 2), med_usd=round(float(np.median(w)), 1),
                price_wtd=round(float(np.average(f('p'), weights=w)), 3))
out = {}
for who, rs in rows.items():
    o = dict(all=summ(rs))
    o['fav'] = summ([r for r in rs if r['fav']]); o['dog'] = summ([r for r in rs if not r['fav']])
    o['map'] = summ([r for r in rs if r['kind'] == 'map']); o['match'] = summ([r for r in rs if r['kind'] == 'match'])
    for lo, hi in ((0, .1), (.1, .3), (.3, .5), (.5, .7), (.7, .9), (.9, 1.01)):
        o[f'p{lo}-{hi}'] = summ([r for r in rs if lo <= r['p'] < hi])
    for lo, hi in ((-1, 0), (0, .01), (.01, .02), (.02, .03), (.03, .05), (.05, .1), (.1, 1)):
        o[f'disc{lo}-{hi}'] = summ([r for r in rs if lo <= r['disc'] < hi])
    for lo, hi in ((0, 30), (30, 60), (60, 120), (120, 1e9)):
        o[f'since{lo}-{hi:g}'] = summ([r for r in rs if lo <= r['since'] < hi])
    out[who] = o
out['n_matches'] = len({g['match'] for g in games}); out['n_markets'] = len(games)
json.dump(out, open(os.path.join(HERE, 'out_rn1_vs_sim.json'), 'w'), indent=1)
for k in out['rn1']:
    print(f"{k:14s} rn1 {out['rn1'][k]}\n{'':14s} sim {out['sim'].get(k)}")
