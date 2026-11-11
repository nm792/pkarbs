"""Resting-bid backtest with the independent game-state win model (winmodel/).
bid0 = min(market, model fair) x (1-d), bid1 = min(1-market, 1-model fair) x (1-d): never above market.
Optional pull: no bids from event+CANCEL to event+30 s. Model reads the frame state DET_LAG s before T.
Model is refit WITHOUT the 6 backtest matches (no leakage). Same fill/P&L rules as sim_bids.py."""
import os, sys, json, gzip, bisect, math
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, '..', 'winmodel'))
import sim_bids as S
from build import feat, ts
from fit import lin_feats
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss
D = S.D; DET_LAG = S.DET_LAG
def slim(f):
    o = {'t': f['rfc460Timestamp'], 'state': f['gameState']}
    for s in ('blueTeam', 'redTeam'):
        T = f[s]; o[s] = {k: T[k] for k in ('totalGold', 'inhibitors', 'towers', 'barons', 'totalKills', 'dragons')}
        o[s]['p'] = [[p['totalGold'], p['level'], p['kills'], p['deaths'], p['creepScore']] for p in T['participants']]
    return o
def model(exclude):
    R = pd.read_csv(os.path.join(HERE, '..', 'winmodel', 'rows.csv.gz'), dtype={'gid': str, 'match': str})
    R = R[(R.t >= 0.5) & ~R.match.isin(exclude)]
    m = LogisticRegression(C=1.0, max_iter=5000).fit(lin_feats(R), R.y)
    return m, R.gid.nunique()
def gs_series(mid, m):
    fr = [slim(f) for f in json.load(gzip.open(f'{D}/out/{mid}/frames.json.gz')) if f['gameState'] == 'in_game']
    t0 = ts(fr[0]['t']); hist = {'blueTeam': [], 'redTeam': []}; X = []; T = []
    for f in fr:
        X.append(feat(f, t0, hist)); T.append(ts(f['t']))
        for s in hist: hist[s].append((ts(f['t']), f[s]['barons']))
    W = os.path.join(HERE, '..', 'winmodel')
    EL = json.load(open(f'{W}/elo_pre.json')); MM = {x['match_id']: x for x in json.load(open(f'{W}/raw/matches.json'))}
    g1 = [g for g in MM[mid]['games'] if g['number'] == 1][0]['sides']; e = EL[mid]
    elo = math.log(10) * (e[g1['blue']] - e[g1['red']]) / 400
    pb = m.predict_proba(lin_feats(pd.DataFrame(X).assign(elo=elo)))[:, 1]
    return T, pb
def sim(G, M, d, fairf=None, cancel=None):
    fills = []
    for (T, _, ph, sell0, sz) in G['pr']:
        if not (G['t0'] <= T <= G['t1']): continue
        mk = M.at(T - S.QDELAY)
        if mk is None or not (0.05 <= mk <= 0.95): continue
        if cancel is not None and any(st + cancel <= T < st + 30 for (st, _, _, _) in G['evs']): continue
        r0, r1 = mk, 1 - mk
        if fairf is not None:
            fv = fairf(T)
            if fv is not None: r0, r1 = min(r0, fv), min(r1, 1 - fv)
        b0, b1 = r0 * (1 - d), r1 * (1 - d)
        assert b0 <= mk * (1 - d) + 1e-9 and b1 <= (1 - mk) * (1 - d) + 1e-9
        if sell0 and ph < b0 - 1e-9: fills.append((T, 0, b0, min(sz, S.Q)))
        if (not sell0) and (1 - ph) < b1 - 1e-9: fills.append((T, 1, b1, min(sz, S.Q)))
    rows = []
    for (T, tok, b, q) in fills:
        rt = M.at(T); m60 = M.at(T + 60); m300 = M.at(T + 300)
        if tok == 1: rt, m60, m300 = 1 - rt, 1 - m60, 1 - m300
        out = 1.0 if (G['win0'] == (tok == 0)) else 0.0
        rows.append(dict(q=q, usd=q * b, entry=q * (rt - b), m1=q * (m60 - rt), m5=q * (m300 - m60), rest=q * (out - m300),
                         pnl=q * (out - b), reb=q * S.REB * b * (1 - b)))
    return rows
def main():
    xs = json.load(open(f'{D}/matched.json'))
    m, ng = model([x['match_id'] for x in xs])
    print(f'model: logistic on {ng} games, the 6 backtest matches excluded')
    games = {}; acc = []
    for x in xs:
        G = S.load(x); M = S.Mid(G['pr']); T, pb = gs_series(x['match_id'], m)
        p0 = pb if G['blue0'] else 1 - pb
        def ff(t, T=T, p0=p0):
            i = bisect.bisect_right(T, t - DET_LAG) - 1
            return float(p0[i]) if i >= 0 else None
        games[x['match_id']] = (G, M, ff, '-'.join(x['teams']))
        # model vs market as forecasters, every 60 s in play
        for t in np.arange(G['t0'] + 60, G['t1'], 60):
            mk = M.at(t); fv = ff(t)
            if mk is not None and fv is not None: acc.append((x['match_id'], fv, mk, float(G['win0']), (t - G['t0']) / 60))
    A = pd.DataFrame(acc, columns=['mid', 'model', 'mkt', 'y', 'tmin'])
    print(f"forecast check, every 60 s in play ({len(A)} points, 6 games): Brier model {brier_score_loss(A.y, A.model):.4f}, "
          f"market {brier_score_loss(A.y, A.mkt):.4f}; mean |model-market| {np.mean(np.abs(A.model - A.mkt)):.3f}")
    res = []
    print(f"{'variant':16}{'d':>6}{'fills':>7}{'$fill':>9}{'entry%':>8}{'m1%':>7}{'e+m1%':>7}{'1-5m%':>7}{'rest%':>7}{'reb%':>6}  per-game e+m1 %")
    for d in [0.01, 0.02, 0.025, 0.03, 0.05]:
        for name, use, cancel in [('mkt', False, None), ('gs-min', True, None), ('mkt+pull30', False, 3), ('gs-min+pull30', True, 3)]:
            per = []; allr = []
            for mid, (G, M, ff, nm) in games.items():
                r = sim(G, M, d, ff if use else None, cancel); allr += r
                a = S.agg(r) if r else None
                per.append(round(100 * (a['entry'] + a['m1']) / a['usd'], 1) if a and a['usd'] else None)
            a = S.agg(allr); u = a['usd'] or 1
            res.append(dict(variant=name, d=d, **{k: round(v, 1) for k, v in a.items()}, per_game_e_m1_pct=per))
            print(f"{name:16}{d:>6}{a['n']:>7}{a['usd']:>9.0f}{100*a['entry']/u:>8.2f}{100*a['m1']/u:>7.2f}{100*(a['entry']+a['m1'])/u:>7.2f}"
                  f"{100*a['m5']/u:>7.2f}{100*a['rest']/u:>7.2f}{100*a['reb']/u:>6.2f}  {per}")
    json.dump(dict(forecast=dict(n=len(A), brier_model=brier_score_loss(A.y, A.model), brier_mkt=brier_score_loss(A.y, A.mkt)), runs=res),
              open(os.path.join(HERE, 'out_gs.json'), 'w'), indent=1)
if __name__ == '__main__':
    main()
