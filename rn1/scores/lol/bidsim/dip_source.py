"""Where does the 'timing + veto E=5%' P&L come from? Classify each fill by the latest event cluster in the
30 s before it (pj = event model's predicted move for OUR token, rm = market move of our token from
pre-event anchor to fill time):
 A no event in prior 30 s; B event, predicted move < 1c; C market moved opposite to prediction (wrong way);
 D same direction, |rm| > |pj| (overshoot); E same direction, |rm| <= |pj| (not yet caught up)."""
import os, sys, numpy as np, collections
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
os.environ['LOAD_ONLY'] = '1'
import veto_timing as V
def cls(ev):
    if ev is None: return 'A no event in prior 30 s'
    pj, rm = ev
    if abs(pj) < 0.01: return 'B event, predicted move <1c'
    if np.sign(rm) != np.sign(pj): return 'C moved opposite to prediction'
    return 'D same way, overshot prediction' if abs(rm) > abs(pj) else 'E same way, not yet caught up'
agg = collections.defaultdict(lambda: np.zeros(5)); sub = collections.defaultdict(lambda: collections.Counter())
for gid, (G, M, ff, x, fb) in V.B.GAMES.items():
    for z in V.run(G, M, ff, timing=True, veto=0.05):
        c = cls(z[4]); agg[c] += np.array([*z[:4], 1])
        if z[4] is not None and abs(z[4][0]) >= 0.01: sub[c]['ours_favoured' if z[4][0] > 0 else 'ours_hurt'] += z[0]
tot = sum(a[2] + a[3] for a in agg.values()); U = sum(a[0] for a in agg.values())
print(f"{'class':34}{'fills':>7}{'$filled':>10}{'%$':>6}{'1min%':>7}{'res%':>7}{'res$':>9}{'share':>7}")
for c in sorted(agg):
    a = agg[c]; r = a[2] + a[3]
    print(f"{c:34}{int(a[4]):>7}{a[0]:>10.0f}{100*a[0]/U:>6.1f}{100*(a[1]+a[3])/a[0]:>7.2f}{100*r/a[0]:>7.2f}{r:>9.0f}{100*r/tot:>6.0f}%  {dict((k, round(v)) for k, v in sub[c].items())}")
print('total res$', round(tot), 'filled', round(U))
