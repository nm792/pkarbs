#!/usr/bin/env python3
"""Follow-up (4 Nov 2026): (a) rows where the new price is placeable BEFORE the market moves (a feed ahead of the
price could post there first); (b) lower-tier numbers: queue at the new price, prints there in 30 s, sports-WS lag vs
the price, and a slow-bot fill/markout estimate at our current feed (join at R at mid(R) x 0.975, cap CAP shares,
fills = prints at or below our price in [R, R+30 s] beyond the shares resting ahead, markout vs mid at R+60 s and
vs result-free mid at R+300 s). Usage: lowtier.py QUEUEJSON CAPDIR [CAPDIR...]"""
import json, sys, os, io, contextlib, statistics as st, collections
qj = json.load(open(sys.argv[1])); dirs = sys.argv[2:]
sys.argv = ['queue.py', '/tmp/_q_unused.json'] + dirs
with contextlib.redirect_stdout(io.StringIO()):
    exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'queue.py')).read())
def med(v):
    v = [x for x in v if x is not None]; return round(st.median(v), 1) if v else None
def tokof(r):
    cands = [k for k, v in tok.items() if v[0] == r['gid'] and v[1] == r['kind']]
    return next((c for c in cands if mid(c, r['Tm'] + 6000) is not None and abs(mid(c, r['Tm'] + 6000) - r['mid_6']) < 5e-4), None)
def prints_le(k, a, b, p):
    s = sum(sz for t, px, sz, sd in TR.get(k, []) if a <= t <= b and sd == 'SELL' and px <= p + 1e-9)
    c = comp.get(k)
    if c: s += sum(sz for t, px, sz, sd in TR.get(c, []) if a <= t <= b and sd == 'BUY' and (1 - px) <= p + 1e-9)
    return s
res = {}
for grp, rs in (('tier1', [r for r in qj['rows'] if 'IEM' in r['title']]), ('lower', [r for r in qj['rows'] if 'IEM' not in r['title']])):
    pre = []; slow = []; games = set()
    for r in rs:
        k = tokof(r)
        if not k: continue
        games.add(r['gid'])
        x = at(k, r['Tm'] - 2000)
        if x and x[3] is not None: pre.append((x[3] > r['P_new'] + 1e-9, size_at(k, r['Tm'] - 2000, r['P_new'])))
        R = r['R']; mR = mid(k, R)
        if mR is None: continue
        P = floor_t(mR * 0.975); ahead = size_at(k, R, P) or 0.0
        pr = prints_le(k, R, R + 30000, P)
        m60, m300 = mid(k, R + 60000), mid(k, R + 300000)
        slow.append(dict(lag=(R - r['Tm']) / 1000, ahead=ahead, prints=pr, P=P, m60=m60, m300=m300))
    out = dict(rows=len(rs), games=len(games), lag_s_median=med([s['lag'] for s in slow]),
               new_price_placeable_before_move=sum(1 for a, q in pre if a), new_price_q_then_median=med([q for a, q in pre if a]),
               slow_ahead_median=med([s['ahead'] for s in slow]), slow_prints30_total=round(sum(s['prints'] for s in slow)),
               slow_rows_with_prints=sum(1 for s in slow if s['prints'] > 0))
    for CAP in (100, 500):
        fills = []; pnl60 = pnl300 = 0.0
        for s in slow:
            f = min(CAP, max(0.0, s['prints'] - s['ahead']))
            if f > 0:
                fills.append(f)
                if s['m60'] is not None: pnl60 += f * (s['m60'] - s['P'])
                if s['m300'] is not None: pnl300 += f * (s['m300'] - s['P'])
        out['cap%d' % CAP] = dict(fill_rows=len(fills), shares=round(sum(fills)), usd_markout_60s=round(pnl60, 2),
                                  usd_markout_300s=round(pnl300, 2), usd_per_event_60s=round(pnl60 / max(1, len(slow)), 3))
    res[grp] = out
print(json.dumps(res, indent=1))
