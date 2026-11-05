"""Failsafe guards for slow orders, Pinnacle/bet365-trigger tennis backtest (Nick 5 Nov 04:44Z).
Order latency per signal is drawn from the 30 measured Nautilus submit->OrderAccepted times
(agent/outbox/nautilus-order-latency-2026-11-05.csv). Guards:
  A(N): ack timeout. If the ack takes longer than N s, cancel; the order never rests
        (on late ack Nautilus cancels at once; ~0.13 s median residual exposure ignored).
  B(f): on ack, cancel if PM price has already moved >= f of the book's jump in our direction.
  C(X): skip the signal if it is older than X s when we are ready to send (receive delay R).
Usage: python3 guard_sim.py <oddspapi_dir>.  PM trades have 1 s timestamps, so sub-second
differences are only roughly resolved; fills are trade-based with queue ignored (optimistic)."""
import os, sys, csv, bisect, json
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(f'{HERE}/pin_trigger.py').read()
exec(compile(src[:src.index('out = dict(step=STEP')], 'pin_trigger_head', 'exec'))   # loads games, triggers, m0_for, H, C

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
LAT = np.array([float(r['submit_to_accepted_s']) for r in csv.DictReader(open(f'{ROOT}/agent/outbox/nautilus-order-latency-2026-11-05.csv')) if r['submit_to_accepted_s']])
print('latency samples', len(LAT), 'median', np.median(LAT), 'p90', np.percentile(LAT, 90), flush=True)

def run_ev(g, W, caught=0.5, max_gap=0.01, d=0.025, Q=500, B=None):
    tot = np.zeros(4); pr, M = g['pr'], g['M']
    E = [e for e in g['E'] if not e.get('skip')]
    if B is not None:
        keep = []
        for e in E:
            mk = M.at(e['on'] + e['lag'] - C.QDELAY)
            if mk is None: continue
            mv = (mk - e['m0']) if e['pj'] > 0 else (e['m0'] - mk)
            if mv < B * abs(e['pj']): keep.append(e)
        E = keep
    et = [e['on'] for e in E]
    for (T, _, ph, sell0, sz) in pr:
        i = bisect.bisect_right(et, T) - 1; e = None
        while i >= 0 and et[i] >= T - W - 5:
            c = E[i]
            if c['on'] + c['lag'] <= T <= c['on'] + c['lag'] + W: e = c; break
            i -= 1
        if e is None: continue
        tok = 0 if e['pj'] > 0 else 1
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

ND = int(os.environ.get('NDRAW', 60))
SCEN = [('no guard', None, None, 0.0), ('A 0.8 s', 0.8, None, 0.0), ('A 0.5 s', 0.5, None, 0.0), ('A 0.3 s', 0.3, None, 0.0),
        ('A 0.5 s + B 0.5', 0.5, 0.5, 0.0), ('A 0.5 s + B 0.25', 0.5, 0.25, 0.0), ('A 0.3 s + B 0.25', 0.3, 0.25, 0.0),
        ('R 0.5 s, A 0.5 s + B 0.25', 0.5, 0.25, 0.5), ('R 1.0 s, A 0.5 s + B 0.25', 0.5, 0.25, 1.0)]
out = dict(latency_samples=LAT.tolist(), draws=ND, results=[])
for bk, W in [('pinnacle', 5), ('pinnacle', 10), ('bet365', 5)]:
    gs = [g for g in games if len(g['books'].get(bk, [])) > 20]
    for g in gs: g['E'] = m0_for(g, triggers(g['books'][bk]))
    n = len(gs)
    for name, A, Bf, R in SCEN:
        rng = np.random.default_rng(1); rows = []
        for k in range(ND):
            sent = 0; skipped = 0
            for g in gs:
                for e in g['E']:
                    l = float(rng.choice(LAT)); e['lag'] = R + l
                    e['skip'] = A is not None and l > A
                    sent += 1; skipped += e['skip']
            P = [run_ev(g, W, B=Bf) for g in gs]; s = C.summarize(P, rng=np.random.default_rng(k), nb=400)
            rows.append((s['net_result_usd'] / n, s['ci_result_usd'][0] / n, s['ci_result_usd'][1] / n, s['ex_top5_result_pct'],
                         s.get('ex_top5_result_usd', 0) / n, sum(1 for p in P if p[0] > 0), skipped / max(1, sent)))
        a = np.array(rows, float); md = np.median(a, axis=0)
        r = dict(book=bk, W=W, scenario=name, result_per_match=round(md[0], 2), ci90=[round(md[1], 2), round(md[2], 2)],
                 draw_range_5_95=[round(x, 2) for x in np.percentile(a[:, 0], [5, 95])], ex_top5_pct=round(md[3], 1),
                 ex_top5_per_match=round(md[4], 2), matches_filled=int(md[5]), share_signals_cancelled=round(md[6], 2))
        out['results'].append(r)
        print(f"{bk} W{W} {name:28s} ${r['result_per_match']:6.2f}/match 90% [{r['ci90'][0]}, {r['ci90'][1]}] draws {r['draw_range_5_95']} ex-top5 {r['ex_top5_pct']}% (${r['ex_top5_per_match']}/match) filled {r['matches_filled']}/{n} cancelled {r['share_signals_cancelled']}", flush=True)
json.dump(out, open(f'{HERE}/out_guard_sim.json', 'w'), indent=1)
