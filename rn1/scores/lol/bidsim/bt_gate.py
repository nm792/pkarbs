"""Nick's rule (3 Nov 05:03Z): bid = market x (1 - d), never other prices. Place the bid on a token ONLY when
fair - bid >= E (fair = game-state model, or average of model and market). 30 s pull after events.
Same fills/P&L as sim_bids.py. Games: all loaded by bt_many.load (frame winner == Polymarket winner)."""
import os, sys, json, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import bt_many as B, sim_bids as S
def sim(G, M, d, fair, E, cancel=3):
    fills = []
    for (T, _, ph, sell0, sz) in G['pr']:
        if not (G['t0'] <= T <= G['t1']): continue
        mk = M.at(T - S.QDELAY)
        if mk is None or not (0.05 <= mk <= 0.95): continue
        if cancel is not None and any(st + cancel <= T < st + 30 for (st, _, _, _) in G['evs']): continue
        b0, b1 = mk * (1 - d), (1 - mk) * (1 - d)
        f0 = fair(T, mk) if fair else None
        if fair and f0 is None: continue
        if sell0 and ph < b0 - 1e-9 and (f0 is None or f0 - b0 >= E): fills.append((T, 0, b0, min(sz, S.Q)))
        if (not sell0) and (1 - ph) < b1 - 1e-9 and (f0 is None or (1 - f0) - b1 >= E): fills.append((T, 1, b1, min(sz, S.Q)))
    rows = []
    for (T, tok, b, q) in fills:
        rt, m60 = M.at(T), M.at(T + 60)
        if tok == 1: rt, m60 = 1 - rt, 1 - m60
        out = 1.0 if (G['win0'] == (tok == 0)) else 0.0
        rows.append(dict(usd=q * b, em1=q * (m60 - b), pnl=q * (out - b), reb=q * S.REB * b * (1 - b)))
    return rows
def main():
    import io, contextlib
    os.environ['LOAD_ONLY'] = '1'; B.main()
    rng = np.random.default_rng(0); out = []
    hdr = f"{'fair':6}{'E%':>5}{'games':>7}{'fills':>7}{'$filled':>10}{'1min+reb%':>11}{'90% range':>16}{'result+reb%':>12}{'90% range':>18}"
    print(hdr)
    G_ = B.GAMES
    for d in [0.025]:
        cfgs = [('none', None)] + [(fn, E) for fn in ('model', 'blend') for E in (0, 0.01, 0.02, 0.03, 0.05, 0.07, 0.10)]
        for fn, E in cfgs:
            per = []
            for gid, (G, M, ff, x, fb) in G_.items():
                fair = None if fn == 'none' else ((lambda T, mk, ff=ff: ff(T)) if fn == 'model' else (lambda T, mk, ff=ff: None if ff(T) is None else (ff(T) + mk) / 2))
                r = sim(G, M, d, fair, E or 0)
                if r: per.append([sum(z[k] for z in r) for k in ('usd', 'em1', 'pnl', 'reb')])
            P = np.array(per); u = P[:, 0].sum()
            em = 100 * (P[:, 1] + P[:, 3]).sum() / u; pn = 100 * (P[:, 2] + P[:, 3]).sum() / u
            bs = []
            for _ in range(2000):
                s = rng.integers(0, len(P), len(P)); Q = P[s]; uu = Q[:, 0].sum()
                bs.append((100 * (Q[:, 1] + Q[:, 3]).sum() / uu, 100 * (Q[:, 2] + Q[:, 3]).sum() / uu))
            bs = np.array(bs); c1 = np.percentile(bs[:, 0], [5, 95]); c2 = np.percentile(bs[:, 1], [5, 95])
            out.append(dict(fair=fn, E=E, d=d, games=len(P), usd=round(u), net_1min_pct=round(em, 2), ci1=list(c1.round(2)), net_result_pct=round(pn, 2), ci2=list(c2.round(2)), pnl_usd=round((P[:, 2] + P[:, 3]).sum())))
            print(f"{fn:6}{'' if E is None else round(100*E):>5}{len(P):>7}{'':>7}{u:>10.0f}{em:>11.2f}{f'[{c1[0]:.1f}, {c1[1]:.1f}]':>16}{pn:>12.2f}{f'[{c2[0]:.1f}, {c2[1]:.1f}]':>18}")
    json.dump(out, open(os.path.join(HERE, 'out_gate.json'), 'w'), indent=1)
if __name__ == '__main__':
    main()
