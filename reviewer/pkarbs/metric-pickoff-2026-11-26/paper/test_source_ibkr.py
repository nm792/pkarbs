"""Planted checks for source_ibkr (no IBKR connection; each can fail)."""
import sys, source_ibkr as I
bad = []
def ck(c, m):
    if not c: bad.append(m)
R = 1795802400
B = {'NVDA': [(R - 120, 126.0), (R - 60, 127.31)], 'SPY': [(R - 120, 600.0)]}
s = I.Source({'nvda-week-november-27-2026': [], 'spy-week-november-27-2026': []}, '/tmp', release_s=R, bars=lambda t, r: B[t], now=lambda: R + 1)
ck(s.poll() == [], 'nothing before R+2')
s.now = lambda: R + 3
o = s.poll()
ck(len(o) == 1 and o[0][0].startswith('nvda') and o[0][2] == 127.31, 'final-minute bar close, SPY bar missing -> not sent: %s' % o)
ck(s.poll() == [], 'each event released once')
def boom(t, r): raise RuntimeError('gateway down')
s2 = I.Source({'nvda-week-november-27-2026': []}, '/tmp', release_s=R, bars=boom, now=lambda: R + 3)
ck(s2.poll() == [], 'gateway error -> nothing, no crash')
print('FAIL: ' + '; '.join(bad) if bad else 'PASS (4 checks)'); sys.exit(1 if bad else 0)
