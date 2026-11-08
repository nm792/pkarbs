# Why only ~45% of days are positive: calibration of filtered fills, concentration by series/day.
import os, sys, datetime as dt, collections, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bt_many as B, bt_gate as BG, sim_bids as S
os.environ['LOAD_ONLY'] = '1'; B.main()
S.Q = 500; E = 0.10; R = []
for gid, (G, M, ff, x, fb) in B.GAMES.items():
    for z in BG.sim(G, M, 0.025, lambda T, mk, ff=ff: ff(T), E):
        f0 = ff(z['T']); mk = M.at(z['T'] - S.QDELAY)
        R.append(dict(gid=gid, series=x['match_id'], title=x['title'][5:50], day=dt.datetime.fromtimestamp(z['T'], dt.UTC).date(),
                      usd=z['usd'], price=z['b'], model=f0 if z['tok'] == 0 else 1 - f0, mkt=mk if z['tok'] == 0 else 1 - mk,
                      won=float(G['win0'] == (z['tok'] == 0)), pnl=z['pnl'] + z['reb']))
D = pd.DataFrame(R)
w = lambda g, c: np.average(g[c], weights=g.usd)
print(f"fills {len(D)}, $ {D.usd.sum():,.0f}, games {D.gid.nunique()}, series {D.series.nunique()}, days {D.day.nunique()}")
print(f"$-weighted: price paid {w(D,'price'):.3f}, market {w(D,'mkt'):.3f}, model {w(D,'model'):.3f}, actual win rate {w(D,'won'):.3f}")
D['bin'] = pd.cut(D.model, [0, .2, .3, .4, .5, .6, .8, 1])
print(D.groupby('bin', observed=True).apply(lambda g: pd.Series({'fills': len(g), 'usd': g.usd.sum(), 'games': g.gid.nunique(), 'paid': w(g,'price'), 'mkt': w(g,'mkt'), 'model': w(g,'model'), 'won': w(g,'won'), 'pnl': g.pnl.sum()})).round(3).to_string())
# per-game independent outcome check: one row per game ($-weighted model vs result)
gg = D.groupby('gid').apply(lambda g: pd.Series({'model': w(g,'model'), 'mkt': w(g,'mkt'), 'won': g.won.iloc[0] if g.won.nunique()==1 else w(g,'won'), 'usd': g.usd.sum()}))
print(f"per game (n={len(gg)}): mean model {gg.model.mean():.3f}, mean market {gg.mkt.mean():.3f}, won {gg.won.mean():.3f}")
day = D.groupby('day').pnl.sum().sort_values(); ser = D.groupby('series').pnl.sum().sort_values()
print(f"total {D.pnl.sum():,.0f}; positive days {np.mean(day>0):.0%}; minus top 3 days {day.iloc[:-3].sum():,.0f}; top 3 days {list(day.iloc[-3:].round())}")
print(f"series: {len(ser)}, positive {np.mean(ser>0):.0%}; top 5 series {ser.iloc[-5:].sum():,.0f} = {100*ser.iloc[-5:].sum()/D.pnl.sum():.0f}% of total; minus top 5 {ser.iloc[:-5].sum():,.0f}")
rng = np.random.default_rng(0); sv = ser.values
bs = [rng.choice(sv, len(sv)).sum() for _ in range(5000)]; print(f"series-bootstrap total P&L 90% range {np.percentile(bs,5):,.0f} to {np.percentile(bs,95):,.0f}; P(<0) {np.mean(np.array(bs)<0):.0%}")
