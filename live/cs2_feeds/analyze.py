#!/usr/bin/env python3
"""Answer two questions from a capture.py folder (4 Nov 2026).

1. Queue: at the price a FAST bot would bid (pre-event mid x 0.975, floored to the tick) how much size was already
   resting BEFORE the market reacted, versus at the moment our slow (sports WS) bot joins?
2. Feed race: market reaction time T_m (book mid makes half its move) vs sports WS receipt R and vs the first
   Thunderpick odds change mirrored by bo3.gg.
Usage: analyze.py CAPDIR [CAPDIR...]  -> prints a table + writes CAPDIR0/analysis.json
"""
import json, sys, os, math, bisect, statistics as st, collections

dirs = sys.argv[1:]
def rd(name):
    for d in dirs:
        p = os.path.join(d, name + '.jsonl')
        if os.path.exists(p):
            for l in open(p):
                try: yield json.loads(l)
                except Exception: pass

tok = {}; gid_names = {}
for m in rd('markets'):
    k = m['kind']; kind = 'match' if k == 'Match Winner' else 'map' + k[4]
    for i, t in enumerate(m['tokens']): tok[t] = (m['gid'], kind, i)
    gid_names[m['gid']] = m['title']

books = collections.defaultdict(list)   # token -> [(ms, bids{p:s}, bb, ba)]
for b in rd('books'):
    bids = {float(x['price']): float(x['size']) for x in b['bids'] or []}
    asks = {float(x['price']): float(x['size']) for x in b['asks'] or []}
    bb = max(bids) if bids else None; ba = min(asks) if asks else None
    books[b['asset']].append((b['recv_ms'], bids, bb, ba))
for v in books.values(): v.sort(key=lambda x: x[0])

def at(token, t):
    v = books.get(token) or []; i = bisect.bisect_right([x[0] for x in v], t) - 1
    return v[i] if i >= 0 else None
def mid(token, t):
    x = at(token, t)
    if not x or x[2] is None or x[3] is None or x[3] - x[2] > 0.10: return None
    return (x[2] + x[3]) / 2
def tick(p): return 0.001 if p < 0.04 or p > 0.96 else 0.01
def floor_t(p): tk = tick(p); return round(math.floor(p / tk + 1e-9) * tk, 3)
def size_at(token, t, p):
    x = at(token, t); return None if not x else round(x[1].get(round(p, 3), 0.0) + sum(s for q, s in x[1].items() if abs(q - p) < 1e-6 and q != round(p, 3)))
def ahead_at_or_above(token, t, p):
    x = at(token, t); return None if not x else round(sum(s for q, s in x[1].items() if q >= p - 1e-9))

def parse(sc):
    try:
        a, b, bo = sc.split('|'); ra, rb = map(int, a.split('-')); ma, mb = map(int, b.split('-')); return ra, rb, ma, mb
    except Exception: return None

events = []; last = {}
for s in rd('sports'):
    g = s.get('gameId'); p = parse(s.get('score') or '')
    if p is None: continue
    q = last.get(g); last[g] = p
    if not q: continue
    if p[2:] == q[2:] and 1 <= (p[0] + p[1]) - (q[0] + q[1]) <= 3 and p[0] >= q[0] and p[1] >= q[1]:
        per = s.get('period') or ''; mp = int(per.split('/')[0]) if per[:1].isdigit() else p[2] + p[3] + 1
        events.append(dict(gid=g, R=s['recv_ms'], map=mp, prev=q, new=p))

bo3 = list(rd('bo3'))
def bo3_first_change(gid, t0, t1):
    name = (gid_names.get(gid) or '').lower()
    prev = {}; out = None
    for r in bo3:
        slug = (r.get('slug') or '').replace('-', ' ')
        teams = name.split(':', 1)[-1].split('(')[0].split(' vs ')
        if not all(tm.strip().split()[0] in slug for tm in teams if tm.strip()): continue
        key = (r['c1'], r['c2'], r['a1'], r['a2'])
        if r['id'] in prev and prev[r['id']] != key and t0 <= r['recv_ms'] <= t1 and out is None: out = r['recv_ms']
        prev[r['id']] = key
    return out

TR = collections.defaultdict(list)   # token -> [(ms, price, size)] from data-api v2 trades files (trades/*.json)
import glob
for d in dirs:
    for f in glob.glob(os.path.join(d, 'trades', '*.json')):
        for x in json.load(open(f)): TR[x['token_id']].append((x['timestamp'] * 1000, float(x['price']), float(x['size'])))
def prints(token, a, b, p):
    v = TR.get(token)
    if v is None: return None
    return round(sum(sz for t, px, sz in v if a <= t <= b and px <= p + 1e-9))

rows = []
for e in events:
    R = e['R']
    for t, (g, kind, idx) in tok.items():
        if g != e['gid'] or kind not in ('match', 'map%d' % e['map']): continue
        pre = [mid(t, R - ms) for ms in range(90000, 44000, -1000)]; pre = [x for x in pre if x is not None]
        post = mid(t, R + 30000)
        if len(pre) < 10 or post is None: continue
        m0 = st.median(pre); mv = post - m0
        if mv < 0.01: continue                     # keep the rising token only, >= 1c move
        Tm = None; best = 0.0
        for ms in range(-75000, 5001, 500):
            a, b = mid(t, R + ms - 3000), mid(t, R + ms)
            if a is not None and b is not None and b - a > best: best, Tm = b - a, R + ms - 3000
        if best < max(0.01, mv / 3): Tm = None
        if Tm is None: continue
        pf = floor_t(m0 * 0.975); ms_ = mid(t, R) or m0; ps = floor_t(ms_ * 0.975)
        bbR = (at(t, R) or (0, 0, None))[2]
        bb_pre = (at(t, Tm - 2000) or (0, 0, None))[2]
        fills_fast = prints(t, Tm - 2000, Tm + 30000, pf); fills_slow = prints(t, R, R + 30000, ps)
        rows.append(dict(bb_pre=bb_pre, q_bb_Tm_m2=None if bb_pre is None else size_at(t, Tm - 2000, bb_pre),
                         prints_le_Pfast=fills_fast, prints_le_Pslow=fills_slow,
gid=g, kind=kind, R=R, move=round(mv, 3), mid_pre=round(m0, 3), ws_lag_s=round((R - Tm) / 1000, 1),
                         P_fast=pf, q_fast_Tm_m30=size_at(t, Tm - 30000, pf), q_fast_Tm_m10=size_at(t, Tm - 10000, pf),
                         q_fast_Tm_m2=size_at(t, Tm - 2000, pf), q_fast_Tm_p5=size_at(t, Tm + 5000, pf),
                         P_slow=ps, ticks_below_bb_R=None if bbR is None else round((bbR - ps) / tick(ps)),
                         q_slow_Tm_m30=size_at(t, Tm - 30000, ps), q_slow_R=size_at(t, R, ps),
                         bo3_lag_s=(lambda x: None if x is None else round((x - Tm) / 1000, 1))(bo3_first_change(g, Tm - 60000, Tm + 120000))))

hdr = ['gid', 'kind', 'move', 'mid_pre', 'ws_lag_s', 'P_fast', 'q_fast_Tm_m30', 'q_fast_Tm_m10', 'q_fast_Tm_m2', 'q_fast_Tm_p5',
       'P_slow', 'ticks_below_bb_R', 'q_slow_Tm_m30', 'q_slow_R', 'bb_pre', 'q_bb_Tm_m2', 'prints_le_Pfast', 'prints_le_Pslow', 'bo3_lag_s']
print('\t'.join(hdr))
for r in rows: print('\t'.join(str(r[h]) for h in hdr))
def med(k):
    v = [r[k] for r in rows if r[k] is not None]; return (round(st.median(v), 1), len(v)) if v else None
summ = {k: med(k) for k in hdr[4:] if k not in ('P_fast', 'P_slow', 'bb_pre')}
summ['events'] = len(events); summ['rows'] = len(rows)
summ['share_fast_q_preexisting'] = None
v = [(r['q_fast_Tm_m30'], r['q_fast_Tm_m2']) for r in rows if r['q_fast_Tm_m30'] is not None and r['q_fast_Tm_m2'] is not None]
if v: summ['share_fast_q_preexisting'] = round(sum(min(a, b) for a, b in v) / max(1, sum(b for a, b in v)), 2)
print(json.dumps(summ, indent=1))
json.dump(dict(rows=rows, summary=summ), open(os.path.join(dirs[0], 'analysis.json'), 'w'), indent=1)
