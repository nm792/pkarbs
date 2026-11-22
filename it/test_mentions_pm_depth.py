"""Offline checks for mentions_pm_depth.py. Run: python3 -I test_mentions_pm_depth.py <mentions_pm_depth.py> <mentions_pm_daily_scorer.py>"""
import sys, importlib.util
def L(n, p):
    sp = importlib.util.spec_from_file_location(n, p); m = importlib.util.module_from_spec(sp); sys.modules[n] = m; sp.loader.exec_module(m); return m
a = sys.argv[1:]; sys.argv = [sys.argv[0], '--scorer', a[1], '--state', '/tmp', '--out', '/tmp/x']
D = L('d', a[0]); sc = L('sc', a[1]); ok = N = 0
def chk(n, c):
    global ok, N; N += 1; ok += bool(c); print('check', N, 'ok' if c else 'FAIL', n)
T0 = 1_800_000_000.0
def mk(c, w, yes, ct): return dict(cond=c, word=sc.norm(w), label=w, prices=[1., 0.] if yes else [0., 1.], toks=['y' + c, 'n' + c], closed=True, start='2026-01-01T00:00:00+00:00', closedTime=ct, fee=.04)
H = [dict(id=f'h{i}', title='x', fam='other', closed=True, markets=[mk(f'h{i}{w}', w, 1, '2026-01-01T00:00:00+00:00') for w in 'abc']) for i in range(5)]
E = dict(id='f', title='x', fam='other', closed=True, markets=[mk('fa', 'a', 1, '2026-01-02T00:00:00+00:00'), mk('fb', 'b', 1, '2026-01-02T00:00:00+00:00'), mk('fc', 'c', 1, '2026-01-02T00:00:00+00:00')])
tr = {'fa': [(T0 + 10, 'BUY', .50, 100, 0), (T0 + 20, 'BUY', .60, 50, 0)], 'fb': [(T0 + 30, 'BUY', .97, 100, 0), (T0 + 4000, 'BUY', .50, 100, 0), (T0 + 40, 'SELL', .50, 100, 0)], 'fc': [(T0 + 50, 'BUY', .30, 10, 1)]}
r = D.print_depth(sc, E, H, tr, T0)   # q = 1 for all words (always yes) -> YES edge = 1-p; NO edge = 0-p <0
chk('YES prints at .50 and .60 count: 100*.5+50*.6 = 80', abs(r['usd_yes'] - 80) < 1e-6)
chk('.97 out of range, late print, SELL, NO print (edge<0) all excluded', r['n_prints'] == 2 and r['usd_no'] == 0)
chk('first print notional = 50', r['first_print_usd'] == 50)
chk('ask depth counts only asks at or under the limit', abs(D.ask_depth([(.5, 100), (.8, 100), (.02, 1000)], .6) - 50) < 1e-9)
chk('summary: share >= $200', D.summarize([dict(usd_total=250), dict(usd_total=10), dict(usd_total=0)])['events_ge_200'] == 1)
print(f'{"PASS" if ok == N else "FAIL"} ({ok} of {N} checks)'); sys.exit(0 if ok == N else 1)
