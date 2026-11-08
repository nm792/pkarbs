"""Out-of-sample NBA delay curve on 2025-26 season games (raw/us_nba_hist, moneyline only), with the rule frozen
from nba_delay_curve.py (locked params + jump beta from 22-27 Oct 2026 train games). Same fills, caps, hold to result.
Note: the margin-variance model (params.json) was fit on 2025-26 ESPN games, so the fair model has seen these
games' score paths (not their prices); the rule parameters have not."""
import sys, os, json, math, gzip, bisect, tempfile
import numpy as np
from scipy.optimize import minimize_scalar
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
import common as C
REAL = C.RAW
tmp = tempfile.mkdtemp(); os.makedirs(f'{tmp}/us'); os.makedirs(f'{tmp}/us_bt')
os.symlink(f'{REAL}/us_nba_hist/gamma_events.json.gz', f'{tmp}/us/gamma_events.json.gz')
os.symlink(f'{REAL}/us_nba_hist/match.json', f'{tmp}/us/match_pm_espn.json')
os.symlink(f'{REAL}/us_nba_hist/trades', f'{tmp}/us/trades')
os.symlink(f'{REAL}/us_hist/nba', f'{tmp}/us_bt/nba')
import backtest as B, nba_guard as NG     # imported before the switch: fit_hist reads REAL us_hist
C.RAW = tmp
B.SPORTS = ['nba']; SP = 'nba'
L0 = json.load(open(os.path.join(HERE, 'out_nba_delay_curve.json')))
beta = L0['beta']; L = L0['locked']
EV, why = B.load(); print('events', len(EV), dict(why), flush=True)
games = []
for E in EV:
    mk = []
    for m in E['markets']:
        if m['type'] != 'moneyline': continue
        fn = f"{C.RAW}/us/trades/{m['cond']}.json.gz"
        if not os.path.exists(fn): continue
        pr = C.prints(json.load(gzip.open(fn)))
        if len(pr) < 20: continue
        hf, af = E['fin']
        if round(B.prob(m, hf, af, 0, 1e-6, 0, 1e-6)) != (1 if m['win0'] else 0): continue
        mk.append((m, pr, C.Mid(pr)))
    if not mk: continue
    t0 = E['t0']; sd0m = math.sqrt(B.V(SP, 'Vm', 0))
    tm = [(m, M.at(t0 - 60)) for m, pr, M in mk]; tm = [(m, p) for m, p in tm if p is not None and 0.03 < p < 0.97]
    if not tm: continue
    mu = minimize_scalar(lambda x: sum((B.prob(m, 0, 0, x, sd0m, 0, 1) - p) ** 2 for m, p in tm), bounds=(-40, 40), method='bounded').x
    g = dict(E=E, mk=mk, mu=mu, tau=225.0); g['ev'] = {}
    tl = E['tl']
    for m, pr, M in mk:
        g['ev'][m['cond']] = [(tl[k][0], NG.fair_at(g, m, tl[k]) - NG.fair_at(g, m, tl[k - 1])) for k in range(1, len(tl)) if tl[k][3:] != tl[k - 1][3:]]
    games.append(g)
print('games with moneyline trades', len(games), flush=True)
def run(g, lag, W, minj, caught, Q, max_gap=0.01, d=0.025):
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
            mk_ = M.at(T - C.QDELAY); pre = M.at(t - 2)
            if mk_ is None or pre is None or not (0.05 <= mk_ <= 0.95): continue
            moved = (mk_ - pre) if tok == 0 else (pre - mk_)
            if moved >= caught * abs(pj): continue
            if tok == 0:
                b = mk_ * (1 - d)
                if not sell0 or ph >= b - 1e-9 or (b - ph) / b > max_gap: continue
            else:
                b = (1 - mk_) * (1 - d)
                if sell0 or (1 - ph) >= b - 1e-9 or (b - (1 - ph)) / b > max_gap: continue
            q = min(sz, Q); m60 = M.at(T + 60); m60 = m60 if tok == 0 else 1 - m60
            out = 1.0 if (m['win0'] == (tok == 0)) else 0.0
            tot += [q * b, q * (m60 - b), q * (out - b), q * m['reb'] * b * (1 - b)]
    return tot
res = []
for Q in (100, 500):
    for lag in (0, 2, 5, 10, 20, 30, 60):
        s = C.summarize([run(g, lag, L['W'], L['minj'], L['caught'], Q) for g in games])
        row = dict(cap=Q, delay=lag, games=len(games), per_game_usd=round(s['net_result_usd'] / len(games), 1), **s); res.append(row)
        print(f"2025-26 cap{Q:>4} delay{lag:>3}s: games {len(games)} filled ${s['usd']:>7} (${s['usd']/len(games):.0f}/game) 1min {s['net_1min_pct']:>6}% {s['ci_1min']} "
              f"result {s['net_result_pct']:>6}% {s['ci_result']} ${s['net_result_usd']:>6} (${row['per_game_usd']}/game, 90% {s['ci_result_usd']}) ex-top5 {s['ex_top5_result_pct']}%", flush=True)
json.dump(dict(beta=beta, locked=L, n_games=len(games), curve=res), open(os.path.join(HERE, 'out_nba_delay_hist.json'), 'w'), indent=1, default=float)
