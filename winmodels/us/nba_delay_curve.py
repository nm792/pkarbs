"""NBA event-only rule: delay curve at TRUE event time (Nick's 4 Nov rule: test the rule, not the feed).
True event time = ESPN play wallclock (lag_nba.py: the Polymarket price starts moving AT the wallclock, so it is
not late). Rule (unchanged from nba_event.py): after a score change, for W s, bid market x 0.975 (maker only,
never at/above ask) only on the token the jump model says should rise >= MINJ and that has not yet moved CAUGHT
of that; fill only on taker prints within max_gap 1% below our bid (corrected fill rule, PR #27); hold to result.
Rule parameters are chosen on TRAIN games at delay 0 and frozen, then run on held-out TEST games at every delay.
Delay = how many seconds after the true event our system learns the new score."""
import sys, os, json, bisect, itertools
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
import common as C, nba_guard as NG
SPLIT = 1793145600   # 2026-10-28T00:00Z (same split as nba_event.py)
DELAYS = [0, 2, 5, 10, 20, 30, 60]
games = NG.prep()
for g in games:
    E = g['E']; tl = E['tl']; g['ev'] = {}
    for m, pr, M in g['mk']:
        ev = []
        for k in range(1, len(tl)):
            if tl[k][3:] == tl[k - 1][3:]: continue
            ev.append((tl[k][0], NG.fair_at(g, m, tl[k]) - NG.fair_at(g, m, tl[k - 1])))
        g['ev'][m['cond']] = ev
train = [g for g in games if g['E']['t0'] < SPLIT]; test = [g for g in games if g['E']['t0'] >= SPLIT]
X = []; Y = []
for g in train:
    for m, pr, M in g['mk']:
        for t, df in g['ev'][m['cond']]:
            a, b = M.at(t - 2), M.at(t + 30)
            if a is None or b is None or not (0.05 < a < 0.95): continue
            X.append(df); Y.append(b - a)
X, Y = np.array(X), np.array(Y); beta = float(X @ Y / (X @ X))
print(f'games train {len(train)} test {len(test)}; jump beta {beta:.3f}', flush=True)

def run(g, lag, W, minj, caught, Q, max_gap=0.01, d=0.025):
    E = g['E']; tot = np.zeros(4)
    for m, pr, M in g['mk']:
        ev = g['ev'][m['cond']]; et = [e[0] for e in ev]
        for (T, _, ph, sell0, sz) in pr:
            if not (E['t0'] <= T <= E['t1']): continue
            i = bisect.bisect_right(et, T - lag) - 1             # latest event we KNOW about at time T
            if i < 0 or T > et[i] + lag + W: continue
            t, df = ev[i]; pj = beta * df
            if abs(pj) < minj: continue
            tok = 0 if pj > 0 else 1
            mk = M.at(T - C.QDELAY); pre = M.at(t - 2)
            if mk is None or pre is None or not (0.05 <= mk <= 0.95): continue
            moved = (mk - pre) if tok == 0 else (pre - mk)
            if moved >= caught * abs(pj): continue
            if tok == 0:
                b = mk * (1 - d)
                if not sell0 or ph >= b - 1e-9 or (b - ph) / b > max_gap: continue
            else:
                b = (1 - mk) * (1 - d)
                if sell0 or (1 - ph) >= b - 1e-9 or (b - (1 - ph)) / b > max_gap: continue
            q = min(sz, Q); m60 = M.at(T + 60); m60 = m60 if tok == 0 else 1 - m60
            out = 1.0 if (m['win0'] == (tok == 0)) else 0.0
            tot += [q * b, q * (m60 - b), q * (out - b), q * m['reb'] * b * (1 - b)]
    return tot

grid = list(itertools.product([10, 20, 30], [0.005, 0.01, 0.02], [0.5, 1.0]))
res = []
for W, minj, caught in grid:
    s = C.summarize([run(g, 0, W, minj, caught, 100) for g in train], nb=300)
    res.append(dict(W=W, minj=minj, caught=caught, **s))
cand = [r for r in res if r['usd'] >= 5000]
best = max(cand, key=lambda r: r['net_result_pct'])          # lock on hold-to-result, the P&L Nick's rule is judged on
L = {k: best[k] for k in ('W', 'minj', 'caught')}
print('LOCKED on train at delay 0:', L, 'train 1min', best['net_1min_pct'], '% result', best['net_result_pct'], '%', flush=True)
out = dict(beta=beta, locked=L, n_train=len(train), n_test=len(test), train_grid=res, curve=[])
for Q in (100, 500):
    for nm, gs in (('test', test), ('all', games)):
        for lag in DELAYS:
            per = [run(g, lag, L['W'], L['minj'], L['caught'], Q) for g in gs]
            s = C.summarize(per)
            row = dict(set=nm, cap=Q, delay=lag, games=len(gs), per_game_usd=round(s['net_result_usd'] / len(gs), 1), **s)
            out['curve'].append(row)
            print(f"{nm:>4} cap{Q:>4} delay{lag:>3}s: games {len(gs)} filled ${s['usd']:>7} 1min {s['net_1min_pct']:>6}% {s['ci_1min']} "
                  f"result {s['net_result_pct']:>6}% {s['ci_result']} ${s['net_result_usd']:>6} (${row['per_game_usd']}/game, 90% {s['ci_result_usd']}) "
                  f"ex-top5 {s['ex_top5_result_pct']}%", flush=True)
json.dump(out, open(os.path.join(HERE, 'out_nba_delay_curve.json'), 'w'), indent=1, default=float)
