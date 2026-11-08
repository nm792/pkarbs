"""CS2 event-only rule on MAP-winner and match-winner markets (4 Nov). Round scores = Polymarket sports WS as our
server logger received them (2 Nov 06:49Z - 4 Nov 04:00Z). Same rule as LoL/Dota: after a round change seen at
recv+lag, for W s, bid mid x 0.975 (maker only, never at/above market) on the side whose model jump >= minj has not
yet shown in the mid. Corrected fills (print <=1% below bid). Hold to result. Holdout = later half of matches by time;
beta (price move per unit model move) fitted on the earlier half only."""
import sys, os, json, gzip, bisect, functools, collections, re
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import common as C
G = json.load(gzip.open(f'{C.RAW}/esports/gamma_cs2_2026-11-02_04.json.gz'))['cs2']
CH = collections.defaultdict(list)
for l in gzip.open('/home/user/pkarbs/rn1/scores/cs2/server-2026-11/cs2_changes.jsonl.gz', 'rt'):
    d = json.loads(l)
    if '|Bo' in (d.get('score') or ''): CH[d['gameId']].append(d)
def norm(s): return re.sub(r'[^a-z0-9]', '', (s or '').lower())
def parse(s):
    p = s.split('|')
    try: r = [int(x) for x in p[0].split('-')]; m = [int(x) for x in p[1].split('-')]; return (m[0], m[1], r[0], r[1])
    except Exception: return None
@functools.lru_cache(None)
def pmap(a, b, q):
    if a >= 12 and b >= 12:                      # overtime: crude, lead-based
        return min(max(0.5 + 0.22 * (a - b), 0.03), 0.97)
    if a >= 13: return 1.0
    if b >= 13: return 0.0
    return q * pmap(a + 1, b, q) + (1 - q) * pmap(a, b + 1, q)
def q_from(p):
    lo, hi = 0.3, 0.7
    for _ in range(30):
        m = (lo + hi) / 2; lo, hi = (m, hi) if pmap(0, 0, round(m, 3)) < p else (lo, m)
    return round(lo, 3)
def series(ma, mb, w, pm=0.5):
    def rest(x, y):
        if x >= 2: return 1.0
        if y >= 2: return 0.0
        return pm * rest(x + 1, y) + (1 - pm) * rest(x, y + 1)
    return w * rest(ma + 1, mb) + (1 - w) * rest(ma, mb + 1)
def mkt(e, title):
    for m in e['markets']:
        if m.get('closed') and (m.get('groupItemTitle') or '') == title: return m
def load(m, home):
    fn = f"{C.RAW}/esports/trades/{m['conditionId']}.json.gz"
    if not os.path.exists(fn): return None
    tr = json.load(gzip.open(fn))
    if len(tr) < 20: return None
    oc = json.loads(m['outcomes']); op = json.loads(m['outcomePrices'])
    h = norm(home); o0 = norm(oc[0]); o0_home = o0[:5] in h or h[:5] in o0
    pr = C.prints(tr)
    return dict(m=m, o0_home=o0_home, win0=op[0] == '1', M=C.Mid(pr), pr=pr)
def build():
    """-> list of 'games' (one per traded market): dict(title, t0, kind, s, ev=[(R, d_fair_token0)])"""
    out = []
    for e in G:
        ch = sorted(CH.get(int(e['gameId']), []), key=lambda d: d['recv_ms'])
        if len({x['score'].split('|')[0] for x in ch}) < 4: continue
        home = ch[-1]['home']; st = [(x['recv_ms'] / 1000, parse(x['score'])) for x in ch]; st = [x for x in st if x[1]]
        mw = load(mkt(e, 'Match Winner') or {'conditionId': 'x', 'outcomes': '[]', 'outcomePrices': '[]'}, home) if mkt(e, 'Match Winner') else None
        for k in (1, 2, 3):
            m = mkt(e, f'Map {k} Winner')
            s = load(m, home) if m else None
            evs = []; q = None
            for (R0, a), (R1, b) in zip(st, st[1:]):
                if a == b or a[0] + a[1] + 1 != k: continue
                if s is None: continue
                if q is None:
                    p0 = s['M'].at(R0 - 60)
                    if p0 is None: break
                    q = q_from(min(max(p0 if s['o0_home'] else 1 - p0, 0.05), 0.95))
                f0 = pmap(a[2], a[3], q)
                if b[0] + b[1] > a[0] + a[1]: f1 = 1.0 if b[0] > a[0] else 0.0
                elif b[0] + b[1] == a[0] + a[1] and (b[2] + b[3]) > (a[2] + a[3]) and (b[2] + b[3]) - (a[2] + a[3]) <= 3: f1 = pmap(b[2], b[3], q)
                else: continue
                d = f1 - f0; evs.append((R1, d if s['o0_home'] else -d))
            if s and evs: out.append(dict(title=e['title'][:48], kind=f'map{k}', t0=evs[0][0], s=s, ev=evs))
        if mw:   # match winner: series fair with map-in-play win prob from pmap at q=0.5
            evs = []
            for (R0, a), (R1, b) in zip(st, st[1:]):
                if a == b: continue
                f0 = series(a[0], a[1], pmap(a[2], a[3], 0.5))
                if b[0] + b[1] > a[0] + a[1] or ((b[2] + b[3]) - (a[2] + a[3]) in (1, 2, 3)):
                    f1 = series(b[0], b[1], pmap(b[2], b[3], 0.5)) if b[0] + b[1] == a[0] + a[1] else series(b[0], b[1], 0.5) if max(b[0], b[1]) < 2 else (1.0 if b[0] >= 2 else 0.0)
                    d = f1 - f0; evs.append((R1, d if mw['o0_home'] else -d))
            if evs: out.append(dict(title=e['title'][:48], kind='match', t0=evs[0][0], s=mw, ev=evs))
    return out
def fit_beta(games):
    xs, ys = [], []
    for g in games:
        M = g['s']['M']
        for R, d in g['ev']:
            a, b = M.at(R - 30), M.at(R + 60)
            if a is None or b is None or abs(d) < 1e-4 or not (0.03 < a < 0.97): continue
            xs.append(d); ys.append(b - a)
    xs, ys = np.array(xs), np.array(ys)
    beta = float((xs * ys).sum() / (xs * xs).sum())
    return beta, float(1 - ((ys - beta * xs) ** 2).sum() / ((ys - ys.mean()) ** 2).sum()), len(xs)
def run(games, beta, lag=0, W=30, minj=0.01, pre=30, d=0.025, max_gap=0.01, Q=None):
    Q = Q or C.Q; per = []; rows = []
    for g in games:
        s = g['s']; M = s['M']; reb = C.reb_rate(s['m']); tot = np.zeros(4)
        evt = [(R + lag, dd, M.at(R - pre)) for R, dd in g['ev']]; et = [x[0] for x in evt]
        for (T, _, ph, sell0, sz) in s['pr']:
            i = bisect.bisect_right(et, T) - 1
            if i < 0 or T > et[i] + W: continue
            _, dd, base = evt[i]; mk = M.at(T - 1)
            if base is None or mk is None or not (0.05 <= mk <= 0.95): continue
            j = beta * dd
            if abs(j) < minj: continue
            if j > 0:
                if mk - base >= j: continue
                b = mk * (1 - d); tok = 0
                if not sell0 or ph >= b - 1e-9 or (b - ph) / b > max_gap: continue
            else:
                if base - mk >= -j: continue
                b = (1 - mk) * (1 - d); tok = 1
                if sell0 or (1 - ph) >= b - 1e-9 or (b - (1 - ph)) / b > max_gap: continue
            q = min(sz, Q); m60 = M.at(T + 60); m60 = m60 if tok == 0 else 1 - m60
            out = 1.0 if (s['win0'] == (tok == 0)) else 0.0
            tot += [q * b, q * (m60 - b), q * (out - b), q * reb * b * (1 - b)]
        per.append(tot); rows.append((g['title'], g['kind'], round(tot[0]), round(tot[2] + tot[3])))
    return C.summarize(per), rows
def lag_profile(games, sl=np.arange(-60, 61, 5)):
    """signed mid move around WS receipt (sign = model direction), map markets only, in cents"""
    acc = np.zeros(len(sl) - 1); n = 0
    for g in games:
        if g['kind'] == 'match': continue
        M = g['s']['M']
        for R, d in g['ev']:
            if abs(d) < 0.02: continue
            pts = [M.at(R + x) for x in sl]
            if any(p is None for p in pts) or not (0.08 < pts[0] < 0.92): continue
            acc += np.sign(d) * np.diff(pts); n += 1
    return n, (np.cumsum(acc) / max(n, 1) * 100).round(2).tolist()
if __name__ == '__main__':
    games = build(); games.sort(key=lambda g: g['t0'])
    matches = sorted({g['title'] for g in games}, key=lambda t: min(g['t0'] for g in games if g['title'] == t))
    half = set(matches[:len(matches) // 2])
    tr = [g for g in games if g['title'] in half]; te = [g for g in games if g['title'] not in half]
    print('matches', len(matches), 'markets', len(games), 'maps', sum(g['kind'] != 'match' for g in games), 'rounds', sum(len(g['ev']) for g in games))
    res = dict(matches=matches, n_markets=len(games))
    for nm, gs in (('all', games), ('train', tr), ('holdout', te)):
        n, prof = lag_profile(gs); res[f'lag_{nm}'] = dict(n=n, prof=prof)
        print('lag profile', nm, n, 'rounds; cum signed move (c) at -60..+60 by 5s:', prof)
    bm, r2m, nm_ = fit_beta([g for g in tr if g['kind'] != 'match']); bM, r2M, nM = fit_beta([g for g in tr if g['kind'] == 'match'])
    print(f'beta maps {bm:.2f} R2 {r2m:.2f} n {nm_} | beta match {bM:.2f} R2 {r2M:.2f} n {nM}')
    res['beta'] = dict(maps=[bm, r2m, nm_], match=[bM, r2M, nM]); res['runs'] = []
    for Q in (100, 500):
        for lag in (0, 10, 20):
            for W in (10, 30):
                for nm, gs in (('train', tr), ('holdout', te)):
                    out = {}
                    for kind, b in (('maps', bm), ('match', bM)):
                        s, rows = run([g for g in gs if (g['kind'] == 'match') == (kind == 'match')], b, lag, W, Q=Q)
                        out[kind] = s
                        print(f"Q{Q} lag{lag} W{W} {nm} {kind}: mkts {s['events']} $fill {s['usd']} 1min {s.get('net_1min_pct')}% {s.get('ci_1min')} result {s.get('net_result_pct')}% ${s.get('net_result_usd')} {s.get('ci_result_usd')} ex-top5 {s.get('ex_top5_result_pct')}%", flush=True)
                        if Q == 100 and lag == 0 and W == 30 and nm == 'holdout': out[kind + '_rows'] = rows
                    res['runs'].append(dict(Q=Q, lag=lag, W=W, set=nm, **out))
    json.dump(res, open('out_cs2_maps.json', 'w'), indent=1, default=str)
