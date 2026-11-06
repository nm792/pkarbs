#!/usr/bin/env python3
"""NFL live feed delays vs the Polymarket PRICE, and queue at our bid (5-6 Nov 2026).

Inputs: capture.py folders (books 1 s full depth, ESPN summary + scoreboard, sports WS) from one or more runs.
Time of a book change = exchange 'ts' (ms; local clock agrees within 0.4 s median). Price onset = first book change that has
covered 20% of a >= MOVE mid move (token0 mid, spread <= 10c), same definition as the backtests.
Usage: analyze.py CAPDIR [CAPDIR...]  (writes out_live_analysis.json next to this file)"""
import sys, os, json, bisect, math, statistics as st, datetime as dt, collections
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(HERE)), 'winmodels'))
import common as C
dirs = sys.argv[1:]
def rd(name):
    for d in dirs:
        p = os.path.join(d, name + '.jsonl')
        if os.path.exists(p):
            for l in open(p):
                try: yield json.loads(l)
                except Exception: pass
def tsiso(s): return dt.datetime.fromisoformat(s.replace('Z', '+00:00')).timestamp()
MOVE = float(os.environ.get('MOVE', 0.02))
mk = next(rd('markets')); tok0, tok1 = mk['tokens']; cond = mk['cond']; start = tsiso(mk['start'])
# ---- books (dedupe by asset+ts)
B = {tok0: {}, tok1: {}}
for b in rd('books'):
    t = int(b['ts']) / 1000 if b.get('ts') else b['recv_ms'] / 1000
    bids = {float(x['price']): float(x['size']) for x in b['bids'] or []}; asks = {float(x['price']): float(x['size']) for x in b['asks'] or []}
    B[b['asset']][t] = (bids, asks)
S = {k: sorted(v) for k, v in B.items()}
def snap(tok, t):
    i = bisect.bisect_right(S[tok], t) - 1
    return None if i < 0 else B[tok][S[tok][i]]
def mid0(t):
    x = snap(tok0, t)
    if not x or not x[0] or not x[1]: return None
    bb, ba = max(x[0]), min(x[1])
    return None if ba - bb > 0.10 else (bb + ba) / 2
tk0 = S[tok0]; t_lo, t_hi = tk0[0], tk0[-1]
# ---- price moves and onsets
cand = []
for t in range(int(max(start, t_lo)), int(t_hi) - 30):
    a, b = mid0(t), mid0(t + 20)
    if a is None or b is None or not (0.03 < a < 0.97): continue
    if abs(b - a) >= MOVE: cand.append((abs(b - a), t))
cand.sort(reverse=True); taken = []; moves = []
for _, t in cand:
    if any(abs(t - u) < 40 for u in taken): continue
    taken.append(t); a, b = mid0(t), mid0(t + 30)
    if b is None or abs(b - a) < MOVE / 2: continue
    for u in tk0[bisect.bisect_left(tk0, t):bisect.bisect_right(tk0, t + 30)]:
        m = mid0(u)
        if m is not None and (m - a) / (b - a) >= 0.2: moves.append(dict(on=u, a=a, b=b, sign=1 if b > a else -1)); break
moves.sort(key=lambda m: m['on'])
print('books', {k[:6]: len(v) for k, v in S.items()}, 'moves >=', MOVE, len(moves))
# ---- feeds: first receipt per event
espn = {}
for r in rd('espn'):
    k = r['id']
    if k not in espn or r['recv_ms'] < espn[k]['recv_ms']: espn[k] = r
plays = sorted(espn.values(), key=lambda r: int(r['seq']))
sb = {}
for r in rd('sb'):
    if r.get('lp') and (r['lp'] not in sb or r['recv_ms'] < sb[r['lp']]['recv_ms']): sb[r['lp']] = r
ws = {}
for r in rd('sports'):
    if r.get('score') and r['score'] not in ws: ws[r['score']] = r
out = dict(n_moves=len(moves), n_plays=len(plays))
# ---- ESPN delivery vs its own wallclock and vs price (all plays with a wallclock)
lag_wc = [p['recv_ms'] / 1000 - tsiso(p['wc']) for p in plays if p.get('wc')]
out['espn_recv_minus_wallclock'] = dict(n=len(lag_wc), median=st.median(lag_wc), p10=sorted(lag_wc)[len(lag_wc) // 10], p90=sorted(lag_wc)[9 * len(lag_wc) // 10])
print('ESPN summary receipt minus play wallclock', out['espn_recv_minus_wallclock'])
# score changes (any play whose score differs from the previous play, so the extra point counts). token0 = away (JAX).
prev = (0, 0); rows = []
for p in plays:
    h, a = p['h'], p['a']
    if h is None: continue
    if (h, a) != prev:
        d = (a - prev[0]) - (h - prev[1])
        rows.append(dict(id=p['id'], text=p['text'][:50], score=f'{a}-{h}', sign=1 if d > 0 else -1, espn=p['recv_ms'] / 1000, wc=tsiso(p['wc']) if p.get('wc') else None,
                         sb=(sb.get(p['id']) or {}).get('recv_ms', 0) / 1000 or None, ws=ws.get(f'{a}-{h}', {}).get('recv_ms', 0) / 1000 or None))
        prev = (h, a)
def summ(v): v = sorted(v); return dict(n=len(v), median=round(st.median(v), 1), min=round(v[0], 1), max=round(v[-1], 1)) if v else None
out['sb_minus_espn_receipt'] = summ([r['sb'] - r['espn'] for r in rows if r['sb']]) ; out['ws_minus_espn_receipt'] = summ([r['ws'] - r['espn'] for r in rows if r['ws']])
print('scoreboard lastPlay receipt minus ESPN summary receipt (same play, score changes):', out['sb_minus_espn_receipt'])
print('Polymarket sports WS receipt minus ESPN summary receipt (same score):', out['ws_minus_espn_receipt'])
# single-play moves: a play whose wallclock is within +-20 s of a price onset (the play most likely caused the move), all play types
cl = []
for m in moves:
    c = [p for p in plays if p.get('wc') and abs(tsiso(p['wc']) - m['on']) <= 20]
    if not c: continue
    p = min(c, key=lambda q: abs(tsiso(q['wc']) - m['on']))
    sbr = (sb.get(p['id']) or {}).get('recv_ms')
    cl.append(dict(text=p['text'][:44], move=round(m['b'] - m['a'], 3), wc_minus_onset=round(tsiso(p['wc']) - m['on'], 1), espn_minus_onset=round(p['recv_ms'] / 1000 - m['on'], 1),
                   sb_minus_onset=None if not sbr else round(sbr / 1000 - m['on'], 1)))
out['single_play_moves'] = cl
for r in cl: print(f"  move {r['move']:+.3f} {r['text']:<44} wallclock-onset {r['wc_minus_onset']:>6} ESPN-onset {r['espn_minus_onset']:>6} scoreboard-onset {r['sb_minus_onset']}")
if cl:
    out['espn_minus_onset_single'] = summ([r['espn_minus_onset'] for r in cl]); out['sb_minus_onset_single'] = summ([r['sb_minus_onset'] for r in cl if r['sb_minus_onset'] is not None]); out['wc_minus_onset_single'] = summ([r['wc_minus_onset'] for r in cl])
    print('single-play moves: ESPN summary receipt minus onset', out['espn_minus_onset_single'], '| scoreboard', out['sb_minus_onset_single'], '| wallclock', out['wc_minus_onset_single'])
out['score_changes'] = rows
# ---- queue: bid at mid x 0.975 rounded UP to tick, kept below best ask, on the rising token
def tick(p): return 0.001 if p < 0.04 or p > 0.96 else 0.01
def ceil_t(p): tk = tick(p); return round(math.ceil(p / tk - 1e-9) * tk, 3)
def tokmid(tok, t):
    x = snap(tok, t)
    if not x or not x[0] or not x[1]: return None
    bb, ba = max(x[0]), min(x[1]); return None if ba - bb > 0.10 else (bb + ba) / 2
def ahead(tok, t, P):
    x = snap(tok, t)
    return None if not x else (round(sum(s for q, s in x[0].items() if q >= P - 1e-9)), round(x[0].get(P, 0)))
trades = C.pull_trades(cond, start - 1800, start + 5 * 3600, 'nfl_live_jaxbal'); tr = C.prints(trades)
win0 = None
try:
    c, g = C.jget('https://gamma-api.polymarket.com/events', {'slug': mk['slug']}); mm = [m for m in g[0]['markets'] if m['conditionId'] == cond][0]
    op = json.loads(mm['outcomePrices']); win0 = op[0] == '1' if sorted(op) == ['0', '1'] else None
except Exception as e: print('result lookup', e)
print('trades', len(trades), 'token0 wins', win0)
def sells_into(tok, t0, t1):
    """taker prints that hit a bid on `tok` in [t0, t1]: [(ts, price_on_tok, size)]"""
    o = []
    for (T, _, ph, sell0, sz) in tr:
        if not (t0 <= T <= t1): continue
        if tok == tok0 and sell0: o.append((T, ph, sz))
        if tok == tok1 and not sell0: o.append((T, 1 - ph, sz))
    return o
DELAYS = (0, 2, 5, 10, 20, 30, 60); W = 30; CAP = 500
Q = {d: [] for d in DELAYS}; fills = {d: [] for d in DELAYS}; pnl = {d: [] for d in DELAYS}; pre = []
for m in moves:
    tok = tok0 if m['sign'] > 0 else tok1
    mid_pre = tokmid(tok, m['on'] - 2)
    if mid_pre is None or not (0.05 < mid_pre < 0.95): continue
    P_old = ceil_t(mid_pre * 0.975); x = snap(tok, m['on'] - 2)
    if x[1] and P_old >= min(x[1]) - 1e-9: P_old = round(min(x[1]) - tick(P_old), 3)
    a = ahead(tok, m['on'] - 2, P_old)
    if a: pre.append(a[0])
    for d in DELAYS:
        t0 = m['on'] + d; mid_t = tokmid(tok, t0 - 1)
        if mid_t is None or not (0.05 < mid_t < 0.95): continue
        moved = (mid_t - mid_pre)
        if moved >= 0.5 * abs(m['b'] - m['a']): continue            # market already moved >= 50%: rule does not bid
        P = ceil_t(mid_t * 0.975); xs = snap(tok, t0 - 1)
        if xs[1] and P >= min(xs[1]) - 1e-9: P = round(min(xs[1]) - tick(P), 3)
        aa = ahead(tok, t0 - 1, P)
        if not aa: continue
        Q[d].append(aa[0])
        s = sells_into(tok, t0, t0 + W)
        below = sum(z for _, p, z in s if p < P - 1e-9); eq = sum(z for _, p, z in s if abs(p - P) < 1e-9)
        qat = aa[1]
        f = CAP if below > 0 else max(0.0, min(CAP, eq - qat))      # conservative: nothing ahead of us cancels
        f_opt = min(CAP, below + eq)                                  # optimistic: queue ahead all cancels
        fills[d].append((f, f_opt, P))
        if win0 is not None:
            won = (win0 == (tok == tok0)); pnl[d].append((f * ((1.0 if won else 0.0) - P), f_opt * ((1.0 if won else 0.0) - P)))
out['queue'] = dict(pre_move_ahead_at_old_price_median=st.median(pre) if pre else None, n_pre=len(pre), W=W, cap=CAP, rows=[])
n_games = 1
print('\nqueue at mid x 0.975 (rising token), shares at or above our price, and fills in the next', W, 's (cap', CAP, ')')
for d in DELAYS:
    if not Q[d]: continue
    f = fills[d]; r = dict(delay=d, n=len(Q[d]), ahead_median=st.median(Q[d]), ahead_p25=sorted(Q[d])[len(Q[d]) // 4], ahead_p75=sorted(Q[d])[3 * len(Q[d]) // 4],
                           filled_cons=round(sum(x[0] for x in f)), filled_opt=round(sum(x[1] for x in f)), n_fill_cons=sum(1 for x in f if x[0] > 0), n_fill_opt=sum(1 for x in f if x[1] > 0),
                           pnl_cons=round(sum(x[0] for x in pnl[d]), 1) if pnl[d] else None, pnl_opt=round(sum(x[1] for x in pnl[d]), 1) if pnl[d] else None)
    out['queue']['rows'].append(r)
    print(f"delay {d:>3}s: n {r['n']:>3} shares ahead median {r['ahead_median']:>6} (IQR {r['ahead_p25']}-{r['ahead_p75']}) | filled cons {r['filled_cons']:>5} sh in {r['n_fill_cons']} events, opt {r['filled_opt']:>5} sh in {r['n_fill_opt']} | held-to-result P&L cons ${r['pnl_cons']} opt ${r['pnl_opt']}")
json.dump(out, open(os.path.join(HERE, 'out_live_analysis.json'), 'w'), indent=1, default=float)
