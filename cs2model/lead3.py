#!/usr/bin/env python3
"""lead3: audit of lead2 (12 Nov 2026).  Same inputs/args as lead2.py: SNAPS.pkl PAIRS.json BOOKS.pkl.
Adds to lead2 (round-end events only, same time-aligned signed mid increments, direction-shuffled placebo):
 A. map-clustered bootstrap (2000 resamples of MAPS) of the pre-feed move (sum of real-minus-placebo over [-60,-5]) and post-feed move ([0,+60]).
 B. condition-matched split: round ends with a kill event (alive-count drop) in the 15 s before the feed message vs none. If the pre-feed move only exists
    when kills precede, the price is reacting to kills we also see (not leading); if it exists with no preceding kill, the price leads the feed.
 C. all increments use the 1-s-poll book mid (receive time); stated resolution +-1-2 s.
PASS criterion for 'price leads feed on round ends': pre-feed bootstrap 95% CI excludes 0 AND post-feed CI includes 0 AND the no-preceding-kill split has the same sign.
Memory: streams nothing big; ~1-2 GB (book pickle). Run once, no overlap."""
import sys, json, pickle, bisect, random, collections
import numpy as np
S = pickle.load(open(sys.argv[1], 'rb')); P = json.load(open(sys.argv[2]))['pairs']; B = pickle.load(open(sys.argv[3], 'rb'))['book']
T = {k: [x[0] for x in v] for k, v in B.items()}
def mid(tk, t, maxage=20):
    ts = T.get(tk)
    if not ts: return None
    i = bisect.bisect_right(ts, t) - 1
    if i < 0 or t - ts[i] > maxage: return None
    return (B[tk][i][1] + B[tk][i][2]) / 2
ev = collections.defaultdict(list)   # key -> [(t, dir, type)]
for key in P:
    prev = None
    for r in S[key]['rows']:
        if prev is not None and r['t'] - prev['t'] < 8:
            if r['rn'] == prev['rn'] and (r['ch'], r['ca']) == (prev['ch'], prev['ca']) and None not in (r['al_h'], r['al_a'], prev['al_h'], prev['al_a']):
                if prev['al_h'] - r['al_h'] == 1 and r['al_a'] == prev['al_a']: ev[key].append((r['t'], -1, 'kill'))
                elif prev['al_a'] - r['al_a'] == 1 and r['al_h'] == prev['al_h']: ev[key].append((r['t'], +1, 'kill'))
            d = (r['ch'] - prev['ch'], r['ca'] - prev['ca'])
            if d == (1, 0): ev[key].append((r['t'], +1, 'end'))
            elif d == (0, 1): ev[key].append((r['t'], -1, 'end'))
        prev = r
BINS = list(range(-60, 60, 5))
def per_map(key, rng, shuffle, sel):
    """returns dict bin -> (sum, n) of signed increments for round ends in this map selected by sel(t, kills_before)."""
    L = sorted(ev[key]); kills = [t for t, _, ty in L if ty == 'kill']
    ends = [(t, d) for t, d, ty in L if ty == 'end']
    ds = [d for _, d in ends]
    if shuffle: rng.shuffle(ds)
    tk = P[key]['tok_home']; out = {b: [0.0, 0] for b in BINS}
    for (t, _), d in zip(ends, ds):
        k = bisect.bisect_left(kills, t) - bisect.bisect_left(kills, t - 15)
        if not sel(k): continue
        m0 = mid(tk, t - 10)
        if m0 is None or not (0.08 <= m0 <= 0.92): continue
        for b in BINS:
            a, c = mid(tk, t + b), mid(tk, t + b + 5)
            if a is not None and c is not None: out[b][0] += d * (c - a) * 100; out[b][1] += 1
    return out
def stats(sel, label, nplc=10):
    keys = [k for k in P if k in ev]
    real = {k: per_map(k, None, False, sel) for k in keys}
    pl = [{k: per_map(k, random.Random(s * 1000 + i), True, sel) for i, k in enumerate(keys)} for s in range(nplc)]
    def stat(ks, lo, hi):
        r = n = 0; p = 0.0
        for k in ks:
            for b in BINS:
                if lo <= b < hi: r += real[k][b][0]; n += real[k][b][1]
        for run in pl:
            pp = 0.0
            for k in ks:
                for b in BINS:
                    if lo <= b < hi: pp += run[k][b][0]
            p += pp
        # per-event-bin mean difference (c per bin summed over bins)
        nb = sum(real[k][b][1] for k in ks for b in BINS if lo <= b < hi) / max(1, len([1 for b in BINS if lo <= b < hi]))
        return (r - p / len(pl)) / max(nb, 1)
    rng = random.Random(1); res = {}
    for nm, lo, hi in (('pre-feed [-60,-5)', -60, -5), ('post-feed [0,+60)', 0, 60)):
        pt = stat(keys, lo, hi)
        bs = [stat([rng.choice(keys) for _ in keys], lo, hi) for _ in range(2000)]
        print('%-34s %-18s maps=%d events/bin~%d  point %+.2f c  boot95 [%+.2f, %+.2f]' % (label, nm, len(keys), sum(real[k][-60][1] for k in keys), pt, np.percentile(bs, 2.5), np.percentile(bs, 97.5)))
stats(lambda k: True, 'round ends ALL')
stats(lambda k: k >= 1, 'round ends, kill in prev 15 s')
stats(lambda k: k == 0, 'round ends, NO kill in prev 15 s')
