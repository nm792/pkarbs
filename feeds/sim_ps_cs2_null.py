#!/usr/bin/env python3
"""Null simulation of the PandaScore CS2 sequential rule (checker, 18 Nov): per-match d iid from a null distribution, matches arrive Poisson(rate) per day, 12 daily looks, min 12 matches,
N_MAX 60, pass if z_eq >= 2.60/sqrt(min(1, n/60)) at ANY look (same cell_t as the daily script). Result 18 Nov: false-pass rate <= 0.63% in all 8 scenarios (6000 sims each; target < 0.93%).
Usage: python3 sim_ps_cs2_null.py"""
import sys, math, random
import os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import goalserve_odds_vs_pm_v2 as g
C, NMAX, LOOKS, MINM = 2.60, 60, 12, 12
def run(rate, dist, sims=6000, seed=7, lag_extra=0):
    rnd = random.Random(seed); fp = 0
    for _ in range(sims):
        vals = []; hit = False
        for k in range(1, LOOKS+1):
            # Poisson arrivals per day
            L = math.exp(-rate); n = 0; p = 1.0
            while True:
                p *= rnd.random()
                if p <= L: break
                n += 1
            for _i in range(n):
                if len(vals) < NMAX:
                    vals.append(dist(rnd))
            m = len(vals)
            if m < MINM: continue
            _, mu, se, t, z = g.cell_t(vals)
            if z is None: continue
            if z >= C/math.sqrt(min(1.0, m/NMAX)): hit = True; break
        fp += hit
    return fp/sims
norm = lambda r: r.gauss(0, 6)
heavy = lambda r: r.gauss(0, 3) * (1 if r.random() < .8 else 5)
if __name__ == "__main__":
    for rate in (3, 5, 8, 15):
        print(rate, "normal", run(rate, norm), "heavy", run(rate, heavy), flush=True)
