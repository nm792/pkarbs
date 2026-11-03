"""Nick 05:21Z. Base: bid = market x 0.975 on both tokens, 30 s pull after events unless noted.
(a) veto: skip a token's bid only when model fair < bid - E (model says the price is too high by > E).
(b) timing: ev-rules event-jump model (betas fit on the 6 Worlds games, applied out of sample) predicts the
    jump sign of each event cluster; for 30 s pull ONLY the hurt side's bid, keep the favoured side (vs pulling both).
Series-bootstrap 90% range, result with top 5 series removed. Fills/P&L as sim_bids.py, 500-share cap."""
import os, sys, math, json, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import bt_many as B, sim_bids as S
os.environ['LOAD_ONLY'] = '1'; B.main()
S.Q = 500; d = 0.025
xs, betas = S.beta_logo()
beta = {k: float(np.mean([b[k] for b in betas.values()])) for k in S.KEYS}
print('event betas (logit per unit, mean of LOGO fits):', {k: round(v, 3) for k, v in beta.items()})
def run(G, M, ff, veto=None, timing=False, pull=True):
    W = []
    for (st, en, sb, sa) in G['evs']:
        z = sum(beta[k] * (sa[k] - sb[k]) for k in ['kills', 'towers', 'dragons', 'barons', 'inhibs'])
        anc = M.at(st - 1)
        if anc is None: W.append((st, 0)); continue
        a = anc if G['blue0'] else 1 - anc; a = min(max(a, .02), .98)
        jb = 1 / (1 + math.exp(-(math.log(a / (1 - a)) + z))) - a          # predicted move of blue
        j0 = jb if G['blue0'] else -jb
        W.append((st, 1 if j0 >= 0.04 else (-1 if j0 <= -0.04 else 0)))
    rows = []
    for (T, _, ph, sell0, sz) in G['pr']:
        if not (G['t0'] <= T <= G['t1']): continue
        mk = M.at(T - S.QDELAY)
        if mk is None or not (0.05 <= mk <= 0.95): continue
        on0 = on1 = True
        if pull:
            act = [s for (st, s) in W if st + 3 <= T < st + 30]
            if act:
                if timing and all(s != 0 for s in act) and len(set(act)) == 1:
                    on0, on1 = (True, False) if act[0] > 0 else (False, True)
                else: on0 = on1 = False
        b0, b1 = mk * (1 - d), (1 - mk) * (1 - d)
        if veto is not None:
            f0 = ff(T)
            if f0 is not None:
                if f0 < b0 - veto: on0 = False
                if (1 - f0) < b1 - veto: on1 = False
        tok = None
        if sell0 and on0 and ph < b0 - 1e-9: tok, b = 0, b0
        if (not sell0) and on1 and (1 - ph) < b1 - 1e-9: tok, b = 1, b1
        if tok is None: continue
        q = min(sz, S.Q); rt, m60 = M.at(T), M.at(T + 60)
        if tok == 1: rt, m60 = 1 - rt, 1 - m60
        out = 1.0 if (G['win0'] == (tok == 0)) else 0.0
        rows.append((q * b, q * (m60 - b), q * (out - b), q * S.REB * b * (1 - b)))
    return rows
cfgs = [('no filter, pull30', {}), ('no filter, no pull', dict(pull=False))] + \
       [(f'veto E={int(E*100)}%, pull30', dict(veto=E)) for E in (0, 0.02, 0.05, 0.10)] + \
       [('timing: pull hurt side only', dict(timing=True)), ('timing + veto E=5%', dict(timing=True, veto=0.05))]
rng = np.random.default_rng(0); out = []
print(f"{'variant':30}{'games':>6}{'$filled':>10}{'1min%':>7}{'res%':>7}{'res$':>9}{'res$ 90% (series)':>22}{'res$ ex top5 ser':>18}")
for name, kw in cfgs:
    per = {}
    for gid, (G, M, ff, x, fb) in B.GAMES.items():
        r = run(G, M, ff, **kw)
        if r:
            a = np.array(r).sum(0); s = per.setdefault(x['match_id'], np.zeros(4)); s += a
    P = np.array(list(per.values())); u = P[:, 0].sum(); res = P[:, 2] + P[:, 3]
    bs = [res[rng.integers(0, len(res), len(res))].sum() for _ in range(3000)]
    ex5 = np.sort(res)[:-5].sum()
    out.append(dict(variant=name, series=len(P), usd=u, m1=100 * (P[:, 1] + P[:, 3]).sum() / u, res=100 * res.sum() / u, res_usd=res.sum(), ci=list(np.percentile(bs, [5, 95])), ex_top5=ex5))
    print(f"{name:30}{len(P):>6}{u:>10.0f}{100*(P[:,1]+P[:,3]).sum()/u:>7.2f}{100*res.sum()/u:>7.2f}{res.sum():>9.0f}{f'[{np.percentile(bs,5):.0f}, {np.percentile(bs,95):.0f}]':>22}{ex5:>18.0f}")
print('games', len(B.GAMES))
json.dump(out, open(os.path.join(HERE, 'out_veto_timing.json'), 'w'), indent=1, default=float)
