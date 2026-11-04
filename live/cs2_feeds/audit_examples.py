#!/usr/bin/env python3
"""Print sample tier-1 rows with pre/post bid, ask, mid, both target prices (4 Nov 2026). Usage: audit_examples.py QUEUEJSON CAPDIR..."""
import json, sys, os, io, contextlib, statistics as st, time
qj = json.load(open(sys.argv[1])); dirs = sys.argv[2:]
sys.argv = ['cs2_queue.py', '/tmp/_q_unused.json'] + dirs
with contextlib.redirect_stdout(io.StringIO()):
    exec(open('cs2_queue.py').read())
rs = [r for r in qj['rows'] if 'IEM' in r['title']]
n_above = 0; moves = []; out = []
for r in rs:
    cands = [k for k, v in tok.items() if v[0] == r['gid'] and v[1] == r['kind']]
    k = next((c for c in cands if mid(c, r['Tm'] + 6000) is not None and abs(mid(c, r['Tm'] + 6000) - r['mid_6']) < 5e-4), None)
    x = at(k, r['Tm'] - 2000); y = at(k, r['Tm'] + 6000)
    c = comp[k]; xc = at(c, r['Tm'] - 2000)
    above = x[3] <= r['P_new'] + 1e-9
    n_above += above; moves.append(r['mid_6'] - x[2]/2 - x[3]/2)
    out.append((r, k, x, y, xc, above))
print('rows', len(rs), 'P_new>=pre ask', n_above, 'median move pre-mid -> mid+6', round(st.median(moves), 3))
print('median spread pre', st.median([o[2][3]-o[2][2] for o in out]))
import random; random.seed(3)
for r, k, x, y, xc, above in random.sample(out, 5):
    ts = lambda ms: time.strftime('%H:%M:%S', time.gmtime(ms/1000))
    print(f"\n{r['title'][:40]} {r['kind']} outcome_idx={tok[k][2]}  Tm={ts(r['Tm'])}Z  WS R={ts(r['R'])}Z")
    print(f"  pre (Tm-2s, {ts(x[0])}): bid {x[2]} ask {x[3]} mid {(x[2]+x[3])/2:.3f} | median mid 45-90s before R {r['mid_pre']}")
    print(f"  other token same time: bid {xc[2]} ask {xc[3]}  (1-ask={1-xc[3]:.3f}, 1-bid={1-xc[2]:.3f})")
    print(f"  post (Tm+6s, {ts(y[0])}): bid {y[2]} ask {y[3]} mid {r['mid_6']}")
    print(f"  P_old = {r['mid_m2']} x 0.975 = {r['P_old']}   P_new = {r['mid_6']} x 0.975 = {r['P_new']}   P_new >= pre ask: {above}")
