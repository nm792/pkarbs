"""When inside a CS2 round does rn1 get filled? (4 Nov 2026)
rn1 maker fills 22-29 Oct (rn1/raw act7d + trades7d taker set) on the bo3-timed CS2 markets from bo3bt.build.
Round times = market-reaction centre (bo3bt). For each rn1 maker fill and each market print we take
  since = seconds since the previous round end, before = seconds until the next round end.
rn1 share = rn1 maker $ / all printed $ in that bin. If rn1 pulls on kills/plants (intra-round feed), its share
should fall in the last part of rounds (before round end), not only after round ends."""
import sys, os, json, gzip, glob, bisect, collections
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import bo3bt as B
SCR = sys.argv[1]   # folder with extracted trades7d/*.json
W = '0x2005d16a84ceefa912d4e380cd32e7ff827875ea'
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
SB = [0, 10, 20, 30, 45, 60, 90, 120, 1e9]; TB = [0, 5, 10, 20, 40, 60, 90, 1e9]
def binof(x, bins): return min(bisect.bisect_right(bins, x) - 1, len(bins) - 2)
agg = {k: collections.defaultdict(lambda: np.zeros(5)) for k in ('since', 'before')}   # rn1_maker$, mkt$, rn1_m1 pnl, rn1_taker$, n
nm = set(); nmk = 0; tot = np.zeros(3)
for g in games:
    s = g['s']; M = s['M']; T = np.array([t for t, _ in g['ev']]); T.sort()
    t0, t1 = T[0] - 110, T[-1]
    def where(t):
        i = bisect.bisect_left(T, t)
        if t < t0 or t > t1 or i >= len(T): return None
        prev = T[i - 1] if i > 0 else t0
        return t - prev, T[i] - t
    nm.add(g['match']); nmk += 1
    for (t, _, ph, sell0, sz) in s['pr']:
        w = where(t)
        if w is None: continue
        usd = sz * (ph if sell0 else 1 - ph)
        agg['since'][binof(w[0], SB)][1] += usd; agg['before'][binof(w[1], TB)][1] += usd
    for a in fills[s['m']['conditionId']]:
        t = a['timestamp']; w = where(t)
        if w is None: continue
        m60 = M.at(t + 60)
        if m60 is None: continue
        if a['outcomeIndex'] == 1: m60 = 1 - m60
        mk = a['transactionHash'] not in taker; usd = a['size'] * a['price']
        pnl = a['size'] * (m60 - a['price'])
        for k, b in (('since', binof(w[0], SB)), ('before', binof(w[1], TB))):
            if mk: agg[k][b] += [usd, 0, pnl, 0, 1]
            else: agg[k][b][3] += usd
        tot += [usd if mk else 0, 0 if mk else usd, pnl if mk else 0]
out = dict(matches=len(nm), markets=nmk, rn1_maker_usd=round(tot[0]), rn1_taker_usd=round(tot[1]),
           rn1_maker_1min_pct=round(100 * tot[2] / max(tot[0], 1), 2), bins={})
for k, bins in (('since', SB), ('before', TB)):
    rows = []
    for b in range(len(bins) - 1):
        v = agg[k][b]
        rows.append(dict(bin=f'{bins[b]:g}-{bins[b + 1]:g}s', rn1_maker_usd=round(v[0]), mkt_usd=round(v[1]),
                         rn1_share_pct=round(100 * v[0] / max(v[1], 1), 2), rn1_maker_1min_pct=round(100 * v[2] / max(v[0], 1), 2),
                         rn1_taker_usd=round(v[3]), n_fills=int(v[4])))
    out['bins'][k] = rows
print(json.dumps(out, indent=1))
json.dump(out, open(os.path.join(HERE, 'out_rn1_phase.json'), 'w'), indent=1)
