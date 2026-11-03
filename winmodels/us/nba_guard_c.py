"""NBA guards rerun with the corrected fill rule: only prints within max_gap of our bid fill us (see fillcheck/)."""
import sys, os, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
import common as C, nba_guard as NG
games = NG.prep(); res = []
for mg in (0.01, 0.03):
    for name, lag, pull, E_, veto in [('plain', 10, 0, 0, False), ('guard lag3 pull30', 3, 30, 0, False), ('guard lag10 pull30', 10, 30, 0, False),
                                      ('veto E2 lag10', 10, 0, 0.02, True), ('veto E5 lag10', 10, 0, 0.05, True), ('guard+veto E5 lag3', 3, 30, 0.05, True), ('guard+veto E5 lag10', 10, 30, 0.05, True)]:
        s = C.summarize([NG.run_game(g, lag, pull, E_, veto, mg) for g in games])
        res.append(dict(max_gap=mg, variant=name, **s))
        print(f"gap<={mg} {name:22} $fill {s['usd']:>8} 1min {s['net_1min_pct']:>6}% {s['ci_1min']} result {s['net_result_pct']:>6}% {s['ci_result']} ${s['net_result_usd']} | ex-top5 {s['ex_top5_result_pct']}% ${s['ex_top5_result_usd']}", flush=True)
json.dump(res, open(os.path.join(HERE, 'out_nba_guard_corrected.json'), 'w'), indent=1)
