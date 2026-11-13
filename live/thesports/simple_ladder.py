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

random.seed(2)
SP = ('tennis', 'lol', 'cs2', 'nba')
sig = collections.defaultdict(lambda: collections.defaultdict(list))
pn = collections.defaultdict(lambda: collections.defaultdict(lambda: collections.defaultdict(list)))
for tk, (s_, key, sign) in claimed.items():
    sp = key[0]
    if sp not in SP: continue
    for t, sd in ev[key]:
        fav = tk if sd * sign > 0 else partner.get(tk)
        if fav is None or fav not in book: continue
        r0 = row(fav, t + DELAY); pre = mid_at(fav, t - 10)
        if not r0 or pre is None: continue
        resv = settle(fav)
        m0 = (r0[1] + r0[2]) / 2
        # (1) signal check: events where the price has NOT yet moved when TheSports lands
        if m0 - pre < 0.01:
            sig[sp]['n'].append(1)
            for h in (5, 10, 30):
                x = mid_at(fav, t + DELAY + h)
                if x is not None: sig[sp]['d%d' % h].append(x - m0)
            if resv is not None: sig[sp]['res'].append(resv - m0)
        # (2),(3) all events, no gates
        if r0[2] < 0.99 and resv is not None:
            pn[sp]['taker_hold'][key].append(resv - r0[2])
        if r0[2] < 0.99:
            b30 = row(fav, t + DELAY + 30)
            if b30: pn[sp]['taker_sell30'][key].append(b30[1] - r0[2])
        pb = sim(fav, t, 'bestbid', 30)
        if pb and resv is not None: pn[sp]['post_hold'][key].append(resv - pb)
        if pb:
            b30 = row(fav, t + DELAY + 30)
            # exit at +30 s after fill-window start is not defined for post-only; hold only
def ci(g):
    if len(g) < 3: return None
    b = sorted(sum(random.choice(g) for _ in g) / len(g) for _ in range(500))
    return sum(g) / len(g), b[25], b[474]
print('== (1) SIGNAL: events where TheSports lands before the price moves (mid <1c up since -10 s), favoured-side mid change, cents')
for sp in SP:
    r = sig[sp]; f = lambda k: (100 * sum(r[k]) / len(r[k]) if r[k] else float('nan'))
    up = lambda k: (100 * sum(1 for x in r[k] if x > 0.004) / len(r[k]) if r[k] else float('nan'))
    print(sp, 'events', len(r['n']), '| mean c at +5/+10/+30 s: %.2f %.2f %.2f' % (f('d5'), f('d10'), f('d30')),
          '| share up >0.4c at +5/+10/+30: %.0f%% %.0f%% %.0f%%' % (up('d5'), up('d10'), up('d30')),
          '| to resolution mean c %.1f (n=%d)' % (f('res'), len(r['res'])))
print('== (2)/(3) PAPER P&L per share and per game (1 share per event, no gates; 90% range across games)')
for sp in SP:
    for k in ('taker_hold', 'taker_sell30', 'post_hold'):
        d = pn[sp][k]; g = [sum(v) for v in d.values()]; allp = [x for v in d.values() for x in v]
        c = ci(g)
        if c: print(sp, k, 'events', len(allp), 'games', len(g), '$/share %.3f' % (sum(allp) / len(allp)),
                    '$/game %.2f [%.2f, %.2f]' % c, 'CLEARS0' if c[1] > 0 else '')
