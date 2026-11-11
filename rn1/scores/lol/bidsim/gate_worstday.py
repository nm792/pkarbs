import os, sys, datetime as dt, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bt_many as B, bt_gate as BG, sim_bids as S
os.environ['LOAD_ONLY'] = '1'; B.main()
S.Q = 500; E = 0.10; by = collections.defaultdict(list)
for gid, (G, M, ff, x, fb) in B.GAMES.items():
    r = BG.sim(G, M, 0.025, lambda T, mk, ff=ff: ff(T), E)
    if not r: continue
    d = dt.datetime.fromtimestamp(G['t0'], dt.UTC).date()
    by[d].append((dt.datetime.fromtimestamp(G['t0'], dt.UTC).strftime('%H:%M'), dt.datetime.fromtimestamp(G['t1'], dt.UTC).strftime('%H:%M'), x['title'][5:60], x['game'], round(sum(z['usd'] for z in r)), round(sum(z['pnl'] + z['reb'] for z in r)),
                  'won' if sum(z['pnl'] for z in r) > 0 else 'lost'))
tot = {d: sum(g[5] for g in v) for d, v in by.items()}
for d in sorted(tot, key=tot.get)[:1] + sorted(tot, key=tot.get)[-1:]:
    print(d, 'day P&L', tot[d], 'filled', sum(g[4] for g in by[d]))
    for g in sorted(by[d]): print('  ', *g)
