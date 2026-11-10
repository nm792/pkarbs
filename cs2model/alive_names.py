#!/usr/bin/env python3
"""Step 14a: names of ALIVE players (hp>0) for each sample row, plus rosters, so an alive-weighted player-strength feature can be built.
Output alive.pkl {key: {t: (tuple(alive home names), tuple(alive away names))}}, rosters {key: (home names, away names)}."""
import sys, json, gzip, pickle, collections
S = pickle.load(open(sys.argv[2], 'rb'))['samples']
want = collections.defaultdict(set)
for r in S: want[r['key']].add(r['t'])
al = collections.defaultdict(dict); ros = {}
for l in gzip.open(sys.argv[1], 'rt'):
    r = json.loads(l); k = '%s|%s' % (r['mid'], r['map'])
    if k not in want: continue
    h = r['h']['pl']; a = r['a']['pl']
    if len(h) == 5 and len(a) == 5 and all(len(q) >= 4 for q in h + a):
        ros[k] = (tuple(q[0] for q in h), tuple(q[0] for q in a))
        if r['t'] in want[k]: al[k][r['t']] = (tuple(q[0] for q in h if q[3] > 0), tuple(q[0] for q in a if q[3] > 0))
pickle.dump(dict(alive=dict(al), rosters=ros), open(sys.argv[3], 'wb'))
print('maps', len(al), 'rows', sum(len(v) for v in al.values()))
