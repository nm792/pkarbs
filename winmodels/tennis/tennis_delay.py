"""Tennis event-only rule: delay curve at (proxy) true event time, 2-4 Nov 2026 matches (4 Nov 2026).

Events: game/set changes in the server's Polymarket sports-WS log (rn1/scores/cs2/server-2026-11/cs2_frames.jsonl.gz;
snapshots ~30 s apart, so the WS time is only known to within the snapshot gap). Game winner = side whose game count went up
(set change: side that led the previous snapshot; 6-6 skipped).
True event time (proxy): first print, within [previous snapshot - 30 s, this snapshot + 30 s], that has moved >= 20% of the
(prev - 60 s -> this + 60 s) mid move toward the game winner. If none, the event is skipped for timing and placed at the
snapshot time (we would act on the WS anyway).
Rule (same as NBA/NFL): after an event, for W s, bid market x 0.975 (maker only, never at/above ask) on the game winner's token
if its price has not already risen CAUGHT x the expected jump; expected jump = beta (fit on TRAIN events by type game/set,
mean 30 s move after onset). Fill only on taker prints within 1% below our bid; hold to result; rebate estimate from the
market feeSchedule. Train = matches starting before SPLIT, test = after. Delay = seconds after true event time we act.
Also reports the WS-log lag (snapshot time - onset)."""
import sys, os, json, gzip, bisect, itertools, collections, datetime as dt, re, unicodedata
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import common as C
SPLIT = dt.datetime(2026, 11, 3, 12, tzinfo=dt.timezone.utc).timestamp()
G = json.load(gzip.open(f'{C.RAW}/tennis/gamma_tennis_events_2026-10-30_on.json.gz'))
byg = {e['gameId']: e for e in G if e.get('gameId')}
F = collections.defaultdict(list)
for l in gzip.open(os.path.join(C.HERE, '..', 'rn1/scores/cs2/server-2026-11/cs2_frames.jsonl.gz'), 'rt'):
    d = json.loads(l)
    if d.get('leagueAbbreviation') in ('atp', 'wta', 'challenger', 'wta challenger') and d['gameId'] in byg: F[d['gameId']].append(d)
def nm(s): return re.sub(r'[^a-z ]', '', unicodedata.normalize('NFKD', s or '').encode('ascii', 'ignore').decode().lower()).split()
def parse(d):
    m = re.match(r'(\d+)-(\d+)', d.get('score') or ''); p = re.match(r'S(\d)', d.get('period') or '')
    return (int(p.group(1)), int(m.group(1)), int(m.group(2))) if m and p else None
games = []; why = collections.Counter()
for gid, fr in F.items():
    e = byg[gid]; ml = [m for m in e['markets'] if m.get('sportsMarketType') == 'moneyline']
    if not ml: why['no ml'] += 1; continue
    m = ml[0]; fn = f"{C.RAW}/tennis/trades/{m['conditionId']}.json.gz"
    if not os.path.exists(fn): why['no trades'] += 1; continue
    tr = json.load(gzip.open(fn)); pr = C.prints(tr)
    if len(pr) < 50: why['few prints'] += 1; continue
    oc = json.loads(m['outcomes']); op = json.loads(m['outcomePrices'] or '[]')
    if sorted(op) != ['0', '1']: why['unresolved'] += 1; continue
    h = nm(fr[0]['homeTeam']); a = nm(fr[0]['awayTeam']); o0 = nm(oc[0])
    if h and h[-1] in o0: home0 = True
    elif a and a[-1] in o0: home0 = False
    else: why['name mismatch'] += 1; continue
    fr.sort(key=lambda d: d['recv_ms']); ev = []; last = None; lt = None
    for d in fr:
        s = parse(d); t = d['recv_ms'] / 1000
        if s is None: continue
        if last is not None and s != last:
            if s[0] == last[0]:
                dh, da = s[1] - last[1], s[2] - last[2]
                w = 'home' if (dh == 1 and da == 0) else 'away' if (da == 1 and dh == 0) else None; typ = 'game'
            elif s[0] == last[0] + 1:
                w = 'home' if last[1] > last[2] else 'away' if last[2] > last[1] else None; typ = 'set'
            else: w = None; typ = None
            if w: ev.append(dict(t=t, tprev=lt, typ=typ, tok0=(w == 'home') == home0))
            else: why['ambiguous change'] += 1
        last = s; lt = t
    if len(ev) < 5: why['few events'] += 1; continue
    games.append(dict(gid=gid, slug=e['slug'], pr=pr, M=C.Mid(pr), win0=op[0] == '1', reb=C.reb_rate(m), ev=ev, t0=fr[0]['recv_ms'] / 1000, t1=fr[-1]['recv_ms'] / 1000 + 120))
print('matches', len(games), dict(why), 'events', sum(len(g['ev']) for g in games), flush=True)
lags = collections.defaultdict(list)
for g in games:
    pr, M = g['pr'], g['M']; tt = [p[0] for p in pr]
    for x in g['ev']:
        x['te'] = None; t, tp = x['t'], x['tprev'] or x['t'] - 30
        a, b = M.at(tp - 60), M.at(t + 60)
        if a is None or b is None: continue
        mv = (b - a) if x['tok0'] else (a - b)
        if mv < 0.01: continue
        for p in pr[bisect.bisect_left(tt, tp - 30):bisect.bisect_right(tt, t + 30)]:
            r = (p[2] - a) / (b - a)
            if r >= 0.2: x['te'] = p[0]; break
        if x['te'] is not None: lags[x['typ']].append(t - x['te'])
LAG = {k: dict(n=len(v), median_s=float(np.median(v)), p25=float(np.percentile(v, 25)), p75=float(np.percentile(v, 75))) for k, v in lags.items()}
print('WS-log snapshot time minus price onset:', LAG, flush=True)
EVT = os.environ.get('EVT', 'onset')
for g in games:
    for x in g['ev']: x['T'] = x['te'] if (EVT == 'onset' and x['te'] is not None) else x['t']
    g['ev'].sort(key=lambda x: x['T'])
train = [g for g in games if g['t0'] < SPLIT]; test = [g for g in games if g['t0'] >= SPLIT]
beta = {}
for typ in ('game', 'set'):
    mv = []
    for g in train:
        for x in g['ev']:
            if x['typ'] != typ: continue
            a, b = g['M'].at(x['T'] - 2), g['M'].at(x['T'] + 30)
            if a is None or b is None or not (0.05 < a < 0.95): continue
            mv.append((b - a) if x['tok0'] else (a - b))
    beta[typ] = float(np.mean(mv)) if mv else 0.0
print('train', len(train), 'test', len(test), 'expected jump toward game winner (30 s):', beta, flush=True)

def run(g, lag, W, caught, Q, onlyset=False, max_gap=0.01, d=0.025):
    tot = np.zeros(4); pr, M = g['pr'], g['M']; ev = [x for x in g['ev'] if not onlyset or x['typ'] == 'set']; et = [x['T'] for x in ev]
    for (T, _, ph, sell0, sz) in pr:
        if not (g['t0'] - 60 <= T <= g['t1']): continue
        i = bisect.bisect_right(et, T - lag) - 1
        if i < 0 or T > et[i] + lag + W: continue
        x = ev[i]; pj = beta[x['typ']]; tok = 0 if x['tok0'] else 1
        mk = M.at(T - C.QDELAY); pre = M.at(x['T'] - 2)
        if mk is None or pre is None or not (0.05 <= mk <= 0.95): continue
        moved = (mk - pre) if tok == 0 else (pre - mk)
        if moved >= caught * pj: continue
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
res = []
for W, caught, onlyset in itertools.product([10, 20, 30], [0.5, 1.0], [False, True]):
    s = C.summarize([run(g, 0, W, caught, 100, onlyset) for g in train], nb=300); res.append(dict(W=W, caught=caught, onlyset=onlyset, **s))
cand = [r for r in res if r['usd'] >= 1000] or res
best = max(cand, key=lambda r: r['net_1min_pct'])
L = {k: best[k] for k in ('W', 'caught', 'onlyset')}
print('LOCKED on train at delay 0:', L, 'train 1min', best['net_1min_pct'], '% result', best['net_result_pct'], '%', flush=True)
out = dict(event_time=EVT, ws_log_lag=LAG, beta=beta, locked=L, n_train=len(train), n_test=len(test), train_grid=res, curve=[])
for Q in (100, 500):
    for nmn, gs in (('test', test), ('all', games)):
        for lag in (0, 2, 5, 10, 20, 30, 60):
            s = C.summarize([run(g, lag, L['W'], L['caught'], Q, L['onlyset']) for g in gs])
            row = dict(set=nmn, cap=Q, delay=lag, games=len(gs), per_game_usd=round(s['net_result_usd'] / len(gs), 1),
                       per_game_1min_usd=round(s['usd'] * s['net_1min_pct'] / 100 / len(gs), 1), **s); out['curve'].append(row)
            print(f"{nmn:>4} cap{Q:>4} delay{lag:>3}s: matches {len(gs)} filled ${s['usd']:>7} (${s['usd']/len(gs):.0f}/match) 1min {s['net_1min_pct']:>6}% {s['ci_1min']} "
                  f"(${row['per_game_1min_usd']}/match) result {s['net_result_pct']:>6}% {s['ci_result']} (${row['per_game_usd']}/match) ex-top5 {s['ex_top5_result_pct']}%", flush=True)
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'out_tennis_delay_{EVT}.json'), 'w'), indent=1, default=float)
