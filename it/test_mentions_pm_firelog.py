"""Offline checks. Run: python3 -I test_mentions_pm_firelog.py <mentions_pm_firelog.py> <mentions_pm_daily_scorer.py>"""
import sys, importlib.util
def L(n, p):
    sp = importlib.util.spec_from_file_location(n, p); m = importlib.util.module_from_spec(sp); sys.modules[n] = m; sp.loader.exec_module(m); return m
a = sys.argv[1:]; sys.argv = [sys.argv[0], '--scorer', a[1], '--state', '/tmp', '--out', '/tmp/x']
F = L('f', a[0]); ok = N = 0
def chk(n, c):
    global ok, N; N += 1; ok += bool(c); print('check', N, 'ok' if c else 'FAIL', n)
asks = [(.30, 100), (.40, 1000), (.80, 5000)]
chk('limit: YES q=.6 -> .50 ; NO q=.6 -> .30', abs(F.limit_price(.6, 0, .1) - .5) < 1e-9 and abs(F.limit_price(.6, 1, .1) - .3) < 1e-9)
f = F.fills_at(asks, .5, 200.)
chk('walks .30x100 ($30) then .40 up to $200 total; ask at .80 never touched', abs(f['cost'] - 200) < 1e-6 and abs(f['size'] - (100 + 170 / .4)) < 1e-6 and not f['partial'])
chk('depth_usd counts only asks <= limit (30 + 400 = 430)', abs(f['depth_usd'] - 430) < 1e-6)
g = F.fills_at([(.30, 100)], .5, 200.)
chk('short depth -> partial fill of $30, flagged', g['partial'] and abs(g['cost'] - 30) < 1e-9)
chk('no ask under limit -> size 0', F.fills_at([(.60, 100)], .5, 200.)['size'] == 0)
chk('ask exactly at limit is allowed (edge = 10c)', F.fills_at([(.50, 10)], .5, 200.)['size'] == 10)
chk('day cap room 50 limits the bet to $50', abs(F.paper_bet(asks, .5, 200., 50., .04)['cost'] - 50) < 1e-6)
chk('no room left -> no bet', F.paper_bet(asks, .5, 200., 0., .04) is None)
chk('parse_asks sorts and floats', F.parse_asks({'asks': [{'price': '0.5', 'size': '3'}, {'price': '0.2', 'size': '1'}]}) == [(.2, 1.), (.5, 3.)])
runs = [dict(t=1000 - 120 * i, pid=5, books_expected=10, books_read=10) for i in range(7)]
w, rr, rb, be, br, errs, okh = F.health_eval(runs, 1000, '')
chk('health PASS: 7 runs, 100% books, no errors', okh and rb == 1.0)
chk('health FAIL on 90% books', not F.health_eval([dict(r, books_read=9) for r in runs], 1000, '')[-1])
chk('health FAIL on a traceback in the log', not F.health_eval(runs, 1000, 'Traceback (most recent call last)')[-1])
chk('health FAIL when only 3 runs in 15 min (stopped cron)', not F.health_eval(runs[:3], 1000, '')[-1])
print(f'{"PASS" if ok == N else "FAIL"} ({ok} of {N} checks)'); sys.exit(0 if ok == N else 1)
