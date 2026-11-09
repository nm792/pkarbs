#!/usr/bin/env python3
"""Event-only paper backtest on TheSports capture (first cut). Usage: backtest_first.py SLIMDIR
Per event: TheSports receive time t_r; our bid at t_r+DELAY on the side the event favours,
price = floor(mid*0.975, 0.01) (market-2.5%), post-only (skipped if >= best ask); fills only if
best ask later trades down to <= bid within HOLD s (trade-through proxy); payoff held to
resolution (settle proxy: last mid >=0.95 -> 1, <=0.05 -> 0, else game excluded). Matching of
TheSports ids to PM tokens is by price co-movement (no team names yet)."""
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



HS = {}
for r in msgs:
    if r['topic'].endswith('lol/match/v1'):
        try:
            for p in json.loads(r['p']): HS[(p['match_id'], p['box_num'])] = p['home']['side']
        except Exception: pass
def outidx(tk):
    m = [m for m in mk.values() if tk in m['tokens']][0]; return m['tokens'].index(tk)
def conv_sign(tk, key):
    c = 1 if outidx(tk) == 0 else -1
    if key[0] == 'lol': c *= (1 if HS.get((key[1], key[2])) == 1 else -1)
    return c

# ---- winners from TheSports' own final state (independent of price)
fin = {}
cs_last = {}; tn_last = {}
for r in msgs:
    sp_ = r['topic'].split('/')[1]
    if sp_ not in ('csgo', 'tennis'): continue
    try: ps = json.loads(r['p'])
    except Exception: continue
    for p in ps:
        if sp_ == 'csgo': cs_last[('cs2', p['match_id'], p.get('map_id'))] = (p['home']['c_score'], p['away']['c_score'])
        elif p.get('timeline'): tn_last[('tennis', p['id'])] = p['timeline']
def tennis_winner(tl):
    h = a = 0
    for st_ in tl:
        rs = [x for x in st_.get('rounds', []) if x.get('score')]
        if not rs: continue
        sc = rs[-1]['score']
        if sc['home'] > sc['away']: h += 1
        elif sc['away'] > sc['home']: a += 1
    return None if h == a else (1 if h > a else -1)
for k, (h, a) in cs_last.items():
    if h != a: fin[k] = 1 if h > a else -1
for k, tl in tn_last.items():
    w = tennis_winner(tl)
    if w: fin[k] = w
# re-pair by |co-movement| (sign-free); sign from settlement + TheSports winner (home won <=> token settles 1 if token is home's)
claimed2 = {}
for key, evs in ev.items():
    sp = key[0]
    if sp not in ('cs2', 'tennis') or key not in fin: continue
    if len(evs) < (10 if sp == 'tennis' else 6): continue
    pool = cand[sp]
    if sp == 'tennis': pool = [t for t in pool if tk_sport[t][2] == 'moneyline']
    best = None
    for tk in pool:
        if settle(tk) is None: continue
        sc = n = 0
        for t, sd in evs:
            m = move(tk, t)
            if m is None: continue
            sc += abs(m); n += 1
        if n >= 0.6 * len(evs):
            v = sc / n
            if best is None or v > best[0]: best = (v, tk)
    if best and (best[0] > claimed2.get(best[1], (0,))[0]):
        claimed2[best[1]] = (best[0], key)
print('re-paired', collections.Counter(k[0] for _, k in claimed2.values()))
agree = collections.defaultdict(lambda: [0, 0])
signs = {}
for tk, (v, key) in claimed2.items():
    r_ = settle(tk); w = fin[key]
    sg = 1 if ((w == 1) == (r_ == 1)) else -1            # tk is the home side's token iff it settles 1 exactly when home won
    signs[tk] = (key, sg)
    old = claimed.get(tk)
    if old: agree[key[0]][0] += 1; agree[key[0]][1] += (old[2] == sg)
print('settlement-derived sign vs old price-derived sign (same token):', {k: '%d/%d' % (v[1], v[0]) for k, v in agree.items()})

# LoL orientation from home/away + home.side (verified 3/3), others from settlement (identity of the token only)
HSd = {}
for r in msgs:
    if r['topic'].endswith('lol/match/v1'):
        try:
            for p in json.loads(r['p']): HSd[(p['match_id'], p['box_num'])] = p['home']['side']
        except Exception: pass
def outidx(tk):
    m = [m for m in mk.values() if tk in m['tokens']][0]; return m['tokens'].index(tk)
for tk, (s_, key, sg) in claimed.items():
    if key[0] == 'lol':
        c = (1 if outidx(tk) == 0 else -1) * (1 if HSd.get((key[1], key[2])) == 1 else -1)
        signs[tk] = (key, c)
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
random.seed(31)
rows = {'real': collections.defaultdict(list), 'plac': collections.defaultdict(list)}   # sport -> list of (game, dict)
for tk, (key, sg) in signs.items():
    sp = key[0]
    if sp not in ('lol', 'cs2', 'tennis'): continue
    for t0, sd in ev[key]:
        m = measure(tk, key, sg, t0, sd)
        if m: rows['real'][sp].append((key, m))
        for _ in range(3):
            tp = t0 + random.choice([-1, 1]) * random.uniform(60, 600)
            m = measure(tk, key, sg, tp, sd)      # same scorer side, random time
            if m: rows['plac'][sp].append((key, m))
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
for sp in ('cs2', 'tennis', 'lol'):
    R, P = rows['real'][sp], rows['plac'][sp]
    print('== %s: feed-first, price 25-75%%, events real n=%d (games %d), placebo n=%d. cents per share' % (sp, len(R), len(set(g for g, _ in R)), len(P)))
    print('horizon | mid change real / placebo | NET (bid at +h minus ask after 1 s delay) real / placebo | real-minus-placebo net 90% CI over games')
    for h in HS:
        f = lambda L, k: 100 * sum(m[k] for _, m in L) / len(L) if L else float('nan')
        ci = boot_diff(R, P, 'net%d' % h)
        print('+%ds | %+.2f / %+.2f | %+.2f / %+.2f | %s' % (h, f(R, 'mid%d' % h), f(P, 'mid%d' % h), f(R, 'net%d' % h), f(P, 'net%d' % h),
              ('[%+.2f, %+.2f]' % ci) if ci else 'n/a'))
