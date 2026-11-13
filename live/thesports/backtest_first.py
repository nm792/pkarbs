#!/usr/bin/env python3
"""Event-only paper backtest on TheSports capture (first cut). Usage: backtest_first.py SLIMDIR
Per event: TheSports receive time t_r; our bid at t_r+DELAY on the side the event favours,
price = floor(mid*0.975, 0.01) (market-2.5%), post-only (skipped if >= best ask); fills only if
best ask later trades down to <= bid within HOLD s (trade-through proxy); payoff held to
resolution (settle proxy: last mid >=0.95 -> 1, <=0.05 -> 0, else game excluded). Matching of
TheSports ids to PM tokens is by price co-movement (no team names yet)."""
import sys, json, gzip, glob, bisect, collections, statistics as st, math, random
D = sys.argv[1]
DELAYS = [0.2, 1.3]; HOLD = 120
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
claimed = {}; matched = []
for key, evs in ev.items():
    sp = key[0]
    if len(evs) < (8 if sp == 'nba' else (10 if sp == 'tennis' else 6)): continue
    pool = cand[sp]
    if sp == 'tennis':
        pool = [t for t in pool if tk_sport[t][2] == 'moneyline']
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
            s = abs(sc) / n
            if best is None or s > best[0]: best = (s, tk, 1 if sc > 0 else -1)
    if best and best[0] >= 0.012:
        s, tk, sign = best
        if s > claimed.get(tk, (0,))[0]:
            claimed[tk] = (s, key, sign)
for tk, (s, key, sign) in claimed.items(): matched.append((key[0], key, tk, sign))
out = collections.defaultdict(lambda: dict(events=0, lead=0, left=[], placed=0, fills=0, pnl=[], games=collections.defaultdict(float)))
for sp, key, tk, sign in matched:
    res = settle(tk)
    for t, sd in ev[key]:
        o = out[(sp, )]; o['events'] += 1
        m = move(tk, t)
        a = mid_at(tk, t - 10)
        if m is None or abs(m) < 0.02 or m * sd * sign <= 0: continue
        for dly in DELAYS[:1]:
            r0 = row(tk, t + dly)
            if not r0: continue
            moved = (r0[1] + r0[2]) / 2 - a
            left = max(0.0, abs(m) - abs(moved)) if moved * m >= 0 else abs(m) + abs(moved)
            o['left'].append(left / abs(m)); o['lead'] += (abs(moved) < abs(m) / 2)
            # bid on the favoured token side (token tk if sd*sign>0 -> price up, else bid the opposite side: skip)
            if m < 0: continue                        # favoured side is the other token; skipped (first cut)
            mid = (r0[1] + r0[2]) / 2; p = math.floor(mid * 0.975 * 100 + 1e-9) / 100
            if p <= 0.02 or p >= r0[2]: continue
            o['placed'] += 1
            i0 = bisect.bisect_left(T[tk], t + dly)
            filled = False
            for x in book[tk][i0:bisect.bisect_right(T[tk], t + dly + HOLD)]:
                if x[2] <= p + 1e-9: filled = True; break
            if filled:
                o['fills'] += 1
                if res is not None:
                    o['pnl'].append(res - p); o['games'][tk] += (res - p)
print('matched games:', collections.Counter(s for s, *_ in matched))
for (sp,), o in out.items():
    n = len(o['pnl']); gm = list(o['games'].values())
    left = sorted(o['left'])
    print(sp, 'events', o['events'], 'big-move events', len(left), 'TheSports before half the move', o['lead'],
          'median share of move left %.2f' % (st.median(left) if left else float('nan')),
          'bids', o['placed'], 'fills', o['fills'], 'resolved fills', n,
          'avg $/share %.3f' % (sum(o['pnl']) / n if n else float('nan')), 'games', len(gm),
          '$/game@1sh/fill %.2f' % (sum(gm) / len(gm) if gm else float('nan')))
