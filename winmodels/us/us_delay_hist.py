"""Event-only rule delay curve at TRUE event time for NFL (and later CFB/NHL), on a past season (4 Nov 2026).

Data: raw/us_<sp>_hist (built by s1_hist_<sp>.py): Polymarket moneyline trades + ESPN play wallclock timeline.
Step 1 (true event time check): for every score change, when does the Polymarket mid move? Median time from ESPN
wallclock to half of the 60 s move. If the price moves BEFORE the wallclock, wallclock is late and delays are
shifted by that lag (true event time = wallclock + median lead, reported).
Step 2: same rule as nba_delay_curve.py: after a score change, for W s, bid market x 0.975 (maker only, never at/above
ask) only on the token the jump model says should rise >= MINJ and that has not yet moved CAUGHT x of that; fill only
on taker prints within 1% below our bid; hold to result; rebate estimate added. Parameters W, MINJ, CAUGHT and the jump
beta are fit on TRAIN games (before SPLIT) at delay 0 and frozen; TEST games run at every delay.
Fair model: normal remaining-margin model (params.json, fit on the same season's ESPN score paths, prices unseen),
pre-game mean from the Polymarket moneyline 60 s before kickoff, fixed total TAU (moneyline does not use it).
Usage: python3 us_delay_hist.py nfl"""
import sys, os, json, math, gzip, bisect, tempfile, itertools, collections
import numpy as np
from scipy.optimize import minimize_scalar
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
import common as C
SP = sys.argv[1] if len(sys.argv) > 1 else 'nfl'
YEAR = os.environ.get('YEAR', '')          # '' = 2025 season; '26' = 2026 season to date (nfl/s1_hist_nfl26.py)
SPLIT = {'': {'nfl': 1761955200}, '26': {'nfl': 1791158400}}[YEAR][SP]   # 2025: train Sep-Oct, test Nov-Jan; 2026: train before 5 Oct 2026, test 5 Oct-3 Nov
TAU = {'nfl': 45.0}[SP]
REAL = C.RAW
tmp = tempfile.mkdtemp(); os.makedirs(f'{tmp}/us'); os.makedirs(f'{tmp}/us_bt')
os.symlink(f'{REAL}/us_{SP}{YEAR}_hist/gamma_events.json.gz', f'{tmp}/us/gamma_events.json.gz')
os.symlink(f'{REAL}/us_{SP}{YEAR}_hist/match.json', f'{tmp}/us/match_pm_espn.json')
os.symlink(f'{REAL}/us_{SP}{YEAR}_hist/trades', f'{tmp}/us/trades')
os.symlink(f'{REAL}/us_hist{YEAR}/{SP}', f'{tmp}/us_bt/{SP}')
import backtest as B
C.RAW = tmp
B.SPORTS = [SP]
EV, why = B.load(); print('events', len(EV), dict(why), flush=True)
def fair_at(g, m, row):
    _, per, clk, h, a = row; fr = B.frac(SP, per, clk); rem = 1 - fr
    return B.prob(m, h, a, g['mu'] * rem, math.sqrt(B.V(SP, 'Vm', fr)), g['tau'] * rem, math.sqrt(B.V(SP, 'Vt', fr)))
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
    g = dict(E=E, mk=mk, mu=mu, tau=TAU); g['ev'] = {}
    tl = E['tl']
    for m, pr, M in mk:
        g['ev'][m['cond']] = [(tl[k][0], fair_at(g, m, tl[k]) - fair_at(g, m, tl[k - 1])) for k in range(1, len(tl)) if tl[k][3:] != tl[k - 1][3:]]
    games.append(g)
print('games with moneyline trades', len(games), flush=True)

# ---- Step 1: does the price move before or after the ESPN wallclock? (per score change, |model jump| >= 3c)
lead = []
for g in games:
    for m, pr, M in g['mk']:
        tt = [p[0] for p in pr]
        for t, df in g['ev'][m['cond']]:
            if abs(df) < 0.03: continue
            a, b = M.at(t - 120), M.at(t + 90)
            if a is None or b is None or not (0.05 < a < 0.95): continue
            mv = b - a
            if abs(mv) < 0.02 or np.sign(mv) != np.sign(df): continue
            i0 = bisect.bisect_left(tt, t - 120); i1 = bisect.bisect_right(tt, t + 90)
            for p in pr[i0:i1]:
                if (p[2] - a) / mv >= 0.5: lead.append(p[0] - t); break
lead = np.array(lead)
LAGINFO = dict(n=int(len(lead)), median_s=float(np.median(lead)) if len(lead) else None, p25=float(np.percentile(lead, 25)) if len(lead) else None,
               p75=float(np.percentile(lead, 75)) if len(lead) else None, share_before_wallclock=float((lead < 0).mean()) if len(lead) else None)
print('price half-move vs ESPN wallclock:', LAGINFO, flush=True)
SHIFT = min(0.0, LAGINFO['median_s'] or 0.0)      # if the price moves before wallclock, true event = wallclock + SHIFT
EVT = os.environ.get('EVT', 'wall')
if EVT == 'onset':
    # ESPN wallclock scatters -65..+19 s around the price move (NFL), so it is not true event time. Proxy for true
    # event time: the first print that has moved >= 20% of the (t-120 -> t+90) move in the model's direction (onset);
    # if no such move, wallclock + SHIFT. delay 0 = we learn the score the moment the market starts to react (best case).
    SHIFT = 0.0
    for g in games:
        for m, pr, M in g['mk']:
            tt = [p[0] for p in pr]; new = []
            for t, df in g['ev'][m['cond']]:
                a, b = M.at(t - 120), M.at(t + 90); te = t + min(0.0, LAGINFO['median_s'] or 0.0)
                if a is not None and b is not None and abs(b - a) >= 0.01 and np.sign(b - a) == np.sign(df):
                    for p in pr[bisect.bisect_left(tt, t - 120):bisect.bisect_right(tt, t + 90)]:
                        if (p[2] - a) / (b - a) >= 0.2: te = p[0]; break
                new.append((te, df))
            new.sort(); g['ev'][m['cond']] = new

train = [g for g in games if g['E']['t0'] < SPLIT]; test = [g for g in games if g['E']['t0'] >= SPLIT]
X = []; Y = []
for g in train:
    for m, pr, M in g['mk']:
        for t, df in g['ev'][m['cond']]:
            a, b = M.at(t + SHIFT - 2), M.at(t + SHIFT + 30)
            if a is None or b is None or not (0.05 < a < 0.95): continue
            X.append(df); Y.append(b - a)
X, Y = np.array(X), np.array(Y); beta = float(X @ Y / (X @ X))
print(f'games train {len(train)} test {len(test)}; jump beta {beta:.3f}', flush=True)

def run(g, lag, W, minj, caught, Q, max_gap=0.01, d=0.025):
    E = g['E']; tot = np.zeros(4)
    for m, pr, M in g['mk']:
        ev = [(t + SHIFT, df) for t, df in g['ev'][m['cond']]]; et = [e[0] for e in ev]
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

grid = list(itertools.product([10, 20, 30], [0.005, 0.01, 0.02], [0.5, 1.0]))
res = []
for W, minj, caught in grid:
    s = C.summarize([run(g, 0, W, minj, caught, 100) for g in train], nb=300)
    res.append(dict(W=W, minj=minj, caught=caught, **s))
cand = [r for r in res if r['usd'] >= 2000] or res
best = max(cand, key=lambda r: r['net_result_pct'])
L = {k: best[k] for k in ('W', 'minj', 'caught')}
print('LOCKED on train at delay 0:', L, 'train 1min', best['net_1min_pct'], '% result', best['net_result_pct'], '%', flush=True)
out = dict(sport=SP, event_time=EVT, lag_vs_wallclock=LAGINFO, shift=SHIFT, beta=beta, locked=L, n_train=len(train), n_test=len(test), train_grid=res, curve=[])
for Q in (100, 500):
    for nm, gs in (('test', test), ('all', games)):
        for lag in (0, 2, 5, 10, 20, 30, 60, 120, 300):
            s = C.summarize([run(g, lag, L['W'], L['minj'], L['caught'], Q) for g in gs])
            row = dict(set=nm, cap=Q, delay=lag, games=len(gs), per_game_usd=round(s['net_result_usd'] / len(gs), 1), **s); out['curve'].append(row)
            print(f"{nm:>4} cap{Q:>4} delay{lag:>3}s: games {len(gs)} filled ${s['usd']:>7} (${s['usd']/len(gs):.0f}/game) 1min {s['net_1min_pct']:>6}% {s['ci_1min']} "
                  f"result {s['net_result_pct']:>6}% {s['ci_result']} ${s['net_result_usd']:>6} (${row['per_game_usd']}/game, 90% {s['ci_result_usd']}) ex-top5 {s['ex_top5_result_pct']}%", flush=True)
json.dump(out, open(os.path.join(HERE, f'out_{SP}{YEAR}_delay_hist_{EVT}.json'), 'w'), indent=1, default=float)
