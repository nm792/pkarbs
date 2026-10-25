"""Gates for the MECE scanner. Expected values were fixed BEFORE running this engine:
G1-G3 by hand, G4 from the independent 25 Oct script (scripts/midterms/senate_cover.py and the
report), G5-G11 by construction. Run: python3 scanner/test_scanner.py"""
import json, os, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fees import kalshi_fee, pm_fee
from books import Book, pm_mirror_no, kalshi_books
from engine import walk
from guards import check, tradeable
from persist import Tracker
from structures import senate_structures, negrisk_set, ladder, _mk, _ins

HERE = os.path.dirname(os.path.abspath(__file__))
R = []
def gate(name, ok, detail=''):
    R.append((name, bool(ok))); print(('PASS ' if ok else 'FAIL ') + name + ('  ' + detail if detail else ''))

def near(a, b, tol): return abs(a - b) <= tol

# G1 fees (hand): Kalshi 100 @0.63 -> 0.07*100*0.63*0.37 = 1.6317 -> 1.64 (ceil to cent). PM rate 0.04, 100 @0.5 -> 1.00
gate('G1 fees', kalshi_fee(0.63, 100) == 1.64 and near(pm_fee(0.5, 100, 0.04), 1.0, 1e-9) and kalshi_fee(0.5, 0) == 0)

# G2 negRisk set walk (hand): A asks (.30,100)(.31,100); B (.65,50)(.66,200).
# 50 @ .95 (+2.5), 50 @ .96 (+2.0), 100 @ .97 (+3.0) -> 200 sets, profit 7.5
bk = {'pm:A': Book([(0.30, 100), (0.31, 100)], [], ts=0), 'pm:B': Book([(0.65, 50), (0.66, 200)], [], ts=0)}
s = _mk('t', 'negrisk_set', [dict(name='A', instruments=[_ins('A', ['pm:A'])]), dict(name='B', instruments=[_ins('B', ['pm:B'])])])
r = walk(s, bk)
gate('G2 set walk', near(r['sets'], 200, 1e-6) and near(r['profit'], 7.5, 1e-6), f"sets {r['sets']} profit {r['profit']:.4f}")

# G3 Kalshi conversion: NO bid 0.37 x 10 -> YES ask 0.63 x 10; YES bid 0.62 -> NO ask 0.38
y, n = kalshi_books({'orderbook_fp': {'no_dollars': [['0.3700', '10']], 'yes_dollars': [['0.6200', '7']]}}, fetched=0)
gate('G3 kalshi books', y.asks == [(0.63, 10.0)] and n.asks == [(0.38, 7.0)] and not y.crossed())

# Load the 25 Oct snapshot
fx = json.load(open(os.path.join(HERE, 'fixtures', 'senate_2026-10-25.json')))
now = fx['fetched'] + 10
books = {}
for t, b in fx['pm'].items():
    books['pm:' + t] = Book(b['asks'], b['bids'], ts=b['ts'], fetched=now - 5)
for tk, raw in fx['kalshi'].items():
    yb, nb = kalshi_books(raw, fetched=now - 5)
    books[f'k:{tk}:yes'] = yb; books[f'k:{tk}:no'] = nb
S = {x['id']: x for x in senate_structures()}

# G4a reproduce cross-venue Senate (expected 2636.80 with combos; independent script) +/- $3.
# The independent script only had Kalshi D YES on the Kalshi side, so strip 'k R NO' here.
old = json.loads(json.dumps(S['xv:senate:K-D+PM-notD']))
old['buckets'][0]['instruments'] = [i for i in old['buckets'][0]['instruments'] if i['name'] == 'k D YES']
r = walk(old, books)
gate('G4a xv Senate with combos ~ $2,636.80', near(r['profit'], 2636.80, 3.0), f"profit {r['profit']:.2f} on {r['cost']:.0f}, sets {r['sets']:.0f}")
# G4b main-market only (expected 894.55)
main = json.loads(json.dumps(old))
main['buckets'][1]['instruments'] = [i for i in main['buckets'][1]['instruments'] if i['name'] in ('pm main R YES', 'pm main D NO (R or Other)')]
r = walk(main, books)
gate('G4b xv Senate main only ~ $894.55', near(r['profit'], 894.55, 3.0), f"profit {r['profit']:.2f}")
# G4c Polymarket-only synthetic. The 25 Oct figure ($62.45) also used main D YES on the D side,
# which leaves 'Other' uncovered; the strict structure only allows main R NO there. Expected for
# the strict version (independent script restricted the same way): $58.21
r = walk(S['pm:senate:R+notR'], books)
gate('G4c PM-only synthetic (strict MECE) ~ $58.21', near(r['profit'], 58.21, 0.5) and tradeable(S['pm:senate:R+notR'], ['pm']), f"profit {r['profit']:.2f} on {r['cost']:.0f}")
gate('G4d cross-venue not tradeable without Kalshi', not tradeable(S['xv:senate:K-D+PM-notD'], ['pm']))
rf = walk(S['xv:senate:K-D+PM-notD'], books); r2 = walk(S['xv:senate:K-R+PM-notR'], books)
print(f"     info: full K-D pair (adds Kalshi R NO) {rf['profit']:.2f}; reverse pair K-R+PM-notR {r2['profit']:.2f}")
gate('G4e snapshot clean (no crossed/stale)', check(S['xv:senate:K-D+PM-notD'], books, now) == [], str(check(S['xv:senate:K-D+PM-notD'], books, now)[:3]))

# G5 crossed book rejected (replay artefact from the sports work)
cb = dict(books); cb['pm:X'] = Book([(0.30, 100)], [(0.32, 100)], ts=now, fetched=now)
sx = _mk('x', 'negrisk_set', [dict(name='X', instruments=[_ins('X', ['pm:X'])])])
gate('G5 crossed rejected', any('crossed' in m for m in check(sx, cb, now)))
# G6 stale book rejected (missing-hour stitched book from the rescan audit)
sb = {'pm:X': Book([(0.30, 100)], [], ts=now - 3600, fetched=now)}
gate('G6 stale rejected', any('stale' in m for m in check(sx, sb, now)))
# G7 one-poll blip does not open; 3 polls over 120 s do
with tempfile.TemporaryDirectory() as d:
    tr = Tracker(os.path.join(d, 'a.jsonl'), polls=3, min_secs=120)
    snap = dict(edge=0.01, profit=10, sets=1000, cost=990, ret=0.01, tradeable=True)
    a = [tr.update('s', 0, True, snap), tr.update('s', 60, False)]
    b = [tr.update('s', 100, True, snap), tr.update('s', 160, True, snap), tr.update('s', 220, True, dict(snap, profit=12)),
         tr.update('s', 280, True, snap), tr.update('s', 340, False)]
    log = [json.loads(x) for x in open(os.path.join(d, 'a.jsonl'))]
    gate('G7 blip ignored, persistent opens', a == [None, None] and b == [None, None, 'open', None, 'close'])
    gate('G10 alert log duration/peak', len(log) == 2 and log[1]['duration_s'] == 240 and log[1]['peak']['profit'] == 12,
         str([(x['event'], x.get('duration_s')) for x in log]))
# G8 incomplete negRisk set rejected (AL-04: one live candidate + placeholder not accepting orders)
ev = dict(slug='al-04', markets=[dict(groupItemTitle='Aderholt', clobTokenIds='["a","an"]', acceptingOrders=True),
                                 dict(groupItemTitle='Party B', clobTokenIds='["b","bn"]', acceptingOrders=False)])
gate('G8 incomplete set rejected', any('incomplete' in m for m in check(negrisk_set(ev), {'pm:a': Book([(0.989, 30)], [], ts=now), 'pm:b': Book([], [], ts=now)}, now)))
# G9 thin set (Hormuz 3-way shape: 19, 10.75, 30 shares at the gap) stays below a $5 profit floor
hb = {'pm:h1': Book([(0.017, 19.34), (0.019, 29.97), (0.02, 265.27)], [], ts=now),
      'pm:h2': Book([(0.045, 10.75), (0.047, 11.91), (0.048, 481.57)], [], ts=now),
      'pm:h3': Book([(0.925, 30), (0.926, 426), (0.928, 382.07)], [], ts=now)}
hs = _mk('h', 'negrisk_set', [dict(name=n, instruments=[_ins(n, ['pm:' + n])]) for n in ('h1', 'h2', 'h3')])
r = walk(hs, hb)
gate('G9 thin Hormuz set < $5', r['profit'] < 5, f"profit {r['profit']:.2f} sets {r['sets']:.1f}")
# G11 time ladder: NO(by A) ask .70 + YES(by B) ask .25 -> .95 locked (hand: 100 x .05 = 5.00)
lb = {'pm:noA': Book([(0.70, 100)], [], ts=now), 'pm:yesB': Book([(0.25, 300)], [], ts=now)}
r = walk(ladder('l', 'pm:noA', 'pm:yesB'), lb)
gate('G11 ladder', near(r['profit'], 5.0, 1e-9), f"profit {r['profit']:.2f}")

# G12 end-to-end dry run: replay the snapshot for 5 polls 60 s apart with a fake clock.
# Expect: PM-only Senate synthetic opens as TRADEABLE, cross-venue opens as ALERT-ONLY, both close at the end.
import run as runmod
clk = [1e9]
def fake_fetch(legs):
    out = {}
    for t, b in fx['pm'].items(): out['pm:' + t] = Book(b['asks'], b['bids'], ts=clk[0], fetched=clk[0])
    for tk, raw in fx['kalshi'].items():
        y, n = kalshi_books(raw, fetched=clk[0]); out[f'k:{tk}:yes'] = y; out[f'k:{tk}:no'] = n
    return out
def fake_sleep(sec): clk[0] += sec
with tempfile.TemporaryDirectory() as d:
    lp = os.path.join(d, 'al.jsonl')
    runmod.main(['--minutes', '5', '--poll', '60', '--log', lp, '--snapshots', os.path.join(d, 's.jsonl'), '--no-discover'],
                fetcher=fake_fetch, clock=lambda: clk[0], sleep=fake_sleep, structs=senate_structures())
    log = [json.loads(x) for x in open(lp)]
    opened = {x['sid']: x['last']['tradeable'] for x in log if x['event'] == 'open'}
    closed = {x['sid'] for x in log if x['event'] == 'close'}
    gate('G12 dry run alerts', opened.get('pm:senate:R+notR') is True and opened.get('xv:senate:K-D+PM-notD') is False and set(opened) <= closed,
         str(opened))

fails = [n for n, ok in R if not ok]
print(f"\n{len(R) - len(fails)}/{len(R)} gates pass" + (f"; FAILED: {fails}" if fails else ''))
sys.exit(1 if fails else 0)
