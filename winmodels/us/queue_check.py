"""NBA queue check from 1 s CLOB books (agent/tasks/nba-feed-delay/books.py). For every snapshot of every moneyline
token: our bid price = mid x 0.975 rounded DOWN to the tick (maker only, below best bid); shares resting ahead of us
= all bid size at prices >= that price (price-time priority; anything at our price is ahead of a new order).
Also: spread, depth in clips, and a paper-bid test: place a 500-share bid at that price at each event (+delay), see
whether sells trade through it within W s (queue-free) or hit it at-level (needs queue consumed)."""
import sys, os, json, math, bisect, collections, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))
import common as C
BOOKS, MKTS, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
M = json.load(open(MKTS)); tok2m = {}
for m in M:
    for i, t in enumerate(m['tokens']): tok2m[t] = (m, i)
snap = collections.defaultdict(list)
for l in open(BOOKS):
    r = json.loads(l)
    if 'tok' in r and r['bids'] and r['asks']: snap[r['tok']].append(r)
rows = []
for tok, S in snap.items():
    for r in S:
        bb, ba = r['bids'][0][0], r['asks'][0][0]; mid = (bb + ba) / 2
        if not (0.05 < mid < 0.95): continue
        px = math.floor(mid * 0.975 * 1000 + 1e-9) / 1000
        ahead = sum(s for p, s in r['bids'] if p >= px - 1e-9)
        rows.append((mid, ba - bb, px, bb - px, ahead, sum(s for p, s in r['bids'])))
R = np.array(rows)
print(f'snapshots {len(R)}, tokens {len(snap)}')
print(f'spread: median {np.median(R[:,1])*100:.1f}c; our bid sits median {np.median(R[:,3])*100:.1f}c below the best bid')
print('shares resting AHEAD of a new bid at mid x 0.975: median %.0f, p25 %.0f, p75 %.0f, p90 %.0f' % (np.median(R[:,4]), *np.percentile(R[:,4], [25, 75, 90])))
print('  = %.1f x a 500-share clip (median)' % (np.median(R[:,4]) / 500))
for lo, hi in ((0.05, 0.2), (0.2, 0.4), (0.4, 0.6), (0.6, 0.8), (0.8, 0.95)):
    s = R[(R[:, 0] >= lo) & (R[:, 0] < hi)]
    if len(s): print(f'  mid {lo:.2f}-{hi:.2f}: n {len(s)}, ahead median {np.median(s[:,4]):.0f}, share with ahead < 500: {np.mean(s[:,4] < 500)*100:.0f}%')
# trade-through test using data-api trades for the same window
t0 = min(r['recv_ms'] for S in snap.values() for r in S) / 1000 - 5; t1 = max(r['recv_ms'] for S in snap.values() for r in S) / 1000 + 90
res = dict(snapshots=len(R), tokens=len(snap), spread_c_med=float(np.median(R[:, 1]) * 100), bid_below_best_c_med=float(np.median(R[:, 3]) * 100),
           ahead=dict(med=float(np.median(R[:, 4])), p25=float(np.percentile(R[:, 4], 25)), p75=float(np.percentile(R[:, 4], 75)), p90=float(np.percentile(R[:, 4], 90))))
# paper bids: every 5 s on each token, bid at mid x 0.975, does ANY sell print at price <= bid happen within 30 s / 60 s ?
hit = collections.Counter(); tot = 0; atlevel = 0
for m in M:
    tr = C.pull_trades(m['cond'], t0 - 600, t1 + 600, 'us_live/trades')
    pr = C.prints(tr)
    for i, tok in enumerate(m['tokens']):
        S = snap.get(tok, [])
        if not S: continue
        for r in S[::5]:
            bb, ba = r['bids'][0][0], r['asks'][0][0]; mid = (bb + ba) / 2
            if not (0.05 < mid < 0.95): continue
            px = math.floor(mid * 0.975 * 1000 + 1e-9) / 1000; T = r['recv_ms'] / 1000
            ahead = sum(s for p, s in r['bids'] if p >= px - 1e-9); tot += 1
            for W in (30, 60):
                thr = at = vol = 0
                for (t, _, ph, sell0, sz) in pr:
                    if not (T < t <= T + W): continue
                    pt = ph if i == 0 else 1 - ph; sell = sell0 if i == 0 else (not sell0)
                    if not sell: continue
                    if pt < px - 1e-9: thr += 1
                    if pt <= px + 1e-9: vol += sz
                hit[('through', W)] += thr > 0; hit[('vol>=ahead', W)] += vol >= ahead + 500
print(f'paper bids (every 5 s, mid x 0.975, 500 sh): n {tot}')
for W in (30, 60):
    print(f'  within {W} s: price trades through our bid (queue-free fill) {hit[("through", W)]/tot*100:.1f}% ; sell volume at/below our price >= queue ahead + 500: {hit[("vol>=ahead", W)]/tot*100:.1f}%')
res['paper'] = {str(W): dict(through_pct=hit[('through', W)] / tot * 100, vol_ge_ahead_pct=hit[('vol>=ahead', W)] / tot * 100) for W in (30, 60)}; res['paper_n'] = tot
json.dump(res, open(OUT, 'w'), indent=1)
