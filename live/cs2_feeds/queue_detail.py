#!/usr/bin/env python3
"""Second-by-second detail behind queue.py (4 Nov 2026): when does the new price level become placeable as a maker
(best ask above it) and how big is the queue there at that moment; plus a no-event control for churn at the
2.5%-under-mid level. Usage: queue_detail.py QUEUEJSON CAPDIR [CAPDIR...]"""
import json, sys, os, random, statistics as st, collections
sys.argv = [sys.argv[0], '/dev/null'] + sys.argv[2:] if False else sys.argv
qj = json.load(open(sys.argv[1])); dirs = sys.argv[2:]
sys.argv = ['queue.py', '/tmp/_q_unused.json'] + dirs
import io, contextlib
with contextlib.redirect_stdout(io.StringIO()):
    exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'queue.py')).read())
OF = qj['offsets_s']
def med(v):
    v = [x for x in v if x is not None]; return round(st.median(v)) if v else None
def p(v, q):
    v = sorted(x for x in v if x is not None); return v[int(q * (len(v) - 1))] if v else None
out = {}
for grp, rs in (('tier1', [r for r in qj['rows'] if 'IEM' in r['title']]), ('other', [r for r in qj['rows'] if 'IEM' not in r['title']])):
    prof = {o: dict(q_old=med([r['q_old'][OF.index(o)] for r in rs]), q_new=med([r['q_new'][OF.index(o)] for r in rs])) for o in range(-10, 11)}
    pl = []
    for r in rs:
        t = None
        for o in range(-10, 31):
            x = at(next(k for k, v in tok.items() if v[0] == r['gid'] and v[1] == r['kind'] and abs((mid(k, r['Tm'] + 6000) or 0) - r['mid_6']) < 1e-6) if False else None, 0) if False else None
        pl.append(r)
    # placeable second: first offset >= -10 where best ask > P_new (needs token id: recover from tok + mid match)
    det = []
    for r in rs:
        cands = [k for k, v in tok.items() if v[0] == r['gid'] and v[1] == r['kind']]
        k = next((c for c in cands if mid(c, r['Tm'] + 6000) is not None and abs(mid(c, r['Tm'] + 6000) - r['mid_6']) < 5e-4), None)
        if not k: continue
        T0 = None
        for o in range(-10, 31):
            x = at(k, r['Tm'] + o * 1000)
            if x and x[3] is not None and x[3] > r['P_new'] + 1e-9 and (x[2] is None or x[2] >= r['P_new'] - 1e-9 or True):
                if o >= -10 and (at(k, r['Tm'] + (o - 1) * 1000) or (0, 0, 0, 0))[3] is not None:
                    T0 = o; break
        q0 = None if T0 is None else size_at(k, r['Tm'] + T0 * 1000, r['P_new'])
        q1 = None if T0 is None else size_at(k, r['Tm'] + (T0 + 1) * 1000, r['P_new'])
        bb0 = None if T0 is None else at(k, r['Tm'] + T0 * 1000)[2]
        det.append(dict(T0=T0, q_at_T0=q0, q_at_T0p1=q1, ticks_below_bb=None if bb0 is None else round((bb0 - r['P_new']) / tick(r['P_new']))))
    out[grp] = dict(rows=len(rs), profile=prof,
                    placeable_s_median=med([d['T0'] for d in det]),
                    q_when_first_placeable_median=med([d['q_at_T0'] for d in det]),
                    q_when_first_placeable_p25=p([d['q_at_T0'] for d in det], .25),
                    q_1s_after_placeable_median=med([d['q_at_T0p1'] for d in det]),
                    rows_lt100_when_placeable=sum(1 for d in det if d['q_at_T0'] is not None and d['q_at_T0'] < 100),
                    rows_with_T0=sum(1 for d in det if d['T0'] is not None))
# no-event control: tier-1 tokens, times with no WS round event within 90 s, P = floor(mid x 0.975); churn over 40 s
random.seed(1)
evR = collections.defaultdict(list)
for e in events: evR[e['gid']].append(e['R'])
ctl = []
for k, (g, kind, i) in tok.items():
    if 'IEM' not in gid_names.get(g, '') or k not in books or len(books[k]) < 100: continue
    t0, t1 = bk_t[k][0] + 60000, bk_t[k][-1] - 60000
    for _ in range(40):
        T = random.uniform(t0, t1)
        if any(abs(T - R) < 90000 for R in evR[g]): continue
        m = mid(k, T)
        if m is None or m < 0.08 or m > 0.92: continue
        P = floor_t(m * 0.975); qs = [size_at(k, T + o * 1000, P) for o in range(-10, 31)]
        if None in qs or qs[0] < 100: continue
        rem = sum(max(0, a - b) for a, b in zip(qs, qs[1:])); add = sum(max(0, b - a) for a, b in zip(qs, qs[1:]))
        ctl.append(dict(q0=qs[0], left15=min(qs[0], qs[15]), left40=min(qs[0], qs[-1]), rem=rem, add=add))
out['control_no_event_tier1'] = dict(n=len(ctl), q_median=med([c['q0'] for c in ctl]),
    share_left_after_15s=round(sum(c['left15'] for c in ctl) / max(1, sum(c['q0'] for c in ctl)), 2),
    share_left_after_40s=round(sum(c['left40'] for c in ctl) / max(1, sum(c['q0'] for c in ctl)), 2),
    removed_per_window_median=med([c['rem'] for c in ctl]), removed_per_window_over_q=round(sum(c['rem'] for c in ctl) / max(1, sum(c['q0'] for c in ctl)), 2))
ev1 = [r for r in qj['rows'] if 'IEM' in r['title'] and (r['q_old'][OF.index(-10)] or 0) >= 100]
out['event_tier1_removed_over_q'] = round(sum(r['old_removed'] for r in ev1) / max(1, sum(r['q_old'][OF.index(-10)] for r in ev1)), 2)
print(json.dumps(out, indent=1))
