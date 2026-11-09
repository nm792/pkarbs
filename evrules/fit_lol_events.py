"""LoL event-jump model, fitted on price moves around game events.

For a latency strategy the question is: when an event lands, where will
the price go? We fit, across all events in the Worlds games we hold,
  logit(post) - logit(pre) = beta . (state_after - state_before)
with state = blue-minus-red kills, towers, dragons, barons, inhibitors and
gold (k), and a sign constraint (a lead can't hurt). Events within 10 s
are merged into one cluster. pre = median trade price 15-1 s before the
cluster, post = median trade price 20-60 s after its end.
Leave-one-game-out (LOGO) test: does it call the size and direction of
the move better than 'no change'?
Usage: python3 -m evrules.fit_lol_events
"""
import json, gzip, os
import numpy as np
from evrules import fit_lol as F

KEYS = ['kills', 'towers', 'dragons', 'barons', 'inhibs', 'gold']
POS = [True] * 6


def signed_ridge(X, y, lam=0.5):
    keep = list(range(X.shape[1]))
    while True:
        Xa = X[:, keep]
        b = np.linalg.solve(Xa.T @ Xa + lam * np.eye(len(keep)), Xa.T @ y)
        bad = [k for k, v in zip(keep, b) if POS[k] and v < 0]
        if not bad:
            out = np.zeros(X.shape[1]); out[keep] = b; return out
        keep.remove(min(bad, key=lambda k: b[keep.index(k)]))


def game_events(x, g):
    D = F.D
    fr = json.load(gzip.open(f"{D}/out/{x['match_id']}/frames.json.gz"))
    tr = json.load(gzip.open(f"{D}/out/{x['match_id']}/trades.json.gz"))
    o0 = x['outcomes'][0]
    px = sorted((t['timestamp'], (t['price'] if t['outcome'] == o0 else 1 - t['price'])) for t in tr)
    pt = np.array([a for a, _ in px], float); pp = np.array([c for _, c in px])
    if not g['blue_is_outcome0']:
        pp = 1 - pp
    fr = [f for f in fr if f['gameState'] == 'in_game']
    t0 = F.ts(fr[0]['rfc460Timestamp'])
    out = []; prev = None; start = None; s_before = None; last_change = None
    for f in fr:
        s = F.state(f); T = F.ts(f['rfc460Timestamp'])
        changed = prev is not None and any(s[c] != prev[c] for c in KEYS[:5])
        if changed:
            if start is None:
                start, s_before = T, prev
            last_change = T
        if start is not None and T - last_change > 10:
            dx = np.array([s[c] - s_before[c] for c in KEYS], float); dx[5] /= 1000.0
            w0 = (pt >= start - 15) & (pt < start - 1); w1 = (pt >= last_change + 20) & (pt <= last_change + 60)
            if w0.sum() >= 2 and w1.sum() >= 2 and (start - t0) > 180:
                pre = float(np.median(pp[w0])); post = float(np.median(pp[w1]))
                if 0.05 < pre < 0.95:
                    out.append(dict(t=start, tmin=(start - t0) / 60, dx=dx, pre=pre, post=post))
            start = None
        prev = s
    return out


def main():
    D = F.D
    m = json.load(open(f'{D}/matched.json'))
    xs = [x for x in m if os.path.exists(f"{D}/out/{x['match_id']}/frames.json.gz")]
    ev = [game_events(x, F.load_game(x['match_id'], x['outcomes'][0])) for x in xs]
    def XY(es):
        X = np.array([e['dx'] for e in es]); y = np.array([F.logit(e['post']) - F.logit(e['pre']) for e in es])
        return X, y
    allX, ally = XY([e for g in ev for e in g])
    beta = signed_ridge(allX, ally)
    rows = []
    for k in range(len(ev)):
        X, y = XY([e for j, g in enumerate(ev) if j != k for e in g])
        b = signed_ridge(X, y)
        for e in ev[k]:
            pred = 1 / (1 + np.exp(-(F.logit(e['pre']) + e['dx'] @ b)))
            rows.append((e['pre'], e['post'], float(pred)))
    r = np.array(rows)
    mv = r[:, 1] - r[:, 0]; pm = r[:, 2] - r[:, 0]
    sig = np.abs(mv) > 0.01
    res = {}
    for thr in (0.02, 0.04, 0.06):
        sel = np.abs(pm) >= thr
        res[f'pred_ge_{int(thr*100)}c'] = dict(n=int(sel.sum()),
            mean_pred_move=float(np.mean(np.abs(pm[sel]))) if sel.any() else None,
            mean_realised_move_in_pred_dir=float(np.mean(np.sign(pm[sel]) * mv[sel])) if sel.any() else None,
            dir_hit=float(np.mean(np.sign(pm[sel]) == np.sign(mv[sel]))) if sel.any() else None)
    out = dict(beta=dict(zip(KEYS, map(float, beta))), beta_units='logit per unit diff (gold per 1k)',
               n_games=len(ev), n_clusters=int(len(r)),
               logo=dict(model_abs_err_median=float(np.median(np.abs(r[:, 1] - r[:, 2]))),
                         naive_abs_err_median=float(np.median(np.abs(mv))),
                         model_abs_err_mean=float(np.mean(np.abs(r[:, 1] - r[:, 2]))),
                         naive_abs_err_mean=float(np.mean(np.abs(mv))),
                         dir_hit_moves_gt_1c=float(np.mean(np.sign(pm[sig]) == np.sign(mv[sig]))),
                         by_pred_size=res),
               method='pre=median trade 15-1 s before; post=median 20-60 s after; events merged within 10 s')
    print(json.dumps(out, indent=1))
    json.dump(out, open(os.path.join(os.path.dirname(__file__), 'params', 'lol_events.json'), 'w'), indent=1)


if __name__ == '__main__':
    main()
