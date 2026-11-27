"""Planted checks for source_ibkr (no IBKR connection; each can fail)."""
import sys, source_ibkr as I
bad = []
def ck(c, m):
    if not c: bad.append(m)
R = 1795802400
class FakeStream:
    def __init__(self): self.subs = []; self.B = {}
    def subscribe(self, t): self.subs.append(t); self.B.setdefault(t, [])
    def bars(self, t): return self.B[t]
F = FakeStream(); T = [R - 200]
s = I.Source({'nvda-week-november-27-2026': [], 'spy-week-november-27-2026': []}, '/tmp', release_s=R, stream=F, now=lambda: T[0])
s.poll(); ck(F.subs == [], 'no subscription before R-120')
T[0] = R - 100; s.poll(); ck(sorted(F.subs) == ['NVDA', 'SPY'], 'streams subscribed from R-120: %s' % F.subs)
F.B['NVDA'] = [(R - 15, 127.20, 300), (R - 10, 127.31, 200), (R - 5, 0.0, 0)]
F.B['SPY'] = [(R - 10, 600.0, 10)]
ck(s.poll() == [], 'nothing before R even with bars in')
T[0] = R + 0.3
o = s.poll()
ck(len(o) == 1 and o[0][0].startswith('nvda') and o[0][2] == 127.31, 'released at R+0.3 s: last traded bar in final minute; SPY waits for the bar ending at R: %s' % o)
F.B['SPY'].append((R - 5, 600.5, 5)); o2 = s.poll()
ck(len(o2) == 1 and o2[0][2] == 600.5 and s.poll() == [], 'SPY released when its R-5 bar lands, once: %s' % o2)
ck(I.final_minute_close([(R - 70, 1.0, 5), (R, 2.0, 5)], R) is None, 'no trade inside the final minute -> None (not a stale earlier price)')
ck(I.Source.POLL_S <= 0.05, 'polls every 50 ms')
print('FAIL: ' + '; '.join(bad) if bad else 'PASS (7 checks)'); sys.exit(1 if bad else 0)
