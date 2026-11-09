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
DIRS = D.split(':')   # several slim dirs may be pooled, colon separated
DELAY = 0.2
def rdm(suffix):
    for d_ in DIRS:
        yield from rd(d_ + suffix)
def rd(p):
    for f in sorted(glob.glob(p, recursive=True)):
        for l in gzip.open(f, 'rt'):
            try: yield json.loads(l)
            except Exception: pass
book = collections.defaultdict(list)
for r in rdm('/books_mid/**/*.gz'):
    book[r['tk']].append((r['ms'] / 1000.0, r['bb'], r['ba'], r['q']))
T = {}
for k in book:
    book[k].sort(); T[k] = [x[0] for x in book[k]]
mk = {}
for m in rdm('/markets.jsonl.gz'):
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
msgs = sorted(rdm('/ts_mqtt/**/*.gz'), key=lambda r: r['ms'])
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
DI = os.path.join(os.path.dirname(DIRS[0].rstrip('/')), 'diary')
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
    if difflib.SequenceMatcher(None, ja.replace(' ', ''), jb.replace(' ', '')).ratio() >= 0.85: return True
    # family-name-first order (Shimizu Yuta vs Yuta Shimizu) and truncated surnames (Staeheli vs Staehel)
    ra, rb = ' '.join(reversed(na)), ' '.join(reversed(nb))
    if difflib.SequenceMatcher(None, ra.replace(' ', ''), jb.replace(' ', '')).ratio() >= 0.85: return True
    if len(na) == len(nb) >= 2 and sorted(na) == sorted(nb): return True
    sa_, sb_ = sorted(na, key=len)[-1], sorted(nb, key=len)[-1]
    k = min(len(sa_), len(sb_))
    if k >= 5 and sa_[:k-1] == sb_[:k-1] and na[0][0] == nb[0][0] or (k >= 5 and sa_[:k-1] == sb_[:k-1] and na[-1][0] == nb[-1][0]): return True
    return False
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

# ================= POINT-LEVEL tennis (coordinator 07:23Z) =================
if os.environ.get('POINTS'):
    RKm = {'0': 0, '15': 1, '30': 2, '40': 3, 'A': 4}
    serve_of = {}
    for r in msgs:
        if not r['topic'].endswith('tennis/match/v1'): continue
        try: ps = json.loads(r['p'])
        except Exception: continue
        for p in ps:
            for s_ in (p.get('timeline') or []):
                for q_ in s_.get('rounds', []):
                    sc = q_.get('score')
                    if sc and sc.get('serve') in (1, 2): serve_of[(p['id'], s_['set'], q_['round'])] = 1 if sc['serve'] == 1 else -1
    def server(m_, s_, r_):
        if (m_, s_, r_) in serve_of: return serve_of[(m_, s_, r_)]
        for d in (1, 2, 3, 4, 5, 6):
            for rr, fl in ((r_ - d, 1 if d % 2 == 0 else -1), (r_ + d, 1 if d % 2 == 0 else -1)):
                if (m_, s_, rr) in serve_of: return fl * serve_of[(m_, s_, rr)]
        return None
    pcls = collections.defaultdict(list); seen_p = set(); fmp = set(); npts = 0; pmeta = {}
    for r in msgs:
        if not r['topic'].endswith('tennis/match/v1'): continue
        try: ps = json.loads(r['p'])
        except Exception: continue
        t = r['ms'] / 1000.0
        for p in ps:
            tl = p.get('timeline')
            if not tl: continue
            m_ = p['id']; fm = m_ not in fmp; fmp.add(m_)
            for s_ in tl:
                for q_ in s_.get('rounds', []):
                    pts = q_.get('points') or []
                    sv = server(m_, s_['set'], q_['round'])
                    prev = (0, 0)
                    for i, pt in enumerate(pts):
                        cur = (RKm.get(pt[0]), RKm.get(pt[1]))
                        k = (m_, s_['set'], q_['round'], i)
                        if None in cur: prev = (0, 0); continue
                        if k in seen_p: prev = cur; continue
                        seen_p.add(k)
                        a, b = prev, cur; prev = cur
                        if fm or sv is None: continue
                        if i > 0 and None in (RKm.get(pts[i - 1][0]), RKm.get(pts[i - 1][1])): continue
                        dh, da = b[0] - a[0], b[1] - a[1]
                        if dh == 1 and da <= 0 or da < 0 and dh >= 0: w = 1
                        elif da == 1 and dh <= 0 or dh < 0 and da >= 0: w = -1
                        else: continue
                        npts += 1
                        ser = (lambda x: x[0] if sv == 1 else x[1]); ret = (lambda x: x[1] if sv == 1 else x[0])
                        bp_before = (ret(a) == 3 and ser(a) < 3) or ret(a) == 4
                        bp_after = (ret(b) == 3 and ser(b) < 3) or ret(b) == 4
                        if w != sv and bp_before: cls = 'point: returner wins at break point (game wins/breaks soon)'
                        elif w == sv and bp_before: cls = 'point: server SAVES break point'
                        elif w != sv and bp_after: cls = 'point: returner wins, creates break point'
                        else: cls = 'point: other'
                        pcls[cls].append(((('tennis', m_)), t, w, k))
                        pmeta[(('tennis', m_), t, w)] = (k[1], k[2], k[3], 1 if w == sv else 0)
    pc2 = collections.defaultdict(list)
    for cls, L in pcls.items():
        for key, t0, sd, k in L:
            ts_ = tk_of.get(key)
            if ts_: pc2[cls].append((key, t0, sd, ts_[0], ts_[1]))
    print('\n--- POINT-LEVEL: points seen live (not first message) with server known:', npts, '| paired to name-verified matches ---')
    def netn(f, t, h):
        r0 = row(f, t + DELAY); pre = mid_at(f, t - 10); en = row(f, t + DELAY + 1.0); x = row(f, t + DELAY + h)
        if not (r0 and pre is not None and en and x) or not (0.25 <= pre <= 0.75) or en[2] - en[1] > 0.03: return None   # NO feed-first filter
        return x[1] - en[2]
    random.seed(88)
    for cls in sorted(pc2):
        L = pc2[cls]
        W = [(-30, 0), (0, 30)]
        out = []
        for lab in ('real', 'plac'):
            row_ = []
            for a, b in W:
                v = []
                for key, t0, sd, tk, sg in L:
                    f = fav_tk(tk, sg, sd)
                    if not f: continue
                    for tt in ([t0] if lab == 'real' else [t0 + random.choice([-1, 1]) * random.uniform(60, 600) for _ in range(5)]):
                        x, y = mid_at(f, tt + a), mid_at(f, tt + b)
                        if x is not None and y is not None and 0.25 <= x <= 0.75: v.append(y - x)
                row_.append('[%+d,%+d]s median %+.2fc mean %+.2fc (n%d)' % (a, b, 100 * statistics.median(v), 100 * sum(v) / len(v), len(v)) if v else 'n/a')
            out.append((lab, row_))
        R = {h: [] for h in (10, 30)}; P = {h: [] for h in R}
        for key, t0, sd, tk, sg in L:
            f = fav_tk(tk, sg, sd)
            if not f: continue
            for h in R:
                v = netn(f, t0, h)
                if v is not None: R[h].append((key, v))
                for _ in range(5):
                    v = netn(f, t0 + random.choice([-1, 1]) * random.uniform(60, 600), h)
                    if v is not None: P[h].append((key, v))
        print('\n%s | events %d, matches %d' % (cls, len(L), len(set(k for k, *_ in L))))
        for lab, row_ in out: print('  move %-5s %s' % (lab, ' || '.join(row_)))
        for h in R:
            a, b = R[h], P[h]
            if not a: print('  net +%ds: n=0' % h); continue
            ci = bd(a, b)
            print('  net taker (buy ask +1.2 s, sell bid +%ds, all events, spread<=3c, 25-75%%): real n=%d median %+.2fc mean %+.2fc | placebo n=%d median %+.2fc mean %+.2fc | mean diff 90%% CI %s' % (h, len(a), 100 * statistics.median([v for _, v in a]), 100 * sum(v for _, v in a) / len(a), len(b), 100 * statistics.median([v for _, v in b]), 100 * sum(v for _, v in b) / len(b), ('[%+.2f, %+.2f]' % ci) if ci else 'n/a'))

# ---- half-move timing at 1 s resolution (coordinator 07:24Z)
if os.environ.get('POINTS'):
    def halft(f, t):
        pre = mid_at(f, t - 30); post = mid_at(f, t + 10)
        if pre is None or post is None or not (0.25 <= pre <= 0.75) or post - pre < 0.03: return None
        for s in range(-30, 11):
            x = mid_at(f, t + s)
            if x is not None and x - pre >= (post - pre) / 2 - 1e-9: return s
        return None
    pq = lambda a, q: sorted(a)[min(len(a) - 1, int(q * len(a)))]
    random.seed(99)
    print('\n--- HALF-MOVE TIME relative to feed message (s; negative = price got half its move BEFORE the message). Events whose total move t-30..t+10 is >=3c favourable ---')
    for cls in sorted(pc2):
        for lab in ('real', 'placebo'):
            hs = []; tot = 0
            for key, t0, sd, tk, sg in pc2[cls]:
                f = fav_tk(tk, sg, sd)
                if not f: continue
                for tt in ([t0] if lab == 'real' else [t0 + random.choice([-1, 1]) * random.uniform(60, 600) for _ in range(5)]):
                    tot += 1; h = halft(f, tt)
                    if h is not None: hs.append(h)
            if hs: print('%-62s %-7s n_big=%3d of %4d (%.0f%%) | median %+d s, 10-90%% range [%+d, %+d] s | share before message (<=-1): %.0f%%' % (cls, lab, len(hs), tot, 100 * len(hs) / tot, statistics.median(hs), pq(hs, .1), pq(hs, .9), 100 * sum(1 for h in hs if h <= -1) / len(hs)))
            else: print(cls, lab, 'none')

# ================= LAG reference: Polymarket sports-ws tennis score vs TheSports vs price (same logger clock) =================
if os.environ.get('LAG'):
    pass
    pmg = collections.defaultdict(dict); pmnames = {}
    for r in rdm('/pmws.jsonl.gz'):
        if r.get('leagueAbbreviation') not in ('atp', 'wta', 'challenger'): continue
        gid = r['gameId']; pmnames[gid] = (r['homeTeam'], r['awayTeam'])
        sc = (r.get('score') or '').split(',')[-1].strip(); per = r.get('period') or ''
        try: a, b = [int(x) for x in sc.split('-')]; s_ = int(per.replace('S', ''))
        except Exception: continue
        pmg[gid].setdefault((s_, a, b), r['ms'] / 1000.0)
    tsg = collections.defaultdict(dict); fm_ = set()
    for r in msgs:
        if not r['topic'].endswith('tennis/match/v1'): continue
        try: ps = json.loads(r['p'])
        except Exception: continue
        t = r['ms'] / 1000.0
        for p in ps:
            tl = p.get('timeline')
            if not tl: continue
            for s_ in tl:
                for q_ in s_.get('rounds', []):
                    sc = q_.get('score')
                    if sc: tsg[p['id']].setdefault((s_['set'], sc.get('home', 0), sc.get('away', 0)), t)
    diffs = []; halfpm = []; halfts = []; used = 0
    for key, (tk, sg) in tk_of.items():
        if key[0] != 'tennis': continue
        hm = matches.get(key[1])
        gid = [g for g, nm in pmnames.items() if hm and ((same(hm[0], nm[0]) and same(hm[1], nm[1])) or (same(hm[0], nm[1]) and same(hm[1], nm[0])))]
        if not gid: continue
        gid = gid[0]; sw = same(hm[0], pmnames[gid][1]) and not same(hm[0], pmnames[gid][0]); used += 1
        for (s_, a, b), tt in tsg[key[1]].items():
            if (s_, a, b) not in tsg[key[1]] or tt - min(tsg[key[1]].values()) < 1: continue    # skip history in first message
            k2 = (s_, b, a) if sw else (s_, a, b)
            if k2 not in pmg[gid]: continue
            tp = pmg[gid][k2]; diffs.append(tt - tp)
            prev = (s_, a - 1, b) if a > 0 else None
    pq = lambda a, q: sorted(a)[min(len(a) - 1, int(q * len(a)))]
    print('\nLAG: matches matched between TheSports and PM sports-ws:', used, '| game-score changes seen by both:', len(diffs))
    if diffs: print('TheSports first-seen minus PM sports-ws first-seen (s; positive = TheSports later): median %+.1f, 10-90%% range [%+.1f, %+.1f]' % (statistics.median(diffs), pq(diffs, .1), pq(diffs, .9)))

# ================= END-OF-MATCH timestamps (Nick 07:42Z) =================
if os.environ.get('ENDS'):
    dstat = {}
    for f in glob.glob(DI + '/tennis-*.json'):
        d = json.load(open(f))
        for m in d.get('results', []): dstat[m['id']] = m
    pm_end = {}
    for r in rdm('/pmws.jsonl.gz'):
        if r.get('leagueAbbreviation') in ('atp', 'wta', 'challenger') and r.get('ended'): pm_end.setdefault(r['gameId'], r['ms'] / 1000.0)
    tsg2 = collections.defaultdict(dict); lastmsg = {}
    for r in msgs:
        if not r['topic'].endswith('tennis/match/v1'): continue
        try: ps = json.loads(r['p'])
        except Exception: continue
        t = r['ms'] / 1000.0
        for p in ps:
            lastmsg[p['id']] = t
            for s_ in (p.get('timeline') or []):
                for q_ in s_.get('rounds', []):
                    sc = q_.get('score')
                    if sc: tsg2[p['id']].setdefault((s_['set'], q_['round'], sc.get('home', 0), sc.get('away', 0)), t)
    rowsE = []
    for key, (tk, sg) in tk_of.items():
        if key[0] != 'tennis': continue
        dm = dstat.get(key[1]); hm = matches.get(key[1])
        if not dm or dm.get('status_id') != 100 or not dm.get('scores') or 'ft' not in dm['scores']: continue
        ft = dm['scores']['ft']
        if ft[0] == ft[1]: continue
        hw = 1 if ft[0] > ft[1] else -1
        wtk = fav_tk(tk, sg, hw)
        if not wtk: continue
        gid = [g for g, nm in pmnames.items() if ((same(hm[0], nm[0]) and same(hm[1], nm[1])) or (same(hm[0], nm[1]) and same(hm[1], nm[0])))] if 'pmnames' in globals() else []
        # price final: first t where winner mid >=0.95 and stays >=0.95 through end of data
        ts_ = T[wtk]; mids = [(book[wtk][i][1] + book[wtk][i][2]) / 2 for i in range(len(ts_))]
        pf = None
        for i in range(len(ts_) - 1, -1, -1):
            if mids[i] < 0.95: pf = ts_[i + 1] if i + 1 < len(ts_) else None; break
        else: pf = ts_[0]
        lastgame = max(tsg2[key[1]].items(), key=lambda kv: kv[1])[1] if tsg2[key[1]] else None
        pf99 = None
        for i in range(len(ts_) - 1, -1, -1):
            if mids[i] < 0.985: pf99 = ts_[i + 1] if i + 1 < len(ts_) else None; break
        rowsE.append(dict(m=key[1], upd=dm.get('updated_at'), pf=pf, pf99=pf99, lg=lastgame, lm=lastmsg.get(key[1]), pm=pm_end.get(gid[0]) if gid else None))
    print('\nEND-OF-MATCH: ended matches with winner token and diary: %d' % len(rowsE))
    pq = lambda a, q: sorted(a)[min(len(a) - 1, int(q * len(a)))]
    def rep(lab, a):
        a = [x for x in a if x is not None]
        print('%-70s n=%2d median %+7.1f s, 10-90%% [%+.1f, %+.1f]' % (lab, len(a), statistics.median(a), pq(a, .1), pq(a, .9)) if a else lab + ' n=0')
    rep('price final jump (winner stays >=95%) minus TheSports diary updated_at', [r['pf'] - r['upd'] for r in rowsE if r['pf'] and r['upd']])
    rep('TheSports last game-result message minus diary updated_at', [r['lg'] - r['upd'] for r in rowsE if r['lg'] and r['upd']])
    rep('TheSports last message minus diary updated_at', [r['lm'] - r['upd'] for r in rowsE if r['lm'] and r['upd']])
    rep('PM sports-ws "ended" minus diary updated_at', [r['pm'] - r['upd'] for r in rowsE if r['pm'] and r['upd']])
    rep('price final jump minus TheSports last game-result message', [r['pf'] - r['lg'] for r in rowsE if r['pf'] and r['lg']])
    rep('PM sports-ws "ended" minus TheSports last game-result message', [r['pm'] - r['lg'] for r in rowsE if r['pm'] and r['lg']])
    rep('price reaches and STAYS >=98.5% minus TheSports last game-result message', [r['pf99'] - r['lg'] for r in rowsE if r['pf99'] and r['lg']])
    rep('PM sports-ws "ended" minus price STAYS >=98.5%', [r['pm'] - r['pf99'] for r in rowsE if r['pm'] and r['pf99']])

if os.environ.get('DUMP'):
    dm_ = {}
    for f in glob.glob(DI + '/tennis-*.json'):
        for m in json.load(open(f)).get('results', []): dm_[m['id']] = m
    print('match_id,home,away,scheduled_start_utc_epoch,first_ts_msg_epoch,last_ts_msg_epoch')
    fl = {}
    for r in msgs:
        if r['topic'].endswith('tennis/match/v1'):
            try:
                for p in json.loads(r['p']): fl.setdefault(p['id'], [r['ms'] / 1000, 0])[1] = r['ms'] / 1000
            except Exception: pass
    for key in tk_of:
        if key[0] == 'tennis' and key[1] in dm_:
            h, a = matches[key[1]]; print('%s,"%s","%s",%s,%.0f,%.0f' % (key[1], h, a, dm_[key[1]]['match_time'], fl[key[1]][0], fl[key[1]][1]))

# ================= CS2 / generic: unfiltered windows, half-move timing, taker net (no feed-first filter) =================
if os.environ.get('CS2'):
    def halft2(f, t):
        pre = mid_at(f, t - 30); post = mid_at(f, t + 10)
        if pre is None or post is None or not (0.25 <= pre <= 0.75) or post - pre < 0.03: return None
        for s in range(-30, 11):
            x = mid_at(f, t + s)
            if x is not None and x - pre >= (post - pre) / 2 - 1e-9: return s
        return None
    pq2 = lambda a, q: sorted(a)[min(len(a) - 1, int(q * len(a)))]
    def netn2(f, t, h):
        r0 = row(f, t + DELAY); pre = mid_at(f, t - 10); en = row(f, t + DELAY + 1.0); x = row(f, t + DELAY + h)
        if not (r0 and pre is not None and en and x) or not (0.25 <= pre <= 0.75) or en[2] - en[1] > 0.03: return None
        return x[1] - en[2]
    random.seed(123)
    SP = os.environ['CS2']
    allL = [x for c in classes if c.startswith(SP) for x in classes[c]]
    for cls, L in [(c, classes[c]) for c in sorted(classes) if c.startswith(SP)] + [(SP + ' ALL', allL)]:
        print('\n== %s | events %d, maps/matches %d' % (cls, len(L), len(set(k for k, *_ in L))))
        W = [(-90, -60), (-60, -30), (-30, -15), (-15, -5), (-5, 5), (5, 15), (15, 60)]
        for lab in ('real', 'placebo'):
            out = []
            for a, b in W:
                v = []
                for key, t0, sd, tk, sg in L:
                    f = fav_tk(tk, sg, sd)
                    if not f: continue
                    for tt in ([t0] if lab == 'real' else [t0 + random.choice([-1, 1]) * random.uniform(60, 600) for _ in range(3)]):
                        x, y = mid_at(f, tt + a), mid_at(f, tt + b)
                        if x is not None and y is not None and 0.25 <= x <= 0.75: v.append(y - x)
                out.append('[%+d,%+d] %+.1fc(n%d)' % (a, b, 100 * statistics.median(v), len(v)) if v else 'n/a')
            print('  move %-7s %s' % (lab, ' | '.join(out)))
        for lab in ('real', 'placebo'):
            hs = []; tot = 0
            for key, t0, sd, tk, sg in L:
                f = fav_tk(tk, sg, sd)
                if not f: continue
                for tt in ([t0] if lab == 'real' else [t0 + random.choice([-1, 1]) * random.uniform(60, 600) for _ in range(5)]):
                    tot += 1; h = halft2(f, tt)
                    if h is not None: hs.append(h)
            print('  half-move %-7s big moves %d of %d (%.0f%%)%s' % (lab, len(hs), tot, 100 * len(hs) / max(tot, 1), (' | median %+d s, 10-90%% [%+d, %+d]' % (statistics.median(hs), pq2(hs, .1), pq2(hs, .9))) if hs else ''))
        for h in (10, 30):
            a, b = [], []
            for key, t0, sd, tk, sg in L:
                f = fav_tk(tk, sg, sd)
                if not f: continue
                v = netn2(f, t0, h)
                if v is not None: a.append((key, v))
                for _ in range(5):
                    v = netn2(f, t0 + random.choice([-1, 1]) * random.uniform(60, 600), h)
                    if v is not None: b.append((key, v))
            if a: 
                ci = bd(a, b)
                print('  net taker +%ds: real n=%d median %+.2fc mean %+.2fc | placebo n=%d median %+.2fc mean %+.2fc | diff 90%% CI %s' % (h, len(a), 100 * statistics.median([v for _, v in a]), 100 * sum(v for _, v in a) / len(a), len(b), 100 * statistics.median([v for _, v in b]) if b else float('nan'), 100 * sum(v for _, v in b) / len(b) if b else float('nan'), ('[%+.2f, %+.2f]' % ci) if ci else 'n/a'))
            else: print('  net taker +%ds: n=0' % h)

# ================= CS2 in-round events (typeid 8 kill, typeid 2 round end) vs c_score (coordinator 13:18Z) =================
if os.environ.get('CS2EV'):
    cev = collections.defaultdict(list); seen_c = set(); fmc = set(); cs_lag = []
    cs_first_score = {}
    for r in msgs:
        if not r['topic'].endswith('csgo/match/v1'): continue
        try: ps = json.loads(r['p'])
        except Exception: continue
        t = r['ms'] / 1000.0
        for p in ps:
            key = ('cs2', p['match_id'], p.get('map_id')); fm = key not in fmc; fmc.add(key)
            hs = p['home'].get('side')
            for e in (p.get('event') or []):
                k2 = (key, e['typeid'], e['index'])
                if k2 in seen_c: continue
                seen_c.add(k2)
                if fm: continue
                if e['typeid'] == 8 and e.get('killerside') in (1, 2) and hs in (1, 2):
                    cev[key].append((t, 1 if e['killerside'] == hs else -1, 'cs2 kill (typeid 8)'))
                elif e['typeid'] == 2 and e.get('winner_side') in (1, 2) and hs in (1, 2):
                    cev[key].append((t, 1 if e['winner_side'] == hs else -1, 'cs2 round-end event (typeid 2)'))
    cl = collections.defaultdict(list)
    for key, evs in cev.items():
        if key not in tk_of: continue
        tk, sg = tk_of[key]
        for t0, sd, cls in evs: cl[cls].append((key, t0, sd, tk, sg))
    # lag of typeid-2 round-end event vs c_score update for same round (first-seen times)
    cs_t = {}
    for key, evs in ev.items():
        if key[0] == 'cs2':
            for i, (t0, sd) in enumerate(evs): cs_t.setdefault(key, []).append(t0)
    for key, evs in cev.items():
        r2 = [t for t, sd, c in evs if c.startswith('cs2 round-end')]
        if key in cs_t and r2:
            for t in r2:
                near = [x - t for x in cs_t[key] if abs(x - t) < 60]
                if near: cs_lag.append(min(near, key=abs))
    if cs_lag: print('\nround-end event (typeid 2) first-seen vs c_score change first-seen for the same round: c_score minus event median %+.1f s, 10-90%% [%+.1f, %+.1f] (n=%d)' % (statistics.median(cs_lag), sorted(cs_lag)[int(.1 * len(cs_lag))], sorted(cs_lag)[int(.9 * len(cs_lag))], len(cs_lag)))
    random.seed(7)
    for cls in sorted(cl):
        L = cl[cls]
        print('\n== %s | events %d, maps %d' % (cls, len(L), len(set(k for k, *_ in L))))
        for lab in ('real', 'placebo'):
            out = []
            for a, b in ((-60, -30), (-30, -15), (-15, -5), (-5, 0), (0, 5), (5, 15), (15, 30), (30, 60), (-60, 60)):
                v = []
                for key, t0, sd, tk, sg in L:
                    f = fav_tk(tk, sg, sd)
                    if not f: continue
                    for tt in ([t0] if lab == 'real' else [t0 + random.choice([-1, 1]) * random.uniform(60, 600) for _ in range(3)]):
                        x, y = mid_at(f, tt + a), mid_at(f, tt + b)
                        if x is not None and y is not None and 0.1 <= x <= 0.9: v.append(y - x)
                out.append('[%+d,%+d] mean %+.2fc(n%d)' % (a, b, 100 * sum(v) / len(v), len(v)) if v else 'n/a')
            print('  signed move %-7s %s' % (lab, ' | '.join(out)))
        for h in (5, 10, 30):
            a, b = [], []
            for key, t0, sd, tk, sg in L:
                f = fav_tk(tk, sg, sd)
                if not f: continue
                v = netn2(f, t0, h) if 'netn2' in globals() else None
                if v is not None: a.append((key, v))
                for _ in range(5):
                    v = netn2(f, t0 + random.choice([-1, 1]) * random.uniform(60, 600), h)
                    if v is not None: b.append((key, v))
            if a:
                ci = bd(a, b)
                print('  net taker +%ds (all events, spread<=3c, 25-75%%): real n=%d mean %+.2fc median %+.2fc | placebo n=%d mean %+.2fc | diff 90%% CI %s' % (h, len(a), 100 * sum(v for _, v in a) / len(a), 100 * statistics.median([v for _, v in a]), len(b), 100 * sum(v for _, v in b) / len(b) if b else float('nan'), ('[%+.2f, %+.2f]' % ci) if ci else 'n/a'))
if os.environ.get('CS2EV'):
    agree = collections.Counter()
    for key, evs in cev.items():
        if key not in tk_of: continue
        for t, sd, c in evs:
            if not c.startswith('cs2 round-end'): continue
            near = [(abs(x - t), s2) for x, s2 in ev[key] if abs(x - t) < 60]
            if near:
                s2 = min(near)[1]; agree[(key[1][:6], sd == s2)] += 1
    tot = collections.Counter()
    for (m, ok), n in agree.items(): tot[ok] += n
    print('\nround-end typeid-2 side vs c_score-derived side: agree %d, disagree %d' % (tot[True], tot[False]))
    for m in sorted(set(m for m, _ in agree)): print('  match', m, 'agree', agree[(m, True)], 'disagree', agree[(m, False)])
if os.environ.get('CS2EV'):
    def mv(key, t, sd, a, b):
        tk, sg = tk_of[key]; f = fav_tk(tk, sg, sd)
        if not f: return None
        x, y = mid_at(f, t + a), mid_at(f, t + b)
        return None if x is None or y is None or not (0.1 <= x <= 0.9) else y - x
    print('\nSAME-ROUND COMPARISON (window -90..+60, mean signed move, cents)')
    A, B, C = [], [], []
    for key, evs in cev.items():
        if key not in tk_of: continue
        for t, sd, c in evs:
            if not c.startswith('cs2 round-end'): continue
            near = [(abs(x - t), x, s2) for x, s2 in ev[key] if abs(x - t) < 60]
            if not near: continue
            _, x, s2 = min(near)
            m1 = mv(key, x, s2, -90, 60)        # c_score event: its own time and side
            m2 = mv(key, t, sd, -90, 60)        # typeid-2 event: its time and side
            m3 = mv(key, x, s2, -90, 60) if sd == s2 else None
            if m1 is not None: A.append(m1)
            if m2 is not None: B.append(m2)
            if m3 is not None: C.append(m3)
    f_ = lambda a: 'mean %+.2fc n=%d' % (100 * sum(a) / len(a), len(a)) if a else 'n/a'
    print('c_score events (matched to a typeid-2 event):', f_(A)); print('typeid-2 events:', f_(B)); print('c_score events where both sides agree:', f_(C))

# ================= DOTA 2 (Nick/coordinator 15:02Z): kills, towers, barracks, Roshan vs price, same method as corrected CS2 =================
if os.environ.get('DOTA'):
    pop = lambda x: bin(int(x)).count('1')
    dkey_names = {}
    dev = collections.defaultdict(list); dprev = {}; dfm = set()
    for r in msgs:
        if not r['topic'].endswith('dota2/match/v1'): continue
        try: ps = json.loads(r['p'])
        except Exception: continue
        t = r['ms'] / 1000.0
        for p in ps:
            key = ('dota2', p['match_id'], p['box_num'])
            if p.get('status_id') != 2 and key not in dprev: pass
            h, a = p['home']['stats'], p['away']['stats']
            cur = (h[0], a[0], pop(h[1]), pop(a[1]), pop(h[2]), pop(a[2]), p.get('roushan_timer') or 0)
            if key in dprev:
                pv = dprev[key]
                # kills
                for side, i in ((1, 0), (-1, 1)):
                    if cur[i] - pv[i] == 1: dev[key].append((t, side, 'dota kill (stats[0])'))
                # towers destroyed (alive-count falls): team losing tower -> OTHER side gains
                if cur[2] < pv[2]: dev[key].append((t, -1, 'dota tower (home tower lost -> away favoured)'))
                if cur[3] < pv[3]: dev[key].append((t, 1, 'dota tower (away tower lost -> home favoured)'))
                if cur[4] < pv[4]: dev[key].append((t, -1, 'dota barracks (home lost -> away favoured)'))
                if cur[5] < pv[5]: dev[key].append((t, 1, 'dota barracks (away lost -> home favoured)'))
                if pv[6] == 0 and cur[6] > 0: dev[key].append((t, 0, 'dota roshan timer started'))
            dprev[key] = cur
    # pair to PM Game N Winner markets by names
    dk = {}
    for key in dev:
        hm = matches.get(key[1])
        if not hm or None in hm: continue
        for tk in [t for t, (sp, q, smt) in tk_sport.items() if sp == 'dota2' and t in book]:
            q = tk_sport[tk][1]
            if ('Game %d Winner' % key[2]) not in q: continue
            m = [m_ for m_ in mk.values() if tk in m_['tokens']][0]
            i = m['tokens'].index(tk); o = m['outcomes'][i]; po = m['outcomes'][1 - i]
            if same(hm[0], o) and same(hm[1], po): dk[key] = (tk, 1); break
            if same(hm[1], o) and same(hm[0], po): dk[key] = (tk, -1); break
    print('\nDOTA: event games %d, names found %d, paired to PM Game-N-Winner market %d' % (len(dev), sum(1 for k in dev if matches.get(k[1])), len(dk)))
    for key, (tk, sg) in dk.items():
        b = book[tk]; print('  ', key[1][:6], 'game', key[2], tk_sport[tk][1][:70], '| rows', len(b), 'median spread %.3f' % statistics.median([x[2] - x[1] for x in b]), '| events', len(dev[key]))
    dl = collections.defaultdict(list)
    for key, evs in dev.items():
        if key not in dk: continue
        tk, sg = dk[key]
        for t0, sd, cls in evs:
            if sd == 0: continue
            dl[cls].append((key, t0, sd, tk, sg))
    random.seed(11)
    def fav_d(tk, sg, side):
        f = tk if side * sg > 0 else partner.get(tk)
        return f if f is not None and f in book else None
    def halft_d(f, t):
        pre = mid_at(f, t - 30); post = mid_at(f, t + 10)
        if pre is None or post is None or not (0.1 <= pre <= 0.9) or post - pre < 0.03: return None
        for s in range(-30, 11):
            x = mid_at(f, t + s)
            if x is not None and x - pre >= (post - pre) / 2 - 1e-9: return s
    def net_d(f, t, h):
        r0 = row(f, t + DELAY); pre = mid_at(f, t - 10); en = row(f, t + DELAY + 1.0); x = row(f, t + DELAY + h)
        if not (r0 and pre is not None and en and x) or not (0.1 <= pre <= 0.9) or en[2] - en[1] > 0.03: return None
        return x[1] - en[2]
    allk = [x for c, L in dl.items() if c.startswith('dota kill') for x in L]
    tw = [x for c, L in dl.items() if c.startswith('dota tower') for x in L]
    br = [x for c, L in dl.items() if c.startswith('dota barracks') for x in L]
    for cls, L in (('KILLS', allk), ('TOWERS', tw), ('BARRACKS', br)):
        print('\n== DOTA %s | events %d, games %d' % (cls, len(L), len(set(k for k, *_ in L))))
        for lab in ('real', 'placebo'):
            out = []
            for a, b in ((-90, -60), (-60, -30), (-30, -15), (-15, 0), (0, 15), (15, 60), (-90, 60)):
                v = []
                for key, t0, sd, tk, sg in L:
                    f = fav_d(tk, sg, sd)
                    if not f: continue
                    for tt in ([t0] if lab == 'real' else [t0 + random.choice([-1, 1]) * random.uniform(60, 600) for _ in range(3)]):
                        x, y = mid_at(f, tt + a), mid_at(f, tt + b)
                        if x is not None and y is not None and 0.1 <= x <= 0.9: v.append(y - x)
                out.append('[%+d,%+d] mean %+.2fc(n%d)' % (a, b, 100 * sum(v) / len(v), len(v)) if v else 'n/a')
            print('  signed move %-7s %s' % (lab, ' | '.join(out)))
        for lab in ('real', 'placebo'):
            hs = []; tot = 0
            for key, t0, sd, tk, sg in L:
                f = fav_d(tk, sg, sd)
                if not f: continue
                for tt in ([t0] if lab == 'real' else [t0 + random.choice([-1, 1]) * random.uniform(60, 600) for _ in range(5)]):
                    tot += 1; h = halft_d(f, tt)
                    if h is not None: hs.append(h)
            print('  half-move %-7s big moves %d of %d%s' % (lab, len(hs), tot, (' | median %+d s, 10-90%% [%+d, %+d]' % (statistics.median(hs), sorted(hs)[int(.1 * len(hs))], sorted(hs)[min(len(hs) - 1, int(.9 * len(hs)))])) if hs else ''))
        for h in (10, 30):
            a, b = [], []
            for key, t0, sd, tk, sg in L:
                f = fav_d(tk, sg, sd)
                if not f: continue
                v = net_d(f, t0, h)
                if v is not None: a.append((key, v))
                for _ in range(5):
                    v = net_d(f, t0 + random.choice([-1, 1]) * random.uniform(60, 600), h)
                    if v is not None: b.append((key, v))
            if a:
                ci = bd(a, b)
                print('  net taker +%ds: real n=%d mean %+.2fc median %+.2fc | placebo n=%d mean %+.2fc | diff 90%% CI %s' % (h, len(a), 100 * sum(v for _, v in a) / len(a), 100 * statistics.median([v for _, v in a]), len(b), 100 * sum(v for _, v in b) / len(b) if b else float('nan'), ('[%+.2f, %+.2f]' % ci) if ci else 'n/a'))
            else: print('  net taker +%ds: n=0' % h)
    print('\nRoshan timer starts (side unknown, counts only):', sum(1 for evs in dev.values() for e in evs if e[2].startswith('dota roshan')))


# ================= SIGNAL vs NOISE (Nick 8 Nov 02:28Z): per-event lead distributions vs placebo, subsets, cluster-bootstrap =================
# Needs POINTS=1 CS2=cs2 DOTA=1 so the event lists exist. Pool slims with D1:D2.
if os.environ.get('SIGNAL'):
    BOOT = 1500
    NPL = int(os.environ.get('NPL', '20'))   # placebo shifts per event (more = less placebo noise)
    random.seed(2024)
    def curve(f, t):
        """favourable mid at selected offsets, or None"""
        return {s_: mid_at(f, t + s_) for s_ in (-60, -30, 0, 30, 60)}
    def half_lead(f, t):
        pre = mid_at(f, t - 60); post = mid_at(f, t + 60)
        if pre is None or post is None or post - pre < 0.03: return None
        for s_ in range(-60, 61):
            x = mid_at(f, t + s_)
            if x is not None and x - pre >= (post - pre) / 2 - 1e-9: return s_
        return None
    def feats(f, t):
        c = curve(f, t)
        if c[-30] is None or c[0] is None: return None
        before = c[0] - c[-30]
        o = {'p': c[-30], 'before': before, 'quiet': abs(before) < 0.01}
        o['after'] = (c[30] - c[0]) if c[30] is not None else None
        h = half_lead(f, t)
        o['lead'] = h
        o['big'] = h is not None
        return o
    def sig_events(L, band=None):
        R, P = collections.defaultdict(list), collections.defaultdict(list)
        for key, t0, sd, tk, sg in L:
            f = fav_tk(tk, sg, sd)
            if not f: continue
            o = feats(f, t0)
            if o is None or not (0.02 < o['p'] < 0.98): continue
            if band and not (band[0] <= o['p'] < band[1]): continue
            R[key].append(o)
            for _ in range(NPL):
                tt = t0 + random.choice([-1, 1]) * random.uniform(60, 600)
                q = feats(f, tt)
                if q is not None and (not band or band[0] <= q['p'] < band[1]) and 0.02 < q['p'] < 0.98: P[key].append(q)
        return R, P
    def agg(G, fn):
        """per-game (sum, n) of fn over events where fn is not None"""
        out = {}
        for k, L in G.items():
            v = [fn(o) for o in L]; v = [x for x in v if x is not None]
            if v: out[k] = (sum(v), len(v))
        return out
    def mean_of(a):
        n = sum(x[1] for x in a.values()); return (sum(x[0] for x in a.values()) / n, n) if n else (None, 0)
    def bdiff(ra, pa):
        games = sorted(set(ra) | set(pa))
        if not ra or not pa: return None
        ds = []
        for _ in range(BOOT):
            g = random.choices(games, k=len(games))
            rs = sum(ra[k][0] for k in g if k in ra); rn = sum(ra[k][1] for k in g if k in ra)
            ps = sum(pa[k][0] for k in g if k in pa); pn = sum(pa[k][1] for k in g if k in pa)
            if rn and pn: ds.append(rs / rn - ps / pn)
        if len(ds) < BOOT // 2: return None
        ds.sort(); lo, hi = ds[int(.05 * len(ds))], ds[int(.95 * len(ds))]
        pv = 2 * min(sum(1 for d in ds if d <= 0), sum(1 for d in ds if d >= 0)) / len(ds)
        return lo, hi, min(1.0, pv)
    def line(name, R, P, fn, scale=100, unit='c', cond=None):
        f2 = (lambda o: fn(o) if (cond is None or cond(o)) else None)
        ra, pa = agg(R, f2), agg(P, f2)
        (rm, rn), (pm, pn) = mean_of(ra), mean_of(pa)
        if rn < 5 or pn < 5: return '    %-44s n real %d / placebo %d (too few)' % (name, rn, pn)
        b = bdiff(ra, pa)
        return '    %-44s real %+7.2f%s (n%d) | placebo %+7.2f%s (n%d) | diff 90%% CI %s p=%s' % (name, rm * scale, unit, rn, pm * scale, unit, pn, ('[%+.2f, %+.2f]' % (b[0] * scale, b[1] * scale)) if b else 'n/a', ('%.2f' % b[2]) if b else 'n/a')
    tp = [x for c, L in pc2.items() for x in L]
    groups = collections.OrderedDict()
    groups['TENNIS all points'] = tp
    groups['TENNIS break-point points'] = [x for c, L in pc2.items() if 'break point' in c or 'SAVES' in c for x in L]
    groups['TENNIS other points'] = pc2.get('point: other', [])
    groups['TENNIS game-level breaks (set goes on)'] = classes.get('tennis break (set goes on)', [])
    groups['CS2 all round wins'] = [x for c, L in classes.items() if c.startswith('cs2') for x in L]
    groups['CS2 late rounds (loser>=10)'] = classes.get('cs2 round, loser already >=10 (late, winner<12)', [])
    groups['DOTA kills'] = allk
    groups['DOTA towers'] = tw
    BANDS = [('all prices', None), ('fav price 0.10-0.40', (0.10, 0.40)), ('fav price 0.40-0.60', (0.40, 0.60)), ('fav price 0.60-0.90', (0.60, 0.90))]
    print('\n=== SIGNAL vs NOISE: pooled over %d slim dir(s); favourable = side the event helps; cents; placebo = same events shifted +-60-600 s (5 each); CI/p = bootstrap over games ===' % len(DIRS))
    print('before = fav mid move t-30..t (price already reacting); after = move t..t+30; QUIET = price moved <1c in the 30 s before the message (known at message time, so tradeable-filter, not look-ahead)')
    for gname, L in groups.items():
        for bname, band in BANDS:
            R, P = sig_events(L, band)
            ne = sum(len(v) for v in R.values())
            if ne < 8: continue
            print('\n## %s | %s | events with prices %d, games %d' % (gname, bname, ne, len(R)))
            print(line('before: move t-30..t, all', R, P, lambda o: o['before']))
            print(line('after: move t..t+30, all', R, P, lambda o: o['after']))
            print(line('after: move t..t+30, QUIET only', R, P, lambda o: o['after'], cond=lambda o: o['quiet']))
            print(line('share QUIET at message', R, P, lambda o: 1.0 if o['quiet'] else 0.0, scale=100, unit='%'))
            print(line('share with a big move (>=3c, t-60..t+60)', R, P, lambda o: 1.0 if o['big'] else 0.0, scale=100, unit='%'))
            print(line('lead s (half-move rel. message), big only', R, P, lambda o: o['lead'], scale=1, unit='s', cond=lambda o: o['big']))
            print(line('share of big moves LATE (half-move >0 s)', R, P, lambda o: 1.0 if o['lead'] > 0 else 0.0, scale=100, unit='%', cond=lambda o: o['big']))
            print(line('share of big moves EARLY (<=-10 s)', R, P, lambda o: 1.0 if o['lead'] <= -10 else 0.0, scale=100, unit='%', cond=lambda o: o['big']))

# ---- tennis state splits (needs POINTS=1 SIGNAL=1 SPLIT=1)
if os.environ.get('SPLIT') and os.environ.get('SIGNAL'):
    def split_filter(L, fn):
        return [x for x in L if (x[0], x[1], x[2]) in pmeta and fn(pmeta[(x[0], x[1], x[2])])]
    tsplits = [
        ('set 1', lambda m: m[0] == 1), ('set 2', lambda m: m[0] == 2), ('set 3+', lambda m: m[0] >= 3),
        ('game 1-4 of set', lambda m: m[1] <= 4), ('game 5-8 of set', lambda m: 5 <= m[1] <= 8), ('game 9+ of set', lambda m: m[1] >= 9),
        ('first 2 points of game', lambda m: m[2] <= 1), ('3rd+ point of game', lambda m: m[2] >= 2),
        ('server won point', lambda m: m[3] == 1), ('returner won point', lambda m: m[3] == 0),
    ]
    print('\n=== TENNIS STATE SPLITS (all points, all prices; QUIET = price moved <1c in the 30 s before the message) ===')
    for nm, fn in tsplits:
        L = split_filter(tp, fn)
        R, P = sig_events(L, None)
        ne = sum(len(v) for v in R.values())
        if ne < 8: print('\n## %s | events %d (too few)' % (nm, ne)); continue
        print('\n## %s | events with prices %d, games %d' % (nm, ne, len(R)))
        print(line('after: move t..t+30, QUIET only', R, P, lambda o: o['after'], cond=lambda o: o['quiet']))
        print(line('after: move t..t+30, all', R, P, lambda o: o['after']))
        print(line('share QUIET at message', R, P, lambda o: 1.0 if o['quiet'] else 0.0, scale=100, unit='%'))
        print(line('share of big moves LATE (half-move >0 s)', R, P, lambda o: 1.0 if o['lead'] > 0 else 0.0, scale=100, unit='%', cond=lambda o: o['big']))

# ================= TRADEABILITY (coordinator 9 Nov 00:12Z, pre-authorised): do the quiet-moment moves survive spread, 1 s PM delay, queue, hold to resolution? =================
# TRADE=1 with SIGNAL=1 POINTS=1 CS2=cs2 DOTA=1. Quiet-at-message events only. Order lands at t + 0.2 s (our latency) + DLY (PM sports delay, default 1 s).
# TAKER: buy favourable token at best ask at landing, hold to resolution (settle proxy; unresolved games excluded). Payoff per share = settle - ask.
# BID: post-only at best bid at landing (queue = size shown in books q; fill only if best ask falls to <= our bid within HOLD s = trade-through proxy), hold to resolution; per attempt (0 if unfilled).
# Placebo = same rule at the same events shifted +-60-600 s (conditions re-checked there). Real minus placebo = what the TIMING adds over the side/price bias.
if os.environ.get('TRADE') and os.environ.get('SIGNAL'):
    DLY = float(os.environ.get('DLY', '1.0')); HOLDS = float(os.environ.get('HOLD', '60'))
    def extras(f, t, S):
        te = t + 0.2 + DLY
        r = row(f, te, maxage=5)
        if not r or r[1] <= 0 or r[2] >= 1 or r[2] <= r[1]: return None
        bb, ba, q = r[1], r[2], r[3]
        d = {'taker': S - ba, 'mid': S - (bb + ba) / 2, 'spread': ba - bb, 'ask': ba, 'q': q}
        for hz in (60, 300, 900):
            r2 = row(f, te + hz, maxage=15); m2 = mid_at(f, te + hz)
            d['mtm%d' % hz] = (m2 - ba) if m2 is not None else None            # buy at ask, valued at later mid (no exit cost)
            d['rt%d' % hz] = (r2[1] - ba) if r2 else None                       # buy at ask, sell at later best bid (full round trip)
        ts = T[f]; i = bisect.bisect_right(ts, te)
        filled = False
        while i < len(ts) and ts[i] <= te + HOLDS:
            if book[f][i][2] <= bb + 1e-9: filled = True; break
            i += 1
        d['filled'] = 1.0 if filled else 0.0
        d['bid'] = (S - bb) if filled else 0.0
        d['bidfill'] = (S - bb) if filled else None
        return d
    def trade_events(L, band):
        R, P = collections.defaultdict(list), collections.defaultdict(list)
        for key, t0, sd, tk, sg in L:
            f = fav_tk(tk, sg, sd)
            if not f: continue
            S = settle(f)
            if S is None: continue
            def mk_(t):
                o = feats(f, t)
                if o is None or not o['quiet'] or not (0.02 < o['p'] < 0.98): return None
                if band and not (band[0] <= o['p'] < band[1]): return None
                x = extras(f, t, S)
                if x is None: return None
                o.update(x); return o
            o = mk_(t0)
            if o: R[key].append(o)
            for _ in range(NPL):
                q_ = mk_(t0 + random.choice([-1, 1]) * random.uniform(60, 600))
                if q_: P[key].append(q_)
        return R, P
    print('\n=== TRADEABILITY: quiet-at-message events, order lands t+0.2 s+%.1f s PM delay, hold to resolution, cents per share; placebo = same rule at shifted times; CI/p bootstrap over games ===' % DLY)
    TG = [('TENNIS all points', tp, [('fav 0.10-0.40', (0.10, 0.40)), ('fav 0.40-0.60', (0.40, 0.60)), ('fav 0.10-0.60', (0.10, 0.60)), ('fav 0.60-0.90', (0.60, 0.90))]),
          ('DOTA kills', allk, [('fav 0.60-0.90', (0.60, 0.90)), ('fav 0.40-0.90', (0.40, 0.90))]),
          ('CS2 all round wins', groups['CS2 all round wins'], [('fav 0.40-0.60', (0.40, 0.60))])]
    for gname, L, bands in TG:
        for bname, band in bands:
            R, P = trade_events(L, band)
            ne = sum(len(v) for v in R.values())
            if ne < 8: print('\n## %s | %s | too few (%d)' % (gname, bname, ne)); continue
            print('\n## %s | %s | resolved quiet events %d, games %d' % (gname, bname, ne, len(R)))
            print(line('mean spread paid (ask-bid)', R, P, lambda o: o['spread']))
            print(line('TAKER at ask, hold: net per share', R, P, lambda o: o['taker']))
            print(line('(same, valued at mid, no spread)', R, P, lambda o: o['mid']))
            for hz in (60, 300, 900):
                print(line('TAKER buy ask, value at mid +%ds (no exit cost)' % hz, R, P, lambda o, hz=hz: o['mtm%d' % hz]))
                print(line('TAKER buy ask, SELL at bid +%ds (round trip)' % hz, R, P, lambda o, hz=hz: o['rt%d' % hz]))
            print(line('BID at best bid: fill rate', R, P, lambda o: o['filled'], scale=100, unit='%'))
            print(line('BID net per attempt (0 if no fill)', R, P, lambda o: o['bid']))
            print(line('BID net per FILL', R, P, lambda o: o['bidfill'], cond=lambda o: o['filled'] > 0))
            print(line('queue ahead at landing (shares)', R, P, lambda o: o['q'], scale=1, unit=' sh'))

# ---- TRADE_DETAIL (Nick 9 Nov 00:19Z "how is this noisy?"): per-match view of hold-to-resolution taker payoff, clustered bootstrap, leave-out, multiple-test correction
if os.environ.get('TRADE_DETAIL') and os.environ.get('TRADE') and os.environ.get('SIGNAL'):
    def hold_diff(R, P, skip=()):
        ra = agg({k: v for k, v in R.items() if k not in skip}, lambda o: o['taker']); pa = agg({k: v for k, v in P.items() if k not in skip}, lambda o: o['taker'])
        (rm, rn), (pm, pn) = mean_of(ra), mean_of(pa)
        return ra, pa, rm, pm
    allp = []   # p-values of every hold-to-resolution taker test run above (for correction)
    for gname, L, bands in TG:
        for bname, band in bands:
            R, P = trade_events(L, band)
            if sum(len(v) for v in R.values()) < 8: continue
            ra, pa = agg(R, lambda o: o['taker']), agg(P, lambda o: o['taker'])
            b = bdiff(ra, pa)
            if b: allp.append(((gname, bname), b[2]))
    print('\n### hold-to-resolution TAKER: %d tests run; Holm-adjusted p-values (clustered by match)' % len(allp))
    order = sorted(allp, key=lambda x: x[1]); m = len(order); run = 0.0
    for i, (nm, pv) in enumerate(order):
        run = max(run, min(1.0, (m - i) * pv)); print('   %-45s raw p=%.3f  Holm p=%.3f' % (nm[0] + ' | ' + nm[1], pv, run))
    R, P = trade_events(tp, (0.40, 0.60))
    ra, pa, rm, pm = hold_diff(R, P)
    print('\n### TENNIS 40-60%% per match (cluster = match): real events %d in %d matches; placebo %d' % (sum(len(v) for v in R.values()), len(R), sum(len(v) for v in P.values())))
    rows = []
    for k in sorted(R):
        rv = [o['taker'] for o in R[k]]; pv = [o['taker'] for o in P.get(k, [])]
        win = sum(1 for o in R[k] if o['taker'] + o['ask'] > 0.5) / len(R[k])
        rows.append((k, len(rv), sum(rv) / len(rv), (sum(pv) / len(pv)) if pv else None, win, sum(o['ask'] for o in R[k]) / len(R[k])))
    print('   match key                       n   real c   placebo c   fav-won share  mean ask')
    for r in sorted(rows, key=lambda r: -(r[2] - (r[3] or 0))):
        print('   %-30s %3d  %+7.1f  %9s   %5.0f%%   %.2f' % (str(r[0])[:30], r[1], r[2] * 100, ('%+.1f' % (r[3] * 100)) if r[3] is not None else 'n/a', r[4] * 100, r[5]))
    diffs = [(r[2] - r[3]) for r in rows if r[3] is not None]
    rr = [(r[2], r[3]) for r in rows if r[3] is not None]
    print('   equal-weight-per-match mean(real-placebo) = %+.1fc over %d matches, sd %.1fc, se %.1fc' % (statistics.mean(diffs) * 100, len(diffs), statistics.pstdev(diffs) * 100, statistics.pstdev(diffs) / len(diffs) ** 0.5 * 100))
    print('   matches with real > placebo: %d of %d' % (sum(1 for d in diffs if d > 0), len(diffs)))
    bd = bdiff(ra, pa)
    print('   event-pooled, match-clustered bootstrap: real %+.1fc placebo %+.1fc diff 90%% CI [%+.1f, %+.1f] raw p=%.3f' % (rm * 100, pm * 100, bd[0] * 100, bd[1] * 100, bd[2]))
    # leave-top-k-matches-out
    ranked = [r[0] for r in sorted(rows, key=lambda r: -(r[2] - (r[3] or 0)))]
    for kk in (1, 2, 3, 5):
        sk = set(ranked[:kk]); ra2, pa2, rm2, pm2 = hold_diff(R, P, skip=sk); b2 = bdiff(ra2, pa2)
        print('   drop top %d matches: real %+.1fc placebo %+.1fc diff 90%% CI [%+.1f, %+.1f] p=%.3f' % (kk, rm2 * 100, pm2 * 100, b2[0] * 100, b2[1] * 100, b2[2]))
    # why noisy: payoff per share is S - ask, S is 0/1
    allv = [o['taker'] for v in R.values() for o in v]
    print('   per-event payoff sd = %.1fc (S is 0 or 1), so naive se with n=%d is %.1fc; clustered over %d matches larger because events in one match share one winner' % (statistics.pstdev(allv) * 100, len(allv), statistics.pstdev(allv) / len(allv) ** 0.5 * 100, len(R)))

# ================= PRE-REGISTERED RULES (committed 9 Nov before 01:00Z; see reviews/PREREG-thesports-2026-11-09.md) =================
# PREREG=1 PREREG_AFTER=1794186000 (2026-11-09T01:00:00Z) with SIGNAL=1 TRADE=1 POINTS=1 DOTA=1. Only events at or after PREREG_AFTER count. Parameters are FIXED; do not edit after commit.
if os.environ.get('PREREG') and os.environ.get('TRADE') and os.environ.get('SIGNAL'):
    AFTER = float(os.environ.get('PREREG_AFTER', '1794186000'))
    RULES = [
        # name, event list, band, statistic key, label, target N (qualifying matches/games with >=1 entry)
        ('T1 TENNIS point, quiet, fav 0.40-0.60, buy ask at t+1.2 s, hold to resolution', tp, (0.40, 0.60), 'taker', 60),
        ('D1 DOTA kill, quiet, fav 0.60-0.90, buy ask at t+1.2 s, value at mid 60 s later', allk, (0.60, 0.90), 'mtm60', 40),
    ]
    print('\n=== PRE-REGISTERED RULES: events at/after %s UTC only; success = 90%% match-clustered CI for (real - placebo) entirely above 0, evaluated ONCE at target N ===' % __import__('datetime').datetime.utcfromtimestamp(AFTER).strftime('%Y-%m-%d %H:%MZ'))
    for name, L, band, key, N in RULES:
        L2 = [x for x in L if x[1] >= AFTER]
        R, P = trade_events(L2, band)
        n = len(R); ne = sum(len(v) for v in R.values())
        print('\n## %s\n   post-cutoff qualifying matches/games: %d of target %d (entries %d)' % (name, n, N, ne))
        # history rate (pre-cutoff too), for the ETA
        Rh, _ = trade_events(L, band); days = collections.defaultdict(set)
        for k, v in Rh.items():
            pass
        if n >= N or os.environ.get('PREREG_INTERIM'):
            ra, pa = agg(R, lambda o: o[key]), agg(P, lambda o: o[key])
            (rm, rn), (pm, pn) = mean_of(ra), mean_of(pa); b = bdiff(ra, pa)
            tag = 'PRE-REGISTERED TEST' if n >= N else 'INTERIM, NOT A TEST (n below target)'
            if b: print('   %s: real %+.2fc (n%d) placebo %+.2fc (n%d) diff 90%% CI [%+.2f, %+.2f] p=%.3f' % (tag, rm * 100, rn, pm * 100, pn, b[0] * 100, b[1] * 100, b[2]))
            else: print('   %s: no data' % tag)
        else:
            print('   not evaluated: below target N (no peeking)')
