"""Offline check. Run: python3 -I test_mentions_pm_earnings_table.py <earnings_table.py> <scorer> <backtest>"""
import sys, importlib.util
def L(n, p):
    sp = importlib.util.spec_from_file_location(n, p); m = importlib.util.module_from_spec(sp); sys.modules[n] = m; sp.loader.exec_module(m); return m
a = sys.argv[1:]; sys.argv = [sys.argv[0], '--scorer', a[1], '--backtest', a[2], '--state', '/tmp', '--out', '/tmp/x', '--freeze', '2026-01-01T00:00:00+00:00']
E_ = L('e', a[0]); sc = L('sc', a[1]); bt = L('bt', a[2]); ok = N = 0
def chk(n, c):
    global ok, N; N += 1; ok += bool(c); print('check', N, 'ok' if c else 'FAIL', n)
T0 = 1_800_000_000.0
def mk(c, w, yes): return dict(cond=c, word=sc.norm(w), label=w, prices=[1., 0.] if yes else [0., 1.], toks=['y' + c, 'n' + c], closed=True, start='2026-01-01T00:00:00+00:00', closedTime='2026-01-01T00:00:00+00:00', fee=.04)
H = [dict(id=f'h{i}', title='x', fam='earnings-call', closed=True, markets=[mk(f'h{i}{w}', w, 1) for w in 'abc']) for i in range(5)]
E = dict(id='f', title='Acme earnings', fam='earnings-call', closed=True, markets=[mk('fa', 'a', 1), mk('fb', 'b', 1), mk('fc', 'c', 1)])
tr = {'fa': [(T0 + 10, 'BUY', .5, 100, 0), (T0 + 90000, 'BUY', .9, 10, 0)], 'fb': [], 'fc': [(T0 + 20, 'BUY', .97, 50, 0)]}
r = E_.call_row(sc, bt, E, H, tr, T0)
chk('event volume = 50 + 9 + 48.5 = 107.5 -> 108', r['event_usd_total'] == 108)
chk('first 24h volume excludes the day-2 print (50 + 48.5 -> 98 or 99)', r['event_usd_first24h'] in (98, 99))
chk('qualifying first-hour print $ = 50 (.97 out of range)', r['qualifying_print_usd_first_hour'] == 50.0)
chk('contracts counted', r['contracts'] == 3)
print(f'{"PASS" if ok == N else "FAIL"} ({ok} of {N} checks)'); sys.exit(0 if ok == N else 1)
