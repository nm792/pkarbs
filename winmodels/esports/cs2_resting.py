"""rn1's CS2 pattern on the same 20 matches (4 Nov): bids resting at mid x 0.975 on BOTH sides through play, pulled for
30 s after each round change (pull time = WS receipt + lag), maker only, corrected fills (max_gap 1%), held to result,
plus estimated maker rebate. gate=False = no model filter (plain resting bids); gate=True adds Nick's filter fair-bid>=E
with fair = pre-map price + cumulative model moves (beta-scaled)."""
import sys, numpy as np, json, bisect
import cs2_maps as X, common as C
games = X.build(); games.sort(key=lambda g: g['t0'])
matches = sorted({g['title'] for g in games}, key=lambda t: min(g['t0'] for g in games if g['title'] == t))
half = set(matches[:len(matches) // 2]); tr = [g for g in games if g['title'] in half]
bm = X.fit_beta([g for g in tr if g['kind'] != 'match'])[0]; bM = X.fit_beta([g for g in tr if g['kind'] == 'match'])[0]
def run(gs, lag, gate, E=0.02, Q=100):
    C.Q = Q; per = []
    for g in gs:
        s = g['s']; M = s['M']; ev = g['ev']; t0, t1 = ev[0][0] - 120, ev[-1][0]
        f_start = M.at(t0 - 60); beta = bm if g['kind'] != 'match' else bM
        if f_start is None: continue
        et = [R for R, _ in ev]; cum = np.cumsum([beta * d for _, d in ev])
        def fair(T):
            i = bisect.bisect_right(et, T - max(lag, 0)) - 1
            return min(max(f_start + (cum[i] if i >= 0 else 0), 0.01), 0.99)
        rows = C.sim(s['pr'], M, t0, t1, fair, s['win0'], E, evs=[R + min(lag, 0) for R in et], lag=max(lag, 0),
                     reb=C.reb_rate(s['m']), gate=gate, max_gap=0.01)
        per.append([sum(r[k] for r in rows) for k in ('usd', 'em1', 'pnl', 'reb')])
    return C.summarize(per)
res = []
for Q in (100, 500):
    for gate in (False, True):
        for lag in (0, -20):
            for nm, gs in (('all20', games), ('holdout10', [g for g in games if g['title'] not in half])):
                o = {}
                for kind in ('maps', 'match'):
                    s = run([g for g in gs if (g['kind'] == 'match') == (kind == 'match')], lag, gate, Q=Q); o[kind] = s
                nmat = 20 if nm == 'all20' else 10
                tot = o['maps'].get('net_result_usd', 0) + o['match'].get('net_result_usd', 0)
                res.append(dict(Q=Q, gate=gate, lag=lag, set=nm, per_match=round(tot / nmat), **o))
                print(f"Q{Q} gate={gate} pull_lag{lag:+d} {nm}: per match ${tot / nmat:.0f} | maps fill ${o['maps']['usd']} 1min {o['maps'].get('net_1min_pct')}% result {o['maps'].get('net_result_pct')}% ${o['maps'].get('net_result_usd')} {o['maps'].get('ci_result_usd')} reb ${o['maps'].get('reb_usd')} | match fill ${o['match']['usd']} 1min {o['match'].get('net_1min_pct')}% result {o['match'].get('net_result_pct')}% ${o['match'].get('net_result_usd')} {o['match'].get('ci_result_usd')} reb ${o['match'].get('reb_usd')}", flush=True)
json.dump(res, open('out_cs2_resting.json', 'w'), indent=1, default=str)
