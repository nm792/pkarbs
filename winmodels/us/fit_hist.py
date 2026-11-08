"""Fit remaining-margin and remaining-total variance by game fraction from previous-season ESPN games.
mu (pre-game expected margin, home) and tau (expected total) come from ESPN pickcenter (DraftKings) lines.
Model: final - now ~ Normal(mean*(1-f), V(f)), V fitted per fraction bin (empirical, monotone)."""
import sys, os, json, gzip, glob, re, datetime as dt
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common import RAW
from espn import PLEN, NPER
HERE = os.path.dirname(os.path.abspath(__file__))
def frac(sp, per, clock):
    L = PLEN[sp]; n = NPER[sp]
    if per > n: return 1.0
    return min(((per - 1) * L + (L - clock)) / (n * L), 1.0)
def pre(g):
    o = (g.get('odds') or [{}])[0]
    if o.get('spread') is None or o.get('total') is None or not o.get('details'): return None
    det = o['details']; ab = det.split()[0]
    if det.upper().startswith('EVEN'): mu = 0.0
    else:
        try: v = float(det.split()[-1])
        except ValueError: return None
        mu = -v if ab == g['comp']['home']['abbr'] else v      # details "BOS -6.5" = BOS favoured by 6.5
        if ab not in (g['comp']['home']['abbr'], g['comp']['away']['abbr']): return None
    return mu, float(o['total'])
BINS = np.array([0, .1, .2, .3, .4, .5, .6, .7, .8, .9, .95, 1.0])
def fit(sp):
    rows = []
    for fn in glob.glob(f'{RAW}/us_hist/{sp}/*.json.gz'):
        g = json.load(gzip.open(fn))
        if not g.get('completed') or not g['tl']: continue
        p = pre(g)
        if p is None: continue
        fh, fa = int(g['comp']['home']['score']), int(g['comp']['away']['score'])
        reg = [r for r in g['tl'] if r[1] <= NPER[sp]]
        if not reg: continue
        lastreg = reg[-1]; mf, tf = lastreg[3] - lastreg[4], lastreg[3] + lastreg[4]   # end of regulation margin/total
        for r in reg:
            f = frac(sp, r[1], r[2])
            rows.append((f, mf - (r[3] - r[4]), tf - (r[3] + r[4]), p[0], p[1], fh - fa, g['id']))
    R = np.array([r[:6] for r in rows], float)
    f, dm, dt_, mu, tau = R[:, 0], R[:, 1], R[:, 2], R[:, 3], R[:, 4]
    out = dict(sport=sp, games=len({r[6] for r in rows}), bins=BINS.tolist(), Vm=[], Vt=[], km=[], kt=[], n=[])
    for a, b in zip(BINS[:-1], BINS[1:]):
        m = (f >= a) & (f < b)
        rem = 1 - f[m]
        km = float(np.sum(dm[m] * mu[m] * rem) / max(np.sum((mu[m] * rem) ** 2), 1e-9))     # drift weight on mu (1 = take the line at face value)
        kt = float(np.sum(dt_[m] * tau[m] * rem) / max(np.sum((tau[m] * rem) ** 2), 1e-9))
        out['km'].append(km); out['kt'].append(kt)
        out['Vm'].append(float(np.mean((dm[m] - mu[m] * rem) ** 2))); out['Vt'].append(float(np.mean((dt_[m] - tau[m] * rem) ** 2))); out['n'].append(int(m.sum()))
    sd0 = np.sqrt(out['Vm'][0]); print(sp, 'games', out['games'], 'sd remaining margin at start', round(sd0, 2), 'total', round(np.sqrt(out['Vt'][0]), 2),
                                        'drift weight (should be ~1)', [round(x, 2) for x in out['km'][:3]], [round(x, 2) for x in out['kt'][:3]])
    return out
P = {sp: fit(sp) for sp in ('nba', 'nfl', 'cfb', 'nhl')}
json.dump(P, open(os.path.join(HERE, 'params.json'), 'w'), indent=1)
