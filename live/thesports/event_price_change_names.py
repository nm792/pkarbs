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
if os.environ.get('SHOWUN'):
    pm_out = collections.defaultdict(set)
    for m_ in mk.values():
        if m_['sport'] in ('cs2', 'tennis'): pm_out[m_['sport']].update(m_['outcomes'])
    for key in ev:
        sp = key[0]
        if sp not in ('cs2', 'tennis') or key in tk_of: continue
        hm = matches.get(key[1])
        if not hm: print(sp, 'no diary entry', key[1][:6]); continue
        print(sp, 'UNPAIRED', hm, '| nearest PM outcome by surname:', [o for o in pm_out[sp] if any(w in norm(o) for n in hm if n for w in norm(n)[-1:])][:4])
random.seed(41)
rows = {'real': collections.defaultdict(list), 'plac': collections.defaultdict(list)}
for key, (tk, sg) in tk_of.items():
    sp = key[0]
    for t0, sd in ev[key]:
        m = measure(tk, key, sg, t0, sd)
        if m: rows['real'][sp].append((key, m))
        for _ in range(3):
            tp = t0 + random.choice([-1, 1]) * random.uniform(60, 600)
            m = measure(tk, key, sg, tp, sd)
            if m: rows['plac'][sp].append((key, m))
import statistics as st_
for sp in ('cs2', 'tennis'):
    R, P = rows['real'][sp], rows['plac'][sp]
    print('== %s (names-verified sides): feed-first, 25-75%%, spread<=3c: real n=%d (games %d), placebo n=%d. cents/share' % (sp, len(R), len(set(g for g, _ in R)), len(P)))
    for h in HS:
        f = lambda L, k: 100 * st_.median([m[k] for _, m in L]) if L else float('nan')
        fm = lambda L, k: 100 * sum(m[k] for _, m in L) / len(L) if L else float('nan')
        ci = boot_diff(R, P, 'net%d' % h)
        print('+%ds | mid change median real %+.2f placebo %+.2f (mean %+.2f / %+.2f) | NET median real %+.2f placebo %+.2f | net mean real-placebo 90%% CI %s' % (h, f(R, 'mid%d' % h), f(P, 'mid%d' % h), fm(R, 'mid%d' % h), fm(P, 'mid%d' % h), f(R, 'net%d' % h), f(P, 'net%d' % h), ('[%+.2f, %+.2f]' % ci) if ci else 'n/a'))
