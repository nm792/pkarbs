"""Event-only rule (Nick 05:32Z): no bids in quiet periods. After an event cluster starts (seen LAG s later),
for WIN s, bid market x 0.975 on a token ONLY if the event-jump model predicts our token gains >= 1c
(pj) and the market has not yet given it that (rm < pj: moved the wrong way or not far enough).
Jump model = ev-rules event betas from the 6 Worlds games (not the game-state model). Holdout = games not in
locked_insample_gids.json. Fills/P&L as sim_bids.py, 500-share cap; rebate estimated."""
import os, sys, math, json, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
os.environ['LOAD_ONLY'] = '1'
import veto_timing as V
B, S = V.B, V.S; beta = V.beta; d = 0.025
LOCK = set(json.load(open(os.path.join(HERE, 'locked_insample_gids.json'))))
def run(G, M, LAG, WIN, minj=0.01):
    W = []
    for (st, en, sb, sa) in G['evs']:
        anc = M.at(st - 1)
        if anc is None or not (0.03 < anc < 0.97): continue
        z = sum(beta[k] * (sa[k] - sb[k]) for k in ['kills', 'towers', 'dragons', 'barons', 'inhibs'])
        a = anc if G['blue0'] else 1 - anc
        jb = 1 / (1 + math.exp(-(math.log(a / (1 - a)) + z))) - a
        W.append((st, jb if G['blue0'] else -jb, anc))
    rows = []
    for (T, _, ph, sell0, sz) in G['pr']:
        if not (G['t0'] <= T <= G['t1']): continue
        act = [w for w in W if w[0] + LAG <= T < w[0] + WIN]
        if not act: continue
        st, j0, anc = act[-1]
        mk = M.at(T - S.QDELAY)
        if mk is None or not (0.05 <= mk <= 0.95): continue
        tok = 0 if sell0 else 1
        pj = j0 if tok == 0 else -j0; rm = (mk - anc) if tok == 0 else (anc - mk)
        if pj < minj or rm >= pj: continue
        b = mk * (1 - d) if tok == 0 else (1 - mk) * (1 - d)
        px = ph if tok == 0 else 1 - ph
        if px >= b - 1e-9: continue
        if MAXGAP == MAXGAP and (b - px) / b > MAXGAP: continue
        q = min(sz, S.Q); rt, m60 = M.at(T), M.at(T + 60)
        if tok == 1: rt, m60 = 1 - rt, 1 - m60
        out = 1.0 if (G['win0'] == (tok == 0)) else 0.0
        rows.append((q * b, q * (m60 - b), q * (out - b), q * S.REB * b * (1 - b)))
    return rows
MAXGAP = float(__import__('os').environ.get('FILL_MAX_GAP', 'nan'))   # corrected fill rule (fillcheck note 3 Nov): skip prints > MAXGAP below our bid
rng = np.random.default_rng(0)
def report(name, sel, LAG, WIN):
    per = {}
    for gid, (G, M, ff, x, fb) in B.GAMES.items():
        if not sel(gid): continue
        r = run(G, M, LAG, WIN)
        if r: s = per.setdefault(x['match_id'], np.zeros(4)); s += np.array(r).sum(0)
    if not per: print(name, 'no fills'); return
    P = np.array(list(per.values())); u = P[:, 0].sum(); res = P[:, 2] + P[:, 3]; m1 = P[:, 1] + P[:, 3]
    bs = np.array([[res[i].sum(), m1[i].sum()] for i in (rng.integers(0, len(res), len(res)) for _ in range(3000))])
    print(f"{name:34}{len(P):>5}{u:>9.0f}{100*m1.sum()/u:>7.2f}{f'[{100*np.percentile(bs[:,1],5)/u:.1f},{100*np.percentile(bs[:,1],95)/u:.1f}]':>14}"
          f"{100*res.sum()/u:>7.2f}{res.sum():>8.0f}{f'[{np.percentile(bs[:,0],5):.0f},{np.percentile(bs[:,0],95):.0f}]':>18}{np.sort(res)[:-5].sum():>9.0f}")
print(f"{'set / lag / window':34}{'ser':>5}{'$fill':>9}{'1min%':>7}{'1min 90%':>14}{'res%':>7}{'res$':>8}{'res$ 90% (series)':>18}{'ex top5':>9}")
for setname, sel in [('in-sample', lambda g: g in LOCK), ('HOLDOUT', lambda g: g not in LOCK), ('all', lambda g: True)]:
    for LAG, WIN in [(2, 10), (2, 30), (2, 60), (5, 30), (10, 30), (10, 60), (20, 60)]:
        report(f'{setname} lag {LAG}s win {WIN}s', sel, LAG, WIN)
print('games loaded', len(B.GAMES), 'holdout', sum(g not in LOCK for g in B.GAMES))
