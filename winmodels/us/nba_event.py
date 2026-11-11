"""NBA event-only rule (LoL lesson): bid market x 0.975 ONLY in a short window after a score change, ONLY on the token
an event-jump model says should rise by >= MINJ and has not yet risen by CAUGHT of that. Corrected fill rule (max_gap).
Jump model: dFair from the normal-margin model (fair after - fair before the score), shrunk by beta fitted on training games.
Train = games starting before 28 Oct 00Z; test = later games (held out). Rule is chosen on train, then frozen."""
import sys, os, json, bisect, math, collections, itertools
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
import common as C, nba_guard as NG
SPLIT = 1793145600   # 2026-10-28T00:00Z
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
print('games train', len(train), 'test', len(test), flush=True)
# jump model: actual mid move from 2 s before to 30 s after the event vs model dFair (token0), training games only
X = []; Y = []
for g in train:
    for m, pr, M in g['mk']:
        for t, df in g['ev'][m['cond']]:
            a, b = M.at(t - 2), M.at(t + 30)
            if a is None or b is None or not (0.05 < a < 0.95): continue
            X.append(df); Y.append(b - a)
X, Y = np.array(X), np.array(Y); beta = float(X @ Y / (X @ X))
r2 = 1 - np.sum((Y - beta * X) ** 2) / np.sum((Y - Y.mean()) ** 2)
print(f'jump model (train): {len(X)} events, beta {beta:.2f}, R2 {r2:.2f}; mean |predicted| {np.mean(np.abs(beta*X))*100:.2f}c, mean |actual| {np.mean(np.abs(Y))*100:.2f}c', flush=True)
def run(g, lag, W, minj, caught, max_gap=0.01, d=0.025):
    E = g['E']; tot = np.zeros(4)
    for m, pr, M in g['mk']:
        ev = g['ev'][m['cond']]; et = [e[0] for e in ev]
        for (T, _, ph, sell0, sz) in pr:
            if not (E['t0'] <= T <= E['t1']): continue
            i = bisect.bisect_right(et, T - lag) - 1
            if i < 0 or T > et[i] + lag + W: continue
            t, df = ev[i]; pj = beta * df
            if abs(pj) < minj: continue
            tok = 0 if pj > 0 else 1
            mk = M.at(T - C.QDELAY); pre = M.at(t - 2)
            if mk is None or pre is None or not (0.05 <= mk <= 0.95): continue
            moved = (mk - pre) if tok == 0 else (pre - mk)
            if moved >= caught * abs(pj): continue                 # market already made the move
            if tok == 0:
                b = mk * (1 - d)
                if not sell0 or ph >= b - 1e-9 or (b - ph) / b > max_gap: continue
            else:
                b = (1 - mk) * (1 - d)
                if sell0 or (1 - ph) >= b - 1e-9 or (b - (1 - ph)) / b > max_gap: continue
            q = min(sz, C.Q); m60 = M.at(T + 60); m60 = m60 if tok == 0 else 1 - m60
            out = 1.0 if (m['win0'] == (tok == 0)) else 0.0
            tot += [q * b, q * (m60 - b), q * (out - b), q * m['reb'] * b * (1 - b)]
    return tot
grid = list(itertools.product([0, 3, 10], [10, 20, 30], [0.005, 0.01, 0.02], [0.5, 1.0]))
res = []
for lag, W, minj, caught in grid:
    s = C.summarize([run(g, lag, W, minj, caught) for g in train], nb=500)
    res.append(dict(set='train', lag=lag, W=W, minj=minj, caught=caught, **s))
    print(f"train lag{lag} W{W} minj{minj} caught{caught}: $fill {s['usd']} 1min {s.get('net_1min_pct')}% result {s.get('net_result_pct')}%", flush=True)
# lock: best 1-min net on train at lag 3 (a realistic fast feed), requiring >= $20k filled
cand = [r for r in res if r['lag'] == 3 and r['usd'] >= 5000]
best = max(cand, key=lambda r: r['net_1min_pct'])
print('LOCKED on train:', {k: best[k] for k in ('W', 'minj', 'caught')}, 'train 1min', best['net_1min_pct'], 'result', best['net_result_pct'], flush=True)
out = dict(beta=beta, r2=r2, n_events_train=len(X), locked={k: best[k] for k in ('W', 'minj', 'caught')}, train=res, test=[])
for lag in (0, 3, 10, 30):
    for W in (10, 20, 30):
        for mg in (0.01, 0.03):
            s = C.summarize([run(g, lag, W, best['minj'], best['caught'], mg) for g in test])
            out['test'].append(dict(lag=lag, W=W, max_gap=mg, **s))
            print(f"TEST lag{lag:>3} W{W:>3} gap{mg}: games {s['events']} $fill {s['usd']:>7} 1min {s['net_1min_pct']:>6}% {s['ci_1min']} result {s['net_result_pct']:>6}% {s['ci_result']} ${s['net_result_usd']} | ex-top5 1min {s['ex_top5_1min_pct']}% result {s['ex_top5_result_pct']}% ${s['ex_top5_result_usd']}", flush=True)
json.dump(out, open(os.path.join(HERE, 'out_nba_event.json'), 'w'), indent=1)
