"""NBA: when does the Polymarket moneyline price move relative to ESPN's play wallclock?
For every score change, signed move of the home-win price (sign = scorer) in 5 s slices from -60 s to +60 s."""
import sys, os, json, gzip, collections
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
import common as C, backtest as B
B.SPORTS = ['nba']
EV, _ = B.load()
sl = np.arange(-60, 61, 5); acc = np.zeros(len(sl) - 1); n = 0; big = []
for E in EV:
    ml = [m for m in E['markets'] if m['type'] == 'moneyline']
    if not ml: continue
    fn = f"{C.RAW}/us/trades/{ml[0]['cond']}.json.gz"
    if not os.path.exists(fn): continue
    M = C.Mid(C.prints(json.load(gzip.open(fn)))); sgn0 = 1 if ml[0]['kind'] == 'home' else -1
    tl = E['tl']
    for k in range(1, len(tl)):
        dh = (tl[k][3] - tl[k - 1][3]) - (tl[k][4] - tl[k - 1][4])
        if dh == 0: continue
        t = tl[k][0]; s = np.sign(dh) * sgn0
        pts = [M.at(t + x) for x in sl]
        if any(p is None for p in pts) or not (0.1 < pts[0] < 0.9): continue
        acc += s * np.diff(pts); n += 1
print('score changes', n)
cum = np.cumsum(acc) / n * 100
for a, c in zip(sl[1:], cum): print(f'{a:>4}s  cumulative signed move {c:6.2f}c')
