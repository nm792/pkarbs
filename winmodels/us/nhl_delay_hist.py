"""NHL event-only rule: delay curve at TRUE event time on past games (5 Nov 2026, thread "Time NHL feed against the price").

Data (s1_hist_nhl.py): ESPN NHL summaries (goal wallclock, period, clock, score) + Polymarket moneyline trades
(data-api v2), 2025-26 (every 2nd day) and 2026-27 to 4 Nov (every day).
Fair model (Poisson): remaining regulation goals ~ Poisson(lam_team * remaining fraction); total rate TOT goals per
game (league average from the ESPN games); the home share s solved per game from the Polymarket moneyline mid 60 s
before puck drop. Tied after regulation -> OT/shootout, home wins 0.5 + 0.25*(2s-1). In OT (period > 3) tied ->
same OT value. Empty-net scoring late is ignored (jump beta, fitted on train, scales the model jump).
Step 1: price half-move time vs ESPN goal wallclock (is wallclock true event time?).
EVT=onset (default): true event time = price onset (first print with >= 20% of the move toward the model's direction,
within -120..+90 s of wallclock), as for NFL. EVT=wall: ESPN wallclock.
Rule: for W s after the event (seen `delay` s late), bid market x 0.975 (never at/above ask) only on the token the jump
model says should rise >= MINJ and that has not yet moved CAUGHT x that. Fill on taker prints that sell into our side
at or below our bid (within 1%); first in queue (optimistic). Held to result. Rebates per market feeSchedule.
Lock W/MINJ/CAUGHT on TRAIN (2025-26 before 1 Jan 2026) at delay 0; report TEST (Jan-Apr 2026) and NOW (Oct-Nov 2026).
Usage: EVT=onset python3 nhl_delay_hist.py"""
import sys, os, json, math, gzip, bisect, itertools, re, collections, datetime as dt
import numpy as np
from scipy.stats import poisson
from scipy.optimize import brentq
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))
import common as C
from espn import NPER, PLEN
EVT = os.environ.get('EVT', 'onset')
RAW = C.RAW; H = f'{RAW}/us_nhl_hist'
def ts(s): return dt.datetime.fromisoformat(s.replace('Z', '+00:00')).timestamp()
def nz(s): return re.sub(r'[^a-z0-9]', '', (s or '').lower())
SPLIT1 = ts('2026-01-01T00:00:00Z'); SPLIT2 = ts('2026-07-01T00:00:00Z')
G = json.load(gzip.open(f'{H}/gamma_events.json.gz')); MT = json.load(open(f'{H}/match.json'))
ES = {}
for e in G:
    fn = f"{RAW}/us_hist/nhl/{MT[e['slug']]['espn_id']}.json.gz"
    if os.path.exists(fn): ES[e['slug']] = json.load(gzip.open(fn))
fin = [(int(g['comp']['home']['score']), int(g['comp']['away']['score'])) for g in ES.values() if g.get('completed')]
regtot = []
for g in ES.values():
    reg = [r for r in g['tl'] if r[1] <= 3]
    if reg: regtot.append(reg[-1][3] + reg[-1][4])
TOT = float(np.mean(regtot)); print('games', len(ES), 'regulation goals/game', round(TOT, 2), flush=True)
K = np.arange(0, 15)
def p_home(h, a, rem, s):
    """P(home wins) given score, remaining regulation fraction, home share s of scoring."""
    pot = 0.5 + 0.25 * (2 * s - 1)
    if rem <= 0:
        return 1.0 if h > a else 0.0 if a > h else pot
    ph = poisson.pmf(K, TOT * s * rem); pa = poisson.pmf(K, TOT * (1 - s) * rem)
    J = np.outer(ph, pa); d = (h + K)[:, None] - (a + K)[None, :]
    return float(J[d > 0].sum() + pot * J[d == 0].sum())
def frac(per, clk):
    if per > 3: return 1.0
    return min(((per - 1) * 1200 + (1200 - clk)) / 3600, 1.0)
games = []; why = collections.Counter()
for e in G:
    g = ES.get(e['slug'])
    if not g or not g.get('completed') or len(g['tl']) < 20: why['no summary'] += 1; continue
    tm = {x['ordering']: nz(x['name']) for x in e['teams']}
    ml = [m for m in e['markets'] if m.get('sportsMarketType') == 'moneyline' and m.get('closed')]
    if not ml: why['no moneyline'] += 1; continue
    m = ml[0]; oc = json.loads(m['outcomes']); op = json.loads(m['outcomePrices'])
    if sorted(op) != ['0', '1']: why['unresolved'] += 1; continue
    o0 = nz(oc[0]); home0 = (o0 == tm['home'] or o0 in tm['home'] or tm['home'] in o0)
    if not home0 and not (o0 == tm['away'] or o0 in tm['away'] or tm['away'] in o0): why['outcome name'] += 1; continue
    fn = f"{H}/trades/{m['conditionId']}.json.gz"
    if not os.path.exists(fn): why['no trades file'] += 1; continue
    pr = C.prints(json.load(gzip.open(fn)))
    if len(pr) < 50: why['<50 prints'] += 1; continue
    if not home0: pr = pr  # token0 = away; handled by p0()
    fh, fa = int(g['comp']['home']['score']), int(g['comp']['away']['score'])
    win0 = op[0] == '1'
    if (fh > fa) != (win0 == home0): why['resolution mismatch'] += 1; continue
    tl = sorted((ts(r[0]), r[1], r[2], r[3], r[4]) for r in g['tl'])
    M = C.Mid(pr); t0 = tl[0][0]
    p_pre = M.at(t0 - 60)
    if p_pre is None or not (0.08 < p_pre < 0.92): why['no pre-game price'] += 1; continue
    ph_pre = p_pre if home0 else 1 - p_pre
    try: s = brentq(lambda x: p_home(0, 0, 1, x) - ph_pre, 0.05, 0.95)
    except ValueError: why['solve'] += 1; continue
    def p0(h, a, per, clk, s=s, home0=home0):
        p = p_home(h, a, 1 - frac(per, clk), s); return p if home0 else 1 - p
    ev = []
    for k in range(1, len(tl)):
        if tl[k][3:] != tl[k - 1][3:]:
            r = tl[k]; prev = tl[k - 1]
            ev.append([r[0], p0(r[3], r[4], r[1], r[2]) - p0(prev[3], prev[4], r[1], r[2])])
    games.append(dict(slug=e['slug'], t0=t0, t1=tl[-1][0], pr=pr, M=M, win0=win0, reb=C.reb_rate(m), ev=ev, vol=float(m.get('volumeNum') or 0)))
print('games usable', len(games), dict(why), flush=True)
# ---- Step 1: price half-move vs ESPN wallclock (|model jump| >= 3c)
lead = []
for g in games:
    pr, M = g['pr'], g['M']; tt = [p[0] for p in pr]
    for t, df in g['ev']:
        if abs(df) < 0.03: continue
        a, b = M.at(t - 120), M.at(t + 90)
        if a is None or b is None or not (0.05 < a < 0.95): continue
        mv = b - a
        if abs(mv) < 0.02 or np.sign(mv) != np.sign(df): continue
        for p in pr[bisect.bisect_left(tt, t - 120):bisect.bisect_right(tt, t + 90)]:
            if (p[2] - a) / mv >= 0.5: lead.append(p[0] - t); break
lead = np.array(lead)
LAG = dict(n=int(len(lead)), median_s=float(np.median(lead)), p10=float(np.percentile(lead, 10)), p25=float(np.percentile(lead, 25)),
           p75=float(np.percentile(lead, 75)), p90=float(np.percentile(lead, 90)), share_before_wallclock=float((lead < 0).mean()))
print('price half-move minus ESPN wallclock (s):', LAG, flush=True)
if EVT == 'onset':
    for g in games:
        pr, M = g['pr'], g['M']; tt = [p[0] for p in pr]; new = []
        for t, df in g['ev']:
            a, b = M.at(t - 120), M.at(t + 90); te = t + min(0.0, LAG['median_s'])
            if a is not None and b is not None and abs(b - a) >= 0.01 and np.sign(b - a) == np.sign(df):
                for p in pr[bisect.bisect_left(tt, t - 120):bisect.bisect_right(tt, t + 90)]:
                    if (p[2] - a) / (b - a) >= 0.2: te = p[0]; break
            new.append((te, df))
        new.sort(); g['ev'] = new
train = [g for g in games if g['t0'] < SPLIT1]; test = [g for g in games if SPLIT1 <= g['t0'] < SPLIT2]; now = [g for g in games if g['t0'] >= SPLIT2]
X = []; Y = []
for g in train:
    for t, df in g['ev']:
        a, b = g['M'].at(t - 2), g['M'].at(t + 30)
        if a is None or b is None or not (0.05 < a < 0.95): continue
        X.append(df); Y.append(b - a)
X, Y = np.array(X), np.array(Y); beta = float(X @ Y / (X @ X)); corr = float(np.corrcoef(X, Y)[0, 1])
print(f'train {len(train)} test {len(test)} now {len(now)}; jump beta {beta:.3f} corr {corr:.2f} n {len(X)}', flush=True)
def run(g, lag, W, minj, caught, Q, max_gap=0.01, d=0.025):
    tot = np.zeros(4); pr, M = g['pr'], g['M']; ev = g['ev']; et = [e[0] for e in ev]
    for (T, _, ph, sell0, sz) in pr:
        if not (g['t0'] <= T <= g['t1'] + 60): continue
        i = bisect.bisect_right(et, T - lag) - 1
        if i < 0 or T > et[i] + lag + W: continue
        t, df = ev[i]; pj = beta * df
        if abs(pj) < minj: continue
        tok = 0 if pj > 0 else 1
        mk_ = M.at(T - C.QDELAY); pre = M.at(t - 2)
        if mk_ is None or pre is None or not (0.05 <= mk_ <= 0.95): continue
        moved = (mk_ - pre) if tok == 0 else (pre - mk_)
        if moved >= caught * abs(pj): continue
        if tok == 0:
            b = mk_ * (1 - d)
            if not sell0 or ph >= b - 1e-9 or (b - ph) / b > max_gap: continue
        else:
            b = (1 - mk_) * (1 - d)
            if sell0 or (1 - ph) >= b - 1e-9 or (b - (1 - ph)) / b > max_gap: continue
        q = min(sz, Q); m60 = M.at(T + 60); m60 = m60 if tok == 0 else 1 - m60
        out = 1.0 if (g['win0'] == (tok == 0)) else 0.0
        tot += [q * b, q * (m60 - b), q * (out - b), q * g['reb'] * b * (1 - b)]
    return tot
res = []
for W, minj, caught in itertools.product([10, 20, 30, 60], [0.01, 0.02, 0.04], [0.5, 1.0]):
    s = C.summarize([run(g, 0, W, minj, caught, 100) for g in train], nb=300)
    res.append(dict(W=W, minj=minj, caught=caught, **s))
cand = [r for r in res if r['usd'] >= 2000] or res
best = max(cand, key=lambda r: r['net_result_pct']); L = {k: best[k] for k in ('W', 'minj', 'caught')}
print('LOCKED on train at delay 0:', L, 'train 1min', best['net_1min_pct'], '% result', best['net_result_pct'], '%', flush=True)
out = dict(event_time=EVT, tot_goals=TOT, lag_vs_wallclock=LAG, beta=beta, corr=corr, locked=L, n=dict(train=len(train), test=len(test), now=len(now)),
           exclusions=dict(why), train_grid=res, curve=[])
for Q in (100, 500):
    for nm, gs in (('test', test), ('now', now)):
        for lag in (0, 2, 5, 10, 20, 30, 60):
            s = C.summarize([run(g, lag, L['W'], L['minj'], L['caught'], Q) for g in gs])
            row = dict(set=nm, cap=Q, delay=lag, games=len(gs), per_game_usd=round(s['net_result_usd'] / len(gs), 1), **s); out['curve'].append(row)
            print(f"{nm:>4} cap{Q:>4} delay{lag:>3}s: games {len(gs)} filled ${s['usd']:>7} (${s['usd']/len(gs):.0f}/game) 1min {s['net_1min_pct']:>6}% {s['ci_1min']} "
                  f"result {s['net_result_pct']:>6}% {s['ci_result']} ${s['net_result_usd']:>6} (${row['per_game_usd']}/game, 90% {s['ci_result_usd']}) ex-top5 {s['ex_top5_result_pct']}%", flush=True)
json.dump(out, open(os.path.join(HERE, f'out_nhl_delay_hist_{EVT}.json'), 'w'), indent=1, default=float)
