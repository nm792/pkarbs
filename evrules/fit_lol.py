"""Fit a LoL in-game win-probability model to Worlds 2026 data we hold.

Data: /mnt/project-files/rn1/scores/lol/lag-study-worlds-2026-10/
  out/<match>/frames.json.gz  (Riot livestats frames, ~0.25 s)
  out/<match>/trades.json.gz  (Polymarket Game 1 winner trades)
With only a handful of games we cannot fit on outcomes. We fit to the
MARKET: logit(price_blue) - logit(pre-game price_blue) as a linear
function of the game-state differences (blue minus red). That model says
where the market settles after an event; the edge we chase is the 1-5 s
before it gets there. Leave-one-game-out error is reported.
Usage: python3 -m evrules.fit_lol [data_dir]
"""
import gzip, json, sys, datetime as dt, os
import numpy as np

D = sys.argv[1] if len(sys.argv) > 1 else '/mnt/project-files/rn1/scores/lol/lag-study-worlds-2026-10'
FEATS = ['gold_k', 'gold_k_x_t', 'kills', 'towers', 'dragons', 'barons', 'inhibs']
# signs a game-state lead must have (all but the time interaction must be >= 0)
POS = [True, False, True, True, True, True, True]


def ts(s):
    return dt.datetime.fromisoformat(s.replace('Z', '+00:00')).timestamp()


def state(f):
    b, r = f['blueTeam'], f['redTeam']
    return dict(gold=b['totalGold'] - r['totalGold'], kills=b['totalKills'] - r['totalKills'],
                towers=b['towers'] - r['towers'], dragons=len(b['dragons']) - len(r['dragons']),
                barons=b['barons'] - r['barons'], inhibs=b['inhibitors'] - r['inhibitors'])


def feats(s, tmin):
    g = s['gold'] / 1000.0
    return [g, g * tmin / 30.0, s['kills'], s['towers'], s['dragons'], s['barons'], s['inhibs']]


def logit(p):
    p = np.clip(p, 0.02, 0.98)
    return np.log(p / (1 - p))


def fit_signed(X, y, lam=1.0):
    """Ridge, then drop features whose sign is wrong and refit (a lead
    in kills/towers/etc. cannot lower our win chance)."""
    keep = list(range(X.shape[1]))
    while True:
        Xa = X[:, keep]
        b = np.linalg.solve(Xa.T @ Xa + lam * np.eye(len(keep)), Xa.T @ y)
        bad = [k for k, v in zip(keep, b) if POS[k] and v < 0]
        if not bad:
            out = np.zeros(X.shape[1]); out[keep] = b
            return out
        keep.remove(min(bad, key=lambda k: b[keep.index(k)]))


def load_game(mid, outcome0):
    fr = json.load(gzip.open(f'{D}/out/{mid}/frames.json.gz'))
    tr = json.load(gzip.open(f'{D}/out/{mid}/trades.json.gz'))
    fr = [f for f in fr if f['gameState'] in ('in_game', 'paused', 'finished')]
    t0 = ts(fr[0]['rfc460Timestamp'])
    fin = [f for f in fr if f['gameState'] == 'finished']
    tend = ts(fin[0]['rfc460Timestamp']) if fin else ts(fr[-1]['rfc460Timestamp'])
    px = sorted((t['timestamp'], t['price'] if t['outcome'] == outcome0 else 1 - t['price'], t['size']) for t in tr)
    pt = np.array([x[0] for x in px], float); pp = np.array([x[1] for x in px])
    pre = pp[(pt > t0 - 900) & (pt < t0)]
    p0 = float(np.median(pre)) if len(pre) else 0.5
    # which side is outcome0? sign of corr(gold diff, price) over the game
    rows = []
    fi = 0; ft = np.array([ts(f['rfc460Timestamp']) for f in fr])
    for T in np.arange(t0 + 180, tend - 60, 30):
        i = np.searchsorted(ft, T) - 1
        w = (pt >= T + 5) & (pt <= T + 65)    # price 5-65 s after the state: market has caught up
        if w.sum() < 3:
            continue
        rows.append(((T - t0) / 60.0, state(fr[i]), float(np.median(pp[w]))))
    g = np.array([r[1]['gold'] for r in rows]); p = np.array([r[2] for r in rows])
    blue_is_0 = np.corrcoef(g, p)[0, 1] > 0
    if not blue_is_0:
        p0 = 1 - p0
        rows = [(a, b, 1 - c) for a, b, c in rows]
    endp = rows[-1][2]
    return dict(mid=mid, p0=p0, rows=rows, blue_is_outcome0=bool(blue_is_0), blue_won=endp > 0.5, minutes=(tend - t0) / 60)


def main():
    m = json.load(open(f'{D}/matched.json'))
    games = []
    for x in m:
        if not os.path.exists(f"{D}/out/{x['match_id']}/frames.json.gz"):
            continue
        games.append(load_game(x['match_id'], x['outcomes'][0]))
    X, y, gid = [], [], []
    for k, g in enumerate(games):
        for tmin, s, p in g['rows']:
            X.append(feats(s, tmin)); y.append(logit(p) - logit(g['p0'])); gid.append(k)
    X = np.array(X); y = np.array(y); gid = np.array(gid)
    lam = 1.0  # small ridge, few games
    fit = lambda Xa, ya: fit_signed(Xa, ya, lam)
    beta = fit(X, y)
    # leave-one-game-out error in probability units
    errs = []
    for k in range(len(games)):
        tr = gid != k
        b = fit(X[tr], y[tr])
        p0 = games[k]['p0']
        pred = 1 / (1 + np.exp(-(logit(p0) + X[~tr] @ b)))
        obs = 1 / (1 + np.exp(-(logit(p0) + y[~tr])))
        errs.append(np.abs(pred - obs))
    e = np.concatenate(errs)
    out = dict(features=FEATS, beta=dict(zip(FEATS, map(float, beta))), ridge=lam,
               n_games=len(games), n_rows=int(len(y)),
               logo_abs_err_prob=dict(median=float(np.median(e)), p75=float(np.percentile(e, 75)), p90=float(np.percentile(e, 90))),
               games=[dict(mid=g['mid'], p0_blue=round(g['p0'], 3), blue_won=g['blue_won'], minutes=round(g['minutes'], 1), n=len(g['rows'])) for g in games],
               fitted_to='market price 5-65 s after state (not outcomes)', data_dir=D)
    print(json.dumps(out, indent=1))
    json.dump(out, open(os.path.join(os.path.dirname(__file__), 'params', 'lol.json'), 'w'), indent=1)


if __name__ == '__main__':
    main()
