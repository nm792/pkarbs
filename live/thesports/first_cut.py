#!/usr/bin/env python3
"""First-cut TheSports timing: events from ts_mqtt (basketball score, CS2 round) matched to PM tokens
by price co-movement, then lead_s = PM price half-move onset - our receive time (positive = feed first).
Usage: first_cut.py SLIMDIR"""
import sys, os, json, gzip, glob, bisect, collections, statistics as st
D = sys.argv[1]
def rd(p):
    for f in sorted(glob.glob(p, recursive=True)):
        for l in gzip.open(f, 'rt'):
            try: yield json.loads(l)
            except Exception: pass
# PM mid series
mid = collections.defaultdict(list)
for r in rd(D + '/books_mid/**/*.gz'):
    mid[r['tk']].append((r['ms'] / 1000.0, (r['bb'] + r['ba']) / 2, r['ba'] - r['bb']))
for k in mid: mid[k].sort()
# markets: token -> sport, title
tk_info = {}
for m in rd(D + '/markets.jsonl.gz'):
    for t, o in zip(m['tokens'], m['outcomes']): tk_info[t] = (m['sport'], m['q'], o)
# events
ev = collections.defaultdict(list)       # (sport,match) -> [(recv_s, side, gain)]
last = {}
for r in sorted(rd(D + '/ts_mqtt/**/*.gz'), key=lambda r: r['ms']):
    s = r['topic'].split('/')[1]
    if s not in ('basketball', 'csgo'): continue
    try: ps = json.loads(r['p'])
    except Exception: continue
    for p in ps:
        if s == 'basketball':
            sc = p.get('score')
            if not sc: continue
            key = (s, p['id']); cur = (sum(sc[3]), sum(sc[4]))
        else:
            key = (s, p['match_id'], p.get('map_id')); cur = (p['home']['c_score'], p['away']['c_score'])
        if key in last and cur != last[key]:
            dh, da = cur[0] - last[key][0], cur[1] - last[key][1]
            if (dh >= 0 and da >= 0) and (dh + da) > 0 and (dh + da) <= (3 if s == 'basketball' else 1):
                ev[key].append((r['ms'] / 1000.0, 1 if dh > 0 else -1, dh + da))
        last[key] = cur
def at(ser, t):
    i = bisect.bisect_right([x[0] for x in ser], t) - 1 if False else None
def mk(ser):
    return [x[0] for x in ser]
cache = {k: mk(v) for k, v in mid.items()}
def m_at(tk, t):
    ts = cache[tk]; i = bisect.bisect_right(ts, t) - 1
    return mid[tk][i][1] if i >= 0 and t - ts[i] < 15 else None
def move(tk, t):
    a, b = m_at(tk, t - 10), m_at(tk, t + 30)
    return None if a is None or b is None else b - a
THR = {'nba': 0.012, 'cs2': 0.012}
sport_of = {'basketball': 'nba', 'csgo': 'cs2'}
res = collections.defaultdict(list); matched = collections.defaultdict(list)
claimed = {}
cand_tks = collections.defaultdict(list)
for t, (sp, q, o) in tk_info.items():
    if t in mid: cand_tks[sp].append(t)
for key, evs in ev.items():
    sp = sport_of[key[0]]
    if len(evs) < (8 if sp == 'nba' else 6): continue
    best = None
    for tk in cand_tks[sp]:
        sc = n = 0
        for t, sd, g in evs:
            m = move(tk, t)
            if m is None: continue
            sc += sd * m; n += 1
        if n >= 0.6 * len(evs):
            s = abs(sc) / n
            if best is None or s > best[0]: best = (s, tk, 1 if sc > 0 else -1, n)
    if not best or best[0] < THR[sp]: continue
    s, tk, sign, n = best
    if s <= claimed.get(tk, (0,))[0] and claimed.get(tk, (0,))[0] > 0: continue
    claimed[tk] = (s, key)
    matched[sp].append((key[1], tk_info[tk][1][:60], round(s, 4), len(evs)))
    ser = mid[tk]; ts = cache[tk]
    for t, sd, g in evs:
        m = move(tk, t); base = m_at(tk, t - 10)
        if m is None or abs(m) < 0.02 or (m * sd * sign) <= 0: continue
        half = base + m / 2; onset = None
        for x, v, _ in ser[bisect.bisect_left(ts, t - 30):bisect.bisect_right(ts, t + 30)]:
            if (v - base) * (1 if m > 0 else -1) >= abs(m) / 2: onset = x; break
        if onset is not None: res[sp].append(onset - t)
out = {}
for sp, v in res.items():
    v.sort(); n = len(v)
    out[sp] = dict(n=n, median=round(st.median(v), 1), p10=round(v[int(.1 * n)], 1), p90=round(v[int(.9 * n) - 1], 1),
                   pct_feed_first=round(100 * sum(1 for x in v if x > 0) / n))
print(json.dumps(out, indent=1))
for sp, m in matched.items(): print(sp, 'matched', len(m), m[:5])
