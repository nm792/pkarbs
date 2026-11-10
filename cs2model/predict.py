"""Prediction helpers: in-round model + map DP anchored on the market price."""
import json, math, bisect, functools
from cs2lib import *
W = None
def load_model(path):
    global W
    d = json.load(open(path)); W = d
    return d
def g_state(r, w):
    """state part of the logit (home perspective), WITHOUT intercept; w = coefficient list (intercept first)."""
    s = 1.0 if r['homeT'] else -1.0
    d = r['al_h'] - r['al_a']; tot = r['al_h'] + r['al_a']; pl = r['planted']
    x = [d, d * (10 - tot) / 10.0, (r['hp_h'] - r['hp_a']) / 100.0, pl * s, pl * s * min(r['tplant'], 45) / 40.0, (1 - pl) * (-s) * max(r['el'], 0) / 100.0, s, d * pl * s, r['mdiff'] / 10000.0, (r['adr_h'] - r['adr_a']) / 50.0, (r['k_h'] - r['k_a']) / max(r['n'], 3) / 3.0]
    return sum(a * b for a, b in zip(w[1:], x))
def side_coef(w): return w[1 + 6]
@functools.lru_cache(maxsize=4096)
def dp_for(o, z0q, ws):
    z0 = z0q / 1000.0
    return make_map_dp(o, sig(z0 + ws), sig(z0 - ws))
def pmap_row(r, o, z0, w, use_state=True):
    ws = side_coef(w)
    V = dp_for(o, round(z0 * 1000), round(ws, 4))
    if not use_state: return V(r['h'], r['a'])
    pr = sig(z0 + g_state(r, w))
    return pr * V(r['h'] + 1, r['a']) + (1 - pr) * V(r['h'], r['a'] + 1)
def solve_z0_row(r, o, price, w):
    lo, hi = -3.0, 3.0
    for _ in range(40):
        z = (lo + hi) / 2
        if pmap_row(r, o, z, w) < price: lo = z
        else: hi = z
    return (lo + hi) / 2

import numpy as np
GRID = np.arange(-1.5, 1.5001, 0.05)
def posterior_z(rounds_done, z_anchor, ws, sigma):
    """Grid posterior over the home round-strength logit z: prior N(z_anchor, sigma) times likelihood of completed rounds (side-aware)."""
    lp = -0.5 * ((GRID - z_anchor) / sigma) ** 2
    for (homeT, y) in rounds_done:
        z = GRID + (ws if homeT else -ws)
        p = 1 / (1 + np.exp(-z))
        lp += np.log(p if y else 1 - p)
    w = np.exp(lp - lp.max()); return w / w.sum()
def pmap_row_post(r, o, post, w):
    tot = 0.0
    for z, wz in zip(GRID, post):
        if wz < 1e-4: continue
        tot += wz * pmap_row(r, o, float(z), w)
    return tot
