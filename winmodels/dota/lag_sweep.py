"""4 Nov: event-only rule vs feed delay (lag after the market-aligned event), leak-controlled as event_only_oos.py."""
import sys, io, contextlib
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    src = open('event_only_oos.py').read().split("for name, rs in")[0]
    exec(src)
import json
out = []
for name, rs in (('holdout', te), ('all', R)):
    for W in (10, 30):
        for lag in (0, 5, 10, 15, 20, 30, 45, 60, 90, 120, 180):
            s = E.run(rs, beta, lag, W)
            row = dict(set=name, W=W, lag=lag, games=s['events'], usd=s['usd'], m1=s.get('net_1min_pct'), ci1=s.get('ci_1min'),
                       res_pct=s.get('net_result_pct'), res_usd=s.get('net_result_usd'), ci_res=s.get('ci_result_usd'), ex5=s.get('ex_top5_result_pct'), n_games_set=len(rs))
            out.append(row); print(json.dumps(row, default=float), flush=True)
json.dump(out, open('out_lag_sweep.json', 'w'), indent=0, default=float)
