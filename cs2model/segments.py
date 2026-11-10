#!/usr/bin/env python3
"""Step 16: does the market misprice a KIND of CS2 map?  One reading per map per segment (first snapshot meeting the condition, price 5-95c), from the point of view of
the segment team (trailing team, or the team in the segment); gap = realised map result minus market mid.  Map-clustered (one reading per map, so SE = SD/sqrt(n)).
Reference: the same statistic for ALL maps at their first snapshot 90 s after the anchor (unconditional calibration of the market).  Usage: segments.py samples.pkl pairs.json books.pkl"""
import sys, json, pickle, bisect, re, collections, numpy as np
D = pickle.load(open(sys.argv[1], 'rb')); S = D['samples']; M = D['maps']
P = json.load(open(sys.argv[2]))['pairs']; B = pickle.load(open(sys.argv[3], 'rb'))['book']
T = {k: [x[0] for x in v] for k, v in B.items()}
def mid(tk, t, maxage=20):
    ts = T.get(tk)
    if not ts: return None
    i = bisect.bisect_right(ts, t) - 1
    if i < 0 or t - ts[i] > maxage or B[tk][i][2] - B[tk][i][1] > 0.06: return None
    return (B[tk][i][1] + B[tk][i][2]) / 2
T1 = re.compile(r'major|blast|iem|esl pro|pgl|cologne|katowice|austin|budapest|ipl\b', re.I)
byk = collections.defaultdict(list)
for r in S: byk[r['key']].append(r)
seg = collections.defaultdict(list)
for k in sorted(byk):
    if k not in P or not M[k]['complete']: continue
    p = P[k]; L = sorted(byk[k], key=lambda r: r['t']); tk = p['tok_home']
    mapno = int(re.search(r'Map (\d)', p['q']).group(1)) if re.search(r'Map (\d)', p['q']) else 0
    tier = 1 if T1.search(p.get('tournament') or '') or T1.search(p['title']) else 2
    y = M[k]['y_map']; rounds = sorted(M[k]['rounds'], key=lambda x: x[1])
    first = None
    for r in L:
        pm = mid(tk, r['t'])
        if pm is not None and 0.05 <= pm <= 0.95:
            if first is None: first = (r, pm); first_t = r['t']
    if first is None: continue
    def add(name, r, pm):  # home view; also record trailing-team view
        seg[name].append((y - pm, pm, k))
    r0, pm0 = first
    t90 = [(r, mid(tk, r['t'])) for r in L if r['t'] >= first_t + 90 and mid(tk, r['t']) is not None and 0.05 <= mid(tk, r['t']) <= 0.95]
    if not t90: continue
    r90, pm90 = t90[0]
    seg['ALL maps (home)'].append((y - pm90, pm90, k))
    seg['tier1 events'if tier == 1 else 'tier2 events'].append((y - pm90, pm90, k))
    seg['map %d' % mapno if mapno < 3 else 'map 3+ (late series)'].append((y - pm90, pm90, k))
    # comebacks: first snapshot where one team trails by >=5 rounds; segment team = trailing team
    diff = 0; hs = 0; as_ = 0
    for r, pm in [(r, mid(tk, r['t'])) for r in L]:
        if pm is None or not (0.03 <= pm <= 0.97): continue
        done = [(hT, yy) for (tm, te, n, hT, yy) in rounds if te < r['t']]
        hw = sum(yy for _, yy in done); aw = len(done) - hw
        d = hw - aw
        if abs(d) >= 5:
            tr_home = d < 0
            gap = ((y if tr_home else 1 - y) - (pm if tr_home else 1 - pm))
            seg['trailing team down >=5 rds'].append((gap, pm if tr_home else 1 - pm, k)); break
    for r, pm in [(r, mid(tk, r['t'])) for r in L]:
        if pm is None or not (0.03 <= pm <= 0.97): continue
        done = [(hT, yy) for (tm, te, n, hT, yy) in rounds if te < r['t']]
        hw = sum(yy for _, yy in done); aw = len(done) - hw
        if abs(hw - aw) >= 7:
            tr_home = hw < aw
            gap = ((y if tr_home else 1 - y) - (pm if tr_home else 1 - pm))
            seg['trailing team down >=7 rds'].append((gap, pm if tr_home else 1 - pm, k)); break
print('%-32s %4s %8s %8s %8s %6s' % ('segment (one reading per map)', 'n', 'mean mid', 'win rate', 'gap', 't'))
for name, v in sorted(seg.items()):
    g = np.array([x[0] for x in v]); m = np.array([x[1] for x in v]); n = len(g)
    se = g.std(ddof=1) / np.sqrt(n) if n > 1 else float('nan')
    print('%-32s %4d %8.3f %8.3f %+8.3f %+6.2f' % (name, n, m.mean(), m.mean() + g.mean(), g.mean(), g.mean() / se))
