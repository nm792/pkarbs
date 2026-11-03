# Capital tied up over time for the E-filter rule (model alone, E=10%, d=2.5%, 500-share cap, 30 s pull).
# Each fill locks its cost from fill time until the market's game ends (t1, last frame; resolution assumed then).
import os, sys, datetime as dt, collections, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bt_many as B, bt_gate as BG, sim_bids as S
os.environ['LOAD_ONLY'] = '1'; B.main()
S.Q = 500; E = 0.10
ev = []; pnl = 0; daily = collections.defaultdict(float); games_day = collections.defaultdict(int)
for gid, (G, M, ff, x, fb) in B.GAMES.items():
    orig = BG.sim
    rows = []
    # rerun the rule but keep fill times
    for (T, _, ph, sell0, sz) in G['pr']:
        pass
    r = BG.sim(G, M, 0.025, lambda T, mk, ff=ff: ff(T), E)
    u = sum(z['usd'] for z in r); p = sum(z['pnl'] + z['reb'] for z in r)
    if u == 0: continue
    # fill times: approximate cost locked from first in-play second (upper bound on overlap) -> use t0
    ev.append((G['t0'], u)); ev.append((G['t1'], -u)); pnl += p
    day = dt.datetime.utcfromtimestamp(G['t0']).date(); daily[day] += p; games_day[day] += 1
ev.sort(); cur = 0; peak = 0; peak_t = None; daypeak = collections.defaultdict(float)
for t, du in ev:
    cur += du
    d = dt.datetime.utcfromtimestamp(t).date(); daypeak[d] = max(daypeak[d], cur)
    if cur > peak: peak, peak_t = cur, t
days = sorted(daily); span = (days[-1] - days[0]).days + 1
dp = np.array([daypeak[d] for d in days])
print(f"games with fills {len(ev)//2} on {len(days)} days ({days[0]} to {days[-1]}, span {span} d)")
print(f"peak capital at once {peak:.0f} at {dt.datetime.utcfromtimestamp(peak_t)}; per-trading-day peak median {np.median(dp):.0f}, p90 {np.percentile(dp,90):.0f}")
print(f"total P&L to result incl rebate {pnl:.0f}; return on peak capital {100*pnl/peak:.1f}% over {span} d; per trading day mean P&L {pnl/len(days):.0f}")
dv = np.array([daily[d] for d in days]); print(f"daily P&L: positive days {np.mean(dv>0):.0%}, worst day {dv.min():.0f}, best {dv.max():.0f}")
