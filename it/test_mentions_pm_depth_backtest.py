"""Offline checks. Run: python3 -I test_mentions_pm_depth_backtest.py <mentions_pm_depth_backtest.py> <mentions_pm_daily_scorer.py>"""
import sys, importlib.util
def L(n, p):
    sp = importlib.util.spec_from_file_location(n, p); m = importlib.util.module_from_spec(sp); sys.modules[n] = m; sp.loader.exec_module(m); return m
a = sys.argv[1:]; sys.argv = [sys.argv[0], '--scorer', a[1], '--state', '/tmp', '--out', '/tmp/x', '--freeze', '2026-01-01T00:00:00+00:00']
D = L('d', a[0]); sc = L('sc', a[1]); ok = N = 0
def chk(n, c):
    global ok, N; N += 1; ok += bool(c); print('check', N, 'ok' if c else 'FAIL', n)
T0 = 1_800_000_000.0
def mk(c, w, yes): return dict(cond=c, word=sc.norm(w), label=w, prices=[1., 0.] if yes else [0., 1.], toks=['y' + c, 'n' + c], closed=True, start='2026-01-01T00:00:00+00:00', closedTime='2026-01-01T00:00:00+00:00', fee=0.04)
H = [dict(id=f'h{i}', title='x', fam='other', closed=True, markets=[mk(f'h{i}{w}', w, 1) for w in 'abc']) for i in range(5)]
E = dict(id='f', title='x', fam='other', closed=True, markets=[mk('fa', 'a', 1), mk('fb', 'b', 1), mk('fc', 'c', 1)])
tr = {'fa': [(T0 + 10, 'BUY', .50, 100, 0), (T0 + 20, 'BUY', .60, 1000, 0), (T0 + 30, 'BUY', .99, 100, 0), (T0 + 40, 'BUY', .70, 100, 1), (T0 + 5000, 'BUY', .5, 100, 0)]}
r = D.sweep(sc, E, H, tr, T0, 200.)
# q=1: YES edge = 1-p. prints: .50x100 = $50, .60x1000 -> room 150 -> 250 shares; total cost $200; .99 out of range; NO print edge<0; late ignored
chk('sweep takes 100@.50 then 250@.60 up to $200', r and abs(r['cost'] - 200) < 1e-6 and r['n_fills'] == 2)
exp = (1 - .5) * 100 - 100 * .04 * .5 * .5 + (1 - .6) * 250 - 250 * .04 * .6 * .4
chk('net P&L = gross - taker fee on every fill', abs(r['pnl'] - exp) < 1e-6)
chk('cap 40 limits notional to $40', abs(D.sweep(sc, E, H, tr, T0, 40.)['cost'] - 40) < 1e-6)
chk('no qualifying print -> None', D.sweep(sc, E, H, {'fa': [(T0 + 10, 'BUY', .99, 10, 0)]}, T0, 200.) is None)
b = [dict(day='d1', start=1, cost=1500., pnl=150.), dict(day='d1', start=2, cost=1500., pnl=300.), dict(day='d2', start=3, cost=100., pnl=10.)]
c = D.apply_daycap(b, 2000.)
chk('day cap: 2nd bet scaled to $500 of its $1500; other day untouched', abs(c[1]['cost'] - 500) < 1e-9 and abs(c[1]['pnl'] - 100) < 1e-9 and c[2]['cost'] == 100)
per, mkv = D.volume(E, {'fa': [(T0, 'BUY', .5, 100, 0), (T0 + 90000, 'SELL', .4, 50, 1)]})
chk('volume = price*size over all sides, per UTC day', abs(sum(per.values()) - 70) < 1e-9 and len(per) == 2 and abs(mkv['fa'] - 70) < 1e-9)
chk('trump-event and trump-weekly merge into segment trump', D.segment('trump-weekly') == 'trump' and D.segment('earnings-call') == 'earnings-call')
print(f'{"PASS" if ok == N else "FAIL"} ({ok} of {N} checks)'); sys.exit(0 if ok == N else 1)
