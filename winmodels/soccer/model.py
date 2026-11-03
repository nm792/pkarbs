"""Soccer in-play model: independent Poisson goals for the rest of the match.
Remaining expected goals = pre-match rate x R(effective minute) x red-card multipliers.
Pre-match rates (home, away) are solved from Polymarket's own pre-kickoff prices (1X2 + totals)."""
import os, json, math
import numpy as np
from scipy.optimize import minimize
P = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'params.json')))
EDG, RR = np.array(P['edges']), np.array(P['R'])
S1, END = P['S1'], P['END']
N = 13
_f = np.array([math.factorial(k) for k in range(N)], float)
def pmf(mu): return np.exp(-mu) * mu ** np.arange(N) / _f
def R(e): return float(np.interp(e, EDG, RR))
def grid(h, a, mh, ma):
    """final-score probability matrix offset by current score: G[x, y] = P(home adds x, away adds y)."""
    return np.outer(pmf(mh), pmf(ma))
def prob(kind, line, h, a, G):
    x = np.arange(N)[:, None] + h; y = np.arange(N)[None, :] + a
    if kind == 'home': m = x > y
    elif kind == 'away': m = y > x
    elif kind == 'draw': m = x == y
    elif kind == 'over': m = (x + y) > line
    elif kind == 'home_spread': m = (x - y + line) > 0
    elif kind == 'away_spread': m = (y - x + line) > 0
    elif kind == 'btts': m = (x >= 1) & (y >= 1)
    else: raise ValueError(kind)
    return float(G[m].sum())
def solve_rates(targets):
    """targets: list of (kind, line, price). Least squares in log-rates from 0-0 at kickoff."""
    def loss(v):
        G = grid(0, 0, math.exp(v[0]), math.exp(v[1]))
        return sum((prob(k, l, 0, 0, G) - p) ** 2 for k, l, p in targets)
    r = minimize(loss, [math.log(1.4), math.log(1.15)], method='Nelder-Mead', options=dict(xatol=1e-4, fatol=1e-8))
    return math.exp(r.x[0]), math.exp(r.x[1]), r.fun
def mults(reds_h, reds_a):
    mh = (P['red_carded'] ** reds_h) * (P['red_opp'] ** reds_a)
    ma = (P['red_carded'] ** reds_a) * (P['red_opp'] ** reds_h)
    return mh, ma
