# E-filter rule: per-game $ filled and net % vs the per-print share cap Q (sim_bids.Q).
import os, sys, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bt_many as B, bt_gate as BG, sim_bids as S
os.environ['LOAD_ONLY'] = '1'; B.main()
print(f"{'fair':6}{'E':>4}{'cap(sh)':>9}{'games':>6}{'med$':>7}{'p90$':>7}{'max$':>7}{'total$':>9}{'1min+reb%':>10}{'result+reb%':>12}")
for fn, E in [('model', 0.10), ('blend', 0.10), ('model', 0.05), ('blend', 0.05)]:
    for Q in (100, 250, 500, 1e9):
        S.Q = Q; per = []
        for gid, (G, M, ff, x, fb) in B.GAMES.items():
            fair = (lambda T, mk, ff=ff: ff(T)) if fn == 'model' else (lambda T, mk, ff=ff: None if ff(T) is None else (ff(T) + mk) / 2)
            r = BG.sim(G, M, 0.025, fair, E)
            per.append([sum(z[k] for z in r) for k in ('usd', 'em1', 'pnl', 'reb')])
        P = np.array(per); u = P[:, 0].sum()
        print(f"{fn:6}{int(E*100):>3}%{('all' if Q > 1e8 else int(Q)):>9}{len(P):>6}{np.median(P[:,0]):>7.0f}{np.percentile(P[:,0],90):>7.0f}{P[:,0].max():>7.0f}{u:>9.0f}"
              f"{100*(P[:,1]+P[:,3]).sum()/u:>10.2f}{100*(P[:,2]+P[:,3]).sum()/u:>12.2f}")
