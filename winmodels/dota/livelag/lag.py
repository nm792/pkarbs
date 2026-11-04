# Lag of Valve's free realtime Dota feed versus the Polymarket price, 4 Nov 2026.
# Usage: python3 lag.py <capture data dir> <config.json> [out.json]
# Inputs (written by capture.js): realtime.jsonl, books.jsonl, sportsws.jsonl, league_games.jsonl, opendota_live.jsonl
# Method (all times are our receive times, recv_ms, one clock):
#  1. Each Valve match is paired with the Polymarket market (Game N winner or series) whose radiant price
#     best tracks the Valve net-worth lead over that match (highest correlation), oriented by team name.
#  2. Events in Valve's feed: kill-score lead change (any change) and building destroyed (tower/barracks/ancient).
#  3. Lag A (cross-correlation): 1 s grid; dF = change of Valve "event score" (kill lead + 3 x tower lead + 6 x rax lead)
#     in 6 s buckets, dP = change of radiant price; corr(dF(t), dP(t+L)) for L in -120..+60 s. Peak L* < 0 means the
#     market moved |L*| s BEFORE Valve showed it (feed behind market).
#  4. Lag B (per event): for events with kill swing >=2 within 20 s or a building, the market move time is when
#     the radiant price first covers half of its move from te-120 s to te+30 s (move >= 2c, right sign). lag = te - tm.
#  5. Game end: Valve last update / ancient destroyed vs price crossing 0.90 / 0.10.
import json, sys, os, bisect, statistics as st, re
from collections import defaultdict

D, CFG = sys.argv[1], sys.argv[2]
OUTP = sys.argv[3] if len(sys.argv) > 3 else None
cfg = json.load(open(CFG))

def rows(n):
    p = os.path.join(D, n)
    if not os.path.exists(p): return []
    out = []
    for l in open(p):
        try: out.append(json.loads(l))
        except Exception: pass
    return out

norm = lambda s: re.sub(r'[^a-z0-9]', '', (s or '').lower())

# ---- Valve matches
rt = defaultdict(list)
for r in rows('realtime.jsonl'):
    rt[r['match_id']].append(r)
# ---- books: token -> [(t, mid, bid, ask)]
bk = defaultdict(list); tokinfo = {}
for r in rows('books.jsonl'):
    if r['bid'] is None or r['ask'] is None: continue
    if r['ask'] - r['bid'] > 0.10: continue  # ignore empty/wide books
    bk[r['token']].append((r['recv_ms'] / 1000, (r['bid'] + r['ask']) / 2, r['bid'], r['ask']))
    tokinfo[r['token']] = (r['label'], r['q'], r['outcome'])
for v in bk.values(): v.sort()

def price_at(series, t):
    i = bisect.bisect_right(series, (t, 9e9)) - 1
    return series[i][1] if i >= 0 else None

def same(a, b):
    a, b = norm(a), norm(b)
    return bool(a) and bool(b) and (a == b or a in b or b in a)

def match_series(names):
    # question "Dota 2: A vs B - Game 1 Winner"; Valve names can carry suffixes ("Inner Circle x Insanity")
    out = []
    for s in cfg:
        m = re.match(r'Dota 2: (.+?) vs (.+?)( \(BO\d\))? - ', s['markets'][0]['q'])
        if not m: continue
        a, b = m.group(1), m.group(2)
        if (same(names[0], a) and same(names[1], b)) or (same(names[0], b) and same(names[1], a)): out.append(s)
    return out

def corr(a, b):
    if len(a) < 5: return None
    ma, mb = st.mean(a), st.mean(b)
    va = sum((x - ma) ** 2 for x in a); vb = sum((y - mb) ** 2 for y in b)
    if va == 0 or vb == 0: return None
    return sum((x - ma) * (y - mb) for x, y in zip(a, b)) / (va * vb) ** 0.5

TW = {0: 1, 1: 2}  # building type 0 tower, 1 barracks (Valve realtime schema); others (fort/ancient) counted separately

# spectator-delay tag: GetLiveGames 'time' (live clock) minus GetRealtimeStats game_time, sampled when 'time' updates
delay = defaultdict(list); _last = {}
for r in rows('rt_polls.jsonl'):
    lt, g = r.get('live_time'), r.get('game_time')
    if not lt or lt > 10 ** 6 or not g or g < 60: continue
    if _last.get(r['match_id']) != lt:
        _last[r['match_id']] = lt; delay[r['match_id']].append(lt - g)
delay_tag = {m: st.median(v) for m, v in delay.items() if len(v) >= 3}
res = {'matches': [], 'events': [], 'xcorr': {}, 'delay_tag_s': delay_tag}
for mid_, R in rt.items():
    R.sort(key=lambda r: r['recv_ms'])
    tm = {t['team']: t for t in R[-1]['teams']}
    if 2 not in tm or 3 not in tm: continue
    rad, dire = tm[2]['name'], tm[3]['name']
    ser = match_series([rad, dire])
    if not ser: continue
    s = ser[0]
    T = [r['recv_ms'] / 1000 for r in R]
    nwlead = [next(t['nw'] for t in r['teams'] if t['team'] == 2) - next(t['nw'] for t in r['teams'] if t['team'] == 3) for r in R]
    # pick market by correlation of radiant price with net-worth lead
    best = None
    for m in s['markets']:
        tok = m['tokens'][0]
        if tok not in bk: continue
        spr = [a - b for t, _, b, a in bk[tok] if T[0] <= t <= T[-1]]
        if not spr or st.median(spr) > 0.05: continue  # skip thin books
        o0 = m['outcomes'][0]
        sign = 1 if same(o0, rad) else (-1 if same(o0, dire) else 0)
        if sign == 0: continue
        ps = [price_at(bk[tok], t) for t in T]
        pr = [(p if sign == 1 else 1 - p) if p is not None else None for p in ps]
        pairs = [(a, b) for a, b in zip(nwlead, pr) if b is not None]
        if len(pairs) < 20: continue
        c = corr([a for a, _ in pairs], [b for _, b in pairs])
        if c is not None and (best is None or c > best[0]): best = (c, m, tok, sign)
    if not best or best[0] < 0.3:
        res['matches'].append({'match_id': mid_, 'radiant': rad, 'dire': dire, 'label': s['label'], 'paired': None, 'best_corr': best and round(best[0], 3)})
        continue
    c, m, tok, sign = best
    P = [(t, (p if sign == 1 else 1 - p)) for t, p, _, _ in bk[tok]]
    def prad(t):
        i = bisect.bisect_right(P, (t, 9e9)) - 1
        return P[i][1] if i >= 0 else None
    # event score from Valve
    def esc(r):
        sc = {t['team']: t['score'] for t in r['teams']}
        b = defaultdict(int)
        for team, typ, lane, tier, dest in r['buildings']:
            if dest: b[(team, typ)] += 1
        # building destroyed on dire side helps radiant
        tw = b[(3, 0)] - b[(2, 0)]; rx = b[(3, 1)] - b[(2, 1)]
        return sc.get(2, 0) - sc.get(3, 0), tw, rx
    E = [esc(r) for r in R]
    F = [k + 3 * tw + 6 * rx for k, tw, rx in E]
    t0, t1 = T[0], T[-1]
    # 1 s grids
    grid = list(range(int(t0), int(t1)))
    def f_at(t):
        i = bisect.bisect_right(T, t) - 1
        return F[i] if i >= 0 else F[0]
    fg = [f_at(t) for t in grid]; pg = [prad(t) for t in grid]
    ok = all(p is not None for p in pg[60:])
    xc = {}
    B = 30
    for L in range(-480, 121, 15):
        a, b = [], []
        for i in range(60, len(grid) - B - 130, B):
            j = i + L
            if j < 0 or j + B >= len(grid) or pg[j] is None or pg[j + B] is None: continue
            a.append(fg[i + B] - fg[i]); b.append(pg[j + B] - pg[j])
        cc = corr(a, b)
        if cc is not None: xc[L] = round(cc, 4)
    res['xcorr'][str(mid_)] = xc
    Lstar = max(xc, key=xc.get) if xc else None
    # per-event lag B
    evs = []
    for i in range(1, len(R)):
        dk = E[i][0] - E[i - 1][0]; dtw = E[i][1] - E[i - 1][1]; drx = E[i][2] - E[i - 1][2]
        if dk == 0 and dtw == 0 and drx == 0: continue
        evs.append((T[i], dk, dtw, drx, T[i] - T[i - 1]))
    out_ev = []
    for te, dk, dtw, drx, gap in evs:
        # kill swing within 20 s window
        swing = sum(d for t, d, _, _, _ in evs if te - 20 <= t <= te and d) if not (dtw or drx) else None
        big = (dtw != 0 or drx != 0) or (abs(swing or 0) >= 2)
        if not big: continue
        sgn = (1 if (dtw + drx) > 0 else -1) if (dtw or drx) else (1 if swing > 0 else -1)
        pa, pb = prad(te - 480), prad(te + 30)
        if pa is None or pb is None: continue
        move = (pb - pa) * sgn
        tmv = None
        if move >= 0.02:
            half = pa + sgn * move / 2
            for t in range(int(te - 480), int(te + 31)):
                p = prad(t)
                if p is not None and (p - half) * sgn >= 0: tmv = t; break
        e = {'match_id': mid_, 'label': s['label'], 'q': m['q'], 't': te, 'kill_swing': swing, 'tower': dtw, 'rax': drx,
             'sign': sgn, 'p_before': round(pa, 3), 'p_after': round(pb, 3), 'move_c': round(move * 100, 1),
             'market_move_t': tmv, 'lag_s': (round(te - tmv, 1) if tmv else None), 'valve_gap_s': round(gap, 1)}
        out_ev.append(e)
    res['events'] += out_ev
    # game end
    end_p = None
    fin = R[-1]['recv_ms'] / 1000
    win_rad = None
    pfin = prad(fin + 600)
    cross = None
    for t, p in P:
        if t > t0 and (p >= 0.9 or p <= 0.1):
            cross = t; break
    lags = [e['lag_s'] for e in out_ev if e['lag_s'] is not None]
    res['matches'].append({'match_id': mid_, 'radiant': rad, 'dire': dire, 'label': s['label'], 'paired': m['q'],
        'corr_nw_price': round(c, 3), 'delay_tag_s': delay_tag.get(mid_), 'valve_rows': len(R), 'valve_first': t0, 'valve_last': fin,
        'price_cross_90_10_t': cross, 'valve_last_minus_cross_s': (round(fin - cross, 1) if cross else None),
        'xcorr_peak_L_s': Lstar, 'xcorr_peak': xc.get(Lstar) if Lstar is not None else None,
        'events_big': len(out_ev), 'events_timed': len(lags),
        'event_lag_median_s': (st.median(lags) if lags else None),
        'event_lag_range_s': ([min(lags), max(lags)] if lags else None)})

# pooled
lags = sorted(e['lag_s'] for e in res['events'] if e['lag_s'] is not None)
res['pooled'] = {'n_timed_events': len(lags), 'median_lag_s': st.median(lags) if lags else None,
                 'p10_p90': [lags[len(lags) // 10], lags[(9 * len(lags)) // 10]] if len(lags) >= 10 else None,
                 'range': [lags[0], lags[-1]] if lags else None}
# pooled xcorr
pool = defaultdict(list)
for xc in res['xcorr'].values():
    for L, v in xc.items(): pool[int(L)].append(v)
px = {L: round(st.mean(v), 4) for L, v in pool.items() if v}
res['pooled']['xcorr_mean_peak_L_s'] = max(px, key=px.get) if px else None
res['pooled']['xcorr_mean'] = dict(sorted(px.items()))
for mm in res['matches']: print(json.dumps(mm))
print(json.dumps({k: v for k, v in res['pooled'].items() if k != 'xcorr_mean'}))
if OUTP: json.dump(res, open(OUTP, 'w'), indent=1)
