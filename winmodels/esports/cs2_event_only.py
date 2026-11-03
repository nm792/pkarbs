"""CS2 event-only rule, LoL style (3 Nov). Round scores from the Polymarket sports WS as logged (our receive times),
2 Nov live capture + server logger. After each round change at recv time R (+extra lag), for W s: the side the
jump model says should rise >= minj but whose mid has not yet risen that far gets a bid at mid x 0.975.
Corrected fills (print within 1% below bid). Fair model: rounds first to 13 (12-12 -> 50/50), round p=0.5,
Bo3 maps, map p from pre-match price. Jump = beta x dFair; beta fitted on all events (in-sample, few games)."""
import sys, os, json, gzip, bisect, functools
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C, lag_ws as L
for l in open('/mnt/project-files/rn1/scores/cs2/live/cs2_changes.jsonl'):
    d = json.loads(l); L.CH[d['gameId']].append(d)
@functools.lru_cache(None)
def pmap(a, b, q=0.5):
    if a >= 13 and a - b >= 1 and a > b: return 1.0
    if b >= 13 and b > a: return 0.0
    if a >= 12 and b >= 12: return 0.5
    return q * pmap(a + 1, b, q) + (1 - q) * pmap(a, b + 1, q)
def pser(ma, mb, ra, rb, pm):
    """P(home wins Bo3) at maps ma-mb, rounds ra-rb in current map; later maps with prob pm."""
    if ma >= 2: return 1.0
    if mb >= 2: return 0.0
    w = pmap(ra, rb)
    def rest(x, y):
        if x >= 2: return 1.0
        if y >= 2: return 0.0
        return pm * rest(x + 1, y) + (1 - pm) * rest(x, y + 1)
    return w * rest(ma + 1, mb) + (1 - w) * rest(ma, mb + 1)
def pm_from(p):  # map p giving Bo3 p
    lo, hi = 0.0, 1.0
    for _ in range(40):
        m = (lo + hi) / 2; s = m * m * (3 - 2 * m)
        lo, hi = (m, hi) if s < p else (lo, m)
    return lo
def events(s):
    ch = sorted([x for x in s['ch'] if x.get('score')], key=lambda d: d['recv_ms'])
    M = s['M']; out = []; prev = None; pm = None
    for x in ch:
        cur = L.parse('cs2', x['score'])
        if cur is None: continue
        if cur[2] == 0 and cur[3] == 0 and x['score'].startswith('000'): cur = (cur[0], cur[1], 0, 0)
        R = x['recv_ms'] / 1000
        if pm is None:
            p0 = M.at(R - 120)
            if p0 is None: continue
            ph = p0 if s['o0_home'] else 1 - p0
            pm = pm_from(min(max(ph, 0.02), 0.98))
        if prev is not None and cur != prev:
            f0 = pser(prev[0], prev[1], prev[2], prev[3], pm); f1 = pser(cur[0], cur[1], cur[2], cur[3], pm)
            d0 = (f1 - f0) if s['o0_home'] else (f0 - f1)   # change in token0 fair
            out.append((R, d0))
        prev = cur
    return out
def fit_beta(G):
    xs = []; ys = []
    for e in G:
        s = L.setup('cs2', e)
        if not s: continue
        for R, d0 in events(s):
            a = s['M'].at(R - 30); b = s['M'].at(R + 60)
            if a is None or b is None or abs(d0) < 1e-4: continue
            xs.append(d0); ys.append(b - a)
    xs = np.array(xs); ys = np.array(ys)
    beta = float((xs * ys).sum() / (xs * xs).sum()) if len(xs) else 1.0
    r2 = 1 - ((ys - beta * xs) ** 2).sum() / ((ys - ys.mean()) ** 2).sum() if len(xs) > 2 else None
    return beta, r2, len(xs)
def run(G, beta, lag=0, W=30, minj=0.01, pre=30, d=0.025, max_gap=0.01):
    per = []; games = []
    for e in G:
        s = L.setup('cs2', e)
        if not s: continue
        ev = events(s)
        if not ev: continue
        M = s['M']; reb = C.reb_rate(s['m']); tot = np.zeros(4)
        evt = [(R + lag, d0, M.at(R - pre)) for R, d0 in ev]
        et = [a for a, _, _ in evt]
        for (T, _, ph, sell0, sz) in s['pr']:
            i = bisect.bisect_right(et, T) - 1
            if i < 0 or T > et[i] + W: continue
            _, d0, base = evt[i]; mk = M.at(T - 1)
            if base is None or mk is None or not (0.05 <= mk <= 0.95): continue
            j = beta * d0
            if abs(j) < minj: continue
            if j > 0:   # token0 should rise
                if mk - base >= j: continue
                b = mk * (1 - d); tok = 0
                if not sell0 or ph >= b - 1e-9 or (b - ph) / b > max_gap: continue
            else:
                if base - mk >= -j: continue
                b = (1 - mk) * (1 - d); tok = 1
                if sell0 or (1 - ph) >= b - 1e-9 or (b - (1 - ph)) / b > max_gap: continue
            q = min(sz, C.Q); m60 = M.at(T + 60); m60 = m60 if tok == 0 else 1 - m60
            out = 1.0 if (s['win0'] == (tok == 0)) else 0.0
            tot += [q * b, q * (m60 - b), q * (out - b), q * reb * b * (1 - b)]
        per.append(tot); games.append((e['title'][:45], round(tot[0]), round(tot[1]), round(tot[2] + tot[3])))
    return C.summarize(per), games
if __name__ == '__main__':
    G = L.G['cs2']
    beta, r2, n = fit_beta(G); print(f'beta {beta:.2f} R2 {r2} n_events {n}')
    res = []
    for lag in (0, 2, 5, 10):
        for W in (10, 30):
            s, games = run(G, beta, lag, W)
            res.append(dict(lag=lag, W=W, **s, games=games))
            print(f"lag+{lag} W{W}: games {s['events']} $fill {s['usd']} 1min {s.get('net_1min_pct')}% {s.get('ci_1min')} result {s.get('net_result_pct')}% ${s.get('net_result_usd')} ex-top5 {s.get('ex_top5_result_pct')}%")
            if lag == 0 and W == 30:
                for g in games: print('   ', g)
    json.dump(dict(beta=beta, r2=r2, n=n, res=res), open('out_cs2_event_only.json', 'w'), indent=1, default=str)
