"""Checks for rerun.py; each can fail. Run: python3 -I test_rerun.py"""
import os, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rerun, scan
R = 1_800_000_000; W, LOSE = 'W', 'L'
def row(d, tok, side, p, sz=100): return dict(ts=R + d, tok=tok, side=side, p=p, sz=sz)
m = dict(cid='c', tok='["W","L"]', op='["1","0"]', vol='10', fee={'rate': 0.04, 'exponent': 1})
e = dict(id='1', markets=[m])
rows = [row(-120, W, 'BUY', .30), row(5, W, 'BUY', .80, 50)]
r = rerun.event_result(e, {}, R, fetch=lambda c: rows)
exp = 50 * .2 - 50 * .04 * .8 * .2
assert abs(r['stats'][0]['edge_after_fee'] - round(exp, 2)) < 1e-9, r                       # fee deducted per share
assert r['stats'][0]['edge_after_fee'] < 50 * .2                                             # strictly below the no-fee edge
r2 = rerun.event_result(e, {}, R, fetch=lambda c: [row(5, W, 'BUY', .80, 50)])               # prints start after R-60: incomplete
assert r2['incomplete'] == 1 and r2['stats'][0]['n'] == 0
r3 = rerun.event_result(e, {}, R + 10, fetch=lambda c: rows)                                 # news R later than the print: not counted
assert r3['stats'][0]['n'] == 0
m2 = dict(m, fee=None); r4 = rerun.event_result(dict(id='2', markets=[m2]), {}, R, fetch=lambda c: rows)
assert r4['no_fee_schedule'] == 1 and abs(r4['stats'][0]['edge_after_fee'] - 10.0) < 1e-9
f = tempfile.NamedTemporaryFile('w', suffix='.csv', delete=False); f.write('event_id,news_utc\n7,2027-01-15T08:00:00Z\n8,bad\n'); f.close()
nr = rerun.news_R(f.name); assert nr == {'7': (1800000000, '')} and '8' not in nr, nr
lb, ub = rerun.window([row(3, W, 'BUY', .7), row(9, W, 'BUY', .9), row(12, W, 'BUY', .97), row(20, W, 'BUY', .8)], W, R)
assert (lb, ub) == (9, 12), (lb, ub)                                                          # window bracket; a re-posted ask after W_ub is ignored
def mk(a, edge, w): return dict(anchor=a, stats={5: dict(edge_after_fee=edge)}, W_lb_max=w)
big = [mk('news', 50, 30) for _ in range(15)] + [mk('calendar', 10, 3) for _ in range(15)]
assert rerun.compare(big, draws=2000)['verdict'] == 'SUPPORTS H'
rev = [mk('news', 10, 3) for _ in range(15)] + [mk('calendar', 50, 30) for _ in range(15)]
assert rerun.compare(rev, draws=2000)['verdict'] == 'AGAINST H'
same = [mk('news', 10, 3) for _ in range(15)] + [mk('calendar', 10, 3) for _ in range(15)]
assert rerun.compare(same, draws=2000)['verdict'] != 'SUPPORTS H'
print('ALL RERUN CHECKS PASS (10)')
