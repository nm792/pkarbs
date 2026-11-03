"""CS2 / Dota 2 exploratory event-only sim (2-3 Nov, all logged games, no train/test split: too few events).
After each score change seen in our logger (recv time + extra lag), for W s, bid market x 0.975 only on the scorer's
token in the match-winner market. Corrected fills (print within max_gap of bid). Rebate = 0.15 x 0.05 x p(1-p)."""
import sys, os, json, gzip, bisect
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import common as C, lag_ws as L
def run(sp, W, lag, max_gap=0.01, d=0.025):
    per = []
    for e in L.G[sp]:
        s = L.setup(sp, e)
        if not s: continue
        ev = []; prev = None
        for x in s['ch']:
            cur = L.parse(sp, x['score'])
            if cur is None: continue
            if prev is not None and cur != prev:
                dh = 10 * ((cur[0] - prev[0]) - (cur[1] - prev[1])) + ((cur[2] - prev[2]) - (cur[3] - prev[3]))
                if dh: ev.append((x['recv_ms'] / 1000 + lag, 0 if (dh > 0) == s['o0_home'] else 1))
            prev = cur
        et = [a for a, _ in ev]; M = s['M']; tot = np.zeros(4); reb = C.reb_rate(s['m'])
        for (T, _, ph, sell0, sz) in s['pr']:
            i = bisect.bisect_right(et, T) - 1
            if i < 0 or T > et[i] + W: continue
            tok = ev[i][1]; mk = M.at(T - 1)
            if mk is None or not (0.05 <= mk <= 0.95): continue
            if tok == 0:
                b = mk * (1 - d)
                if not sell0 or ph >= b - 1e-9 or (b - ph) / b > max_gap: continue
            else:
                b = (1 - mk) * (1 - d)
                if sell0 or (1 - ph) >= b - 1e-9 or (b - (1 - ph)) / b > max_gap: continue
            q = min(sz, C.Q); m60 = M.at(T + 60); m60 = m60 if tok == 0 else 1 - m60
            out = 1.0 if (s['win0'] == (tok == 0)) else 0.0
            tot += [q * b, q * (m60 - b), q * (out - b), q * reb * b * (1 - b)]
        if ev: per.append(tot)
    return C.summarize(per)
if __name__ == '__main__':
    res = []
    for sp in ('cs2', 'dota2'):
        for lag in (0, 5):
            for W in (10, 20, 30):
                for mg in (0.01, 0.03):
                    s = run(sp, W, lag, mg); res.append(dict(sport=sp, lag=lag, W=W, max_gap=mg, **s))
                    print(f"{sp} extra-lag{lag} W{W} gap{mg}: games {s['events']} $fill {s['usd']} 1min {s.get('net_1min_pct')}% {s.get('ci_1min')} result {s.get('net_result_pct')}% {s.get('ci_result')} ex-top5 {s.get('ex_top5_result_pct')}%")
    json.dump(res, open('out_event_sim.json', 'w'), indent=1)
