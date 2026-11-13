"""Trade-only tennis check on historical matches (5 Nov 2026).

No point feed exists for past matches here (api.sofascore.com answers 403), so events come from the trades themselves:
  * mid = pair mid from v2 prints (common.Mid). Scan every 2 s for a move |mid(t+20) - mid(t)| >= MOVE (default 2c);
    keep the biggest, suppress others within 40 s (one event per point-sized move).
  * onset = first print in [t, t+30] that has covered 20% of the move a=mid(t) -> b=mid(t+30) (same definition as
    point_delay.py). Side = direction of the move. That is ORACLE side choice (the real rule uses the point model,
    corr 0.74 / beta 1.0 vs the move), so returns here are an upper bound; fill amounts are what matter.
  * fills: TRADE-BASED ESTIMATE, past books don't exist. A print that sells the rising side at most 1% below our bid
    (bid = mid x 0.975, mid seen 1 s earlier) fills us at our bid, min(size, 500). Queue ignored (optimistic).
    Bid lives from onset+delay for W s, only while the mid has moved < 50% of the move, mid in [0.05, 0.95].
  * hold to result; rebate = rebateRate x feeRate x p(1-p).
Mode CAL=1 runs the same on the 99 Cito-timed matches (4-5 Nov) to compare with the point-model result (NOTE 4c)."""
import sys, os, json, gzip, bisect, collections, datetime as dt
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import common as C
from common import RAW
MOVE = float(os.environ.get('MOVE', 0.02)); CAL = os.environ.get('CAL') == '1'
def ts(s): return dt.datetime.fromisoformat(s.replace('Z', '+00:00')).timestamp()

def load():
    if CAL:
        MT = json.load(open(f'{RAW}/tennis/point/match_cito_pm.json'))
        G = {m['conditionId']: (e, m) for e in json.load(gzip.open(f'{RAW}/tennis/point/gamma_tennis_2026-11-02_on.json.gz')) for m in e['markets'] if m.get('conditionId')}
        conds = {v['cond'] for v in MT.values()}; td = f'{RAW}/tennis/point/trades'
        items = [(G[c][0], G[c][1]) for c in conds if c in G]
    else:
        items = [(e, e['markets'][0]) for f in sorted(os.listdir(f'{RAW}/tennis/hist')) if f.startswith('gamma_')
                 for e in json.load(gzip.open(f'{RAW}/tennis/hist/{f}'))]
        td = f'{RAW}/tennis/hist/trades'
    games = []; why = collections.Counter()
    for e, m in items:
        fn = f"{td}/{m['conditionId']}.json.gz"
        if not os.path.exists(fn): why['no trades'] += 1; continue
        pr = C.prints(json.load(gzip.open(fn)))
        if len(pr) < 30: why['few prints'] += 1; continue
        op = json.loads(m.get('outcomePrices') or '[]')
        if sorted(op) != ['0', '1']: why['unresolved'] += 1; continue
        fs = m.get('feeSchedule') or {}; reb = float(fs.get('rebateRate') or 0) * float(fs.get('rate') or 0)
        t0 = ts(e['startTime']); pr = [p for p in pr if p[0] >= t0 - 600]
        if len(pr) < 30: why['few in-play prints'] += 1; continue
        games.append(dict(slug=e['slug'], pr=pr, M=C.Mid(pr), win0=op[0] == '1', reb=reb, t0=t0, t1=pr[-1][0]))
    return games, why

def events(g):
    pr, M = g['pr'], g['M']; tt = [p[0] for p in pr]; c = []
    for t in range(int(max(g['t0'], pr[0][0])), int(pr[-1][0]) - 20, 2):
        a, b = M.at(t), M.at(t + 20)
        if a is None or b is None or not (0.03 < a < 0.97): continue
        if abs(b - a) >= MOVE: c.append((abs(b - a), t))
    c.sort(reverse=True); taken = []; E = []
    for _, t in c:
        if any(abs(t - u) < 40 for u in taken): continue
        taken.append(t); a, b = M.at(t), M.at(t + 30)
        if b is None or abs(b - a) < MOVE / 2: continue
        for p in pr[bisect.bisect_left(tt, t):bisect.bisect_right(tt, t + 30)]:
            if (p[2] - a) / (b - a) >= 0.2:
                mo = M.at(p[0] - 2)
                if mo is not None and 0.03 < mo < 0.97: E.append(dict(on=p[0], pj=b - a, m0=mo))
                break
    E.sort(key=lambda e: e['on']); return E

def run(g, lag, W, Q=500, caught=0.5, max_gap=0.01, d=0.025):
    tot = np.zeros(4); pr, M, E = g['pr'], g['M'], g['E']; et = [e['on'] for e in E]
    for (T, _, ph, sell0, sz) in pr:
        i = bisect.bisect_right(et, T - lag) - 1
        if i < 0 or T > et[i] + lag + W: continue
        e = E[i]; tok = 0 if e['pj'] > 0 else 1
        mk = M.at(T - C.QDELAY)
        if mk is None or not (0.05 <= mk <= 0.95): continue
        moved = (mk - e['m0']) if tok == 0 else (e['m0'] - mk)
        if moved >= caught * abs(e['pj']): continue
        if tok == 0:
            b = mk * (1 - d)
            if not sell0 or ph >= b - 1e-9 or (b - ph) / b > max_gap: continue
        else:
            b = (1 - mk) * (1 - d)
            if sell0 or (1 - ph) >= b - 1e-9 or (b - (1 - ph)) / b > max_gap: continue
        q = min(sz, Q); m60 = M.at(T + 60); m60 = m60 if tok == 0 else 1 - m60
        out = 1.0 if (g['win0'] == (tok == 0)) else 0.0
        tot += [q * b, q * (m60 - b), q * (out - b), q * g['reb'] * b * (1 - b)]
    return tot

if __name__ == '__main__':
    games, why = load()
    for g in games: g['E'] = events(g)
    n = len(games); ne = sum(len(g['E']) for g in games)
    days = (max(g['t0'] for g in games) - min(g['t0'] for g in games)) / 86400 + 1
    print('matches', n, dict(why), 'moves', ne, f'({ne / max(1, n):.0f}/match)', f'{n / days:.0f} usable matches/day', flush=True)
    out = dict(cal=CAL, move=MOVE, matches=n, why=dict(why), moves=ne, matches_per_day=round(n / days, 1), curve=[])
    for W in (30, 120):
        for lag in (-5, 0, 2, 5, 10, 20, 30):
            P = [run(g, lag, W) for g in games]; s = C.summarize(P); s = {k: ([float(x) for x in v] if isinstance(v, list) else v) for k, v in s.items()}
            nf = sum(1 for p in P if p[0] > 0)
            r = dict(W=W, delay=lag, matches_filled=nf, filled_per_match=round(s['usd'] / n, 1), result_per_match=round(s['net_result_usd'] / n, 2),
                     result_per_match_ci=[round(x / n, 2) for x in s['ci_result_usd']], per_day=round(s['net_result_usd'] / n * n / days), **s)
            out['curve'].append(r)
            print(f"W{W:>3} d{lag:>3}s: {nf:>4} matches filled, ${r['filled_per_match']:6.1f} filled/match, 1min {s['net_1min_pct']}% {s['ci_1min']}, "
                  f"result {s['net_result_pct']}% {s['ci_result']} = ${r['result_per_match']}/match {r['result_per_match_ci']}, ex-top5 {s['ex_top5_result_pct']}%", flush=True)
    fn = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"out_hist_{'cal' if CAL else 'oct'}_move{int(MOVE * 100)}.json")
    json.dump(out, open(fn, 'w'), indent=1)
