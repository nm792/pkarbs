"""Where do NBA plain-rule (d=2.5%) losses come from? Split fills by market type, fill price, game fraction and fill size."""
import sys, os, collections, bisect
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
import common as C, nba_guard as NG, backtest as B
games = NG.prep(); A = collections.defaultdict(lambda: np.zeros(4))
for g in games:
    E = g['E']; tt = [r[0] for r in E['tl']]
    for m, pr, M in g['mk']:
        for (T, _, ph, sell0, sz) in pr:
            if not (E['t0'] <= T <= E['t1']): continue
            mk = M.at(T - 1)
            if mk is None or not (0.05 <= mk <= 0.95): continue
            for tok, cond, b, px in ((0, sell0, mk * 0.975, ph), (1, not sell0, (1 - mk) * 0.975, 1 - ph)):
                if not cond or px >= b - 1e-9: continue
                q = min(sz, 100); m60 = M.at(T + 60); m60 = m60 if tok == 0 else 1 - m60
                i = bisect.bisect_right(tt, T) - 1; fr = B.frac('nba', E['tl'][i][1], E['tl'][i][2]) if i >= 0 else 0
                gap = (b - px) / b
                row = [q * b, q * (m60 - b), q * ((1.0 if m['win0'] == (tok == 0) else 0.0) - b), 1]
                for key in (('type', m['type']), ('price', f'{int(b*5)/5:.1f}-{int(b*5)/5+0.2:.1f}'), ('game', f'{int(fr*4)/4:.2f}'),
                            ('print size', 'q<100' if sz < 100 else 'q>=100'), ('print gap', '<1%' if gap < 0.01 else '1-3%' if gap < 0.03 else '3-10%' if gap < 0.1 else '>10%')):
                    A[key] += row
for k in sorted(A):
    v = A[k]; print(f'{k[0]:11}{k[1]:10} fills {int(v[3]):>7} $ {v[0]:>9.0f} 1min {100*v[1]/v[0]:>6.2f}% result {100*v[2]/v[0]:>6.2f}%')
