"""Planted checks for source_yahoo (each can fail)."""
import sys, json, pickoff_core as C, source_yahoo as Y
bad = []
def ck(c, m):
    if not c: bad.append(m)
R = 1795802400
doc = {'chart': {'result': [{'timestamp': [R - 120, R - 60], 'indicators': {'quote': [{'close': [126.0, 127.31]}]}}]}}
s = Y.Source({'nvda-week-november-27-2026': []}, '/tmp', release_s=R, fetcher=lambda u: doc, now=lambda: R + 1)
ck(s.poll() == [], 'nothing before R+5')
s.now = lambda: R + 6
o = s.poll(); ck(len(o) == 1 and o[0][2] == 127.31, 'final-minute close: %s' % o)
s.fetch = lambda u: {'chart': {'result': [{'timestamp': [R - 120], 'indicators': {'quote': [{'close': [1.0]}]}}]}}
ck(s.poll() == [], 'bar not published -> nothing')
mk = [{'cond': 'a', 'q': 'Will NVDA finish week of November 27 above $127.50?'}, {'cond': 'b', 'q': 'Will NVDA finish week of November 27 above $120?'}]
tt = C.truth_table(mk, 127.31, guard_frac=0.003)
ck(tt == {'a': None, 'b': True}, 'guard 0.3%% skips the near line: %s' % tt)
print('FAIL: ' + '; '.join(bad) if bad else 'PASS (4 checks)'); sys.exit(1 if bad else 0)
