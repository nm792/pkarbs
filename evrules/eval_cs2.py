"""Test the CS2 model on the round changes we logged on 2 Nov 2026
(rn1/scores/cs2/live/cs2_changes.jsonl) against Polymarket BO3 trades.
pre  = median trade price 30-5 s before our receive time (before the
       price usually reacts: signed lag p25 was -3.5 s),
post = median trade price 20-60 s after,
pred = fair_after(score_before, score_after, pre).
Usage: python3 -m evrules.eval_cs2 [dir]
"""
import json, sys, os
import numpy as np
from evrules import cs2

D = sys.argv[1] if len(sys.argv) > 1 else '/mnt/project-files/rn1/scores/cs2/live'
TR = {1761567: 'trades_match_winner_bo3.json', 1761577: 'trades_aur_liquid_bo3.json', 1761578: 'trades_prv_g2_bo3.json'}


def main():
    ch = [json.loads(l) for l in open(f'{D}/cs2_changes.jsonl')]
    rows = []
    for gid, fn in TR.items():
        t = json.load(open(f'{D}/{fn}'))
        px = sorted((x['timestamp'], x['price'] if x['outcomeIndex'] == 0 else 1 - x['price']) for x in t)
        pt = np.array([a for a, _ in px], float); pp = np.array([b for _, b in px])
        seen = set()
        for c in ch:
            if c['gameId'] != gid or not c['prev'] or (c['prev'], c['score']) in seen:
                continue
            seen.add((c['prev'], c['score']))
            R = c['recv_ms'] / 1000
            w0 = (pt >= R - 30) & (pt <= R - 5); w1 = (pt >= R + 20) & (pt <= R + 60)
            if w0.sum() < 1 or w1.sum() < 1:
                continue
            pre = float(np.median(pp[w0])); post = float(np.median(pp[w1]))
            if not 0.03 < pre < 0.97:
                continue
            pred = cs2.fair_after(c['prev'], c['score'], pre)
            if pred is None:
                continue
            rows.append((gid, c['prev'], c['score'], pre, post, pred))
    r = np.array([x[3:] for x in rows])
    mv = r[:, 1] - r[:, 0]; pm = r[:, 2] - r[:, 0]
    sig = np.abs(mv) > 0.01
    by = {}
    for thr in (0.02, 0.04):
        s = np.abs(pm) >= thr
        by[f'pred_ge_{int(thr*100)}c'] = dict(n=int(s.sum()), mean_pred=float(np.mean(np.abs(pm[s]))) if s.any() else None,
                                           mean_realised_in_dir=float(np.mean(np.sign(pm[s]) * mv[s])) if s.any() else None,
                                           dir_hit=float(np.mean(np.sign(pm[s]) == np.sign(mv[s]))) if s.any() else None)
    lg = lambda x: np.log(np.clip(x, 1e-3, 1 - 1e-3) / (1 - np.clip(x, 1e-3, 1 - 1e-3)))
    dz_pred = lg(r[:, 2]) - lg(r[:, 0]); dz_real = lg(r[:, 1]) - lg(r[:, 0])
    shrink = float(np.sum(dz_pred * dz_real) / np.sum(dz_pred ** 2))
    # leave-one-match-out shrink, to test it honestly
    gids = np.array([x[0] for x in rows]); lomo = []
    for g in set(gids):
        tr = gids != g
        k = np.sum(dz_pred[tr] * dz_real[tr]) / np.sum(dz_pred[tr] ** 2)
        pz = lg(r[~tr, 0]) + k * dz_pred[~tr]
        lomo += list(np.abs(1 / (1 + np.exp(-pz)) - r[~tr, 1]))
    out = dict(n=len(r), shrink_logit=shrink, lomo_shrunk_abs_err_median=float(np.median(lomo)), lomo_shrunk_abs_err_mean=float(np.mean(lomo)), model_abs_err_median=float(np.median(np.abs(r[:, 1] - r[:, 2]))),
               naive_abs_err_median=float(np.median(np.abs(mv))),
               model_abs_err_mean=float(np.mean(np.abs(r[:, 1] - r[:, 2]))), naive_abs_err_mean=float(np.mean(np.abs(mv))),
               dir_hit_moves_gt_1c=float(np.mean(np.sign(pm[sig]) == np.sign(mv[sig]))),
               slope_realised_on_pred=float(np.polyfit(pm, mv, 1)[0]), by_pred_size=by,
               rows=[dict(game=g, prev=a, score=b, pre=round(c, 3), post=round(d, 3), pred=round(e, 3)) for g, a, b, c, d, e in rows])
    print(json.dumps({k: v for k, v in out.items() if k != 'rows'}, indent=1))
    json.dump(out, open(os.path.join(os.path.dirname(__file__), 'params', 'cs2_event_test.json'), 'w'), indent=1)


if __name__ == '__main__':
    main()
