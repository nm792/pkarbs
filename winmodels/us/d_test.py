"""NBA plain rule at different depths below the market (d), mid reference as in the backtests."""
import sys, os
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
import common as C, nba_guard as NG
games = NG.prep()
for d in (0.0025, 0.005, 0.01, 0.015, 0.025, 0.05):
    C.D = d
    import functools
    per = []
    for g in games:
        E = g['E']; tot = [0, 0, 0, 0]
        for m, pr, M in g['mk']:
            r = C.sim(pr, M, E['t0'], E['t1'], None, m['win0'], 0, (), 10, m['reb'], d=d, gate=False)
            for z in r:
                for j, k in enumerate(('usd', 'em1', 'pnl', 'reb')): tot[j] += z[k]
        per.append(tot)
    s = C.summarize(per)
    print(f"d={d}: $fill {s['usd']} 1min {s['net_1min_pct']}% {s['ci_1min']} result {s['net_result_pct']}% {s['ci_result']} ex-top5 {s['ex_top5_result_pct']}%", flush=True)
