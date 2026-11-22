"""Offline checks. Run: python3 -I test_mentions_pm_open_depth.py <mentions_pm_open_depth.py> <scorer>"""
import sys, importlib.util
a = sys.argv[1:]; sys.argv = [sys.argv[0], '--scorer', a[1], '--state', '/tmp', '--out', '/tmp/x']
sp = importlib.util.spec_from_file_location('od', a[0]); D = importlib.util.module_from_spec(sp)
ok = N = 0
def chk(n, c):
    global ok, N; N += 1; ok += bool(c); print('check', N, 'ok' if c else 'FAIL', n)
sys.modules['sc'] = importlib.util.module_from_spec(importlib.util.spec_from_file_location('sc', a[1])); sp.loader.exec_module(D)
asks = [(.30, 100), (.40, 1000), (.80, 500), (.03, 10)]
r = D.token_row(asks, .6, 0)   # YES fair .6, limit .5: asks .30 and .40 qualify, .03 below 5c excluded
chk('full ladder $ = 30+400+400+0.3', abs(r['full_usd'] - 830.3) < 1e-6)
chk('edge-priced $ = 30 + 400 (<= .50, >= .05)', abs(r['edge_usd'] - 430) < 1e-6 and r['edge_levels'] == 2)
n = D.token_row(asks, .6, 1)   # NO fair .4, limit .30 -> .30 qualifies (30$)
chk('NO side uses 1-q as fair: limit .30 includes the .30 ask only', abs(n['edge_usd'] - 30) < 1e-6 and n['side'] == 'NO' and abs(n['fair'] - .4) < 1e-9)
chk('best ask is min price', r['best_ask'] == .03)
print(f'{"PASS" if ok == N else "FAIL"} ({ok} of {N} checks)'); sys.exit(0 if ok == N else 1)
