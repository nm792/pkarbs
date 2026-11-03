"""NBA: resting bid at market x 0.975 with (a) speed guard: after each score change, seen LAG s after ESPN's
wallclock, pull the bid on the token the score hurts (model fair falls) for PULL s; (b) veto: bid only if
model fair - bid >= E. Pass test: positive with the top 5 games removed; 90% range by game (bootstrap)."""
import sys, os, json, gzip, collections, math, bisect, itertools
import numpy as np
from scipy.optimize import minimize_scalar
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
import common as C, backtest as B
B.SPORTS = ['nba']; SP = 'nba'
def prep():
    EV, why = B.load(); games = []
    for E in EV:
        mk = []
        for m in E['markets']:
            fn = f"{C.RAW}/us/trades/{m['cond']}.json.gz"
            if not os.path.exists(fn): continue
            pr = C.prints(json.load(gzip.open(fn)))
            if len(pr) < 20: continue
            hf, af = E['fin']
            if round(B.prob(m, hf, af, 0, 1e-6, 0, 1e-6)) != (1 if m['win0'] else 0): continue
            mk.append((m, pr, C.Mid(pr)))
        t0 = E['t0']; sd0m, sd0t = math.sqrt(B.V(SP, 'Vm', 0)), math.sqrt(B.V(SP, 'Vt', 0))
        tm = [(m, M.at(t0 - 60)) for m, pr, M in mk]; tm = [(m, p) for m, p in tm if p is not None and 0.03 < p < 0.97]
        sm = [(m, p) for m, p in tm if m['type'] != 'totals']; st_ = [(m, p) for m, p in tm if m['type'] == 'totals']
        if not sm or not st_: continue
        mu = minimize_scalar(lambda x: sum((B.prob(m, 0, 0, x, sd0m, 0, 1) - p) ** 2 for m, p in sm), bounds=(-40, 40), method='bounded').x
        tau = minimize_scalar(lambda x: sum((B.prob(m, 0, 0, 0, 1, x, sd0t) - p) ** 2 for m, p in st_), bounds=(100, 300), method='bounded').x
        games.append(dict(E=E, mk=mk, mu=mu, tau=tau))
    return games
def fair_at(g, m, row):
    _, per, clk, h, a = row; fr = B.frac(SP, per, clk); rem = 1 - fr
    return B.prob(m, h, a, g['mu'] * rem, math.sqrt(B.V(SP, 'Vm', fr)), g['tau'] * rem, math.sqrt(B.V(SP, 'Vt', fr)))
def run_game(g, lag, pull, E_, veto, max_gap=None):
    E = g['E']; tl = E['tl']; tt = [r[0] for r in tl]; out = []
    for m, pr, M in g['mk']:
        sev = []
        if pull and m['cond'] in g.get('sv', {}): sev = g['sv'][m['cond']]
        elif pull:
            for k in range(1, len(tl)):
                if tl[k][3:] == tl[k - 1][3:]: continue
                f0, f1 = fair_at(g, m, tl[k - 1]), fair_at(g, m, tl[k])
                sev.append((tl[k][0], 0 if f1 < f0 else 1))
            g.setdefault('sv', {})[m['cond']] = sev
        fc = g.setdefault('fc', {}).setdefault(m['cond'], {})
        def fair(T):
            i = bisect.bisect_right(tt, T - lag) - 1
            if i < 0: return None
            v = fc.get(i)
            if v is None: v = fc[i] = fair_at(g, m, tl[i])
            return v
        r = C.sim(pr, M, E['t0'], E['t1'], fair if veto else None, m['win0'], E_, (), lag, m['reb'], gate=veto, sevs=sev, pull_s=pull or 30, max_gap=max_gap)
        out.append([sum(z[k] for z in r) for k in ('usd', 'em1', 'pnl', 'reb')])
    return np.sum(out, axis=0) if out else np.zeros(4)
if __name__ == '__main__':
    games = prep(); print('NBA games', len(games), 'markets', sum(len(g['mk']) for g in games), flush=True)
    variants = [('plain', 10, 0, 0, False)]
    for lag in (0, 3, 10):
        for pull in (15, 30):
            variants.append((f'guard lag{lag} pull{pull}', lag, pull, 0, False))
    for lag in (0, 3, 10):
        for E_ in (0, 0.02, 0.05):
            variants.append((f'veto E{int(E_*100)} lag{lag}', lag, 0, E_, True))
            variants.append((f'guard+veto E{int(E_*100)} lag{lag} pull30', lag, 30, E_, True))
    res = []
    for name, lag, pull, E_, veto in variants:
        per = [run_game(g, lag, pull, E_, veto) for g in games]
        s = C.summarize(per); res.append(dict(variant=name, lag=lag, pull=pull, E=E_, veto=veto, **s))
        print(f"{name:32} games {s['events']:>3} $fill {s['usd']:>9} 1min {s['net_1min_pct']:>6}% {s['ci_1min']}  result {s['net_result_pct']:>6}% {s['ci_result']} ${s['net_result_usd']:>8} | ex-top5 1min {s['ex_top5_1min_pct']}% result {s['ex_top5_result_pct']}% ${s['ex_top5_result_usd']}", flush=True)
    json.dump(res, open(os.path.join(HERE, 'out_nba_guard.json'), 'w'), indent=1)
