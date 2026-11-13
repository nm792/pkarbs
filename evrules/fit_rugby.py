"""Fit sigma for the rugby union model from ESPN scoreboards.

ESPN linescores give cumulative points at 20', 40', 60', 80'. For each
game we get four 20-minute margin changes d1..d4. Under the model
  Var(d_i) = sigma^2/4 + Var(mu)/16,   Cov(d_i, d_j) = Var(mu)/16,
so sigma^2 = 4 * (mean variance - mean covariance). Team strength drops
out. Then a calibration check at 40' and 60' with mu = average home edge
(no market info), on the later half of the games (out of sample).
Usage: python3 -m evrules.fit_rugby <dir of scoreboard json>
"""
import json, glob, sys, os, itertools
import numpy as np
from evrules import rugby

UNION = {'270557': 'URC', '242041': 'Super Rugby Pacific', '267979': 'Premiership', '270559': 'Top 14',
         '271937': 'Champions Cup', '180659': 'Six Nations', '289234': 'Test matches'}


def games(D):
    seen = {}
    for f in sorted(glob.glob(f'{D}/sb_*.json')):
        lg = os.path.basename(f).split('_')[1]
        for e in json.load(open(f)).get('events', []):
            if e['status']['type']['name'] != 'STATUS_FINAL': continue
            c = e['competitions'][0]
            try:
                h = [x for x in c['competitors'] if x['homeAway'] == 'home'][0]
                a = [x for x in c['competitors'] if x['homeAway'] == 'away'][0]
                cp = []
                for t in (h, a):
                    ls = {int(x['period']): x['value'] for x in t['linescores']}
                    cp.append([0.0, ls[20], ls[1], ls[60], ls[2]])
                fh, fa = float(h['score']), float(a['score'])
            except (KeyError, IndexError, ValueError):
                continue
            ok = all(all(x[i] <= x[i + 1] for i in range(4)) for x in cp) and cp[0][4] == fh and cp[1][4] == fa
            ok = ok and not (fh + fa > 10 and cp[0][3] + cp[1][3] == 0)   # missing checkpoints
            if ok:
                seen[e['id']] = (e['date'], lg, np.array(cp[0]) - np.array(cp[1]))
    return sorted(seen.values(), key=lambda x: x[0])


def main():
    D = sys.argv[1]
    g = games(D)
    M = np.array([x[2] for x in g]); d = np.diff(M, axis=1)            # n x 4
    half = len(g) // 2
    def sig(dd):
        C = np.cov(dd.T)
        v = np.mean(np.diag(C)); cv = np.mean([C[i, j] for i, j in itertools.combinations(range(4), 2)])
        return float(np.sqrt(4 * (v - cv))), float(np.sqrt(max(16 * cv, 0)))
    s_all, sdmu = sig(d); s_tr, _ = sig(d[:half])
    mu0 = float(np.mean(M[:half, 4]))
    final = M[:, 4]
    draw_obs = float(np.mean(final == 0))
    cal = {}
    for mins_played, col in ((40, 2), (60, 3)):
        p = np.array([rugby.probs(m, 80 - mins_played, mu0, s_tr)[0] for m in M[half:, col]])
        y = (final[half:] > 0).astype(float)
        q = np.quantile(p, np.linspace(0, 1, 6)); rows = []
        for lo, hi in zip(q[:-1], q[1:]):
            s = (p >= lo) & (p <= hi)
            rows.append((round(float(p[s].mean()), 3), round(float(y[s].mean()), 3), int(s.sum())))
        cal[f'{mins_played}min'] = dict(brier=float(np.mean((p - y) ** 2)), calibration_pred_obs_n=rows)
    pdraw = float(np.mean([rugby.probs(0, 80, mu0, s_all)[1]]))
    out = dict(source='ESPN site.api scoreboards, 20-min checkpoints', leagues=sorted({UNION.get(x[1], x[1]) for x in g}),
               n_games=len(g), dates=[g[0][0], g[-1][0]], sigma_full=s_all, sigma_full_train_half=s_tr,
               sd_strength_mu=sdmu, home_edge_mean=float(np.mean(final)), draw_rate_obs=draw_obs,
               draw_rate_model_even_game=pdraw, out_of_sample_calibration=cal)
    print(json.dumps(out, indent=1))
    json.dump(out, open(os.path.join(os.path.dirname(__file__), 'params', 'rugby.json'), 'w'), indent=1)


if __name__ == '__main__':
    main()
