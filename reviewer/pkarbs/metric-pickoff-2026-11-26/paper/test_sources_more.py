"""Planted checks for source_pyth and source_swiss (each can fail)."""
import json, os, tempfile, sys
import source_pyth as P, source_swiss as W, pickoff_core as C
bad = []
def ck(c, m):
    if not c: bad.append(m)
R = 1795802400  # 2026-11-27T18:00:00Z
ck(P.ticker_of('nvda-week-november-27-2026') == 'NVDA' and P.ticker_of('aapl-above-on-november-27-2026') == 'AAPL', 'ticker')
doc = {'s': 'ok', 't': [R - 120, R - 60, R], 'c': [126.0, 127.31, 127.5]}
ck(P.candle_close(doc, R - 60) == 127.31, 'final-minute candle close')
d = tempfile.mkdtemp()
src = P.Source({'nvda-week-november-27-2026': []}, d, release_s=R, fetcher=lambda u: doc, now=lambda: R - 1)
ck(src.poll() == [], 'nothing before R')
src.now = lambda: R + 2
ck(src.poll()[0][2] == 127.31, 'value at R')
src2 = P.Source({'nvda-week-november-27-2026': []}, d, release_s=R, fetcher=lambda u: {'s': 'ok', 't': [R - 120], 'c': [1.0]}, now=lambda: R + 2)
ck(src2.poll() == [], 'candle not yet published -> nothing')
open(os.path.join(d, 'pyth_method.txt'), 'w').write('hermes')
H = {'feeds': [{'id': 'abc', 'attributes': {'symbol': 'Equity.US.NVDA/USD'}}, {'id': 'zzz', 'attributes': {'symbol': 'Equity.US.NVDA/USD.PRE'}}], 'at': {'parsed': [{'price': {'price': '12731000', 'expo': -5}}]}}
s3 = P.Source({'nvda-week-november-27-2026': []}, d, release_s=R, fetcher=lambda u: H['feeds'] if 'price_feeds' in u else H['at'], now=lambda: R + 2)
ck(abs(s3.poll()[0][2] - 127.31) < 1e-9, 'hermes fallback value')
os.remove(os.path.join(d, 'pyth_method.txt'))
json.dump({'Initiative A': 1, 'Initiative B': 2}, open(os.path.join(d, 'swiss_titles.json'), 'w'))
evs = {'ch': [{'cond': 'a', 'title': 'Initiative A'}, {'cond': 'b', 'title': 'Initiative B'}, {'cond': 'c', 'title': 'Other'}]}
part = {'schweiz': {'vorlagen': [{'vorlagenId': 1, 'vorlageBeendet': True, 'vorlageAngenommen': False}, {'vorlagenId': 2, 'vorlageBeendet': False, 'vorlageAngenommen': None}]}}
full = {'schweiz': {'vorlagen': [{'vorlagenId': 1, 'vorlageBeendet': True, 'vorlageAngenommen': False}, {'vorlagenId': 2, 'vorlageBeendet': True, 'vorlageAngenommen': True}]}}
s = W.Source(evs, d, fetcher=lambda u: part)
ck(s.poll() == [], 'fires only when every mapped proposal is final')
s.fetch = lambda u: full
out = s.poll()
ck(len(out) == 1 and out[0][1].startswith('MAP:'), 'one MAP release')
tt = C.truth_by_map(evs['ch'], json.loads(out[0][1][4:]))
ck(tt == {'a': False, 'b': True, 'c': None}, 'truth by map: %s' % tt)
print('FAIL: ' + '; '.join(bad) if bad else 'PASS (9 checks)'); sys.exit(1 if bad else 0)
