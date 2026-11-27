"""Test capture_replay.py on a planted capture (two markets, both tokens). Each check can fail.
Planted: market A 'Will X be 0.3%?' winner YES; YES ask 0.40 x 100 until R+1.0 s, then pulled (0.99). NO book 0.65 then 0.99.
Market B 'Will X be 0.2%?' winner NO; NO ask 0.70 x 50 until R+10 s; YES ask 0.35 then 0.99.
Expected (250 ms Nautilus latency on top of L): L=0.5 fills A-YES (100 at 0.40) and B-NO (50 at 0.70); L=2 must NOT fill A-YES (pulled at R+1 s: the planted case that fails at that delay, register B1) but fills B-NO.
Run: python3 test_capture_replay.py -> PASS or FAIL list."""
import json, gzip, os, sys, tempfile
import capture_replay as CR

R = '2026-12-10T13:30:00Z'
Rms = CR.iso_ns(R) // 1_000_000
bad = []
def ck(c, m):
    if not c: bad.append(m)

d = tempfile.mkdtemp()
mk = [dict(cond='cA', q='Will X be 0.3% in Dec?', outcomes=['Yes', 'No'], tokens=['ay', 'an'], slug='x-dec', title='0.3%', fee={'rate': 0.01}, min_size=5),
      dict(cond='cB', q='Will X be 0.2% in Dec?', outcomes=['Yes', 'No'], tokens=['by', 'bn'], slug='x-dec', title='0.2%', fee={'rate': 0.01}, min_size=5)]
with open(os.path.join(d, 'markets.jsonl'), 'w') as f:
    for m in mk: f.write(json.dumps(m) + '\n')
def row(t, tok, ap, asz):
    return dict(recv_ms=t, asset=tok, asks=[dict(price=ap, size=asz)], bids=[dict(price=0.01, size=100)])
rows = [row(Rms - 60000, 'ay', 0.40, 100), row(Rms + 1000, 'ay', 0.99, 100),
        row(Rms - 60000, 'an', 0.65, 100), row(Rms + 800, 'an', 0.99, 100),
        row(Rms - 60000, 'by', 0.35, 100), row(Rms + 800, 'by', 0.99, 100),
        row(Rms - 60000, 'bn', 0.70, 50), row(Rms + 10000, 'bn', 0.99, 50)]
# dense updates on the already-repriced A-NO token (as in a real capture, ~0.14 s between rows): Nautilus processes in-flight orders when time advances
rows += [row(Rms + 800 + 100 * k, 'an', 0.99, 100 + k) for k in range(1, 100)]
rows.sort(key=lambda r: r['recv_ms'])
with gzip.open(os.path.join(d, 'books-2026121013.jsonl.gz'), 'wt') as f:
    for r in rows: f.write(json.dumps(r) + '\n')

markets, rr = CR.load_capture(d)
Rns = CR.iso_ns(R)
r05 = CR.run_one(markets, rr, Rns, {'x-dec': 0.3}, 0.5, 200)
got05 = {(f['instrument'].split('.')[0], f['avg_px']) for f in r05['fills']}
ck(any(i.endswith('YES') and i.startswith('m0') and abs(float(p) - 0.40) < 1e-9 for i, p in got05), 'L=0.5 must fill A-YES at 0.40: %s' % got05)
ck(any(i.endswith('NO') and i.startswith('m1') and abs(float(p) - 0.70) < 1e-9 for i, p in got05), 'L=0.5 must fill B-NO at 0.70: %s' % got05)
ck(r05['n_fills'] == 2, 'L=0.5 exactly 2 fills (no loser bought): %s' % got05)
ck(all('USDC' in f['commissions'] and not f['commissions'].startswith('0.00') for f in r05['fills']), 'Nautilus fee model must charge: %s' % r05['fills'])
r2 = CR.run_one(markets, rr, Rns, {'x-dec': 0.3}, 2.0, 200)
got2 = {f['instrument'].split('.')[0] for f in r2['fills']}
ck('m0-YES' not in got2, 'L=2 must NOT fill A-YES (ask pulled at R+1 s): %s' % got2)
ck('m1-NO' in got2, 'L=2 must still fill B-NO: %s' % got2)
dt_ = CR.depth_table(markets, rr, Rns, {'x-dec': 0.3})
a = [x for x in dt_ if x['cond'] == 'cA' and x['outcome'] == 'Yes'][0]
ck(a['pre_best_ask'] == [0.40, 100] and a['pre_best_ask_gone_after_ms'] == 1000, 'depth table: A-YES 0.40x100 gone after 1000 ms: %s' % a)
print('FAIL: ' + '; '.join(bad) if bad else 'PASS (8 checks; planted pulled-ask case fails at L=2 as it must)')
sys.exit(1 if bad else 0)
