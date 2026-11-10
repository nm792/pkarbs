#!/usr/bin/env python3
"""Step 4 (v2): lead/lag of TheSports CS2 SNAPSHOT-derived events vs the PM map-winner mid.  Events: a team's alive count drops (kill), map score +1 (round end).
Time-aligned mean signed mid increment (cents per 5 s bin) around feed receive time, real vs direction-shuffled placebo (same times, same map, direction from another event of that map).
Also the share of events where the price had ALREADY moved >=1c in the event's favour over the previous 10 s (price-first) vs placebo."""
import sys, json, pickle, bisect, random, collections, statistics as st
S = pickle.load(open(sys.argv[1], 'rb')); P = json.load(open(sys.argv[2]))['pairs']; B = pickle.load(open(sys.argv[3], 'rb'))['book']
T = {k: [x[0] for x in v] for k, v in B.items()}
def mid(tk, t, maxage=20):
    ts = T.get(tk)
    if not ts: return None
    i = bisect.bisect_right(ts, t) - 1
    if i < 0 or t - ts[i] > maxage: return None
    return (B[tk][i][1] + B[tk][i][2]) / 2
events = collections.defaultdict(list)
for key in P:
    rows = S[key]['rows']; prev = None
    for r in rows:
        if prev is not None and r['t'] - prev['t'] < 8:
            if r['rn'] == prev['rn'] and (r['ch'], r['ca']) == (prev['ch'], prev['ca']) and None not in (r['al_h'], r['al_a'], prev['al_h'], prev['al_a']):
                if prev['al_h'] - r['al_h'] == 1 and r['al_a'] == prev['al_a']: events[key].append((r['t'], -1, 'kill'))
                elif prev['al_a'] - r['al_a'] == 1 and r['al_h'] == prev['al_h']: events[key].append((r['t'], +1, 'kill'))
            if (r['ch'] - prev['ch'], r['ca'] - prev['ca']) == (1, 0): events[key].append((r['t'], +1, 'end'))
            elif (r['ch'] - prev['ch'], r['ca'] - prev['ca']) == (0, 1): events[key].append((r['t'], -1, 'end'))
        prev = r
BINS = list(range(-60, 60, 5))
def curve(evl, rng, shuffle):
    inc = {b: [] for b in BINS}; pre = []
    for key, L in evl.items():
        tk = P[key]['tok_home']; ds = [d for _, d, _ in L]
        if shuffle: rng.shuffle(ds)
        for (t, d0, ty), d in zip(L, ds):
            m0 = mid(tk, t - 10)
            if m0 is None or not (0.08 <= m0 <= 0.92): continue
            m1 = mid(tk, t)
            if m1 is not None: pre.append(d * (m1 - m0) >= 0.01)
            for b in BINS:
                a, c = mid(tk, t + b), mid(tk, t + b + 5)
                if a is not None and c is not None: inc[b].append(d * (c - a))
    return {b: (sum(v) / len(v) * 100 if v else float('nan'), len(v)) for b, v in inc.items()}, (sum(pre) / len(pre) if pre else float('nan'))
for label, flt in (('ALL', lambda e: True), ('kills', lambda e: e[2] == 'kill'), ('round ends', lambda e: e[2] == 'end')):
    evl = {k: [e for e in L if flt(e)] for k, L in events.items()}
    real, pre_r = curve(evl, None, False)
    pls = [curve(evl, random.Random(s), True) for s in range(20)]
    print('== %s: %d events, %d maps | price already >=1c in event direction over previous 10 s: real %.1f%% vs placebo %.1f%%' % (label, sum(len(v) for v in evl.values()), len(evl), 100 * pre_r, 100 * sum(p[1] for p in pls) / len(pls)))
    tot = 0; cum = 0; rows = []
    for b in BINS:
        pm = sum(p[0][b][0] for p in pls) / len(pls); rows.append((b, real[b][0], pm, real[b][1])); tot += real[b][0] - pm
    half = None
    for b, rr, pm, n in rows:
        cum += rr - pm
        if half is None and abs(cum) >= abs(tot) / 2: half = b + 5
        print('%+4d..%+4d real %+7.3f placebo %+7.3f diff %+7.3f cum %+7.3f n=%d' % (b, b + 5, rr, pm, rr - pm, cum, n))
    print('  total real-minus-placebo [-60,+60] = %+.2f c; half reached by %s s' % (tot, half))
