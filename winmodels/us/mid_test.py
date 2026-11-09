"""NBA plain rule (no guards) under different 'market price' references, to see how much of the loss is reference bias."""
import sys, os, json
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
import common as C, nba_guard as NG
games = NG.prep()
for mode, age in (('pair', 120), ('pair', 20), ('pair', 5), ('last', 0)):
    C.MID_MODE, C.MID_AGE = mode, age
    for g in games: g['mk'] = [(m, pr, C.Mid(pr)) for m, pr, _ in g['mk']]
    s = C.summarize([NG.run_game(g, 10, 0, 0, False) for g in games])
    print(f"mid={mode} age<={age}s: $fill {s['usd']} 1min {s['net_1min_pct']}% {s['ci_1min']} result {s['net_result_pct']}% {s['ci_result']} ex-top5 {s['ex_top5_result_pct']}%", flush=True)
