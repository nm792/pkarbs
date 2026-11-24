"""Offline checks. Run: python3 -I test_mentions_pm_event_time.py <mentions_pm_event_time.py> <scorer> <backtest>"""
import sys, importlib.util
a = sys.argv[1:]; sys.argv = [sys.argv[0], '--scorer', a[1], '--backtest', a[2], '--state', '/tmp', '--out', '/tmp/x', '--days', '7']
def L(n, p):
    sp = importlib.util.spec_from_file_location(n, p); m = importlib.util.module_from_spec(sp); sys.modules[n] = m; sp.loader.exec_module(m); return m
sc = L('sc', a[1]); bt = L('bt', a[2]); X = L('x', a[0]); ok = N = 0
def chk(n, c):
    global ok, N; N += 1; ok += bool(c); print('check', N, 'ok' if c else 'FAIL', n)
T = 1_800_000_000.0; t0 = T - 100000
def mk(c, w, yes): return dict(cond=c, word=sc.norm(w), label=w, prices=[1., 0.] if yes else [0., 1.], toks=['y', 'n'], closed=True, start='x', closedTime='x', fee=.04)
E = dict(markets=[mk('c1', 'a', 1)])
qs = {'c1': .8}   # YES limit .70; NO fair .2 -> limit .10
tr = {'c1': [(T - 3000, 'BUY', .60, 100, 0), (T - 2900, 'BUY', .75, 100, 0), (T - 2800, 'BUY', .08, 50, 1), (T - 2700, 'SELL', .5, 100, 0), (T - 9000, 'BUY', .5, 100, 0)]}
f = X.fills(sc, E, qs, tr, T - 3600, 3600)
chk('YES print .60 <= .70 filled; .75 above limit not; NO print .08 <= .10 filled; SELL ignored; outside window ignored', len(f) == 2 and {x['side'] for x in f} == {'YES', 'NO'})
chk('$200 cap per token: 100 @.60 = $60 fully taken', abs([x for x in f if x['side'] == 'YES'][0]['cost'] - 60) < 1e-9)
big = {'c1': [(T - 3000, 'BUY', .60, 1000, 0)]}
chk('cap: 1000 shares @.60 trimmed to $200', abs(X.fills(sc, E, qs, big, T - 3600, 3600)[0]['cost'] - 200) < 1e-9)
pnl_yes = [x for x in f if x['side'] == 'YES'][0]['pnl']
chk('YES wins: pnl = (1-.6)*100 - fee', abs(pnl_yes - (40 - 100 * .04 * .6 * .4)) < 1e-9)
chk('decisions T-15m = one 900 s window at T-900; window before listing dropped', X.decisions('T-15m', t0, T, 'A') == [(T - 900, 900)] and X.decisions('T-24h', T - 100, T, 'A') == [])
chk('during A = 72 five-minute slots; B = 36', len(X.decisions('during', t0, T, 'A')) == 72 and len(X.decisions('during', t0, T, 'B')) == 36)
fl = [dict(t=T, cost=1500., pnl=150.), dict(t=T + 1, cost=1500., pnl=300.)]
c = X.daycap(fl, 2000., bt.day)
chk('day cap scales second fill to $500 of $1500', abs(c[1]['cost'] - 500) < 1e-9 and abs(c[1]['pnl'] - 100) < 1e-9)
chk('peak hour picks the hour with most notional', X.peak_hour({'c1': [(3600 * 5 + 10, 'BUY', .5, 10, 0), (3600 * 9 + 10, 'BUY', .5, 100, 0)]}, E) == 3600 * 9)
chk('R-080 addendum PLANTED trades just before and just after the window are excluded (v2 ignores start/end, the screen filters by timestamp)', X.fills(sc, E, qs, {'c1': [(T - 3601, 'BUY', .60, 100, 0), (T + 1, 'BUY', .60, 100, 0)]}, T - 3600, 3600) == [] and len(X.fills(sc, E, qs, {'c1': [(T - 3600, 'BUY', .60, 100, 0), (T, 'BUY', .60, 100, 0)]}, T - 3600, 3600)) == 2)
print(f'{"PASS" if ok == N else "FAIL"} ({ok} of {N} checks)'); sys.exit(0 if ok == N else 1)
