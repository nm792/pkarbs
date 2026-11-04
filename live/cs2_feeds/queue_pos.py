#!/usr/bin/env python3
"""Queue position after we join, and where the new queue comes from (4 Nov 2026).
For each event row (queue.py output) we join at the new price P_new at the first second it is placeable as a maker
(best ask above it), with 5 shares. Shares ahead of us then shrink when the level loses size:
  optimistic: cancels hit the queue pro-rata (ahead shrinks by removed x ahead/size), fills come off the front
  pessimistic: cancels come from the back first, so ahead only shrinks when the level drops below it: ahead=min(ahead,size)
Size added later always queues behind us. Also: in the second the new level fills up, how much bid size disappeared
from the other bid levels of that token (same makers moving their orders up) versus how much was added at P_new.
Usage: queue_pos.py QUEUEJSON CAPDIR [CAPDIR...]"""
import json, sys, os, io, contextlib, statistics as st
qj = json.load(open(sys.argv[1])); dirs = sys.argv[2:]
sys.argv = ['queue.py', '/tmp/_q_unused.json'] + dirs
with contextlib.redirect_stdout(io.StringIO()):
    exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'queue.py')).read())
def med(v):
    v = [x for x in v if x is not None]; return round(st.median(v), 1) if v else None
res = {}
for grp, rs in (('tier1', [r for r in qj['rows'] if 'IEM' in r['title']]), ('other', [r for r in qj['rows'] if 'IEM' not in r['title']])):
    out = []
    for r in rs:
        cands = [k for k, v in tok.items() if v[0] == r['gid'] and v[1] == r['kind']]
        k = next((c for c in cands if mid(c, r['Tm'] + 6000) is not None and abs(mid(c, r['Tm'] + 6000) - r['mid_6']) < 5e-4), None)
        if not k: continue
        P = r['P_new']; T0 = None
        for o in range(-10, 31):
            x = at(k, r['Tm'] + o * 1000)
            if x and x[3] is not None and x[3] > P + 1e-9: T0 = o; break
        if T0 is None: continue
        J = r['Tm'] + T0 * 1000
        q0 = size_at(k, J, P); ao = ap = q0; prev = q0; d = {}
        fil = 0.0
        for s in range(1, 31):
            q = size_at(k, J + s * 1000, P)
            if q is None: continue
            f = filled_at(k, J + (s - 2) * 1000, J + s * 1000, P) if False else filled_at(k, J + (s - 1) * 1000, J + s * 1000 - 1, P)
            fil += f
            rem = max(0.0, prev - q)
            if prev > 0: ao = max(0.0, ao - min(f, ao) - max(0.0, rem - f) * ao / prev)
            ap = min(ap, q)
            prev = q
            if s in (5, 10, 30): d[s] = (round(ao), round(ap))
        # same-maker signature in the step the level filled up
        jump = None
        for o in range(-10, 31):
            a, b = size_at(k, r['Tm'] + (o - 1) * 1000, P), size_at(k, r['Tm'] + o * 1000, P)
            if a is not None and b is not None and a < 100 and b >= 100:
                xa, xb = at(k, r['Tm'] + (o - 1) * 1000), at(k, r['Tm'] + o * 1000)
                gone = sum(max(0.0, s - xb[1].get(p, 0.0)) for p, s in xa[1].items() if p != P)
                jump = (b - a, gone); break
        out.append(dict(q0=q0, ahead5=d.get(5), ahead10=d.get(10), ahead30=d.get(30), fills30=round(fil), jump=jump))
    res[grp] = dict(rows=len(out), ahead_at_join_median=med([o['q0'] for o in out]),
                    ahead_after_5s_opt_pess=(med([o['ahead5'][0] for o in out if o['ahead5']]), med([o['ahead5'][1] for o in out if o['ahead5']])),
                    ahead_after_10s_opt_pess=(med([o['ahead10'][0] for o in out if o['ahead10']]), med([o['ahead10'][1] for o in out if o['ahead10']])),
                    ahead_after_30s_opt_pess=(med([o['ahead30'][0] for o in out if o['ahead30']]), med([o['ahead30'][1] for o in out if o['ahead30']])),
                    rows_front_by_30s_opt=sum(1 for o in out if o['ahead30'] and o['ahead30'][0] < 5),
                    rows_front_by_30s_pess=sum(1 for o in out if o['ahead30'] and o['ahead30'][1] < 5),
                    prints_at_P_new_30s_total=sum(o['fills30'] for o in out), rows_with_prints=sum(1 for o in out if o['fills30'] > 0),
                    jump_added_sum=round(sum(o['jump'][0] for o in out if o['jump'])),
                    jump_gone_elsewhere_sum=round(sum(o['jump'][1] for o in out if o['jump'])), jump_rows=sum(1 for o in out if o['jump']))
print(json.dumps(res, indent=1))
