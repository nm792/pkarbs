#!/usr/bin/env python3
"""Step 15a: equipment value features from the TheSports weapon dictionary (id -> name, Hermes pull 10 Nov) and standard CS2 buy prices.
Per sample row: value of the MAIN weapon held by each ALIVE player, summed per team (current equipment at risk).  Per round: team main-weapon value at the first
full-roster row 20-40 s after round start (post-buy), alive players only.  Output equip.pkl {'cur': {(key,t): (h,a)}, 'start': {(key,tmr): (h,a)}}."""
import sys, json, gzip, pickle, collections
S = pickle.load(open(sys.argv[2], 'rb'))['samples']; NAMES = json.load(open(sys.argv[3]))
PRICE = {'ak47': 2700, 'm4a1': 3100, 'm4a1-silencer': 2900, 'awp': 4750, 'galilar': 1800, 'famas': 1950, 'glock': 200, 'usp_silencer': 200, 'hkp2000': 200, 'deagle': 700,
         'mp9': 1250, 'mac10': 1050, 'tec9': 500, 'fiveseven': 500, 'Dual Berettas': 300, 'elite': 300, 'p250': 300, 'ssg08': 1700, 'mp7': 1500, 'mag7': 1300, 'xm1014': 2000,
         'ump45': 1200, 'aug': 3300, 'sg556': 3000, 'nova': 1050, 'cz75a': 500, 'scar20': 5000, 'g3sg1': 5000, 'p90': 2350, 'negev': 1700, 'mp5sd': 1500, 'bizon': 1400, 'sawedoff': 1100, 'revolver': 600}
val = {w: PRICE.get(n, 0) for w, n in NAMES.items()}
want = collections.defaultdict(set); wt = collections.defaultdict(set)
for r in S: want[r['key']].add(r['t'])
cur = {}; start = {}
for l in gzip.open(sys.argv[1], 'rt'):
    r = json.loads(l); k = '%s|%s' % (r['mid'], r['map'])
    if k not in want: continue
    h = r['h']['pl']; a = r['a']['pl']
    if not (len(h) == 5 and len(a) == 5 and all(len(q) >= 7 for q in h + a)): continue
    eh = sum(val.get(q[6], 0) for q in h if q[3] > 0); ea = sum(val.get(q[6], 0) for q in a if q[3] > 0)
    if r['t'] in want[k]: cur[(k, r['t'])] = (eh, ea)
    tm = (r['tm'] or [0, 0, 0])[2]
    if tm and (k, tm) not in start and 20 <= r['t'] - tm <= 40: start[(k, tm)] = (eh, ea)
pickle.dump(dict(cur=cur, start=start), open(sys.argv[4], 'wb'))
print('cur', len(cur), 'start', len(start))
