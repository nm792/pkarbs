"""US sports (NBA, NFL, college football): Nick's rule backtest. Normal model for remaining margin and total,
variance by game fraction from the previous season (params.json). Event mu/tau solved from Polymarket's own
pre-game prices (moneyline + spreads for mu, totals for tau). State read LAG s after ESPN play wallclock."""
import sys, os, json, gzip, datetime as dt, collections, math, bisect, re
import numpy as np
from scipy.stats import norm as N
from scipy.optimize import minimize_scalar
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
import common as C
from espn import PLEN, NPER
from fit_hist import frac
LAG = int(os.environ.get('LAG', 10))
P = json.load(open(os.path.join(HERE, 'params.json')))
P['cfb'] = dict(P['nfl']); P['cfb']['Vm'] = [v * 1.15 ** 2 for v in P['nfl']['Vm']]; P['cfb']['Vt'] = [v * 1.15 ** 2 for v in P['nfl']['Vt']]   # ESTIMATE: too few CFB games with lines
SPORTS = os.environ.get('SPORTS', 'nba,nfl,cfb').split(',')
def V(sp, key, f):
    b = P[sp]['bins']; mids = [(x + y) / 2 for x, y in zip(b[:-1], b[1:])]
    v = float(np.interp(f, mids, P[sp][key])) if f < mids[-1] else P[sp][key][-1] * (1 - f) / (1 - mids[-1])
    return max(v, 0.25)
def ts(s): return dt.datetime.fromisoformat(s.replace('Z', '+00:00')).timestamp()
def norm_(s): return re.sub(r'[^a-z0-9]', '', (s or '').lower())
def pwin(mean, sd):           # P(final margin > 0) with ties split (overtime ~ coin flip)
    return 1 - N.cdf((0.5 - mean) / sd) + 0.5 * (N.cdf((0.5 - mean) / sd) - N.cdf((-0.5 - mean) / sd))
def load():
    G = json.load(gzip.open(f'{C.RAW}/us/gamma_events.json.gz')); MT = json.load(open(f'{C.RAW}/us/match_pm_espn.json'))
    out = []; why = collections.Counter()
    for e in G:
        if e['slug'] not in MT: continue
        mt = MT[e['slug']]; sp = mt['sport']
        if sp not in SPORTS: continue
        fn = f"{C.RAW}/us_bt/{sp}/{mt['espn_id']}.json.gz"
        if not os.path.exists(fn): why['nosummary'] += 1; continue
        g = json.load(gzip.open(fn))
        if not g.get('completed') or len(g['tl']) < 20: why['incomplete'] += 1; continue
        tm = {x['ordering']: x for x in e['teams']}
        ek = {ha: norm_(g['comp'][ha]['name']) for ha in ('home', 'away')}
        swapped = (norm_(tm['home']['name']) in ek['away'] or ek['away'] in norm_(tm['home']['name'])) and not (norm_(tm['home']['name']) in ek['home'] or ek['home'] in norm_(tm['home']['name']))
        if swapped: why['swapped (skipped)'] += 1; continue
        names = {norm_(tm['home']['name']): 'home', norm_(tm['away']['name']): 'away'}
        def side(o):
            o = norm_(o)
            for k, v in names.items():
                if o and (o in k or k in o): return v
            return None
        mk = []
        for m in e['markets']:
            ty = m.get('sportsMarketType')
            if ty not in ('moneyline', 'spreads', 'totals') or not m.get('closed'): continue
            op = json.loads(m['outcomePrices']); oc = json.loads(m['outcomes'])
            if sorted(op) != ['0', '1']: continue
            if ty == 'moneyline': kind, line = side(oc[0]), 0.0
            elif ty == 'spreads': kind, line = side(oc[0]), m.get('line')
            else: kind, line = ('over' if oc[0].lower() == 'over' else None), m.get('line')
            if kind is None or line is None: continue
            if ty == 'spreads':
                q = re.search(r'\(([-+]?\d+(?:\.\d+)?)\)', m['question']); qn = norm_(m['question'].split('(')[0].replace('Spread:', ''))
                # line applies to the team named in the question; outcome0 must be that team
                if q is None or side(m['question'].split('(')[0].replace('Spread:', '')) != kind: continue
                line = float(q.group(1))
            mk.append(dict(cond=m['conditionId'], type=ty, kind=kind, line=float(line), win0=op[0] == '1', reb=C.reb_rate(m), slug=m['slug']))
        tl = [(ts(r[0]), r[1], r[2], r[3], r[4]) for r in g['tl']]
        tl.sort()
        fh, fa = int(g['comp']['home']['score']), int(g['comp']['away']['score'])
        out.append(dict(slug=e['slug'], sport=sp, t0=tl[0][0], t1=tl[-1][0], tl=tl, fin=(fh, fa), markets=mk))
    return out, why
def prob(m, h, a, mean_m, sd_m, mean_t, sd_t):
    if m['type'] == 'totals': return 1 - N.cdf((m['line'] - (h + a) - mean_t) / sd_t)
    mm = (h - a) + mean_m if m['kind'] == 'home' else (a - h) - mean_m
    if m['type'] == 'moneyline': return pwin(mm, sd_m)
    return 1 - N.cdf((-m['line'] - mm) / sd_m)          # team margin + line > 0 (half-point lines)
def run():
    EV, why = load(); print('events', len(EV), dict(why), collections.Counter(e['sport'] for e in EV))
    res = []; cal = []; chk = collections.Counter()
    for E in EV:
        sp = E['sport']; mk = []
        for m in E['markets']:
            fn = f"{C.RAW}/us/trades/{m['cond']}.json.gz"
            if not os.path.exists(fn): continue
            pr = C.prints(json.load(gzip.open(fn)))
            if len(pr) < 20: continue
            mk.append((m, pr, C.Mid(pr)))
        t0 = E['t0']; sd0m, sd0t = math.sqrt(V(sp, 'Vm', 0)), math.sqrt(V(sp, 'Vt', 0))
        tm = [(m, M.at(t0 - 60)) for m, pr, M in mk]
        tm = [(m, p) for m, p in tm if p is not None and 0.03 < p < 0.97]
        sm = [(m, p) for m, p in tm if m['type'] != 'totals']; st_ = [(m, p) for m, p in tm if m['type'] == 'totals']
        if not sm or not st_: chk['no pre-game prices'] += 1; continue
        mu = minimize_scalar(lambda x: sum((prob(m, 0, 0, x, sd0m, 0, 1) - p) ** 2 for m, p in sm), bounds=(-40, 40), method='bounded').x
        tau = minimize_scalar(lambda x: sum((prob(m, 0, 0, 0, 1, x, sd0t) - p) ** 2 for m, p in st_), bounds=(1, 300), method='bounded').x
        tt = [x[0] for x in E['tl']]
        def state(T):
            i = bisect.bisect_right(tt, T - LAG) - 1
            if i < 0: return 0, 0, 0.0
            r = E['tl'][i]; return r[3], r[4], frac(sp, r[1], r[2])
        evs = [E['tl'][k][0] for k in range(1, len(E['tl'])) if E['tl'][k][3:] != E['tl'][k - 1][3:]]
        if sp == 'nba': evs = []        # basketball scores every ~30 s: no pull (would remove all quoting)
        for m, pr, M in mk:
            hf, af = E['fin']
            pf = prob(m, hf, af, 0, 1e-6, 0, 1e-6)
            if round(pf) != (1 if m['win0'] else 0): chk[f"resolution mismatch {m['type']}"] += 1; continue
            chk['ok'] += 1
            def f(T, m=m):
                h, a, fr = state(T); rem = 1 - fr
                return prob(m, h, a, mu * rem, math.sqrt(V(sp, 'Vm', fr)), tau * rem, math.sqrt(V(sp, 'Vt', fr)))
            for T in np.arange(E['t0'] + 60, E['t1'], 60):
                mm = M.at(T)
                if mm is not None: cal.append((E['slug'], sp, m['type'], f(T), mm, float(m['win0'])))
            for fair_name in ('model', 'blend'):
                ff = f if fair_name == 'model' else (lambda T, f=f, M=M: None if M.at(T - C.QDELAY) is None else (f(T) + M.at(T - C.QDELAY)) / 2)
                for E_ in (0, 0.02, 0.05):
                    r = C.sim(pr, M, E['t0'], E['t1'], ff, m['win0'], E_, evs, LAG, m['reb'])
                    res.append((E['slug'], sp, m['type'], fair_name, E_, [sum(z[k] for z in r) for k in ('usd', 'em1', 'pnl', 'reb')]))
            r = C.sim(pr, M, E['t0'], E['t1'], None, m['win0'], 0, evs, LAG, m['reb'], gate=False)
            res.append((E['slug'], sp, m['type'], 'none', None, [sum(z[k] for z in r) for k in ('usd', 'em1', 'pnl', 'reb')]))
    print(dict(chk)); return res, cal
def report(res, cal, tag):
    import pandas as pd
    A = pd.DataFrame(cal, columns=['ev', 'sport', 'type', 'model', 'mkt', 'y'])
    out = dict(lag=LAG, forecast={}, runs=[], calibration={})
    for (sp, ty), g in list(A.groupby(['sport', 'type'])) + [(('all', 'all'), A)]:
        out['forecast'][f'{sp}/{ty}'] = dict(points=len(g), events=g.ev.nunique(), brier_model=round(C.brier(g.model, g.y), 4), brier_mkt=round(C.brier(g.mkt, g.y), 4),
                                            brier_blend=round(C.brier((g.model + g.mkt) / 2, g.y), 4), mean_abs_diff=round(float(np.mean(np.abs(g.model - g.mkt))), 4))
    for sp, g in A.groupby('sport'): out['calibration'][sp] = dict(model=C.calib_table(g.model, g.y), mkt=C.calib_table(g.mkt, g.y))
    for sp in sorted(set(A.sport)) + ['all']:
        for ty in ['all', 'moneyline', 'spreads', 'totals']:
            for fn, E_ in [('none', None)] + [(f, e) for f in ('model', 'blend') for e in (0, 0.02, 0.05)]:
                per = collections.defaultdict(lambda: np.zeros(4))
                for ev, s_, t, f, e, v in res:
                    if f == fn and e == E_ and (ty == 'all' or t == ty) and (sp == 'all' or s_ == sp): per[ev] += np.array(v)
                s = C.summarize(list(per.values()))
                out['runs'].append(dict(sport=sp, type=ty, fair=fn, E=E_, **s))
                if ty == 'all' or sp == 'all':
                    print(f"{sp:4}{ty:10}{fn:6}{'' if E_ is None else E_:>5} ev {s['events']:>4} $fill {s['usd']:>9} 1min+reb {s.get('net_1min_pct')}% {s.get('ci_1min')}  result+reb {s.get('net_result_pct')}% {s.get('ci_result')} = ${s.get('net_result_usd')}")
    print(json.dumps(out['forecast'], indent=0))
    json.dump(out, open(os.path.join(HERE, f'out_{tag}.json'), 'w'), indent=1)
    A.to_csv(os.path.join(HERE, f'out_forecast_{tag}.csv.gz'), index=False)
if __name__ == '__main__':
    res, cal = run(); report(res, cal, f'lag{LAG}')
