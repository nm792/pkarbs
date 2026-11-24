"""Planted-pickoff tests for macro_pickoff_score.py. Run: python3 -I test_macro_pickoff_score.py (PASS or FAIL, exit 1). Every check can fail."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from macro_pickoff_score import score

R = 1000000.0   # release, seconds
def mk(delay, min_size=5, fee=0.01):
    return {'cond': 'c1', 'q': 'q', 'title': 'b', 'outcomes': ['Yes', 'No'], 'tokens': ['Y', 'N'], 'seconds_delay': delay, 'min_size': min_size, 'fee': {'rate': fee}}
def row(t, tok, price, size):
    return {'recv_ms': t * 1000, 'asset': tok, 'asks': [{'price': price, 'size': size}] if price is not None else []}
W = {'c1': 'Yes'}
bad = []

# 1. stale ask 0.40 stays up through the print: must fill at 0.40 with positive P&L, shares = 200/0.40 capped by level size 1000
b = {'Y': [row(R - 60, 'Y', 0.40, 1000)], 'N': [row(R - 60, 'N', 0.62, 1000)]}
r = score([mk(0)], b, R, W)
f = r['rows'][0]
if f['result'] != 'FILLED' or abs(f['price'] - 0.40) > 1e-9 or f['pnl'] <= 0 or abs(f['shares'] - 500) > 1e-6: bad.append('1 planted stale ask not filled correctly: %s' % f)

# 2. hold: delay 1 s, ask pulled at R+L+0.5 (before the order lands at R+L+1): must be 'unfilled (hold)'
b = {'Y': [row(R - 60, 'Y', 0.40, 1000), row(R + 1.0, 'Y', 0.99, 1000)], 'N': []}
if score([mk(1)], b, R, W)['rows'][0]['result'] != 'unfilled (hold)': bad.append('2 ask pulled before arrival still filled')
# 2b. same ask pulled AFTER arrival (R+L+1.5): must fill
b = {'Y': [row(R - 60, 'Y', 0.40, 1000), row(R + 2.0, 'Y', 0.99, 1000)], 'N': []}
if score([mk(1)], b, R, W)['rows'][0]['result'] != 'FILLED': bad.append('2b ask still up at arrival not filled')

# 3. seconds_delay unknown: refuse, never assume
if not score([mk(None)], {'Y': [row(R - 60, 'Y', 0.40, 1000)], 'N': []}, R, W)['rows'][0]['result'].startswith('REFUSED'): bad.append('3 null seconds_delay not refused')

# 4. level thinner than the 5-share minimum: no fill
if score([mk(0)], {'Y': [row(R - 60, 'Y', 0.40, 3)], 'N': []}, R, W)['rows'][0]['result'] != 'unfilled (hold)': bad.append('4 thin level filled')

# 5. already repriced to 0.97 at decision: not stale, no fill
if not score([mk(0)], {'Y': [row(R - 60, 'Y', 0.40, 1000), row(R + 0.2, 'Y', 0.97, 1000)], 'N': []}, R, W)['rows'][0]['result'].startswith('not stale'): bad.append('5 repriced ask treated as stale')

# 6. the LOSING token is never bought (winner Yes: N token has a 0.10 ask that must be ignored)
r = score([mk(0)], {'Y': [row(R - 60, 'Y', 0.97, 1000)], 'N': [row(R - 60, 'N', 0.10, 1000)]}, R, W)
if r['filled'] != 0: bad.append('6 loser token bought')

# 7. no hindsight: a cheap ask that appears only AFTER the decision time (R+5) must not be used for the decision price
r = score([mk(0)], {'Y': [row(R - 60, 'Y', 0.97, 1000), row(R + 5, 'Y', 0.30, 1000)], 'N': []}, R, W)
if r['filled'] != 0: bad.append('7 used a book from after the decision')

# 8. $2,000 cap: 11 markets each wanting $200 -> at most 10 filled
mks = []; b = {}
for i in range(11):
    m = mk(0); m['cond'] = 'c%d' % i; m['tokens'] = ['Y%d' % i, 'N%d' % i]; mks.append(m); b['Y%d' % i] = [row(R - 60, 'Y%d' % i, 0.40, 1000)]
r = score(mks, b, R, {m['cond']: 'Yes' for m in mks})
if r['filled'] != 10 or r['stake'] > 2000.01: bad.append('8 cap not enforced: filled %d stake %s' % (r['filled'], r['stake']))

print('FAIL: ' + '; '.join(bad) if bad else 'PASS (9 checks, each able to fail)'); sys.exit(1 if bad else 0)
