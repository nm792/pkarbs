"""How late is ESPN's goal wallclock vs the Polymarket price jump? (moneyline 'home win' market)"""
import sys, os, json, gzip
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
import common as C, backtest as B
EV, _ = B.load_events(); d = []
for E in EV:
    hm = [m for m in E['markets'] if m['kind'] == 'home' and m['type'] == 'moneyline']
    if not hm: continue
    fn = f"{C.RAW}/soccer/trades/{hm[0]['cond']}.json.gz"
    if not os.path.exists(fn): continue
    pr = C.prints(json.load(gzip.open(fn))); M = C.Mid(pr)
    for (t, k, s) in E['tl']:
        if k != 'g': continue
        p0 = M.at(t - 240)
        if p0 is None: continue
        sg = 1 if s == 'home' else -1
        for (T, _, ph, _, _) in pr:
            if T < t - 240: continue
            if T > t + 300: break
            if sg * (ph - p0) > 0.06: d.append(T - t); break
d = np.array(d); print('goals with a >6c move in the home-win market within -240..+300 s:', len(d))
print('first such print minus ESPN wallclock, s: percentiles 10/25/50/75/90 =', np.percentile(d, [10, 25, 50, 75, 90]).round(0))
print('share of moves before the ESPN wallclock:', round(float((d < 0).mean()), 2), ' before wallclock+10s:', round(float((d < 10).mean()), 2))
