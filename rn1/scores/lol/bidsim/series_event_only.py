"""Event-only rule on SERIES ("Match Winner") markets. For each in-game event, the event-jump model gives the
predicted move of the GAME price (anchor = game mid 1 s before the event); it is mapped to the series price via
dS/dp = W(a+1,b) - W(a,b+1), with W = chance of winning the series from score (a,b) when each later game is won with
prob q, and q solved so the formula matches the series mid at the anchor. Same rule as event_only.py: bid series
market x 0.975 only on the side predicted to gain >= 1c and not yet given it; corrected fills (max gap 1%)."""
import os, sys, json, gzip, math, re, numpy as np
os.environ['LOAD_ONLY'] = '1'; os.environ.setdefault('FILL_MAX_GAP', '0.01')
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import bt_many as B, sim_bids as S
B.main()
xs, betas = S.beta_logo(); beta = {k: float(np.mean([b[k] for b in betas.values()])) for k in S.KEYS}
W_ = os.path.join(HERE, '..', 'winmodel'); LOCK = set(json.load(open(os.path.join(HERE, 'locked_insample_gids.json'))))
GAP = float(os.environ['FILL_MAX_GAP']); d = 0.025
def norm(s): return re.sub(r'[^a-z0-9]', '', s.lower().replace('esports', '').replace('gaming', '').replace('team', ''))
from functools import lru_cache
def Wf(a, b, n, q):
    @lru_cache(None)
    def w(a, b):
        if a >= n: return 1.0
        if b >= n: return 0.0
        return q * w(a + 1, b) + (1 - q) * w(a, b + 1)
    return w(a, b)
def solve_q(S0, p, a, b, n):
    lo, hi = 0.01, 0.99
    for _ in range(30):
        q = (lo + hi) / 2; s = p * Wf(a + 1, b, n, q) + (1 - p) * Wf(a, b + 1, n, q)
        lo, hi = (q, hi) if s < S0 else (lo, q)
    return q
def series_rows(j, games, Q, LAG=2, WIN=30, minj=0.01):
    tr = json.load(gzip.open(f"{W_}/raw/series/{j['match_id']}_trades.json.gz"))
    if len(tr) < 100: return None
    o0 = j['outcomes'][0]; A = norm(o0)
    pr = sorted((t['timestamp'], -k, t['price'] if t['outcome'] == o0 else 1 - t['price'],
                 (t['outcome'] == o0 and t['side'] == 'SELL') or (t['outcome'] != o0 and t['side'] == 'BUY'), t['size']) for k, t in enumerate(tr))
    M = S.Mid(pr); winA = j['prices'][0] == '1'
    n = 3 if 'BO5' in j['title'] else (2 if 'BO3' in j['title'] else 1)
    a = b = 0; rows = []; ptimes = [p[0] for p in pr]
    import bisect
    for (G, GM, x) in games:
        gA0 = norm(x['outcomes'][0]) == A          # game token0 is team A?
        Wn = []
        for (st, en, sb, sa) in G['evs']:
            anc = GM.at(st - 1); s0 = M.at(st - 1)
            if anc is None or s0 is None or not (0.03 < anc < 0.97) or not (0.03 < s0 < 0.97): continue
            z = sum(beta[k] * (sa[k] - sb[k]) for k in ['kills', 'towers', 'dragons', 'barons', 'inhibs'])
            ab = anc if G['blue0'] else 1 - anc
            jb = 1 / (1 + math.exp(-(math.log(ab / (1 - ab)) + z))) - ab
            j0 = jb if G['blue0'] else -jb                     # game token0 move
            jA = j0 if gA0 else -j0; pA = anc if gA0 else 1 - anc
            q = solve_q(s0, pA, a, b, n)
            dS = (Wf(a + 1, b, n, q) - Wf(a, b + 1, n, q)) * jA
            Wn.append((st, dS, s0))
        i0 = bisect.bisect_left(ptimes, G['t0']); 
        for (T, _, ph, sell0, sz) in pr[i0:]:
            if T > G['t1']: break
            act = [w for w in Wn if w[0] + LAG <= T < w[0] + WIN]
            if not act: continue
            st, dS, s0 = act[-1]; mk = M.at(T - S.QDELAY)
            if mk is None or not (0.05 <= mk <= 0.95): continue
            tok = 0 if sell0 else 1
            pj = dS if tok == 0 else -dS; rm = (mk - s0) if tok == 0 else (s0 - mk)
            if pj < minj or rm >= pj: continue
            bb = mk * (1 - d) if tok == 0 else (1 - mk) * (1 - d); px = ph if tok == 0 else 1 - ph
            if px >= bb - 1e-9 or (bb - px) / bb > GAP: continue
            q_ = min(sz, Q); rt, m60 = M.at(T), M.at(T + 60)
            if tok == 1: rt, m60 = 1 - rt, 1 - m60
            out = 1.0 if (winA == (tok == 0)) else 0.0
            rows.append((q_ * bb, q_ * (m60 - bb), q_ * (out - bb), q_ * S.REB * bb * (1 - bb)))
        # update series score with this game's result
        gwA = (G['win0'] == gA0)
        a, b = (a + 1, b) if gwA else (a, b + 1)
    return rows
J = json.load(open(f'{W_}/raw/series/series_markets.json'))
bym = {}
for gid, (G, GM, ff, x, fb) in B.GAMES.items(): bym.setdefault(x['match_id'], []).append((G['t0'], gid, G, GM, x))
rng = np.random.default_rng(0)
print(f"{'set':8}{'cap':>6}{'series':>7}{'games':>6}{'$fill/game':>11}{'1min%':>7}{'res$/game':>10}{'res$ 90% (series)':>20}")
for Q in (500, 2000):
    for sn, sel in [('in', lambda g: g in LOCK), ('HOLDOUT', lambda g: g not in LOCK), ('all', lambda g: True)]:
        per = []; ng = 0
        for j in J:
            gs = sorted(bym.get(j['match_id'], []), key=lambda z: z[0])
            if not gs or not os.path.exists(f"{W_}/raw/series/{j['match_id']}_trades.json.gz"): continue
            if not sel(gs[0][1]): continue
            # need every game of the series loaded to keep the score right
            nb = sum(1 for x in json.load(open(f'{W_}/raw/pm/pm_game_markets_matched.json')) if x['match_id'] == j['match_id']) if False else None
            r = series_rows(j, [(G, GM, x) for _, _, G, GM, x in gs], Q)
            if r is None: continue
            ng += len(gs); per.append(np.array(r).sum(0) if r else np.zeros(4))
        P = np.array(per); u = P[:, 0].sum(); res = P[:, 2] + P[:, 3]
        bs = [res[rng.integers(0, len(res), len(res))].sum() for _ in range(3000)]
        print(f"{sn:8}{Q:>6}{len(P):>7}{ng:>6}{u/ng:>11.0f}{100*(P[:,1]+P[:,3]).sum()/u:>7.2f}{res.sum()/ng:>10.1f}{f'[{np.percentile(bs,5)/ng:.0f}, {np.percentile(bs,95)/ng:.0f}]/g':>20}")
