"""Planted checks for mm_core (each can fail). Run: python3 test_mm_core.py"""
import sys, importlib.util, os
import mm_core as M
bad = []
def ck(c, m):
    if not c: bad.append(m)
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))
spec = importlib.util.spec_from_file_location('wp', os.path.join(ROOT, 'it', 'mentions_pm_ws_paper.py')); wp = importlib.util.module_from_spec(spec); spec.loader.exec_module(wp)
ck(M.slots(1000, 200000) == wp.slots(1000, 200000), 'slots identical to the frozen P121 slots')
go, miss = M.due([('a', 100), ('b', 200), ('c', 400)], 250, set())
ck(go == [('b', 200)] and miss == [('a', 100)], 'due/missed at 90 s: %s %s' % (go, miss))
ck(M.mention_order(0.60, 0.45) == (0.5, 400), 'fair .60, ask .45 -> limit .50, 400 sh: %s' % (M.mention_order(0.60, 0.45),))
ck(M.mention_order(0.60, 0.51) is None, 'ask above fair-10c -> no trade')
ck(M.mention_order(0.60, 0.04) is None, 'ask below 5c floor -> no trade')
ck(M.mention_order(0.12, 0.01) is None, 'limit below floor -> no trade')
ck(M.mention_order(0.6, None) is None, 'no ask -> no trade')
f = M.mece_fire([(0.60, 100, 0.0), (0.62, 50, 0.0), (0.70, 80, 0.0)])
ck(f is not None and f[0] == 50 and abs(f[2] - (2 - 1.92)) < 1e-9, 'MECE 3 legs NO sum 1.92 < 2 -> 50 sh (min size), edge 0.08: %s' % (f,))
ck(M.mece_fire([(0.70, 100, 0.0), (0.66, 100, 0.0), (0.70, 100, 0.0)]) is None, 'sum 2.06 >= 2 -> no fire')
ck(M.mece_fire([(0.65, 100, 0.05), (0.66, 100, 0.05), (0.66, 100, 0.05)]) is None, 'fees push 1.97 + 0.034 above 2 -> no fire')
ck(M.mece_fire([(0.6, 100, 0), (0.6, 100, 0)]) is None, 'two legs -> not MECE (needs >= 3)')
ck(M.mece_fire([(0.6, 100, 0), (None, None, 0), (0.6, 100, 0)]) is None, 'missing leg ask -> no fire')
f2 = M.mece_fire([(0.6, 1000, 0), (0.6, 1000, 0), (0.6, 1000, 0)])
ck(f2 and f2[0] == int(200 / 1.8), 'MECE cost cap $200 per set: %s' % (f2,))
print('FAIL: ' + '; '.join(bad) if bad else 'PASS (13 checks)'); sys.exit(1 if bad else 0)
