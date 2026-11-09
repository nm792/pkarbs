"""Tennis point-level event-only rule, delay curve (4 Nov 2026). Nick: react to points, not game ends.

Data: Cito tennis WS POINT_UPDATEs (every point, server, our receive time rt) recorded by the "Run Cito setup and time feeds"
thread (/mnt/project-files/cito-timing/*.jsonl.gz) + Polymarket moneyline v2 trades (raw/tennis/point/trades).
Event = first Cito message showing a new score state (point, game, set). Event time t = Cito receive time.
Model (tmodel.py): Markov point model; before each point, serve-win probabilities (s1+s2 = tour total) are re-fit so the
model equals the market mid 2 s before the event; expected jump = model(new state) - mid. Points that change nothing
important give ~0 jump; break points, game/set points and tiebreak points give big jumps.
Rule: from t+delay to t+delay+W (cut at the next known event), bid market x 0.975 (maker, never at/above ask) on the side the
jump says should rise, only if |jump| >= MINJ and the price has not already moved CAUGHT x the jump; fill only on taker prints
within 1% below our bid (corrected fill rule); hold to result; rebate estimate from feeSchedule.
Also: Cito receive time vs price onset (first print at 20% of the -60..+30 s move toward the jump) for |jump| >= 2c.
No parameters are tuned (too few matches): W=30, MINJ=0.01, CAUGHT=0.5 fixed in advance; a small grid is printed for
information only. Delay curve relative to Cito receipt and relative to price onset ("true" event time proxy)."""
import sys, os, json, gzip, glob, bisect, collections, re, itertools
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.dirname(os.path.dirname(HERE)))
import common as C
from tmodel import match as MP, fit
RAW = f'{C.RAW}/tennis/point'
MT = json.load(open(f'{RAW}/match_cito_pm.json'))
FILES = sys.argv[1:] or sorted(glob.glob('/mnt/project-files/cito-timing/*.jsonl.gz'))
PT = {'0': 0, '15': 1, '30': 2, '40': 3, 'AD': 4, 'A': 4}
def total(tour, tourn, dbl):
    if dbl: return 1.30
    itf = bool(re.match(r'[MW]\d', tourn or ''))
    return (1.22 if itf else 1.26) if tour == 'ATP' else (1.10 if itf else 1.12)
def state(x):
    cs = x.get('current_set') or 1; sets = sorted(x.get('sets') or [], key=lambda s: s.get('set_number') or s.get('set_num'))
    k1 = k2 = 0; g1 = g2 = 0
    for s in sets:
        n = s.get('set_number') or s.get('set_num'); m = re.match(r'(\d+)-(\d+)', s.get('score') or '')
        if not m: continue
        a, b = int(m.group(1)), int(m.group(2))
        if n < cs: k1 += a > b; k2 += b > a
        elif n == cs: g1, g2 = a, b
    tb = False
    if x.get('tiebreak_score'):
        m = re.match(r'(\d+)-(\d+)', str(x['tiebreak_score'])); a, b = (int(m.group(1)), int(m.group(2))) if m else (0, 0); tb = True
    else:
        gs = (x.get('game_score') or '0-0').split('-')
        if len(gs) != 2 or gs[0] not in PT or gs[1] not in PT: return None
        a, b = PT[gs[0]], PT[gs[1]]
    srv = x.get('server') or 1
    return (k1, k2, g1, g2, a, b, srv, tb)
EV = collections.defaultdict(list); INFO = {}
for f in FILES:
    for l in gzip.open(f, 'rt'):
        d = json.loads(l)
        if d['src'] != 'cito_tennis_ws': continue
        try: m = json.loads(d['m'])
        except Exception: continue
        if m.get('type') != 'POINT_UPDATE': continue
        x = m['data']; mid = x['match_id']
        if mid not in MT: continue
        s = state(x)
        if s is None: continue
        INFO[mid] = (x['tour'], x['tournament_name'], '/' in x['player1']['name'])
        if not EV[mid] or EV[mid][-1][1][:6] != s[:6]: EV[mid].append((d['rt'], s))
games = []; why = collections.Counter()
for mid, ev in EV.items():
    v = MT[mid]; fn = f"{RAW}/trades/{v['cond']}.json.gz"
    if not os.path.exists(fn): why['no trades'] += 1; continue
    pr = C.prints(json.load(gzip.open(fn)))
    if len(pr) < 30: why['few prints'] += 1; continue
    op = json.loads(v['prices'] or '[]')
    if sorted(op) == ['0', '1']: win0 = op[0] == '1'
    else:
        last = pr[-1][2]
        if 0.05 < last < 0.95: why['unresolved'] += 1; continue
        win0 = last >= 0.95
    tour, tourn, dbl = INFO[mid]; T = total(tour, tourn, dbl); M = C.Mid(pr)
    fs = (v.get('reb') or {}); reb = float(fs.get('rebateRate') or 0) * float(fs.get('rate') or 0)
    p10 = v['p1is0']; E = []
    for k in range(1, len(ev)):
        t, s = ev[k]; s0 = ev[k - 1][1]
        m0 = M.at(t - 2)
        if m0 is None or not (0.03 < m0 < 0.97): continue
        q0 = m0 if p10 else 1 - m0                                   # market prob of player1
        a1, a2 = fit(q0, T, s0, dbl)
        q1 = MP(a1, a2, *s, doubles=dbl); j1 = q1 - q0                # expected change in P(player1)
        if s[:2] != s0[:2]: typ = 'set'
        elif s[2:4] != s0[2:4]:
            gw = 1 if s[2] > s0[2] else 2; typ = 'break' if gw != s0[6] else 'hold'
        else:
            a, b = s[4], s[5]; sv = s0[6]; rp, spt = (b, a) if sv == 1 else (a, b)   # returner / server points after the point
            if s[7]: typ = 'tiebreak_pt'
            elif rp >= 3 and rp > spt: typ = 'break_pt'                 # returner now has break point
            elif spt >= 3 and spt > rp: typ = 'game_pt'
            else: typ = 'other_pt'
        E.append(dict(t=t, j0=j1 if p10 else -j1, m0=m0, s0=s0, s=s, typ=typ))  # jump in token0 terms
    if len(E) < 5: why['few events'] += 1; continue
    games.append(dict(mid=mid, slug=v['slug'], tour=tour, tourn=tourn, dbl=dbl, pr=pr, M=M, win0=win0, reb=reb, E=E, t0=ev[0][0], t1=ev[-1][0] + 60, T=T, p10=p10))
print('matches', len(games), dict(why), 'events', sum(len(g['E']) for g in games), flush=True)
# Cito receive time vs price onset
lag = []; ons = 0
for g in games:
    pr, M = g['pr'], g['M']; tt = [p[0] for p in pr]
    for e in g['E']:
        e['on'] = None
        if abs(e['j0']) < 0.02: continue
        a, b = M.at(e['t'] - 60), M.at(e['t'] + 30)
        if a is None or b is None or abs(b - a) < 0.01 or np.sign(b - a) != np.sign(e['j0']): continue
        for p in pr[bisect.bisect_left(tt, e['t'] - 60):bisect.bisect_right(tt, e['t'] + 30)]:
            if (p[2] - a) / (b - a) >= 0.2: e['on'] = p[0]; lag.append(e['t'] - p[0]); break
        if e['on'] is not None:                                     # re-fit the model on the mid just before the onset
            mo = M.at(e['on'] - 2)
            if mo is not None and 0.03 < mo < 0.97:
                q0 = mo if g['p10'] else 1 - mo; a1, a2 = fit(q0, g['T'], e['s0'], g['dbl']); j1 = MP(a1, a2, *e['s'], doubles=g['dbl']) - q0
                e['m0on'] = mo; e['j0on'] = j1 if g['p10'] else -j1
            else: e['on'] = None
lag = np.array(lag)
LAG = dict(n=int(len(lag)), median_s=float(np.median(lag)) if len(lag) else None, p25=float(np.percentile(lag, 25)) if len(lag) else None,
           p75=float(np.percentile(lag, 75)) if len(lag) else None)
print('Cito receipt minus price onset (|jump|>=2c):', LAG, flush=True)
# does the model's jump predict the next-30 s move?
X = []; Y = []
for g in games:
    for e in g['E']:
        b = g['M'].at(e['t'] + 30)
        if b is not None: X.append(e['j0']); Y.append(b - e['m0'])
X, Y = np.array(X), np.array(Y); big = np.abs(X) >= 0.01
REG = dict(n=int(len(X)), beta=float(X @ Y / (X @ X)), corr=float(np.corrcoef(X, Y)[0, 1]), n_big=int(big.sum()),
           beta_big=float(X[big] @ Y[big] / (X[big] @ X[big])) if big.any() else None)
print('model jump vs mid move from t-2 to Cito receipt+30 s:', REG, flush=True)
X2 = np.array([e['j0on'] for g in games for e in g['E'] if e.get('on') is not None and g['M'].at(e['on'] + 30) is not None])
Y2 = np.array([g['M'].at(e['on'] + 30) - e['m0on'] for g in games for e in g['E'] if e.get('on') is not None and g['M'].at(e['on'] + 30) is not None])
REG['onset'] = dict(n=int(len(X2)), beta=float(X2 @ Y2 / (X2 @ X2)), corr=float(np.corrcoef(X2, Y2)[0, 1]))
print('model jump vs mid move from onset-2 to onset+30 s:', REG['onset'], flush=True)

def run(g, lag, W, minj, caught, Q, ref='cito', max_gap=0.01, d=0.025, types=None):
    tot = np.zeros(4); pr, M = g['pr'], g['M']
    E = [e for e in g['E'] if ref == 'cito' or e['on'] is not None]
    keep = [e for e in E if types is None or e['typ'] in types]
    et = [(e['t'] if ref == 'cito' else e['on']) for e in E]
    order = np.argsort(et); E = [E[i] for i in order]; et = [et[i] for i in order]
    for (T, _, ph, sell0, sz) in pr:
        if not (g['t0'] <= T <= g['t1']): continue
        i = bisect.bisect_right(et, T - lag) - 1
        if i < 0 or T > et[i] + lag + W: continue
        e = E[i]
        if types is not None and e['typ'] not in types: continue
        pj = e['j0'] if ref == 'cito' else e['j0on']
        if abs(pj) < minj: continue
        tok = 0 if pj > 0 else 1
        mk = M.at(T - C.QDELAY); pre = e['m0'] if ref == 'cito' else e['m0on']
        if mk is None or not (0.05 <= mk <= 0.95): continue
        moved = (mk - pre) if tok == 0 else (pre - mk)
        if moved >= caught * abs(pj): continue
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
W, MINJ, CAUGHT = 30, 0.01, 0.5
out = dict(files=FILES, matches=len(games), cito_vs_onset=LAG, jump_regression=REG, fixed=dict(W=W, minj=MINJ, caught=CAUGHT), curve=[], grid=[])
for ref in ('cito', 'onset'):
    for Q in (100, 500):
        for lag in ((0, 2, 5, 10, 20) if ref == 'cito' else (-10, -5, 0, 2, 5, 10, 20)):
            s = C.summarize([run(g, lag, W, MINJ, CAUGHT, Q, ref) for g in games])
            n = len(games); row = dict(ref=ref, cap=Q, delay=lag, matches=n, filled_per_match=round(s['usd'] / n, 1),
                                       per_match_1min=round(s['usd'] * s['net_1min_pct'] / 100 / n, 2), per_match_result=round(s['net_result_usd'] / n, 2), **s)
            out['curve'].append(row)
            print(f"{ref:>5} cap{Q:>4} delay{lag:>4}s: filled ${s['usd']:>6} (${row['filled_per_match']}/match) 1min {s['net_1min_pct']:>6}% {s['ci_1min']} (${row['per_match_1min']}/match) "
                  f"result {s['net_result_pct']:>6}% {s['ci_result']} (${row['per_match_result']}/match)", flush=True)
DAYM = float(os.environ.get('MATCHES_PER_DAY', 70))
print('--- onset (true time) delay curve, W 30/60/120, cap 500 ---')
for W_ in (30, 60, 120):
    for lag in (-5, 0, 5, 10, 20, 30):
        s_ = C.summarize([run(g, lag, W_, MINJ, CAUGHT, 500, 'onset') for g in games]); n = len(games)
        out['curve'].append(dict(ref='onset', W=W_, cap=500, delay=lag, filled_per_match=round(s_['usd'] / n, 1), per_match_result=round(s_['net_result_usd'] / n, 2), **s_))
        print(f"onset W{W_:>3} delay{lag:>3}s: filled ${s_['usd']/n:6.1f}/match 1min {s_['net_1min_pct']}% {s_['ci_1min']} result {s_['net_result_pct']}% {s_['ci_result']} "
              f"${s_['net_result_usd']/n:.2f}/match (${s_['net_result_usd']/n*DAYM:.0f}/day at {DAYM:.0f} matches)", flush=True)
print('--- by event type, onset delay 0, W 30, cap 500 ---')
print('event counts', dict(collections.Counter(e['typ'] for g in games for e in g['E'])))
for ty in ('break_pt', 'game_pt', 'other_pt', 'hold', 'break', 'set', 'tiebreak_pt'):
    for ref, lag in (('onset', 0), ('onset', 5), ('cito', 0)):
        s_ = C.summarize([run(g, lag, 30, MINJ, CAUGHT, 500, ref, types={ty}) for g in games]); n = len(games)
        out.setdefault('by_type', []).append(dict(type=ty, ref=ref, delay=lag, **s_))
        print(f"{ty:>12} {ref:>5} {lag:>2}s: filled ${s_['usd']/n:6.1f}/match 1min {s_['net_1min_pct']}% result {s_['net_result_pct']}% {s_['ci_result']} ${s_['net_result_usd']/n:.2f}/match", flush=True)
for W_, mj, cg in itertools.product([15, 30], [0.005, 0.01, 0.02], [0.5, 1.0]):
    s = C.summarize([run(g, 0, W_, mj, cg, 500) for g in games], nb=200); out['grid'].append(dict(W=W_, minj=mj, caught=cg, **s))
    print(f'grid W{W_} minj{mj} caught{cg}: filled ${s["usd"]} 1min {s["net_1min_pct"]}% result {s["net_result_pct"]}%')
json.dump(out, open(os.path.join(HERE, 'out_point_delay.json'), 'w'), indent=1, default=float)
