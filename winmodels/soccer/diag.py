"""Diagnostic: where do the losses come from? Split fills by time to the nearest goal (ESPN wallclock)."""
import sys, os, json, gzip, collections, bisect
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
import common as C, backtest as B, model as SM
EV, _ = B.load_events()
agg = collections.defaultdict(lambda: np.zeros(4)); n = collections.Counter()
for E in EV[:400]:
    g = [x[0] for x in E['tl'] if x[1] == 'g']
    for m in E['markets']:
        if m['type'] != 'moneyline': continue
        fn = f"{C.RAW}/soccer/trades/{m['cond']}.json.gz"
        if not os.path.exists(fn): continue
        pr = C.prints(json.load(gzip.open(fn)));
        if len(pr) < 20: continue
        M = C.Mid(pr)
        # replicate sim baseline but keep fill times
        for (T, _, ph, sell0, sz) in pr:
            if not (E['k1'] <= T <= E['e2']): continue
            mk = M.at(T - 1)
            if mk is None or not (0.05 <= mk <= 0.95): continue
            lastT = M.t[max(bisect.bisect_left(M.t, T) - 1, 0)]
            for tok, cond, b, px in ((0, sell0, mk * 0.975, ph), (1, not sell0, (1 - mk) * 0.975, 1 - ph)):
                if not cond or px >= b - 1e-9: continue
                d = min([T - x for x in g], key=abs, default=9999)
                k = 'goal -300..-60s' if -300 <= d < -60 else 'goal -60..+120s' if -60 <= d <= 120 else 'goal +120..600s' if 120 < d <= 600 else 'no goal within 5-10 min'
                stale = 'mid age>120s' if T - lastT > 120 else 'mid age<=120s'
                q = min(sz, 100); m60 = M.at(T + 60); m60 = m60 if tok == 0 else 1 - m60
                gap = (b - px) / b
                for kk in (k, stale, 'print gap>5%' if gap > 0.05 else 'print gap<=5%'):
                    agg[kk] += [q * b, q * (m60 - b), q * ((1.0 if m['win0'] == (tok == 0) else 0.0) - b), 1]
for k, v in sorted(agg.items()): print(f'{k:28} fills {int(v[3]):>7} $ {v[0]:>9.0f} 1min {100*v[1]/v[0]:>6.1f}% result {100*v[2]/v[0]:>6.1f}%')
