"""Placebo: same OOS setup (offset from first half, test on second half), but events shifted by large lags."""
import sys, json, numpy as np
sys.path.insert(0, '..')
import event_only_oos as O, event_only as E
beta = np.array(json.load(open('out_event_only.json'))['beta'])
for lag in (-300, -120, -60, 20, 30, 60, 120, 300):
    s = E.run(O.R, beta, lag, 10)
    print(f"PLACEBO all lag{lag} W10: games {s['events']} $fill {s['usd']} 1min {s.get('net_1min_pct')}% {s.get('ci_1min')} result {s.get('net_result_pct')}% ${s.get('net_result_usd')} ex-top5 {s.get('ex_top5_result_pct')}%", flush=True)
