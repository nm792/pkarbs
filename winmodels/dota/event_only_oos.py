"""Leak check: the offset is refined on FIRST-half events only, then the rule runs on SECOND-half events only."""
import sys, json, numpy as np
sys.path.insert(0, '..'); import align as A, align2 as B, align4 as F, event_only as E
off2 = {}
for r in E.R:
    d, pr, M, ev = E.get(r); c = F.coarse[r['match_id']]['off']; sgn = 1 if r['o0_rad'] else -1
    half = d['duration'] / 2
    evh = sorted([e for e in B.big(d) if e[0] < half] + [(t, 1 if rr else -1) for rr, t in d['kills'] if t < half])
    if len(evh) < 6: continue
    o, _ = F.refine(M, d['start_time'], evh, sgn, c); off2[r['match_id']] = o
    E.CACHE[r['match_id']] = (d, pr, M, [e for e in ev if e[0] >= half])
for k, o in off2.items(): E.AL[k] = dict(off=o)
R = [r for r in E.R if r['match_id'] in off2]
tr = [r for r in R if r['start'] < E.SPLIT]; te = [r for r in R if r['start'] >= E.SPLIT]
beta = np.array(json.load(open('out_event_only.json'))['beta'])
diff = [abs(off2[k] - F.AL4[k]) for k in off2 if k in F.AL4] if hasattr(F, 'AL4') else []
for name, rs in (('train', tr), ('holdout', te), ('all', R)):
    for lag in (0, 2, 5, 10):
        for W in (10, 30):
            s = E.run(rs, beta, lag, W)
            print(f"OOS {name} lag{lag} W{W}: games {s['events']} $fill {s['usd']} 1min {s.get('net_1min_pct')}% {s.get('ci_1min')} result {s.get('net_result_pct')}% ${s.get('net_result_usd')} {s.get('ci_result_usd')} ex-top5 {s.get('ex_top5_result_pct')}%", flush=True)
