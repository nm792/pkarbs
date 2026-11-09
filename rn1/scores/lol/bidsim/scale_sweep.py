"""Scale levers for the event-only rule (corrected fills, FILL_MAX_GAP default 0.01), per game, holdout vs all.
Levers: window after event, per-print share cap, min predicted gain (minj), and a per-series loss limit
(stop bidding for the rest of a series once its realised to-result P&L < -L; games processed in time order)."""
import os, sys, json, numpy as np, collections
os.environ.setdefault('FILL_MAX_GAP', '0.01'); os.environ['LOAD_ONLY'] = '1'
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import event_only as EO
B, S = EO.B, EO.S
LOCK = EO.LOCK
def run_cfg(sel, LAG=2, WIN=30, Q=500, minj=0.01, L=None):
    S.Q = Q; ser = collections.defaultdict(list)
    for gid, (G, M, ff, x, fb) in B.GAMES.items():
        if sel(gid): ser[x['match_id']].append((G['t0'], gid, G, M))
    per_game = []
    for mid, gs in ser.items():
        cum = 0.0; stopped = False
        for _, gid, G, M in sorted(gs):
            if stopped: per_game.append((0, 0, 0)); continue
            r = EO.run(G, M, LAG, WIN, minj)
            a = np.array(r).sum(0) if r else np.zeros(4)
            per_game.append((a[0], a[1] + a[3], a[2] + a[3])); cum += a[2] + a[3]
            if L is not None and cum < -L: stopped = True
    P = np.array(per_game); u = P[:, 0].sum()
    return len(P), u / len(P), 100 * P[:, 1].sum() / max(u, 1), P[:, 2].sum() / len(P), np.percentile(P[:, 2], 5), P[:, 2].min()
cfgs = [('base: win 30 s, cap 500, minj 1c', {}),
        ('win 60 s', dict(WIN=60)), ('win 120 s', dict(WIN=120)),
        ('cap 1000', dict(Q=1000)), ('cap 2000', dict(Q=2000)), ('no cap (within 1% of bid)', dict(Q=1e9)),
        ('minj 0.5c', dict(minj=0.005)), ('minj 2c', dict(minj=0.02)),
        ('win 60 + no cap', dict(WIN=60, Q=1e9)),
        ('win 60 + no cap + loss limit $500/series', dict(WIN=60, Q=1e9, L=500)),
        ('win 60 + no cap + loss limit $1000/series', dict(WIN=60, Q=1e9, L=1000))]
print(f"{'setting':44}{'set':>8}{'games':>6}{'$fill/g':>9}{'1min%':>7}{'res$/g':>8}{'p5 res$/g':>10}{'worst g':>9}")
for name, kw in cfgs:
    for sn, sel in [('holdout', lambda g: g not in LOCK), ('all', lambda g: True)]:
        n, f, e, p, p5, w = run_cfg(sel, **kw)
        print(f"{name:44}{sn:>8}{n:>6}{f:>9.0f}{e:>7.2f}{p:>8.1f}{p5:>10.0f}{w:>9.0f}")
print('games', len(B.GAMES), 'holdout', sum(g not in LOCK for g in B.GAMES))
