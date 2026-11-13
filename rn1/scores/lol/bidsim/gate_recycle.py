# Capital recycling for the E-filter rule (model alone, E=10%, d=2.5%, 500-share cap, 30 s pull).
# Exit A: hold to result (capital locked fill -> game end; markets are per-GAME "Game N Winner").
# Exit B(N): from fill+N min rest a maker ask at the trade-derived mid; filled by the first later
# buy-direction print at >= ask (never crossing); else hold to result. Rebates on entry only (est).
import os, sys, bisect, datetime as dt, collections, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bt_many as B, bt_gate as BG, sim_bids as S
os.environ['LOAD_ONLY'] = '1'; B.main()
S.Q = 500; E = 0.10
fills = []
for gid, (G, M, ff, x, fb) in B.GAMES.items():
    for z in BG.sim(G, M, 0.025, lambda T, mk, ff=ff: ff(T), E): fills.append((G, M, z))
def exit_(G, M, z, N):
    out = 1.0 if (G['win0'] == (z['tok'] == 0)) else 0.0
    if N is None: return G['t1'], out
    ts0 = z['T'] + 60 * N
    if ts0 >= G['t1']: return G['t1'], out
    m = M.at(ts0); ask = m if z['tok'] == 0 else 1 - m
    i = bisect.bisect_left([p[0] for p in G['pr']], ts0)
    for (T, _, ph, sell0, sz) in G['pr'][i:]:
        if T > G['t1']: break
        px = ph if z['tok'] == 0 else 1 - ph
        if (not sell0 if z['tok'] == 0 else sell0) and px >= ask - 1e-9: return T, ask   # buyer lifts our ask
    return G['t1'], out
for N in (None, 1, 5, 15):
    ev = []; pnl = 0; locks = []; days = set(); early = 0
    for G, M, z in fills:
        t2, px = exit_(G, M, z, N)
        early += t2 < G['t1']
        ev += [(z['T'], z['usd']), (t2, -z['usd'])]; pnl += z['q'] * (px - z['b']) + z['reb']
        locks.append((t2 - z['T']) / 60); days.add(dt.datetime.utcfromtimestamp(z['T']).date())
    ev.sort(); cur = peak = 0
    for t, du in ev: cur += du; peak = max(peak, cur)
    usd = sum(z['usd'] for _, _, z in fills); nd = len(days)
    w = np.array([z['usd'] for _, _, z in fills]); L = np.array(locks)
    print(f"{'hold' if N is None else f'exit {N}m':8} fills {len(fills)}, exited early {early/len(fills):.0%}; $-weighted lock {np.average(L, weights=w):.1f} min; "
          f"peak ${peak:,.0f}; P&L ${pnl:,.0f} ({100*pnl/usd:.1f}% of ${usd:,.0f} filled); per trading day ${pnl/nd:,.0f} on {nd} days; "
          f"turnover {usd/peak:.0f}x peak; return/peak/day {100*pnl/peak/nd:.1f}%")
