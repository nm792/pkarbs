"""Event-only rule restricted to what the free Polymarket sports WS shows: kill counts only, sampled every ~20 s.
Measured 4 Nov (TES-IG g4, 13 kills): WS shows a kill 2.6-20 s after the frame time (median 12 s) = ~2 s + wait for
the next 20 s tick. Here: an event counts only if kills changed; jump uses the kills beta only; it becomes visible at
st + 2 s + U(0,20) s (random per event, seeded) or a fixed lag; bid window WIN s from when it becomes visible.
Otherwise identical to event_only.py (bid market x 0.975, side the jump model says should gain >=1c but hasn't,
fills only within FILL_MAX_GAP of bid, 500-share cap). Usage: FILL_MAX_GAP=0.01 python3 kills_only.py"""
import os, sys, math, json, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
os.environ['LOAD_ONLY'] = '1'
import veto_timing as V
B, S = V.B, V.S; beta = V.beta; d = 0.025
LOCK = set(json.load(open(os.path.join(HERE, 'locked_insample_gids.json'))))
MAXGAP = float(os.environ.get('FILL_MAX_GAP', 'nan'))
def run(G, M, lagf, WIN, gid, minj=0.01):
    r = np.random.default_rng(int(gid) % 2**32); W = []
    for (st, en, sb, sa) in G['evs']:
        dk = sa['kills'] - sb['kills']
        if dk == 0: continue
        anc = M.at(st - 1)
        if anc is None or not (0.03 < anc < 0.97): continue
        a = anc if G['blue0'] else 1 - anc
        jb = 1 / (1 + math.exp(-(math.log(a / (1 - a)) + beta['kills'] * dk))) - a
        W.append((st + lagf(r), jb if G['blue0'] else -jb, anc))
    rows = []
    for (T, _, ph, sell0, sz) in G['pr']:
        if not (G['t0'] <= T <= G['t1']): continue
        act = [w for w in W if w[0] <= T < w[0] + WIN]
        if not act: continue
        _, j0, anc = act[-1]
        mk = M.at(T - S.QDELAY)
        if mk is None or not (0.05 <= mk <= 0.95): continue
        tok = 0 if sell0 else 1
        pj = j0 if tok == 0 else -j0; rm = (mk - anc) if tok == 0 else (anc - mk)
        if pj < minj or rm >= pj: continue
        b = mk * (1 - d) if tok == 0 else (1 - mk) * (1 - d)
        px = ph if tok == 0 else 1 - ph
        if px >= b - 1e-9: continue
        if MAXGAP == MAXGAP and (b - px) / b > MAXGAP: continue
        q = min(sz, S.Q); m60 = M.at(T + 60)
        if tok == 1: m60 = 1 - m60
        out = 1.0 if (G['win0'] == (tok == 0)) else 0.0
        rows.append((q * b, q * (m60 - b), q * (out - b), q * S.REB * b * (1 - b)))
    return rows
rng = np.random.default_rng(0)
def report(name, sel, lagf, WIN):
    per = {}
    for gid, (G, M, ff, x, fb) in B.GAMES.items():
        if not sel(gid): continue
        rr = run(G, M, lagf, WIN, gid)
        if rr: s = per.setdefault(x['match_id'], np.zeros(4)); s += np.array(rr).sum(0)
    if not per: print(name, 'no fills'); return
    P = np.array(list(per.values())); u = P[:, 0].sum(); res = P[:, 2] + P[:, 3]; m1 = P[:, 1] + P[:, 3]
    bs = np.array([[res[i].sum(), m1[i].sum()] for i in (rng.integers(0, len(res), len(res)) for _ in range(3000))])
    print(f"{name:34}{len(P):>5}{u:>9.0f}{100*m1.sum()/u:>7.2f}{f'[{100*np.percentile(bs[:,1],5)/u:.1f},{100*np.percentile(bs[:,1],95)/u:.1f}]':>14}"
          f"{100*res.sum()/u:>7.2f}{res.sum():>8.0f}{f'[{np.percentile(bs[:,0],5):.0f},{np.percentile(bs[:,0],95):.0f}]':>18}", flush=True)
if __name__ == '__main__':
    print(f"{'set / lag / window':34}{'ser':>5}{'$fill':>9}{'1min%':>7}{'1min 90%':>14}{'res%':>7}{'res$':>8}{'res$ 90% (series)':>18}")
    lags = [('2s', lambda r: 2.0), ('WS 2+U(0,20)s', lambda r: 2 + r.uniform(0, 20)), ('20s', lambda r: 20.0), ('55s feed', lambda r: 55.0)]
    for setname, sel in [('HOLDOUT', lambda g: g not in LOCK), ('all', lambda g: True)]:
        for ln, lf in lags:
            report(f'{setname} kills lag {ln} win 30', sel, lf, 30)
    print('games loaded', len(B.GAMES), 'holdout', sum(g not in LOCK for g in B.GAMES))
