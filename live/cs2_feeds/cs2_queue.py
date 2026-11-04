#!/usr/bin/env python3
"""Does the CS2 queue at our bid price clear in the seconds after an event? (4 Nov 2026)

Uses capture.py folders (1 s full-depth books, sports WS) + data-api v2 trades (trades/*.json or trades.tar.gz).
Events and market reaction time Tm are found exactly as in analyze.py (rising token, >= 1c move, Tm = start of the
largest 3 s mid step in [R-75 s, R+5 s]).

For each event x rising token, two prices we could bid at (both maker, 2.5% under mid):
  P_old = mid 2 s before the move x 0.975   (a fast bot that bids before the market moves)
  P_new = mid at Tm+6 s x 0.975   (a bot that bids right after the market moves)
and we measure, second by second from Tm-30 s to Tm+30 s:
  - size resting at P_old and at P_new
  - at P_old: shares removed, split into filled (prints at that price: taker SELL of this token at P, or taker BUY of
    the other token at 1-P, which matches the same bid) and cancelled (removed minus filled)
  - re-pricing signature: a cancel at P_old in a 1 s step where another bid level of the same token grows by the same
    amount (+-15%) in that step = most likely the same maker moving its order
  - at P_new: how many seconds after Tm the level stays nearly empty (< 100 sh, i.e. we would be at the front)
Usage: cs2_queue.py OUTJSON CAPDIR [CAPDIR...]
"""
import json, sys, os, math, bisect, statistics as st, collections, glob, tarfile, gzip, io

out_path = sys.argv[1]; dirs = sys.argv[2:]
def opn(p):
    return gzip.open(p, 'rt') if p.endswith('.gz') else open(p)
def rd(name):
    for d in dirs:
        for p in (os.path.join(d, name + '.jsonl'), os.path.join(d, name + '.jsonl.gz')):
            if os.path.exists(p):
                for l in opn(p):
                    try: yield json.loads(l)
                    except Exception: pass
                break

tok = {}; comp = {}; gid_names = {}
for m in rd('markets'):
    k = m['kind']; kind = 'match' if k == 'Match Winner' else 'map' + k[4]
    for i, t in enumerate(m['tokens']): tok[t] = (m['gid'], kind, i)
    if len(m['tokens']) == 2: comp[m['tokens'][0]] = m['tokens'][1]; comp[m['tokens'][1]] = m['tokens'][0]
    gid_names[m['gid']] = m['title']

books = collections.defaultdict(list)
for b in rd('books'):
    bids = {round(float(x['price']), 3): float(x['size']) for x in b['bids'] or []}
    asks = {round(float(x['price']), 3): float(x['size']) for x in b['asks'] or []}
    books[b['asset']].append((b['recv_ms'], bids, max(bids) if bids else None, min(asks) if asks else None))
for v in books.values(): v.sort(key=lambda x: x[0])
bk_t = {k: [x[0] for x in v] for k, v in books.items()}

def at(token, t):
    v = books.get(token) or []; i = bisect.bisect_right(bk_t.get(token, []), t) - 1
    return v[i] if i >= 0 else None
def mid(token, t):
    x = at(token, t)
    if not x or x[2] is None or x[3] is None or x[3] - x[2] > 0.10: return None
    return (x[2] + x[3]) / 2
def tick(p): return 0.001 if p < 0.04 or p > 0.96 else 0.01
def floor_t(p): tk = tick(p); return round(math.floor(p / tk + 1e-9) * tk, 3)
def size_at(token, t, p):
    x = at(token, t); return None if not x else x[1].get(round(p, 3), 0.0)

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
        events.append(dict(gid=g, R=s['recv_ms'], map=mp))

TR = collections.defaultdict(list)   # token -> [(ms, price, size, side)]
def add_trades(lst):
    for x in lst: TR[x['token_id']].append((x['timestamp'] * 1000, round(float(x['price']), 3), float(x['size']), x['side']))
for d in dirs:
    for f in glob.glob(os.path.join(d, 'trades', '*.json')): add_trades(json.load(open(f)))
    tp = os.path.join(d, 'trades.tar.gz')
    if os.path.exists(tp) and not glob.glob(os.path.join(d, 'trades', '*.json')):
        with tarfile.open(tp) as tf:
            for m in tf.getmembers():
                if m.name.endswith('.json'): add_trades(json.load(tf.extractfile(m)))
def filled_at(token, a, b, p):
    """Shares that traded against bids at price p on token in [a, b] ms (trade timestamps are whole seconds)."""
    s = sum(sz for t, px, sz, sd in TR.get(token, []) if a <= t <= b and sd == 'SELL' and abs(px - p) < 1e-6)
    c = comp.get(token)
    if c: s += sum(sz for t, px, sz, sd in TR.get(c, []) if a <= t <= b and sd == 'BUY' and abs(px - (1 - p)) < 1e-6)
    return s

OFFS = list(range(-30, 31))
rows = []
for e in events:
    R = e['R']
    for t, (g, kind, idx) in tok.items():
        if g != e['gid'] or kind not in ('match', 'map%d' % e['map']): continue
        pre = [mid(t, R - ms) for ms in range(90000, 44000, -1000)]; pre = [x for x in pre if x is not None]
        post = mid(t, R + 30000)
        if len(pre) < 10 or post is None: continue
        m0 = st.median(pre); mv = post - m0
        if mv < 0.01: continue
        Tm = None; best = 0.0
        for ms in range(-75000, 5001, 500):
            a, b = mid(t, R + ms - 3000), mid(t, R + ms)
            if a is not None and b is not None and b - a > best: best, Tm = b - a, R + ms - 3000
        if Tm is None or best < max(0.01, mv / 3): continue
        m6 = mid(t, Tm + 6000); mb = mid(t, Tm - 2000)   # mb: mid just before the move (same 1 s snapshot as its bid/ask)
        if m6 is None or mb is None: continue
        # fix 4 Nov 12:45Z: P_old was the median mid 45-90 s before R x 0.975, which can sit far from the live mid
        P_old = floor_t(mb * 0.975); P_new = floor_t(m6 * 0.975)
        q_old = [size_at(t, Tm + o * 1000, P_old) for o in OFFS]
        q_new = [size_at(t, Tm + o * 1000, P_new) for o in OFFS]
        bb = [(at(t, Tm + o * 1000) or (0, 0, None))[2] for o in OFFS]
        # decomposition at P_old over [-10 s, +30 s] (event to move is inside this), step by step
        rem = add = fil = canc = repr_ = 0.0
        for i in range(OFFS.index(-10), len(OFFS) - 1):
            a, b = q_old[i], q_old[i + 1]
            if a is None or b is None: continue
            ta, tb = Tm + OFFS[i] * 1000, Tm + OFFS[i + 1] * 1000
            f = filled_at(t, ta - 1000, tb, P_old)   # +-1 s slack for whole-second trade stamps
            d = b - a
            if d > 0: add += d; continue
            r = -d; rem += r; ff = min(f, r); fil += ff; c = r - ff; canc += c
            if c >= 50:
                xa, xb = at(t, ta), at(t, tb)
                if xa and xb:
                    for p2, s2 in xb[1].items():
                        if p2 == P_old: continue
                        g2 = s2 - xa[1].get(p2, 0.0)
                        if g2 > 0 and abs(g2 - c) <= 0.15 * c: repr_ += c; break
        def first_ge(series, thr, start):
            for o, v in zip(OFFS, series):
                if o >= start and v is not None and v >= thr: return o
            return None
        front = None   # seconds after Tm that P_new stays < 100 sh (counted from Tm)
        for o, v in zip(OFFS, q_new):
            if o < 0: continue
            if v is None or v >= 100: front = o; break
        rows.append(dict(gid=g, title=gid_names.get(g, '')[:60], kind=kind, Tm=Tm, R=R, move=round(mv, 3), mid_pre=round(m0, 3), mid_m2=round(mb, 3),
                         mid_6=round(m6, 3), P_old=P_old, P_new=P_new, q_old=q_old, q_new=q_new, bb=bb,
                         old_removed=round(rem), old_added=round(add), old_filled=round(fil), old_cancelled=round(canc),
                         old_cancel_reprice_match=round(repr_), new_front_s=front,
                         new_half_s=first_ge(q_new, 0.5 * max([v for v in q_new[30:] if v is not None] or [0]), 0) if max([v for v in q_new[30:] if v is not None] or [0]) >= 100 else None))

def med(v):
    v = [x for x in v if x is not None]; return round(st.median(v), 1) if v else None
def summarize(rs):
    if not rs: return None
    s = dict(rows=len(rs))
    for o in (-30, -10, -5, -2, 0, 2, 5, 10, 20, 30):
        i = OFFS.index(o)
        s['old_q_%+d' % o] = med([r['q_old'][i] for r in rs]); s['new_q_%+d' % o] = med([r['q_new'][i] for r in rs])
    base = [(r['q_old'][OFFS.index(-10)], r['q_old'][OFFS.index(5)], r['q_old'][OFFS.index(30)]) for r in rs]
    base = [b for b in base if None not in b and b[0] >= 100]
    s['old_rows_q-10_ge100'] = len(base)
    s['old_share_left_at_+5'] = round(sum(min(a, b) for a, b, c in base) / max(1, sum(a for a, b, c in base)), 2)
    s['old_share_left_at_+30'] = round(sum(min(a, c) for a, b, c in base) / max(1, sum(a for a, b, c in base)), 2)
    for k in ('old_removed', 'old_added', 'old_filled', 'old_cancelled', 'old_cancel_reprice_match'):
        s[k + '_sum'] = sum(r[k] for r in rs)
    s['old_filled_share_of_removed'] = round(s['old_filled_sum'] / max(1, s['old_removed_sum']), 3)
    s['old_reprice_share_of_cancels'] = round(s['old_cancel_reprice_match_sum'] / max(1, s['old_cancelled_sum']), 3)
    fr = [r['new_front_s'] for r in rs]
    s['new_front_s_median'] = med(fr); s['new_front_s_dist'] = collections.Counter(fr).most_common()
    s['new_empty_at_Tm_rows'] = sum(1 for r in rs if (r['q_new'][OFFS.index(0)] or 0) < 100)
    s['new_half_s_median'] = med([r['new_half_s'] for r in rs])
    return s
tier1 = [r for r in rows if 'IEM' in r['title'] or 'BLAST' in r['title'] or 'PGL' in r['title']]
other = [r for r in rows if r not in tier1]
summ = dict(events=len(events), all=summarize(rows), tier1=summarize(tier1), other=summarize(other))
print(json.dumps(summ, indent=1, default=str))
json.dump(dict(offsets_s=OFFS, rows=rows, summary=summ), open(out_path, 'w'), default=str)
