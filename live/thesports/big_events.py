#!/usr/bin/env python3
"""BIG-EVENT test (Nick 7 Nov 07:17Z). Usage: big_events.py SLIMDIR. Head = loaders and name bridge from event_price_change_names.py.
Tennis: breaks, set-winning games, 2nd-set wins. CS2: round wins by late/map-point stage. LoL: tower/inhibitor/monster events.
Keeps classes whose typical (median) favourable mid move over t-10..t+30 is >=3c; reports timing and net vs random-time placebo.
Per event: TheSports receive time t_r; our bid at t_r+DELAY on the side the event favours,
price = floor(mid*0.975, 0.01) (market-2.5%), post-only (skipped if >= best ask); fills only if
best ask later trades down to <= bid within HOLD s (trade-through proxy); payoff held to
resolution (settle proxy: last mid >=0.95 -> 1, <=0.05 -> 0, else game excluded). Matching of
TheSports ids to PM tokens is by price co-movement (no team names yet)."""
import statistics
import sys, json, gzip, glob, bisect, collections, statistics as st, math, random
D = sys.argv[1]
DELAY = 0.2
def rd(p):
    for f in sorted(glob.glob(p, recursive=True)):
        for l in gzip.open(f, 'rt'):
            try: yield json.loads(l)
            except Exception: pass
book = collections.defaultdict(list)
for r in rd(D + '/books_mid/**/*.gz'):
    book[r['tk']].append((r['ms'] / 1000.0, r['bb'], r['ba'], r['q']))
T = {}
for k in book:
    book[k].sort(); T[k] = [x[0] for x in book[k]]
mk = {}
for m in rd(D + '/markets.jsonl.gz'):
    mk[m['cond']] = m
tk_sport = {}
for m in mk.values():
    for t in m['tokens']: tk_sport[t] = (m['sport'], m['q'], m['smt'])
def row(tk, t, maxage=15):
    ts = T[tk]; i = bisect.bisect_right(ts, t) - 1
    return book[tk][i] if i >= 0 and t - ts[i] < maxage else None
def mid_at(tk, t):
    r = row(tk, t); return None if not r else (r[1] + r[2]) / 2
# ---- events
ev = collections.defaultdict(list)
last = {}; seen = set()
msgs = sorted(rd(D + '/ts_mqtt/**/*.gz'), key=lambda r: r['ms'])
for r in msgs:
    s = r['topic'].split('/')[1]
    if s not in ('basketball', 'csgo', 'lol', 'tennis'): continue
    try: ps = json.loads(r['p'])
    except Exception: continue
    t = r['ms'] / 1000.0
    for p in ps:
        if s == 'basketball':
            sc = p.get('score')
            if not sc: continue
            key = ('nba', p['id']); cur = (sum(sc[3]), sum(sc[4]))
            if key in last and cur != last[key]:
                dh, da = cur[0] - last[key][0], cur[1] - last[key][1]
                if dh >= 0 and da >= 0 and 0 < dh + da <= 3: ev[key].append((t, 1 if dh else -1))
            last[key] = cur
        elif s == 'csgo':
            key = ('cs2', p['match_id'], p.get('map_id')); cur = (p['home']['c_score'], p['away']['c_score'])
            if key in last and cur != last[key]:
                dh, da = cur[0] - last[key][0], cur[1] - last[key][1]
                if dh >= 0 and da >= 0 and 0 < dh + da <= 1: ev[key].append((t, 1 if dh else -1))
            last[key] = cur
        elif s == 'tennis':
            tl = p.get('timeline')
            if not tl: continue
            mid_ = p['id']; first_msg = ('tn', mid_) not in last
            RK = {'0': 0, '15': 1, '30': 2, '40': 3, 'A': 4}
            def rk(x):
                return RK[x] if x in RK else (int(x) if str(x).isdigit() else None)
            for st_ in tl:
                prvsc = (0, 0)
                for rd_ in st_.get('rounds', []):
                    pts = rd_.get('points') or []
                    for i in range(1, len(pts)):
                        k2 = ('pt', mid_, st_['set'], rd_['round'], i)
                        if k2 in seen: continue
                        seen.add(k2)
                        a_, b_ = rk(pts[i - 1][0]), rk(pts[i - 1][1]); c_, d_ = rk(pts[i][0]), rk(pts[i][1])
                        if None in (a_, b_, c_, d_) or first_msg: continue
                        w = 1 if (c_ > a_ and d_ <= b_) or (d_ < b_) else (-1 if (d_ > b_ and c_ <= a_) or (c_ < a_) else 0)
                        if w: ev[('tennis', mid_)].append((t, w))
                    sc = rd_.get('score')
                    if sc:
                        cur = (sc.get('home', 0), sc.get('away', 0))
                        k3 = ('gm', mid_, st_['set'], rd_['round'])
                        if k3 not in seen:
                            seen.add(k3)
                            dh, da = cur[0] - prvsc[0], cur[1] - prvsc[1]
                            if not first_msg and dh >= 0 and da >= 0 and dh + da == 1: ev[('tennis', mid_)].append((t, 1 if dh else -1))
                        prvsc = cur
            last[('tn', mid_)] = 1
        else:
            for e in (p.get('event') or []):
                if e['type'] != 1: continue
                k2 = (p['box_num'], e['time'], e['killer'], e['victim'])
                if k2 in seen: continue
                seen.add(k2); ev[('lol', p['match_id'], p['box_num'])].append((t, 1 if e['side'] == 1 else -1))
# ---- candidate tokens per sport
cand = collections.defaultdict(list)
for t, (sp, q, smt) in tk_sport.items():
    if t in book:
        if sp == 'lol' and 'Game' not in q: continue
        cand[sp].append(t)
def move(tk, t):
    a, b = mid_at(tk, t - 10), mid_at(tk, t + 30)
    return None if a is None or b is None else b - a
def settle(tk):
    r = book[tk][-1]; m = (r[1] + r[2]) / 2
    return 1.0 if m >= 0.95 else (0.0 if m <= 0.05 else None)

import random
for k in list(tk_sport):
    pass
partner = {}
for m in mk.values():
    if len(m['tokens']) == 2:
        partner[m['tokens'][0]] = m['tokens'][1]; partner[m['tokens'][1]] = m['tokens'][0]
claimed = {}
for key, evs in ev.items():
    sp = key[0]
    if len(evs) < (8 if sp == 'nba' else (10 if sp == 'tennis' else 6)): continue
    pool = cand[sp]
    if sp == 'tennis': pool = [t for t in pool if tk_sport[t][2] == 'moneyline']
    if sp == 'lol':
        g = key[2]; pool = [t for t in pool if ('Game %d ' % g) in tk_sport[t][1]]
    best = None
    for tk in pool:
        sc = n = 0
        for t, sd in evs:
            m = move(tk, t)
            if m is None: continue
            sc += sd * m; n += 1
        if n >= 0.6 * len(evs):
            s_ = abs(sc) / n
            if best is None or s_ > best[0]: best = (s_, tk, 1 if sc > 0 else -1)
    if best:
        s_, tk, sign = best
        if s_ > claimed.get(tk, (0,))[0]: claimed[tk] = (s_, key, sign)
def tick_floor(x): return math.floor(x * 100 + 1e-9) / 100
def sim(tk, t, kind, N):
    r0 = row(tk, t + DELAY)
    if not r0: return None
    bb, ba = r0[1], r0[2]
    pre = mid_at(tk, t - 10)
    if kind == 'bestbid': p = bb
    elif kind == 'askm1': p = round(ba - 0.01, 2)
    elif kind == 'pre': p = tick_floor(pre) if pre is not None else None
    else: p = tick_floor((bb + ba) / 2 * 0.975)
    if p is None or p <= 0.02 or p >= ba - 1e-9: return None
    i0 = bisect.bisect_right(T[tk], t + DELAY)
    for x in book[tk][i0:bisect.bisect_right(T[tk], t + DELAY + N)]:
        if (p <= bb and x[1] < p - 1e-9) or x[2] <= p + 1e-9: return p
    return 0



HSIDE = {}
for r in msgs:
    if r['topic'].endswith('lol/match/v1'):
        try:
            for p in json.loads(r['p']): HSIDE[(p['match_id'], p['box_num'])] = p['home']['side']
        except Exception: pass
def outidx(tk):
    m = [m for m in mk.values() if tk in m['tokens']][0]; return m['tokens'].index(tk)
def conv_sign(tk, key):
    c = 1 if outidx(tk) == 0 else -1
    if key[0] == 'lol': c *= (1 if HSIDE.get((key[1], key[2])) == 1 else -1)
    return c

import os
HS = (5, 10, 30)
def measure(tk, key, sgn, t, sd):
    fav = tk if sd * sgn > 0 else partner.get(tk)
    if fav is None or fav not in book: return None
    r0 = row(fav, t + DELAY); pre = mid_at(fav, t - 10); entry = row(fav, t + DELAY + 1.0)
    if not r0 or pre is None or not entry: return None
    if (r0[1] + r0[2]) / 2 - pre >= 0.01 or not (0.25 <= pre <= 0.75): return None      # feed-first, 25-75%
    out = {}
    for h in HS:
        x = row(fav, t + DELAY + h)
        if not x: return None
        out['net%d' % h] = x[1] - entry[2]                  # sell at bid after h s, bought at ask after the 1 s delay
        out['mid%d' % h] = (x[1] + x[2]) / 2 - (r0[1] + r0[2]) / 2
    return out
def boot_diff(real, plac, k):
    gs = sorted(set(g for g, _ in real) | set(g for g, _ in plac))
    if len(gs) < 3: return None
    rg = collections.defaultdict(list); pg = collections.defaultdict(list)
    for g, m in real: rg[g].append(m[k])
    for g, m in plac: pg[g].append(m[k])
    ds = []
    for _ in range(400):
        pick = [random.choice(gs) for _ in gs]
        a = [x for g in pick for x in rg[g]]; b = [x for g in pick for x in pg[g]]
        if a and b: ds.append(sum(a) / len(a) - sum(b) / len(b))
    ds.sort()
    return (ds[20] * 100, ds[len(ds) - 21] * 100) if len(ds) > 40 else None
import unicodedata, re
DI = os.path.join(os.path.dirname(D.rstrip('/')), 'diary')
def norm(x):
    x = unicodedata.normalize('NFKD', x).encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[^a-z0-9 ]', ' ', x).split()
import difflib
def surn(x):
    parts = [w for w in re.split(r'/', x) if w.strip()]
    return [norm(w)[-1] for w in parts if norm(w)]
def same(a, b):
    na, nb = norm(a), norm(b)
    if not na or not nb: return False
    ja, jb = ' '.join(na), ' '.join(nb)
    if ja == jb or ja in jb or jb in ja: return True
    if '/' in a or '/' in b:                                     # doubles: compare surname sets
        sa, sb = surn(a), surn(b)
        return len(sa) == len(sb) >= 2 and all(difflib.SequenceMatcher(None, x, y).ratio() >= 0.85 for x, y in zip(sorted(sa), sorted(sb)))
    if na[-1] == nb[-1] and na[0][0] == nb[0][0]: return True
    return difflib.SequenceMatcher(None, ja.replace(' ', ''), jb.replace(' ', '')).ratio() >= 0.85
names = {}; matches = {}
for f in glob.glob(DI + '/*.json'):
    d = json.load(open(f))
    if 'results' not in d: continue
    for t in d['results_extra'].get('team', []): names[t['id']] = t['name']
for f in glob.glob(DI + '/*.json'):
    d = json.load(open(f))
    if 'results' not in d: continue
    for m in d['results']: matches[m['id']] = (names.get(m['home_team_id']), names.get(m['away_team_id']))
box = {}
for r in msgs:
    if r['topic'].endswith('csgo/match/v1'):
        try:
            for p in json.loads(r['p']): box[('cs2', p['match_id'], p.get('map_id'))] = p.get('box_num')
        except Exception: pass
tk_of = {}; cov = collections.Counter()
for key in ev:
    sp = key[0]
    if sp not in ('cs2', 'tennis'): continue
    cov[sp, 'event games'] += 1
    hm = matches.get(key[1])
    if not hm or None in hm: continue
    cov[sp, 'names found'] += 1
    done = False
    for tk in cand[sp]:
        q = tk_sport[tk][1]; smt = tk_sport[tk][2]
        if sp == 'tennis' and smt != 'moneyline': continue
        if sp == 'cs2' and ('Map %s Winner' % box.get(key)) not in q: continue
        m = [m_ for m_ in mk.values() if tk in m_['tokens']][0]
        i = m['tokens'].index(tk); o = m['outcomes'][i]; po = m['outcomes'][1 - i]
        if same(hm[0], o) and same(hm[1], po): tk_of[key] = (tk, 1); done = True; break
        if same(hm[1], o) and same(hm[0], po): tk_of[key] = (tk, -1); done = True; break
    if done: cov[sp, 'paired to PM market by names'] += 1
print('coverage', dict(cov))

# ================= big events =================
random.seed(77)
def sgn_tk(sp, key):
    if sp in ('tennis', 'cs2'):
        return tk_of.get(key)
    c = lolpair.get(key)
    return (c[0], conv_sign(c[0], key)) if c else None
lolpair = {}
for tk, (s_, key, sg) in claimed.items():
    if key[0] == 'lol': lolpair[key] = (tk,)
big = collections.defaultdict(list)           # (sp,key) -> [(t, side, cls)]
firstmsg = set(); sets_won = collections.defaultdict(lambda: [0, 0]); seen_b = set(); cs_last = {}; srv = {}
for r in msgs:
    s = r['topic'].split('/')[1]
    if s not in ('csgo', 'lol', 'tennis'): continue
    try: ps = json.loads(r['p'])
    except Exception: continue
    t = r['ms'] / 1000.0
    for p in ps:
        if s == 'csgo':
            key = ('cs2', p['match_id'], p.get('map_id')); cur = (p['home']['c_score'], p['away']['c_score'])
            if key in cs_last and cur != cs_last[key]:
                dh, da = cur[0] - cs_last[key][0], cur[1] - cs_last[key][1]
                if dh >= 0 and da >= 0 and dh + da == 1:
                    w = 1 if dh else -1; ws, ls = (cur[0], cur[1]) if w == 1 else (cur[1], cur[0])
                    cls = 'cs2 round -> winner at 12 (map point)' if ws == 12 else ('cs2 round, loser already >=10 (late, winner<12)' if ls >= 10 else ('cs2 overtime round' if ws >= 13 else 'cs2 early/mid round (loser<10)'))
                    big[key].append((t, w, cls))
            cs_last[key] = cur
        elif s == 'lol':
            k0 = (p['match_id'], p['box_num']); fm = k0 not in firstmsg; firstmsg.add(k0)
            for e in (p.get('event') or []):
                if e['type'] not in (2, 3, 4): continue
                k2 = (k0, e['type'], e['time'], e['killer'])
                if k2 in seen_b: continue
                seen_b.add(k2)
                if fm: continue
                cls = {2: 'lol tower (type 2)', 3: 'lol inhibitor (type 3)'}.get(e['type'], 'lol monster (type 4)')
                big[('lol',) + k0].append((t, 1 if e['side'] == 1 else -1, cls))
        else:
            tl = p.get('timeline')
            if not tl: continue
            mid_ = p['id']; fm = mid_ not in firstmsg; firstmsg.add(mid_)
            for st_ in tl:
                prv = (0, 0)
                for rd_ in st_.get('rounds', []):
                    sc = rd_.get('score')
                    if not sc: continue
                    cur = (sc.get('home', 0), sc.get('away', 0)); k = (mid_, st_['set'], rd_['round'])
                    if k not in seen_b:
                        seen_b.add(k)
                        dh, da = cur[0] - prv[0], cur[1] - prv[1]
                        if not fm and dh >= 0 and da >= 0 and dh + da == 1 and sc.get('serve') in (1, 2):
                            w = 1 if dh else -1; sv = 1 if sc['serve'] == 1 else -1
                            hi, lo = max(cur), min(cur)
                            setend = (hi >= 6 and hi - lo >= 2) or (hi == 7 and lo in (5, 6))
                            if setend:
                                sets_won[mid_][0 if w == 1 else 1] += 1
                                cls = 'tennis break that wins the set' if w != sv else 'tennis hold that wins the set'
                                if sets_won[mid_][0 if w == 1 else 1] >= 2: cls += ' (winner now 2 sets)'
                                big[('tennis', mid_)].append((t, w, cls))
                            if w != sv and not setend: big[('tennis', mid_)].append((t, w, 'tennis break (set goes on)'))
                            if w == sv and not setend and hi >= 5: big[('tennis', mid_)].append((t, w, 'tennis hold at 5+ games (not set-ending)'))
                    prv = cur
def fav_tk(tk, sg, side):
    f = tk if side * sg > 0 else partner.get(tk)
    return f if f is not None and f in book else None
def jump(tk, sg, t, side):
    f = fav_tk(tk, sg, side)
    if not f: return None
    a, b = mid_at(f, t - 10), mid_at(f, t + 30)
    return None if a is None or b is None or not (0.25 <= a <= 0.75) else (b - a, f, a)
def onset(f, t, pre):
    # first book snapshot in [t-10, t+30] whose mid is >=1c above pre (favourable); returns time rel to feed
    ts = T[f]; i = bisect.bisect_left(ts, t - 10)
    while i < len(ts) and ts[i] <= t + 30:
        if (book[f][i][1] + book[f][i][2]) / 2 - pre >= 0.01: return ts[i] - t
        i += 1
    return None
def net(f, t, h):
    r0 = row(f, t + DELAY); pre = mid_at(f, t - 10); en = row(f, t + DELAY + 1.0); x = row(f, t + DELAY + h)
    if not (r0 and pre is not None and en and x): return None
    if (r0[1] + r0[2]) / 2 - pre >= 0.01 or not (0.25 <= pre <= 0.75) or en[2] - en[1] > 0.03: return None   # feed-first, band, spread<=3c
    return x[1] - en[2]
classes = collections.defaultdict(list)       # cls -> [(game, t, side, tk, sg)]
for key, evs in big.items():
    ts_ = sgn_tk(key[0], key)
    if not ts_: continue
    for t0, sd, cls in evs: classes[cls].append((key, t0, sd, ts_[0], ts_[1]))
print('paired games with big events: tennis %d cs2 %d lol %d' % tuple(len([k for k in big if k[0] == s and sgn_tk(s, k)]) for s in ('tennis', 'cs2', 'lol')))
print('\nJUMP TABLE (favourable mid move t-10..t+30, any timing, pre 25-75%, cents)')
keep = []
for cls in sorted(classes):
    L = classes[cls]; js = [jump(tk, sg, t, sd) for _, t, sd, tk, sg in L]; js = [j[0] for j in js if j]
    med = 100 * statistics.median(js) if js else float('nan')
    print('%-52s events %3d with price data %3d | median move %+.2fc | share >=3c: %s' % (cls, len(L), len(js), med, ('%d%%' % (100 * sum(1 for x in js if x >= 0.03) / len(js))) if js else 'n/a'))
    if js and med >= 3.0: keep.append(cls)
print('\nclasses kept (median >=3c):', keep or 'NONE')
if os.environ.get('KEEPALL'):
    keep = [c for c in classes if len(classes[c]) >= 20 and not c.startswith('lol')]; print('KEEPALL: reporting anyway on', keep)
def bd(R, P):
    gs = sorted(set(g for g, _ in R) | set(g for g, _ in P))
    if len(gs) < 3: return None
    rg = collections.defaultdict(list); pg = collections.defaultdict(list)
    for g, v in R: rg[g].append(v)
    for g, v in P: pg[g].append(v)
    ds = []
    for _ in range(400):
        pick = [random.choice(gs) for _ in gs]
        a = [x for g in pick for x in rg[g]]; b = [x for g in pick for x in pg[g]]
        if a and b: ds.append(sum(a) / len(a) - sum(b) / len(b))
    ds.sort(); return (ds[20] * 100, ds[len(ds) - 21] * 100) if len(ds) > 40 else None
def report(label, L):
    R = {h: [] for h in (5, 10, 30)}; P = {h: [] for h in R}; lead_r = []; lead_p = []; nbig = nbigp = 0
    for key, t0, sd, tk, sg in L:
        f = fav_tk(tk, sg, sd)
        if not f: continue
        for h in R:
            v = net(f, t0, h)
            if v is not None: R[h].append((key, v))
        j = jump(tk, sg, t0, sd)
        if j and j[0] >= 0.03:
            o = onset(f, t0, j[2])
            if o is not None: lead_r.append(o)
        for _ in range(5):
            tp = t0 + random.choice([-1, 1]) * random.uniform(60, 600)
            for h in P:
                v = net(f, tp, h)
                if v is not None: P[h].append((key, v))
            j = jump(tk, sg, tp, sd)
            if j and j[0] >= 0.03:
                o = onset(f, tp, j[2])
                if o is not None: lead_p.append(o)
    print('\n== %s | events %d, games %d' % (label, len(L), len(set(k for k, *_ in L))))
    mdn = lambda a: ('%+.1f s' % statistics.median(a)) if a else 'n/a'
    print('timing (price onset of >=1c in the favourable direction, among events with a >=3c move by +30 s; negative = price first): real %s (n=%d) | random-time placebo %s (n=%d)' % (mdn(lead_r), len(lead_r), mdn(lead_p), len(lead_p)))
    for h in R:
        a = R[h]; b = P[h]
        if not a: print('net at +%ds: n=0 (no event passed feed-first/25-75%%/spread<=3c)' % h); continue
        ma = 100 * statistics.median([v for _, v in a]); mb = 100 * statistics.median([v for _, v in b]) if b else float('nan')
        ea = 100 * sum(v for _, v in a) / len(a); eb = 100 * sum(v for _, v in b) / len(b) if b else float('nan')
        ci = bd(a, b)
        print('net after spread+1s delay, sell at bid +%ds: real n=%d median %+.2fc mean %+.2fc | placebo n=%d median %+.2fc mean %+.2fc | mean real-placebo 90%% CI %s' % (h, len(a), ma, ea, len(b), mb, eb, ('[%+.2f, %+.2f]' % ci) if ci else 'n/a (<3 games)'))
for cls in sorted(classes):
    if cls in keep: report(cls, classes[cls])
for sp in ('tennis', 'cs2', 'lol'):
    L = [x for c in keep for x in classes[c] if c.startswith(sp)]
    if len(keep) and L and len([c for c in keep if c.startswith(sp)]) > 1: report(sp + ' ALL KEPT CLASSES', L)

# ================= sanity check (coordinator 07:22Z) =================
if os.environ.get('CHECK'):
    print('\n--- CHECK 1: unfiltered move, price 60 s before -> 60 s after, all paired tennis events (no feed-first, no band) ---')
    for cls in sorted(c for c in classes if c.startswith('tennis')):
        sg_, un_, n_ = [], [], 0
        for key, t0, sd, tk, sg in classes[cls]:
            f = fav_tk(tk, sg, sd)
            if not f: continue
            a, b = mid_at(f, t0 - 60), mid_at(f, t0 + 60)
            if a is None or b is None: continue
            sg_.append(b - a); un_.append(abs(b - a)); n_ += 1
        if n_: print('%-52s n=%3d signed median %+.2fc mean %+.2fc | unsigned median %.2fc | share signed>=3c %d%%' % (cls, n_, 100 * statistics.median(sg_), 100 * sum(sg_) / n_, 100 * statistics.median(un_), 100 * sum(1 for x in sg_ if x >= .03) / n_))
    print('\n--- CHECK 3: market type of paired tennis tokens ---')
    cc = collections.Counter()
    for key, (tk, sg) in tk_of.items():
        if key[0] == 'tennis':
            m = [m_ for m_ in mk.values() if tk in m_['tokens']][0]; cc[(m['smt'], m['q'][:0] or 'x')] += 1
    print(cc)
    ex = [m_ for m_ in mk.values() if m_['sport'] == 'tennis'][:6]
    for m_ in ex: print(m_['smt'], '|', m_['q'], '|', m_['outcomes'])
    print('\n--- CHECK 2: hand-check set-winning breaks ---')
    shown = 0
    for key, t0, sd, tk, sg in classes['tennis break that wins the set']:
        if shown >= 5: break
        f = fav_tk(tk, sg, sd)
        if not f or mid_at(f, t0 - 60) is None: continue
        hm = matches.get(key[1]); m = [m_ for m_ in mk.values() if tk in m_['tokens']][0]
        print('\nmatch', key[1][:8], 'diary home/away', hm, '| PM q:', m['q'], m['smt'], m['outcomes'], '| tk sign', sg)
        print('feed event t=%.1f side(home=+1)=%+d  -> favoured PM token outcome: %s' % (t0, sd, m['outcomes'][m['tokens'].index(f)]))
        print('fav mid path (t rel feed): ' + ' '.join('%+d:%.3f' % (d, mid_at(f, t0 + d)) for d in (-60, -30, -15, -10, -5, -2, 0, 2, 5, 10, 20, 30, 60) if mid_at(f, t0 + d) is not None))
        shown += 1
if os.environ.get('CHECK'):
    print('\n--- CHECK 4: where the break move sits relative to the feed (signed median cents per window; real vs random-time placebo) ---')
    W = [(-90, -60), (-60, -30), (-30, -15), (-15, -5), (-5, 5), (5, 15), (15, 60)]
    for cls in ('tennis break (set goes on)', 'tennis break that wins the set', 'tennis hold at 5+ games (not set-ending)'):
        for lab in ('real', 'placebo'):
            out = []
            for a, b in W:
                v = []
                for key, t0, sd, tk, sg in classes[cls]:
                    f = fav_tk(tk, sg, sd)
                    if not f: continue
                    for tt in ([t0] if lab == 'real' else [t0 + random.choice([-1, 1]) * random.uniform(60, 600) for _ in range(3)]):
                        x, y = mid_at(f, tt + a), mid_at(f, tt + b)
                        if x is not None and y is not None: v.append(y - x)
                out.append('[%+d,%+d]s %+.1fc(n%d)' % (a, b, 100 * statistics.median(v), len(v)) if v else 'n/a')
            print('%-42s %-7s %s' % (cls, lab, ' | '.join(out)))
