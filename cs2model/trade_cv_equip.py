#!/usr/bin/env python3
"""Step 13b (CV version of step 10): LOCKED TEST of the CS2 win model against the Polymarket price on map-winner markets.
Rule (fixed before the run): at each 5-s sample after the 90-s burn-in, edge = model P - best ask on the side we would buy (home token if model above ask, away token
if (1-model) above its own ask). Signal when edge >= TH. FILL = first real BUY print (data-api /v2/trades) on that token at/after t+1 s, within 10 s, size >= N shares,
and model fair - print price >= TH at the print. Held to resolution (token pays 1 if its team wins the map). Units = maps (one bet per map = first signal), also per-round variant.
Stats: real PnL vs placebo = random BUY prints from OTHER maps, price within 5c, size >= N, drawn 3000 times; oracle check = same timing, knows the winner.
Held-out: round model fitted on the earlier half of maps; headline = later half. Every variant is printed."""
import sys, json, pickle, bisect, random, collections, numpy as np
ROWSETS = pickle.load(open(sys.argv[1], 'rb'))
P = json.load(open(sys.argv[2]))['pairs']; B = pickle.load(open(sys.argv[3], 'rb'))['book']; TR = json.load(open(sys.argv[4]))
D = pickle.load(open(sys.argv[5], 'rb')); M = D['maps']
T = {k: [x[0] for x in v] for k, v in B.items()}
def quote(tk, t, maxage=20):
    ts = T.get(tk)
    if not ts: return None
    i = bisect.bisect_right(ts, t) - 1
    if i < 0 or t - ts[i] > maxage: return None
    return B[tk][i][1], B[tk][i][2]
# BUY tape per token
tape = collections.defaultdict(list)
for cond, L in TR.items():
    for ts, side, price, size, tok in L:
        if side == 'BUY': tape[tok].append((ts, price, size))
for k in tape: tape[k].sort()
tape_ts = {k: [x[0] for x in v] for k, v in tape.items()}
def first_print(tok, t, N, price_cap, wait=10):
    L = tape.get(tok, []); i = bisect.bisect_left(tape_ts.get(tok, []), t + 1)
    while i < len(L) and L[i][0] <= t + 1 + wait:
        if L[i][2] >= N: return L[i]
        i += 1
    return None
def run(model, TH, N, sel, per, oracle=False):
    bets = []; seen = set()
    ROWS = ROWS_CUR
    for x in sorted(ROWS, key=lambda x: (x['key'], x['t'])):
        k = x['key']
        if k not in sel: continue
        unit = (k,) if per == 'map' else (k, x['tmr'])
        if unit in seen: continue
        p = P[k]; Pm = x[model]; y = M[k]['y_map']
        qh = quote(p['tok_home'], x['t']); qa = quote(p['tok_away'], x['t'])
        if not qh or not qa: continue
        cands = []
        if oracle:
            side = 'home' if y == 1 else 'away'; tok = p['tok_home'] if y == 1 else p['tok_away']; ask = qh[1] if y == 1 else qa[1]
            if 0.05 <= ask <= 0.95: cands.append((1.0 - ask, side, tok, 1.0))
        else:
            if Pm - qh[1] >= TH and 0.05 <= qh[1] <= 0.95: cands.append((Pm - qh[1], 'home', p['tok_home'], Pm))
            if (1 - Pm) - qa[1] >= TH and 0.05 <= qa[1] <= 0.95: cands.append(((1 - Pm) - qa[1], 'away', p['tok_away'], 1 - Pm))
        if not cands: continue
        edge, side, tok, fair = max(cands)
        fp = first_print(tok, x['t'], N, None)
        if fp is None: continue
        if not oracle and fair - fp[1] < TH: continue
        if not (0.03 <= fp[1] <= 0.97): continue
        yt = y if side == 'home' else 1 - y
        bets.append(dict(key=k, t=x['t'], side=side, tok=tok, price=fp[1], pnl=(yt - fp[1]) * N, cost=fp[1] * N, y=yt, fill_ts=fp[0]))
        seen.add(unit)
    return bets
# placebo pool: BUY prints of other maps' tokens during the map, size >= N
_POOL = {}
def pool_for(N):
    if N in _POOL: return _POOL[N]
    _POOL[N] = _pool_for(N); return _POOL[N]
def _pool_for(N):
    pool = []
    for k, p in P.items():
        if k not in M: continue
        m = M[k]
        for side, tok in (('home', p['tok_home']), ('away', p['tok_away'])):
            yt = m['y_map'] if side == 'home' else 1 - m['y_map']
            for ts, price, size in tape.get(tok, []):
                if m['t0'] <= ts <= m['t1'] and size >= N and 0.03 <= price <= 0.97: pool.append((k, price, yt))
    return pool
def placebo(bets, pool, N, draws=1000, seed=1):
    rng = random.Random(seed); byp = collections.defaultdict(list)
    for k, pr, yt in pool: byp[round(pr * 20)].append((k, pr, yt))     # 5c bins
    tot = []
    for _ in range(draws):
        s = 0.0
        for b in bets:
            c = []
            for j in (round(b['price'] * 20) - 1, round(b['price'] * 20), round(b['price'] * 20) + 1):
                c += [q for q in byp.get(j, []) if q[0] != b['key'] and abs(q[1] - b['price']) <= 0.05]
            if c: k, pr, yt = rng.choice(c); s += (yt - pr) * N
        tot.append(s)
    return np.mean(tot), np.std(tot)
def report(model, TH, N, sel, per, label):
    bets = run(model, TH, N, sel, per)
    if not bets: print('  %-34s no bets' % label); return
    pnl = sum(b['pnl'] for b in bets); cost = sum(b['cost'] for b in bets); pool = pool_for(N)
    pm, ps = placebo(bets, pool, N)
    mp = collections.defaultdict(float)
    for b in bets: mp[b['key']] += b['pnl']
    arr = np.array(list(mp.values()))
    win = np.mean([b['y'] for b in bets])
    print('  %-34s bets %3d (maps %2d) | PnL $%+8.0f on $%7.0f (%+.1f%%) | win %.0f%% avg price %.2f | placebo $%+.0f +/- %.0f -> z %+.2f | per-map mean $%+.0f se %.0f' % (
        label, len(bets), len(mp), pnl, cost, 100 * pnl / cost, 100 * win, np.mean([b['price'] for b in bets]), pm, ps, (pnl - pm) / ps if ps else float('nan'), arr.mean(), arr.std(ddof=1) / np.sqrt(len(arr)) if len(arr) > 1 else float('nan')))
    return bets

ALLK = None
for name in ('BASE', '+EQUIP', '+EQUIP+PRATE+ELO+SERIES'):
    ROWS_CUR = ROWSETS[name]; ALLK = set(x['key'] for x in ROWS_CUR)
    print('=== feature set %s: 4-fold CV out-of-fold predictions, all %d paired maps held out once' % (name, len(ALLK)))
    for model in ('A', 'S'):
        if model == 'S' and name != 'BASE': continue
        for TH in (0.05, 0.10):
            for N in (25, 100):
                report(model, TH, N, ALLK, 'map', '%s %s TH=%.0fc N=%d per-map' % (name, model, TH * 100, N))
    report('A', 0.05, 100, ALLK, 'round', '%s A TH=5c N=100 per-round' % name)
ROWS_CUR = ROWSETS['+EQUIP']
for N in (25, 100):
    bets = run('A', 0.05, N, set(x['key'] for x in ROWS_CUR), 'map', oracle=True)
    pnl = sum(b['pnl'] for b in bets); pm, ps = placebo(bets, pool_for(N), N)
    print('ORACLE N=%d: bets %d PnL $%+.0f | placebo $%+.0f +/- %.0f -> z %+.1f' % (N, len(bets), pnl, pm, ps, (pnl - pm) / ps))
