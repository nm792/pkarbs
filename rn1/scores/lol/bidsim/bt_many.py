"""Resting-bid backtest on many past Polymarket LoL game markets (winmodel/raw/bt/<gid>/).
Variants: mkt (bid = market x (1-d)), gs-min (bid = min(market, game-state model) x (1-d)), each with/without
a 30 s pull after every livestats event. Never above market (asserted). Same fill and P&L rules as sim_bids.py.
Model = winmodel logistic (state + Elo prior), refit WITHOUT every match in the backtest set."""
import os, sys, json, gzip, bisect, math, glob
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); W = os.path.join(HERE, '..', 'winmodel')
sys.path.insert(0, HERE); sys.path.insert(0, W)
import sim_bids as S
from sim_gs import sim
from build import feat, ts, winner
from fit import lin_feats
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss
import re
def norm(s): return re.sub(r'[^a-z0-9]', '', s.lower().replace('esports', '').replace('gaming', '').replace('team', ''))
GAMES = {}
KEYS = ['kills', 'towers', 'dragons', 'barons', 'inhibs']
def st(f):
    b, r = f['blueTeam'], f['redTeam']
    return dict(kills=b['totalKills'] - r['totalKills'], towers=b['towers'] - r['towers'], dragons=len(b['dragons']) - len(r['dragons']),
                barons=b['barons'] - r['barons'], inhibs=b['inhibitors'] - r['inhibitors'])
CHK = {'ok': 0, 'bad': 0}
def load(x, EL, sides):
    od = f"{W}/raw/bt/{x['gid']}"
    fr = json.load(gzip.open(f'{od}/frames.json.gz')); tr = json.load(gzip.open(f'{od}/trades.json.gz'))
    ing = [f for f in fr if f['state'] == 'in_game']; fin = [f for f in fr if f['state'] == 'finished']
    if not fin: fin = [ing[-1]]           # finished frame can be lost by the 1-per-second thinning; last frame is <10 s before the end
    if len(ing) < 300 or len(tr) < 200: return None
    o0 = x['outcomes'][0]
    nb = norm(x['blue_name']); no = [norm(o) for o in x['outcomes']]
    if nb not in no: return None
    pr = []
    for k, t in enumerate(tr):
        is0 = t['outcome'] == o0; ph = t['price'] if is0 else 1 - t['price']
        sell0 = (is0 and t['side'] == 'SELL') or ((not is0) and t['side'] == 'BUY')
        pr.append((t['timestamp'], -k, ph, sell0, t['size']))
    pr.sort()
    evs = []; prev = None; start = None; sb = None; last = None
    for f in ing:
        s = st(f); T = ts(f['t'])
        if prev is not None and any(s[c] != prev[c] for c in KEYS):
            if start is None: start, sb = T, prev
            last = T
        if start is not None and T - last > 10: evs.append((start, last, sb, s)); start = None
        prev = s
    bw = winner(fin[-1])
    if bw is None or (bw == 1) != (norm(x['winner']) == nb): CHK['bad'] += 1; return None
    CHK['ok'] += 1
    G = dict(pr=pr, t0=ts(ing[0]['t']), t1=ts(fin[0]['t']), win0=(x['winner'] == o0), evs=evs, blue0=(nb == no[0]))
    e = EL.get(x['match_id'], {}); sd = sides[x['gid']]
    elo = math.log(10) * (e.get(sd['blue'], 1500) - e.get(sd['red'], 1500)) / 400
    hist = {'blueTeam': [], 'redTeam': []}; X = []; T = []; t0 = G['t0']
    for f in ing[::5]:                                   # model state every ~5 s
        X.append(feat(f, t0, hist)); T.append(ts(f['t']))
        for s in hist: hist[s].append((ts(f['t']), f[s]['barons']))
    return G, T, pd.DataFrame(X).assign(elo=elo)
def main():
    XS = [x for x in json.load(open(f'{W}/raw/pm/pm_game_markets_matched.json')) if os.path.exists(f"{W}/raw/bt/{x['gid']}/trades.json.gz") and x['blue_name']]
    EL = json.load(open(f'{W}/elo_pre.json'))
    sides = {g['id']: g['sides'] for m in json.load(open(f'{W}/raw/matches_since2026-04_names.json')) for g in m.get('games', [])}
    R = pd.read_csv(f'{W}/rows.csv.gz', dtype={'gid': str, 'match': str})
    excl = set(x['match_id'] for x in XS)
    R = R[(R.t >= 0.5) & ~R.match.isin(excl)]
    m = LogisticRegression(C=1.0, max_iter=5000).fit(lin_feats(R), R.y)
    print(f'model: logistic on {R.gid.nunique()} games; {len(excl)} backtest matches excluded')
    games = {}; acc = []
    for x in XS:
        L = load(x, EL, sides)
        if L is None: continue
        G, T, X = L; M = S.Mid(G['pr'])
        pb = m.predict_proba(lin_feats(X))[:, 1]; p0 = pb if G['blue0'] else 1 - pb
        def ff(t, T=T, p0=p0):
            i = bisect.bisect_right(T, t - S.DET_LAG) - 1
            return float(p0[i]) if i >= 0 else None
        def fb(t, ff=ff, M=M):
            v = ff(t); mk = M.at(t - S.QDELAY)
            return None if v is None or mk is None else (v + mk) / 2
        games[x['gid']] = (G, M, ff, x, fb)
        for t in np.arange(G['t0'] + 60, G['t1'], 60):
            mk = M.at(t); fv = ff(t)
            if mk is not None and fv is not None: acc.append((x['gid'], fv, mk, float(G['win0']), (t - G['t0']) / 60))
    print('frame winner vs Polymarket resolution:', CHK)
    global GAMES; GAMES = games
    if os.environ.get('LOAD_ONLY'): return
    A = pd.DataFrame(acc, columns=['gid', 'model', 'mkt', 'y', 'tmin'])
    A['blend'] = (A.model + A.mkt) / 2
    print(f"games {len(games)}; forecast check every 60 s in play ({len(A)} pts): Brier model {brier_score_loss(A.y, A.model):.4f}, "
          f"market {brier_score_loss(A.y, A.mkt):.4f}, 50/50 blend {brier_score_loss(A.y, A.blend):.4f}; mean |model-market| {np.mean(np.abs(A.model - A.mkt)):.3f}")
    A.to_csv(os.path.join(HERE, 'out_bt_forecast.csv.gz'), index=False)
    res = []; pergame = {}
    print(f"{'variant':16}{'d':>6}{'fills':>7}{'$fill':>10}{'entry%':>8}{'m1%':>7}{'e+m1%':>7}{'1-5m%':>7}{'rest%':>7}{'pnl%':>7}{'reb%':>6}{'games+':>8}")
    for d in [0.01, 0.025, 0.05]:
        for name, use, cancel in [('mkt', False, None), ('gs-min', True, None), ('mkt+pull30', False, 3), ('gs-min+pull30', True, 3), ('blend-min+pull30', 'blend', 3)]:
            allr = []; pos = 0; ng = 0; per = {}
            for gid, (G, M, ff, x, fb) in games.items():
                r = sim(G, M, d, (fb if use == 'blend' else ff) if use else None, cancel); allr += r
                if r:
                    a = S.agg(r); ng += 1; pos += (a['entry'] + a['m1']) > 0
                    per[gid] = dict(usd=a['usd'], em1=a['entry'] + a['m1'], pnl=a['pnl'], reb=a['reb'])
            pergame[(name, d)] = per
            a = S.agg(allr); u = a['usd'] or 1
            res.append(dict(variant=name, d=d, games_with_fills=ng, games_em1_pos=pos, **{k: round(v, 1) for k, v in a.items()}))
            print(f"{name:16}{d:>6}{a['n']:>7}{a['usd']:>10.0f}{100*a['entry']/u:>8.2f}{100*a['m1']/u:>7.2f}{100*(a['entry']+a['m1'])/u:>7.2f}"
                  f"{100*a['m5']/u:>7.2f}{100*a['rest']/u:>7.2f}{100*a['pnl']/u:>7.2f}{100*a['reb']/u:>6.2f}{pos:>5}/{ng}")
    # bootstrap over games: e+m1 % and to-result % for key variants
    rng = np.random.default_rng(0); boot = {}
    for key in [('mkt+pull30', 0.025), ('gs-min+pull30', 0.025), ('mkt', 0.025), ('gs-min', 0.025)]:
        per = pergame[key]; ids = list(per)
        u = np.array([per[i]['usd'] for i in ids]); e = np.array([per[i]['em1'] for i in ids]); p = np.array([per[i]['pnl'] + per[i]['reb'] for i in ids])
        bs = [(e[s].sum() / u[s].sum(), p[s].sum() / u[s].sum()) for s in (rng.integers(0, len(ids), len(ids)) for _ in range(2000))]
        bs = np.array(bs) * 100
        boot[f'{key[0]} d={key[1]}'] = dict(em1_pct_90ci=list(np.percentile(bs[:, 0], [5, 95]).round(2)), net_to_result_pct_90ci=list(np.percentile(bs[:, 1], [5, 95]).round(2)))
    a_, b_ = pergame[('mkt+pull30', 0.025)], pergame[('gs-min+pull30', 0.025)]
    ids = [i for i in a_ if i in b_]
    def rate(per, s, k): return sum(per[ids[j]][k] for j in s) / max(sum(per[ids[j]]['usd'] for j in s), 1e-9)
    diffs = []
    for _ in range(2000):
        s_ = rng.integers(0, len(ids), len(ids))
        diffs.append([100 * (rate(b_, s_, 'em1') - rate(a_, s_, 'em1')), 100 * (rate(b_, s_, 'pnl') - rate(a_, s_, 'pnl'))])
    diffs = np.array(diffs)
    boot['paired gs-min+pull30 minus mkt+pull30, d=0.025'] = dict(em1_pp_90ci=list(np.percentile(diffs[:, 0], [5, 95]).round(2)), pnl_pp_90ci=list(np.percentile(diffs[:, 1], [5, 95]).round(2)))
    print(json.dumps(boot))
    json.dump(dict(n_games=len(games), forecast=dict(n=len(A), brier_model=brier_score_loss(A.y, A.model), brier_mkt=brier_score_loss(A.y, A.mkt),
              brier_blend=brier_score_loss(A.y, A.blend)), runs=res, bootstrap=boot), open(os.path.join(HERE, 'out_bt_many.json'), 'w'), indent=1)
if __name__ == '__main__':
    main()
