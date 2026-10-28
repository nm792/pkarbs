"""Score one capture against the pre-registered rule (book-capture-plan-2026-10-26.md).

usage: analyse.py OUTDIR
Winners come from gamma outcomePrices when the markets have resolved; otherwise from the last captured
YES mid (provisional, flagged). P comes from data-api prints in [R, R+30] s, as in scripts/macro12m.
"""
import gzip, json, statistics as st, sys, time, urllib.request
D = sys.argv[1].rstrip('/') + '/'
H = {'User-Agent': 'curl/8.5.0', 'Accept': 'application/json'}
def get(u):
    with urllib.request.urlopen(urllib.request.Request(u, headers=H), timeout=20) as f: return json.load(f)
f = lambda p: 0.05 * p * (1 - p)
meta = json.load(open(D + 'meta.json')); R = meta['R']; mk = meta['markets']
snaps = [json.loads(x) for x in gzip.open(D + 'books.jsonl.gz', 'rt')]
ok = [s for s in snaps if 'b' in s]
print('polls', len(ok), 'errors', len(snaps) - len(ok))

# gate 3: clock. /time is whole server seconds, so local - server in [0, 1) means the clock is right
offs = [c['local_mid'] - float(c['server']) for c in meta['clock']]
g3 = all(-0.5 <= o <= 1.5 for o in offs)
print('clock local-server', ['%.2f' % o for o in offs], 'PASS' if g3 else 'FAIL')

# gate 1: rate and gaps in R-10..R+30
w = [s['t0'] for s in ok if R - 10 <= s['t0'] <= R + 30]
gaps = [b - a for a, b in zip(w, w[1:])] or [float('inf')]
if not w: sys.exit('no snapshots in R-10..R+30: gate 1 fails, no number for this release')
rate = len(w) / 40
g1 = rate >= 2 and max(gaps) <= 2
print('rate %.2f Hz, max gap %.2f s' % (rate, max(gaps)), 'PASS' if g1 else 'FAIL')

# gate 2: every token in every snapshot used
toks = {m['yes'] for m in mk} | {m['no'] for m in mk}
g2 = all(toks <= {x['a'] for x in s['b']} for s in ok if R - 10 <= s['t0'] <= R + 30)
print('all tokens present', 'PASS' if g2 else 'FAIL')

# winners
win, prov = {}, False
for eid in meta['events']:
    for m in get('https://gamma-api.polymarket.com/events?id=' + eid)[0]['markets']:
        op = json.loads(m.get('outcomePrices') or '[]')
        if m.get('closed') and '1' in op: win[m['conditionId']] = op.index('1')
if len(win) < len(mk):
    prov = True
    last = {x['a']: x for x in ok[-1]['b']}
    for m in mk:
        if m['cid'] in win: continue
        b = last[m['yes']]
        bb = max([float(r['price']) for r in b['bids']] or [0]); aa = min([float(r['price']) for r in b['asks']] or [1])
        win[m['cid']] = 0 if (bb + aa) / 2 > 0.5 else 1   # outcome index 0 = YES
print('winners', 'PROVISIONAL (from last book)' if prov else 'resolved', {m['item']: win[m['cid']] == 0 for m in mk})

def S(snap):
    bk = {x['a']: x for x in snap['b']}; tot = 0.0; per = {}
    for m in mk:
        y = bk[m['yes']]; v = 0
        if win[m['cid']] == 0:   # YES won: stale asks below 1
            v = sum(max(1 - float(r['price']) - f(float(r['price'])), 0) * float(r['size']) for r in y['asks'])
        else:                    # YES lost: stale bids above 0
            v = sum(max(float(r['price']) - f(float(r['price'])), 0) * float(r['size']) for r in y['bids'])
        per[m['item']] = v; tot += v
    return tot, per
pre = [s for s in ok if s['t0'] < R]; post = [s for s in ok if s['t0'] >= R + 1.0]
S_pre, per_pre = S(pre[-1]); S_reach, per_reach = S(post[0])
print('S_pre $%.0f at t0-R %.2f s' % (S_pre, pre[-1]['t0'] - R), {k: round(v) for k, v in per_pre.items()})
print('S_reach $%.0f at t0-R %.2f s' % (S_reach, post[0]['t0'] - R), {k: round(v) for k, v in per_reach.items()})
g4 = S_pre >= S_reach
print('S_pre >= S_reach', 'PASS' if g4 else 'CHECK BY HAND')
for dt in (0.0, 0.5, 2.0, 3.0, 5.0, 10.0):   # context only, not part of pass/fail
    s = next(s for s in ok if s['t0'] >= R + dt); print('  S at t0 >= R+%.1f: $%.0f' % (dt, S(s)[0]))

# P: printed pool 0-30 s, net of fee, as in scripts/macro12m/analyse.py
rows, off = [], 0
cids = ','.join(m['cid'] for m in mk)
while off <= 10000:
    d = get('https://data-api.polymarket.com/trades?market=%s&limit=500&offset=%d' % (cids, off))
    rows += d
    if not d or d[-1]['timestamp'] < R - 5 or len(d) < 500: break
    off += 500
covered = rows and rows[-1]['timestamp'] < R
P = Pg = 0.0; n = 0
for r in rows:
    dd = r['timestamp'] - R
    if not 0 <= dd <= 30: continue
    v = 1.0 if r['outcomeIndex'] == win[r['conditionId']] else 0.0
    p, s = float(r['price']), float(r['size'])
    e = (v - p) * s if r['side'] == 'BUY' else (p - v) * s
    Pg += max(e, 0); P += max(e - f(p) * s, 0); n += 1
print('prints 0-30 s %d, P gross $%.0f net $%.0f, coverage back to R: %s' % (n, Pg, P, covered))
RP = max(P, S_reach)
print('RP $%.0f, RP/P %s' % (RP, ('%.2f' % (RP / P)) if P else 'n/a (P=0)'))
print('gates', 'ALL PASS' if (g1 and g2 and g3) else 'FAIL: no number for this release')
json.dump({'R': R, 'S_pre': S_pre, 'S_reach': S_reach, 'P': P, 'P_gross': Pg, 'RP': RP, 'n_prints': n,
           'gates': [g1, g2, g3, g4], 'provisional_winners': prov, 'covered': bool(covered)},
          open(D + 'summary.json', 'w'))
