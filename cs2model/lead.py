#!/usr/bin/env python3
"""Step 4: does the TheSports CS2 event feed lead or lag the Polymarket map-winner price?  Time-aligned mean signed price increment (cents per 5 s bin)
around the feed receive time t0 (t0=0), real direction vs placebo (same event times, direction taken from a random OTHER event of the same map,
so side/price mix is identical).  Also the 'half-move' time: when the cumulative signed move over [-60,+60] passes half its total.  Clustered (by map) bootstrap CIs."""
import sys, json, pickle, bisect, random, collections, statistics as st
R = json.load(open(sys.argv[1])); P = json.load(open(sys.argv[2]))['pairs']; B = pickle.load(open(sys.argv[3], 'rb'))['book']
T = {k: [x[0] for x in v] for k, v in B.items()}
def mid(tk, t, maxage=20):
    ts = T.get(tk)
    if not ts: return None
    i = bisect.bisect_right(ts, t) - 1
    if i < 0 or t - ts[i] > maxage: return None
    return (B[tk][i][1] + B[tk][i][2]) / 2
def side_home(Rd, side):      # does event-side belong to home team? home_side = side value of home team in this round
    return Rd['home_side'] == side
events = collections.defaultdict(list)    # map -> (t, d)  d=+1 favours home
for key, p in P.items():
    for Rd in R[key]['rounds']:
        if not Rd['clean']: continue
        for (t, ks, vs, vn) in Rd['kills']:
            events[key].append((t, 1 if side_home(Rd, ks) else -1, 'kill'))
        if Rd['end']:
            t, ws, wt = Rd['end'][:3]
            if ws in (1, 2): events[key].append((t, 1 if side_home(Rd, ws) else -1, 'end'))
BINS = list(range(-60, 60, 5))
def curve(evl, shuffle, rng):
    inc = {b: [] for b in BINS}
    for key, L in evl.items():
        tk = P[key]['tok_home']
        ds = [d for _, d, _ in L]
        if shuffle: rng.shuffle(ds)
        for (t, d0, ty), d in zip(L, ds):
            m0 = mid(tk, t - 10)
            if m0 is None or not (0.08 <= m0 <= 0.92): continue
            for b in BINS:
                a, c = mid(tk, t + b), mid(tk, t + b + 5)
                if a is not None and c is not None: inc[b].append((key, d * (c - a)))
    return inc
def summarize(inc):
    return {b: (sum(x for _, x in v) / len(v) * 100 if v else float('nan'), len(v)) for b, v in inc.items()}
rng = random.Random(7)
for label, flt in (('ALL clean events', lambda e: True), ('kills only', lambda e: e[2] == 'kill'), ('round ends only', lambda e: e[2] == 'end')):
    evl = {k: [e for e in L if flt(e)] for k, L in events.items()}
    real = summarize(curve(evl, False, rng))
    pl = [summarize(curve(evl, True, random.Random(s))) for s in range(20)]
    print('== %s: events %d on %d maps' % (label, sum(len(v) for v in evl.values()), len(evl)))
    print('bin(s)   real c/5s   placebo mean   diff   n')
    cum_r = cum_d = 0; tot = sum(real[b][0] - sum(p[b][0] for p in pl) / len(pl) for b in BINS)
    half = None
    for b in BINS:
        pm = sum(p[b][0] for p in pl) / len(pl)
        cum_d += real[b][0] - pm
        if half is None and abs(cum_d) >= abs(tot) / 2: half = b + 5
        print('%+4d..%+4d %+8.3f   %+8.3f   %+8.3f  %d' % (b, b + 5, real[b][0], pm, real[b][0] - pm, real[b][1]))
    print('cumulative real-minus-placebo over [-60,+60]: %+.2f c; half of it reached by t = %s s (negative = price moved before the feed message)' % (tot, half))
