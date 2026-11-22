# Planted-edge test for mece_score.py (Nick/Reviewer rule: every test can fail). Run: python3 -I test_mece_score.py
import gzip, json, os, subprocess, sys, tempfile
here = os.path.dirname(os.path.abspath(__file__)); D = tempfile.mkdtemp(); bad = []
DAY = '2026-11-21'; T0 = 1795219200000 + 3600000 * 12   # 2026-11-21 12:00Z
def build(asks_yes, asks_no, name):
    d = os.path.join(D, name); os.makedirs(d)
    with open(d + '/markets.jsonl', 'w') as h:
        for i in range(3): h.write(json.dumps({'cond': 'c%d' % i, 'tokens': ['y%d' % i, 'n%d' % i], 'outcomes': ['Yes', 'No'], 'set': 'ev|moneyline', 'q': 'q', 'smt': 'moneyline'}) + '\n')
    rows = []
    for i in range(3):
        for tk, a in (('y%d' % i, asks_yes[i]), ('n%d' % i, asks_no[i])):
            rows.append({'recv_ms': T0, 'asset': tk, 'asks': [{'price': str(a), 'size': '100'}], 'bids': [{'price': str(round(a - 0.02, 3)), 'size': '100'}]})
    with gzip.open(d + '/books-2026112112.jsonl.gz', 'wt') as h:
        for r in rows: h.write(json.dumps(r) + '\n')
    return d
def run(d): return subprocess.run([sys.executable, '-I', os.path.join(here, 'mece_score.py'), d, DAY], capture_output=True, text=True).stdout
# 1) planted buy-all-YES edge: asks 0.30 each (sum 0.90 + fees ~0.0105*3 -> net ~ +0.07/share on 100 shares)
o = run(build([0.30] * 3, [0.72] * 3, 'plantYES'))
if 'buyYES:min=0.9000 d0runs=1 d0net=6.' not in o and 'buyYES:min=0.9000 d0runs=1 d0net=7.' not in o: bad.append('planted YES edge not found: ' + o)
if 'd1runs=1' not in o.split('buyYES:')[1].split('buyNO')[0]: bad.append('planted YES edge lost at delay row (book unchanged, must survive): ' + o)
# 2) no edge: asks sum 1.02 for YES (0.34 each) and NO asks 0.68 each (sum 2.04 > payoff 2): nothing may fire
o = run(build([0.34] * 3, [0.68] * 3, 'none'))
if 'd0runs=0' not in o or any(('d0runs=%d' % k) in o for k in range(1, 9)): bad.append('false detection on no-edge book: ' + o)
# 3) planted buy-all-NO edge: NO asks 0.60 each: cost 1.80 < payoff 2, fees ~0.012*3
o = run(build([0.45] * 3, [0.60] * 3, 'plantNO'))
if 'buyNO:min=0.9000 d0runs=1' not in o: bad.append('planted NO edge not found: ' + o)
print('FAIL: ' + '; '.join(bad) if bad else 'PASS (planted YES + planted NO found, no-edge silent)'); sys.exit(1 if bad else 0)
