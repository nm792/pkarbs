"""Fit the cricket models on Cricsheet men's T20I ball-by-ball.
Train: matches before 2024-01-01. Test: 2024 onwards (out of sample).
Skips: no result, ties, D/L or reduced-overs games.
Usage: python3 -m evrules.fit_cricket <dir of unzipped cricsheet json>
"""
import json, glob, sys, os
import numpy as np
from evrules.cricket import x1, x2


def legal(d):
    e = d.get('extras', {})
    return not ('wides' in e or 'noballs' in e)


FULL = {'Afghanistan', 'Australia', 'Bangladesh', 'England', 'India', 'Ireland', 'New Zealand', 'Pakistan',
        'South Africa', 'Sri Lanka', 'West Indies', 'Zimbabwe'}
FULL_ONLY = os.environ.get('FULL_ONLY', '0') == '1'   # FULL_ONLY=1: both teams ICC full members only


def samples(path):
    d = json.load(open(path)); i = d['info']
    if FULL_ONLY and not set(i['teams']) <= FULL: return None
    if i.get('overs') != 20 or i.get('balls_per_over', 6) != 6: return None
    o = i.get('outcome', {})
    if 'winner' not in o or 'method' in o or len(d['innings']) < 2: return None
    inn = d['innings']
    if any(x.get('super_over') for x in inn[:2]): return None
    first = inn[0]['team']; bf_won = o['winner'] == first
    out1, out2 = [], []
    runs = w = b = 0
    for ov in inn[0]['overs']:
        for dl in ov['deliveries']:
            runs += dl['runs']['total']; w += len(dl.get('wickets', []))
            if legal(dl): b += 1
        out1.append((x1(runs, w, b), bf_won))
    tgt = inn[1].get('target', {})
    if tgt.get('overs', 20) != 20: return None
    target = tgt.get('runs', runs + 1)
    r2 = w2 = b2 = 0
    out2.append((x2(target, 10, 120), not bf_won))
    for ov in inn[1]['overs']:
        for dl in ov['deliveries']:
            r2 += dl['runs']['total']; w2 += len(dl.get('wickets', []))
            if legal(dl): b2 += 1
            if r2 >= target or w2 >= 10: break
        if r2 >= target or w2 >= 10 or b2 >= 120: break
        out2.append((x2(target - r2, 10 - w2, 120 - b2), not bf_won))
    return i['dates'][0], out1, out2


def logit_fit(X, y, lam=1e-3, it=50):
    b = np.zeros(X.shape[1])
    for _ in range(it):
        p = 1 / (1 + np.exp(-X @ b)); W = p * (1 - p)
        H = X.T @ (X * W[:, None]) + lam * np.eye(len(b))
        b = b + np.linalg.solve(H, X.T @ (y - p) - lam * b)
    return b


def metrics(X, y, b):
    p = np.clip(1 / (1 + np.exp(-X @ b)), 1e-6, 1 - 1e-6)
    ll = float(-np.mean(y * np.log(p) + (1 - y) * np.log(1 - p)))
    br = float(np.mean((p - y) ** 2))
    base = float(np.mean(y)); bb = float(np.mean((base - y) ** 2))
    # calibration by decile
    q = np.quantile(p, np.linspace(0, 1, 11)); cal = []
    for a, c in zip(q[:-1], q[1:]):
        s = (p >= a) & (p <= c)
        if s.any(): cal.append((round(float(p[s].mean()), 3), round(float(y[s].mean()), 3), int(s.sum())))
    return dict(n=int(len(y)), logloss=ll, brier=br, brier_base_rate=bb, calibration_pred_obs_n=cal)


def main():
    D = sys.argv[1]
    tr1, te1, tr2, te2 = [], [], [], []
    n = 0
    for f in sorted(glob.glob(f'{D}/*.json')):
        s = samples(f)
        if not s: continue
        n += 1
        date, a, b = s
        (te1 if date >= '2024-01-01' else tr1).extend(a)
        (te2 if date >= '2024-01-01' else tr2).extend(b)
    out = dict(source='Cricsheet t20s_male_json.zip (men T20I)', full_members_only=FULL_ONLY, n_matches=n, train='< 2024-01-01', test='>= 2024-01-01')
    for name, tr, te, xf in (('inn1', tr1, te1, 'x1'), ('inn2', tr2, te2, 'x2')):
        Xtr = np.array([x for x, _ in tr]); ytr = np.array([float(v) for _, v in tr])
        Xte = np.array([x for x, _ in te]); yte = np.array([float(v) for _, v in te])
        b = logit_fit(Xtr, ytr)
        out[name] = dict(beta=list(map(float, b)), features=xf, train=metrics(Xtr, ytr, b), test=metrics(Xte, yte, b))
    print(json.dumps({k: (v if not isinstance(v, dict) else {kk: vv for kk, vv in v.items() if kk != 'beta'}) for k, v in out.items()}, indent=1))
    json.dump(out, open(os.path.join(os.path.dirname(__file__), 'params', 'cricket.json'), 'w'), indent=1)


if __name__ == '__main__':
    main()
