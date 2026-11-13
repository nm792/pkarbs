import sys, runpy, numpy as np
sys.argv = ['point_delay.py'] + sys.argv[1:]
import builtins
src = open('point_delay.py').read().split("W, MINJ, CAUGHT = 30, 0.01, 0.5")[0]
g = {'__name__': 'x', '__file__': 'point_delay.py'}; exec(compile(src, 'point_delay.py', 'exec'), g)
C = g['C']; games = g['games']; run = g['run']
for W in (30, 120):
    for lag in (0, 10, 30):
        P = [run(x, lag, W, 0.01, 0.5, 500, 'onset') for x in games]
        s = C.summarize(P); n = sum(1 for p in P if p[0] > 0)
        print(f"W{W} lag{lag}: matches w/ fills {n}, filled ${s['usd']}, result {s['net_result_pct']}% {s['ci_result']} ex-top5 {s['ex_top5_result_pct']}% (${s['ex_top5_result_usd']})")
# placebo: flip side
for x in games:
    for e in x['E']:
        if 'j0on' in e: e['j0on'] = -e['j0on']
for W in (30, 120):
    for lag in (0, 10):
        s = C.summarize([run(x, lag, W, 0.01, 0.5, 500, 'onset') for x in games])
        print(f"PLACEBO (opposite side) W{W} lag{lag}: filled ${s['usd']}, 1min {s['net_1min_pct']}% result {s['net_result_pct']}% {s['ci_result']}")
