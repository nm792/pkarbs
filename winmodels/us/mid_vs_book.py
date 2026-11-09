"""Is the sim's trade-derived mid (common.Mid, 'pair' mode, read QDELAY=1 s late) close to the real book mid?
Per snapshot of each NBA moneyline token in the 1 s book capture. Reports abs error, how often the sim's
bid (mid x 0.975) would sit AT/ABOVE the real best ask (a crossing, non-maker bid) or above the best bid."""
import sys, os, json, math, collections, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))
import common as C
BOOKS, MKTS = sys.argv[1], sys.argv[2]
M = json.load(open(MKTS)); snap = collections.defaultdict(list)
for l in open(BOOKS):
    r = json.loads(l)
    if 'tok' in r and r['bids'] and r['asks']: snap[r['tok']].append(r)
err = []; above_bid = cross = n = 0; stale = []
for m in M:
    allr = [r for t in m['tokens'] for r in snap.get(t, [])]
    if not allr: continue
    T0 = min(r['recv_ms'] for r in allr) / 1000; T1 = max(r['recv_ms'] for r in allr) / 1000
    pr = C.prints(C.pull_trades(m['cond'], T0 - 600, T1 + 600, 'us_live/trades')); Mi = C.Mid(pr)
    S0 = snap.get(m['tokens'][0], [])
    for r in S0:
        bb, ba = r['bids'][0][0], r['asks'][0][0]; bm = (bb + ba) / 2; T = r['recv_ms'] / 1000
        sm = Mi.at(T - C.QDELAY)
        if sm is None or not (0.05 < bm < 0.95): continue
        n += 1; err.append(abs(sm - bm)); b = sm * 0.975
        above_bid += b > bb + 1e-9; cross += b >= ba - 1e-9
err = np.array(err) * 100
print(f'token-0 snapshots {n}: |sim mid - book mid| median {np.median(err):.2f}c, p90 {np.percentile(err,90):.2f}c, p99 {np.percentile(err,99):.2f}c')
print(f'sim bid (mid x 0.975) above the real best bid: {above_bid/n*100:.1f}% of snapshots; at/above the real best ask (would cross): {cross/n*100:.1f}%')
json.dump(dict(n=n, med_c=float(np.median(err)), p90_c=float(np.percentile(err, 90)), p99_c=float(np.percentile(err, 99)), above_best_bid_pct=above_bid / n * 100, cross_pct=cross / n * 100),
          open(os.path.join(HERE, 'out_mid_vs_book.json'), 'w'), indent=1)
