import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import macro_latency_table as T
R = 1000000.0; bad = []
def mk(c='c1'): return {'cond': c, 'q': 'q', 'title': 'b', 'outcomes': ['Yes', 'No'], 'tokens': ['Y', 'N'], 'seconds_delay': 0, 'min_size': 5, 'fee': {'rate': 0.0}}
def row(t, price, size): return {'recv_ms': t * 1000, 'asset': 'Y', 'asks': [{'price': price, 'size': size}] if price else []}
W = {'c1': 'Yes'}
# A. liquidity posted LATER: book empty at R+0.5, a 0.40 ask of 500 appears at R+3: no fill at 0.5 s, fill at 5 s, flagged posted later (first seen 3 s after R, NOT available at Lmin)
b = {'Y': [row(R - 60, None, 0), row(R + 3, 0.40, 500)], 'N': []}
t = T.table([mk()], b, R, W, [0.5, 5])
r05, r5 = t[0], t[1]
if r05['result'] == 'FILLED': bad.append('A fills at 0.5 s although nothing was posted')
if r5['result'] != 'FILLED' or r5.get('available_at_Lmin') is not False or abs(r5.get('level_first_seen_after_R_s', -1) - 3.0) > 1e-6: bad.append('A posted-later flag wrong: %s' % r5)
# B. stale ask that was there all along: fills at both, available at Lmin True, P&L the same
b = {'Y': [row(R - 60, 0.40, 500)], 'N': []}
t = T.table([mk()], b, R, W, [0.5, 5])
if not (t[0]['result'] == t[1]['result'] == 'FILLED' and t[0]['available_at_Lmin'] and t[0]['pnl'] == t[1]['pnl']): bad.append('B always-there level mislabelled: %s' % t)
# C. repriced during the window: cheap at 0.5 s, 0.97 by 5 s: fills at 0.5, not at 5 (P&L must FALL with latency)
b = {'Y': [row(R - 60, 0.40, 500), row(R + 2, 0.97, 500)], 'N': []}
t = T.table([mk()], b, R, W, [0.5, 5])
if not (t[0]['result'] == 'FILLED' and t[1]['result'].startswith('not stale')): bad.append('C repricing case wrong: %s' % t)
# D. lookahead guard: a row stamped after the decision time can never be the decision row
import macro_pickoff_score as S
rows = [row(R + 9, 0.30, 500)]
if S.last_at(rows, (R + 5) * 1000) is not None: bad.append('D last_at returned a future row')
print('FAIL: ' + '; '.join(bad) if bad else 'PASS (4 latency-table checks)'); sys.exit(1 if bad else 0)
