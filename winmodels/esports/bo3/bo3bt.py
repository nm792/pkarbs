"""CS2 rules on 100+ past Polymarket CS2 matches with bo3.gg round data (4 Nov 2026).

Round times: bo3.gg gives per-round winner, score and round_duration (ns) plus each map's begin_at, but no clock time
per round. Round-end time = A + s * cumsum(round_duration). On 32 maps that overlap our Polymarket WS logger this fits
with ~5 s median error (most of it the WS 20 s update grid), s ~1.03-1.09, A varies by map. Here A and s are fitted
per map to the Polymarket price itself: the (A, s) that centres the model-signed price move (mid T+10 minus mid T-10)
on the round ends. So lag 0 = the middle of the market's own reaction; WS receipt sits ~+15-20 s (see overlap check).

Rules (same parameters as cs2_maps.py / cs2_resting.py, 4 Nov note):
  event-only: after a round, for 30 s, bid mid x 0.975 (maker only) on the side the model says should rise
              >= 1c (beta-scaled) but has not yet; corrected fills (print <= 1% below bid); hold to result.
  rn1 resting: bids at mid x 0.975 on both sides through play, pulled 30 s after each round; same fills; + rebate.
Holdout = later half of matches by start time; beta fitted on the earlier half only."""
import sys, os, json, gzip, re, bisect, collections, datetime as dt
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, os.path.dirname(os.path.dirname(HERE)))
import common as C
import cs2_maps as X
RAW = os.path.join(C.RAW, 'bo3')
def ts(s): return dt.datetime.fromisoformat(s.replace('Z', '+00:00')).timestamp()
def norm(s): return re.sub(r'[^a-z0-9]', '', (s or '').lower())
def sim_name(a, b):
    a, b = norm(a), norm(b)
    if not a or not b: return 0
    if a in b or b in a: return 3
    return max((k for k in range(1, 7) if a[:k] == b[:k]), default=0) / 2

def load_mkt(m):
    fn = f"{RAW}/trades/{m['conditionId']}.json.gz"
    if not os.path.exists(fn): return None
    tr = json.load(gzip.open(fn))
    if len(tr) < 20: return None
    pr = C.prints(tr); op = json.loads(m['outcomePrices'])
    if op[0] not in ('0', '1'): return None
    return dict(m=m, oc=json.loads(m['outcomes']), win0=op[0] == '1', M=C.Mid(pr), pr=pr,
                pt=np.array([p[0] for p in pr], float), pm=np.array(C.Mid(pr).m, float))

def mid_vec(s, T):
    i = np.searchsorted(s['pt'], T, side='left') - 1
    out = s['pm'][np.clip(i, 0, None)]; out[i < 0] = np.nan; return out

XFIT = False   # True: fit the anchor on odd rounds only and trade only even rounds (removes look-ahead from the fit)
def fit_anchor(s, cum, d, A0, svals=np.arange(1.02, 1.101, 0.01), Agrid=np.arange(-900, 601, 2.0), h=10):
    """grid-search (A, s): maximise sum sign(d) * (mid(T+h) - mid(T-h)) over rounds with |d| >= 2c."""
    k = np.abs(d) >= 0.02
    if XFIT: k &= (np.arange(len(d)) % 2 == 0)      # round_number odd = index even
    if k.sum() < 6: return None
    c, sg = cum[k], np.sign(d[k]); best = (-9, None, None)
    for sc in svals:
        T = A0 + Agrid[:, None] + sc * c[None, :]
        mv = mid_vec(s, (T + h).ravel()).reshape(T.shape) - mid_vec(s, (T - h).ravel()).reshape(T.shape)
        sc_ = np.nansum(mv * sg[None, :], axis=1)
        j = int(np.argmax(sc_))
        if sc_[j] > best[0]: best = (sc_[j], A0 + Agrid[j], sc)
    tot = np.abs(d[k]).sum()
    return dict(A=best[1], s=best[2], fit=best[0] / tot if tot else 0)

def build(links, ms):
    games = []; anchors = []
    for o in links:
        fn = f"{RAW}/games/{o['bo3']}.json.gz"
        if not os.path.exists(fn): continue
        G = sorted(json.load(gzip.open(fn)), key=lambda g: g['number'] or 9)
        mk = {m['groupItemTitle']: m for m in o['markets']}
        mw = load_mkt(mk['Match Winner']) if 'Match Winner' in mk else None
        oc = mw['oc'] if mw else None
        mstart = ts(ms[o['bo3']]['start_date'])
        maps_won = [0, 0]; mevs = []; ok = True
        played = [g for g in G if g['game_rounds'] and g.get('begin_at')]
        for k, g in enumerate(played, start=1):
            rs = sorted(g['game_rounds'], key=lambda r: r['round_number'])
            sm = load_mkt(mk[f'Map {k} Winner']) if f'Map {k} Winner' in mk else None
            clans = [rs[-1]['winner_clan_name'], rs[-1]['loser_clan_name']]       # map winner, loser
            ref = (sm or mw)
            if ref is None: ok = False; break
            o0 = ref['oc'][0]
            if sm is not None:
                c0 = clans[0] if sm['win0'] else clans[1]
            else:
                c0 = clans[0] if sim_name(o0, clans[0]) >= sim_name(o0, clans[1]) else clans[1]
            c1 = clans[1] if c0 == clans[0] else clans[0]
            if sm is not None and mw is not None and [norm(x) for x in sm['oc']] != [norm(x) for x in mw['oc']]:
                if norm(sm['oc'][0]) == norm(mw['oc'][1]): ok = False; break   # reversed outcome order: skip match
            cum = np.cumsum([r['round_duration'] / 1e9 for r in rs])
            sc = []; a = b = 0
            for r in rs:
                if r['winner_clan_name'] == c0: a += 1
                elif r['winner_clan_name'] == c1: b += 1
                sc.append((a, b))
            if a + b != len(rs) or len(rs) < 13: ok = False; break
            # map-market model moves (token0 = c0)
            dmap = None
            tgt = sm or mw
            A0 = ts(g['begin_at'])
            if sm is not None:
                p0 = sm['M'].at(A0 - 300)
                q = X.q_from(min(max(p0 if p0 is not None else 0.5, 0.05), 0.95))
                prev = (0, 0); dmap = []
                for (x, y) in sc:
                    f0 = X.pmap(prev[0], prev[1], q)
                    f1 = X.pmap(x, y, q)
                    if (x, y) == sc[-1]: f1 = 1.0 if x > y else 0.0
                    dmap.append(f1 - f0); prev = (x, y)
                dmap = np.array(dmap)
            dmw = []
            prev = (0, 0)
            for (x, y) in sc:
                f0 = X.series(maps_won[0], maps_won[1], X.pmap(prev[0], prev[1], 0.5))
                if (x, y) == sc[-1]:
                    w = [maps_won[0] + (x > y), maps_won[1] + (y > x)]
                    f1 = 1.0 if w[0] >= 2 else 0.0 if w[1] >= 2 else X.series(w[0], w[1], 0.5) if max(w) < 2 else 0.5
                else: f1 = X.series(maps_won[0], maps_won[1], X.pmap(x, y, 0.5))
                dmw.append(f1 - f0); prev = (x, y)
            dmw = np.array(dmw)
            # match-winner orientation: token0 of match market vs c0
            flip = False
            if mw is not None:
                if sm is not None: flip = norm(sm['oc'][0]) != norm(mw['oc'][0])
                else: flip = False
            fa = fit_anchor(sm, cum, dmap, A0) if sm is not None else (fit_anchor(mw, cum, -dmw if flip else dmw, A0) if mw else None)
            if fa is None: ok = False; break
            T = fa['A'] + fa['s'] * cum
            keep = (np.arange(len(T)) % 2 == 1) if XFIT else np.ones(len(T), bool)
            keep[-1] = True if not XFIT else keep[-1]
            anchors.append(dict(slug=o['bo3_slug'], map=k, A=float(fa['A']), A_minus_begin=round(fa['A'] - A0), s=fa['s'], fit=round(fa['fit'], 3), n=len(rs), tier=o['tier']))
            if sm is not None:
                games.append(dict(title=o['title'][:48], match=o['id'], kind=f'map{k}', t0=T[0], s=sm, ev=[(t_, d_) for t_, d_, k_ in zip(T.tolist(), dmap.tolist(), keep) if k_], fit=fa['fit']))
            for t_, d_, k_ in zip(T.tolist(), dmw.tolist(), keep):
                if k_: mevs.append((t_, -d_ if flip else d_))
            maps_won = [maps_won[0] + (a > b), maps_won[1] + (b > a)]
        if ok and mw is not None and mevs:
            games.append(dict(title=o['title'][:48], match=o['id'], kind='match', t0=mevs[0][0], s=mw, ev=mevs, fit=1))
        if not ok: games = [g for g in games if g['match'] != o['id']]
    return games, anchors

def resting(gs, beta_m, beta_M, lag, Q):
    C.Q = Q; out = {}
    for g in gs:
        s = g['s']; M = s['M']; ev = g['ev']; t0, t1 = ev[0][0] - 120, ev[-1][0]
        f_start = M.at(t0 - 60); beta = beta_m if g['kind'] != 'match' else beta_M
        if f_start is None: continue
        et = [R for R, _ in ev]; cum = np.cumsum([beta * d for _, d in ev])
        rows = C.sim(s['pr'], M, t0, t1, lambda T: 0.5, s['win0'], 0.02, evs=[R + min(lag, 0) for R in et], lag=max(lag, 0),
                     reb=C.reb_rate(s['m']), gate=False, max_gap=0.01)
        out[(g['match'], g['kind'])] = [sum(r[k] for r in rows) for k in ('usd', 'em1', 'pnl', 'reb')]
    return out

def event_only(gs, beta_m, beta_M, lag, Q, W=30):
    out = {}
    for g in gs:
        out[(g['match'], g['kind'])] = per_market(g, beta_m if g['kind'] != 'match' else beta_M, lag, W, Q)
    return out

def per_market(g, beta, lag, W, Q, minj=0.01, pre=30, d=0.025, max_gap=0.01):
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
    return tot.tolist()

def agg(res, matches, kinds, rng=np.random.default_rng(0), nb=2000):
    """res: {(match, kind): [usd, em1, pnl, reb]} -> per-match totals, $/match with bootstrap 90% range, 1-min edge."""
    P = np.zeros((len(matches), 4)); idx = {m: i for i, m in enumerate(matches)}
    for (m, k), v in res.items():
        if m in idx and ((k == 'match') == (kinds == 'match') or kinds == 'all'): P[idx[m]] += v
    u = P[:, 0].sum() or 1; net = P[:, 2] + P[:, 3]
    bs = [net[rng.integers(0, len(P), len(P))].mean() for _ in range(nb)]
    bs1 = []
    for _ in range(nb):
        s = rng.integers(0, len(P), len(P)); Q_ = P[s]; bs1.append(100 * (Q_[:, 1] + Q_[:, 3]).sum() / (Q_[:, 0].sum() or 1))
    return dict(n=len(matches), usd_per_match=round(P[:, 0].sum() / len(P)), edge_1min_pct=round(100 * (P[:, 1] + P[:, 3]).sum() / u, 2),
                ci_1min=list(np.percentile(bs1, [5, 95]).round(2)), result_pct=round(100 * net.sum() / u, 2),
                per_match=round(net.mean(), 1), ci_per_match=list(np.percentile(bs, [5, 95]).round(1)),
                reb_per_match=round(P[:, 3].mean(), 1), median_match=round(float(np.median(net)), 1))

if __name__ == '__main__':
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 250
    XFIT = len(sys.argv) > 2 and sys.argv[2] == 'xfit'; TAG = '_xfit' if XFIT else ''
    links = sorted(json.load(gzip.open(f'{RAW}/links.json.gz')), key=lambda o: -o['vol'])[:N]
    ms = {m['id']: m for m in json.load(gzip.open(f'{RAW}/matches_2026-09-01_2026-11-04.json.gz'))}
    games, anchors = build(links, ms)
    games = [g for g in games if g['fit'] > 0.15]           # drop maps whose price never lines up with the rounds
    mids = {g['match'] for g in games if g['kind'] != 'match'}
    games = [g for g in games if g['match'] in mids]
    start = {o['id']: o['startTime'] for o in links}
    matches = sorted(mids, key=lambda m: start[m]); half = set(matches[:len(matches) // 2])
    tr = [g for g in games if g['match'] in half]; te_m = matches[len(matches) // 2:]
    bm = X.fit_beta([g for g in tr if g['kind'] != 'match']); bM = X.fit_beta([g for g in tr if g['kind'] == 'match'])
    print('matches', len(matches), 'markets', len(games), 'maps', sum(g['kind'] != 'match' for g in games),
          'rounds', sum(len(g['ev']) for g in games if g['kind'] != 'match'), 'train', len(half), 'holdout', len(te_m),
          'holdout from', start[te_m[0]], flush=True)
    print('beta maps', bm, 'beta match', bM)
    # overlap check: WS receipt time minus fitted (market-reaction) round time, on maps our WS logger also saw
    ov = json.load(open(os.path.join(HERE, 'chk_overlap.json'))); an = {(x['slug'][:30], x['map']): x for x in anchors}
    dif = [w - (an[(sl, k)]['A_minus_begin'] + an[(sl, k)]['s'] * c) for sl, k, n, c, w in ov if w is not None and (sl, k) in an]
    dif = np.array([x for x in dif if abs(x) < 120])
    ovs = dict(n=len(dif), maps=len({(sl, k) for sl, k, n, c, w in ov if (sl, k) in an}), median=float(np.median(dif)) if len(dif) else None,
               p10_p90=np.percentile(dif, [10, 90]).round(1).tolist() if len(dif) else None)
    print('WS minus market-reaction time on overlap maps:', ovs, flush=True)
    res = dict(overlap_ws_minus_anchor=ovs, n_matches=len(matches), holdout_from=start[te_m[0]], beta=dict(maps=bm, match=bM), anchors=anchors, runs=[])
    for nm, gs in (('all', games),):
        n, prof = X.lag_profile(gs); res['lag_profile'] = dict(n=n, prof=prof); print('lag profile', n, prof)
    for rule in (('event_only',) if XFIT else ('event_only', 'resting')):
        for Q in (100, 500):
            for lag in (-10, -5, 0, 5, 10, 20, 30):
                f = event_only if rule == 'event_only' else resting
                r = f(games, bm[0], bM[0], lag, Q)
                for setn, mm in (('all', matches), ('holdout', te_m)):
                    row = dict(rule=rule, Q=Q, lag=lag, set=setn, maps=agg(r, mm, 'maps'), match=agg(r, mm, 'match'), total=agg(r, mm, 'all'))
                    res['runs'].append(row)
                    t = row['total']
                    print(f"{rule} Q{Q} lag{lag:+d} {setn}: $/match {t['per_match']} {t['ci_per_match']} fill/match ${t['usd_per_match']} "
                          f"1min {t['edge_1min_pct']}% {t['ci_1min']} result {t['result_pct']}% | maps 1min {row['maps']['edge_1min_pct']}% "
                          f"$/m {row['maps']['per_match']} | match 1min {row['match']['edge_1min_pct']}% $/m {row['match']['per_match']}", flush=True)
    json.dump(res, open(os.path.join(HERE, f'out_bo3bt{TAG}.json'), 'w'), indent=1, default=str)
