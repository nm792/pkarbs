"""Soccer: Nick's rule backtest on Polymarket markets of 22 Oct - 2 Nov matches (rn1 universe) matched to ESPN goal times.
Model state is read LAG s after ESPN's wallclock for each goal/red card/period change."""
import sys, os, json, gzip, datetime as dt, collections, math, bisect
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
import common as C, model as SM
LAG = int(os.environ.get('LAG', 10))
TYPES = {'moneyline', 'totals', 'spreads', 'both_teams_to_score'}
def ts(s): return dt.datetime.fromisoformat(s.replace('Z', '+00:00')).timestamp()
def norm(s): return ''.join(ch for ch in s.lower() if ch.isalnum())
def load_events():
    G = json.load(gzip.open(f'{C.RAW}/soccer/gamma_events.json.gz')); MT = json.load(open(f'{C.RAW}/soccer/match_pm_espn.json'))
    by = collections.defaultdict(list)
    for e in G:
        b = [s for s in MT if e['slug'] == s or e['slug'].startswith(s + '-')]
        if b: by[max(b, key=len)].append(e)
    out = []; why = collections.Counter()
    for s, evs in by.items():
        base = [e for e in evs if e['slug'] == s][0]; mt = MT[s]
        fn = f"{C.RAW}/soccer/summary/{mt['espn_id']}.json.gz"
        if not os.path.exists(fn): why['nosummary'] += 1; continue
        S = json.load(gzip.open(fn)); hd = S['header']['competitions'][0]
        side = {c['team']['id']: c['homeAway'] for c in hd['competitors']}
        fin = {c['homeAway']: int(c.get('score') or -1) for c in hd['competitors']}
        if mt['swapped']: side = {k: {'home': 'away', 'away': 'home'}[v] for k, v in side.items()}; fin = {'home': fin['away'], 'away': fin['home']}
        ke = S.get('keyEvents') or []
        tl = []; k1 = h1 = k2 = e2 = None
        for k in ke:
            w = k.get('wallclock'); ty = k['type']['type']; per = k.get('period', {}).get('number', 0)
            if not w: continue
            t = ts(w)
            if ty == 'kickoff' and k1 is None: k1 = t
            elif ty == 'halftime' and h1 is None: h1 = t
            elif ty == 'start-2nd-half' and k2 is None: k2 = t
            elif ty == 'end-regular-time' and e2 is None: e2 = t
            if per > 2: continue
            if k.get('scoringPlay') and k.get('team'): tl.append((t, 'g', side.get(k['team']['id'])))
            elif 'red-card' in ty and k.get('team'): tl.append((t, 'r', side.get(k['team']['id'])))
        g = collections.Counter(x[2] for x in tl if x[1] == 'g')
        if None in (k1, h1, k2, e2): why['no period times'] += 1; continue
        if (g['home'], g['away']) != (fin['home'], fin['away']): why['goal list != final score'] += 1; continue
        tl.sort()
        teams = {t['ordering']: t for t in base['teams']}
        mk = []
        for e in evs:
            for m in e['markets']:
                ty = m.get('sportsMarketType')
                if ty not in TYPES or not m.get('closed'): continue
                op = json.loads(m['outcomePrices']); oc = json.loads(m['outcomes'])
                if sorted(op) != ['0', '1']: continue
                win0 = op[0] == '1'; line = m.get('line')
                if ty == 'moneyline':
                    suf = m['slug'].rsplit('-', 1)[1]
                    kind = 'draw' if suf == 'draw' else ('home' if suf == teams['home']['abbreviation'] else 'away' if suf == teams['away']['abbreviation'] else None)
                    if mt['swapped'] and kind in ('home', 'away'): kind = {'home': 'away', 'away': 'home'}[kind]
                elif ty == 'totals': kind = 'over' if oc[0].lower() == 'over' else None
                elif ty == 'both_teams_to_score': kind = 'btts' if oc[0].lower() == 'yes' else None
                else:
                    n0 = norm(oc[0]); kind = 'home_spread' if n0 == norm(teams['home']['name']) else 'away_spread' if n0 == norm(teams['away']['name']) else None
                    if mt['swapped'] and kind: kind = {'home_spread': 'away_spread', 'away_spread': 'home_spread'}[kind]
                if kind is None or (kind in ('over', 'home_spread', 'away_spread') and line is None): continue
                mk.append(dict(cond=m['conditionId'], type=ty, kind=kind, line=line, win0=win0, reb=C.reb_rate(m), slug=m['slug']))
        out.append(dict(slug=s, league=s.split('-')[0], k1=k1, h1=h1, k2=k2, e2=e2, tl=tl, fin=fin, markets=mk))
    return out, why
class State:
    def __init__(s, E): s.E = E; s.tt = [x[0] for x in E['tl']]
    def at(s, T):
        """state the bot knows at time T (events up to T-LAG) and the effective minute."""
        E = s.E; Tk = T - LAG
        i = bisect.bisect_right(s.tt, Tk)
        h = sum(1 for x in E['tl'][:i] if x[1] == 'g' and x[2] == 'home'); a = sum(1 for x in E['tl'][:i] if x[1] == 'g' and x[2] == 'away')
        rh = sum(1 for x in E['tl'][:i] if x[1] == 'r' and x[2] == 'home'); ra = sum(1 for x in E['tl'][:i] if x[1] == 'r' and x[2] == 'away')
        if Tk < E['h1']: e = min((T - E['k1']) / 60, 45 + SM.S1)
        elif Tk < E['k2']: e = 45 + SM.S1
        else: e = min(45 + SM.S1 + (T - E['k2']) / 60, SM.END - 0.25)
        return h, a, rh, ra, e
def run():
    EV, why = load_events()
    print('events usable', len(EV), dict(why), 'markets', sum(len(e['markets']) for e in EV))
    res = []; cal = []; chk = collections.Counter()
    for E in EV:
        mk = []
        for m in E['markets']:
            fn = f"{C.RAW}/soccer/trades/{m['cond']}.json.gz"
            if not os.path.exists(fn): continue
            pr = C.prints(json.load(gzip.open(fn)))
            if len(pr) < 20: continue
            mk.append((m, pr, C.Mid(pr)))
        tg = []
        for m, pr, M in mk:
            p0 = M.at(E['k1'] - 60)
            if p0 is None or not (0.02 < p0 < 0.98): continue
            if m['kind'] in ('home', 'away', 'draw') or (m['kind'] == 'over' and m['line'] in (1.5, 2.5, 3.5)): tg.append((m['kind'], m['line'], p0))
        if sum(k in ('home', 'away') for k, _, _ in tg) < 2: chk['no pre-match 1X2 prices'] += 1; continue
        lh, la, err = SM.solve_rates(tg)
        st = State(E); cache = {}
        def fair_factory(m):
            def f(T):
                h, a, rh, ra, e = st.at(T)
                key = (h, a, rh, ra, round(e * 2) / 2)
                G = cache.get(key)
                if G is None:
                    mh, ma = SM.mults(rh, ra); r = SM.R(key[4])
                    G = cache[key] = SM.grid(h, a, lh * r * mh, la * r * ma)
                return SM.prob(m['kind'], m['line'] or 0, h, a, G)
            return f
        evs = [x[0] for x in E['tl']]
        for m, pr, M in mk:
            f = fair_factory(m)
            # resolution check: model at the final state with no time left
            Gf = SM.grid(0, 0, 0, 0); pf = SM.prob(m['kind'], m['line'] or 0, E['fin']['home'], E['fin']['away'], Gf)
            if round(pf) != (1 if m['win0'] else 0): chk[f"resolution mismatch {m['type']}"] += 1; continue
            chk['ok'] += 1
            for T in np.arange(E['k1'] + 60, E['e2'], 60):
                mm = M.at(T)
                if mm is not None: cal.append((E['slug'], m['type'], f(T), mm, float(m['win0']), (T - E['k1']) / 60))
            for fair_name in ('model', 'blend'):
                ff = f if fair_name == 'model' else (lambda T, f=f, M=M: None if M.at(T - C.QDELAY) is None else (f(T) + M.at(T - C.QDELAY)) / 2)
                for E_ in (0, 0.02, 0.05):
                    r = C.sim(pr, M, E['k1'], E['e2'], ff, m['win0'], E_, evs, LAG, m['reb'])
                    res.append((E['slug'], m['type'], fair_name, E_, [sum(z[k] for z in r) for k in ('usd', 'em1', 'pnl', 'reb')]))
            r = C.sim(pr, M, E['k1'], E['e2'], None, m['win0'], 0, evs, LAG, m['reb'], gate=False)
            res.append((E['slug'], m['type'], 'none', None, [sum(z[k] for z in r) for k in ('usd', 'em1', 'pnl', 'reb')]))
    print(dict(chk))
    return res, cal
def report(res, cal, tag):
    out = dict(lag=LAG, forecast={}, runs=[])
    import pandas as pd
    A = pd.DataFrame(cal, columns=['ev', 'type', 'model', 'mkt', 'y', 'tmin'])
    for ty, g in [('all', A)] + list(A.groupby('type')):
        out['forecast'][ty] = dict(points=len(g), events=g.ev.nunique(), brier_model=round(C.brier(g.model, g.y), 4), brier_mkt=round(C.brier(g.mkt, g.y), 4),
                                   brier_blend=round(C.brier((g.model + g.mkt) / 2, g.y), 4), mean_abs_diff=round(float(np.mean(np.abs(g.model - g.mkt))), 4))
    out['calibration_model_all'] = C.calib_table(A.model, A.y); out['calibration_mkt_all'] = C.calib_table(A.mkt, A.y)
    for ty in ['all', 'moneyline', 'totals', 'spreads', 'both_teams_to_score']:
        for fn, E_ in [('none', None)] + [(f, e) for f in ('model', 'blend') for e in (0, 0.02, 0.05)]:
            per = collections.defaultdict(lambda: np.zeros(4))
            for ev, t, f, e, v in res:
                if f == fn and e == E_ and (ty == 'all' or t == ty): per[ev] += np.array(v)
            s = C.summarize(list(per.values()))
            out['runs'].append(dict(type=ty, fair=fn, E=E_, **s))
            print(f"{ty:20}{fn:6}{'' if E_ is None else E_:>5} ev {s['events']:>4} $fill {s['usd']:>9} 1min+reb {s.get('net_1min_pct')}% {s.get('ci_1min')}  result+reb {s.get('net_result_pct')}% {s.get('ci_result')} = ${s.get('net_result_usd')}")
    print(json.dumps(out['forecast'], indent=0))
    json.dump(out, open(os.path.join(HERE, f'out_{tag}.json'), 'w'), indent=1)
    A.to_csv(os.path.join(HERE, f'out_forecast_{tag}.csv.gz'), index=False)
if __name__ == '__main__':
    res, cal = run(); report(res, cal, f'lag{LAG}')
