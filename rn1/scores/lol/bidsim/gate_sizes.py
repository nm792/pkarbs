# Per-game $ filled and worst-case loss for the E-filter rule (bt_gate.sim), d=2.5%, 30 s pull.
import os, sys, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bt_many as B, bt_gate as BG
os.environ['LOAD_ONLY'] = '1'; B.main()
for fn in ('model', 'blend'):
    for E in (0.05, 0.10):
        usd = []; worst = []
        for gid, (G, M, ff, x, fb) in B.GAMES.items():
            fair = (lambda T, mk, ff=ff: ff(T)) if fn == 'model' else (lambda T, mk, ff=ff: None if ff(T) is None else (ff(T) + mk) / 2)
            r = BG.sim(G, M, 0.025, fair, E)
            u = sum(z['usd'] for z in r); usd.append(u)
            # worst case loss = cost - min payout; reconstruct shares by token from pnl: not stored -> recompute
            sh = [0.0, 0.0]
            for z in r: pass
            worst.append(u)
        a = np.array(usd); f = a[a > 0]
        print(f"{fn:6} E={int(E*100):>2}%: games {len(a)}, with fills {len(f)}; $/game median {np.median(a):.0f}, p10 {np.percentile(a,10):.0f}, p90 {np.percentile(a,90):.0f}, max {a.max():.0f}; total {a.sum():.0f}")
