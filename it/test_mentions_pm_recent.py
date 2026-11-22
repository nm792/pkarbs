"""Offline check. Run: python3 -I test_mentions_pm_recent.py <mentions_pm_recent.py> <scorer> <backtest>"""
import sys, importlib.util
a = sys.argv[1:]; sys.argv = [sys.argv[0], '--scorer', a[1], '--backtest', a[2], '--state', '/tmp', '--out', '/tmp/x']
sp = importlib.util.spec_from_file_location('r', a[0]); R = importlib.util.module_from_spec(sp); sp.loader.exec_module(R)
tr = {'a': [(100, 'BUY', .5, 100, 0), (200, 'SELL', .4, 50, 1), (300, 'BUY', .9, 10, 0)], 'b': [(150, 'BUY', .2, 10, 1)]}
ok = N = 0
def chk(n, c):
    global ok, N; N += 1; ok += bool(c); print('check', N, 'ok' if c else 'FAIL', n)
chk('window [100,300) = 50 + 20 + 2 = 72 (t=300 excluded)', abs(R.vol_between(tr, 100, 300) - 72) < 1e-9)
chk('empty window = 0', R.vol_between(tr, 500, 600) == 0)
chk('whole range = 50+20+9+2 = 81', abs(R.vol_between(tr, 0, 9e18) - 81) < 1e-9)
print(f'{"PASS" if ok == N else "FAIL"} ({ok} of {N} checks)'); sys.exit(0 if ok == N else 1)
