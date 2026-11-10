#!/usr/bin/env python3
"""Step 6: build per-snapshot samples (every >=5 s, full rosters) with state features and labels.
Output samples.pkl: list of dicts + per-map info.  Label y_round = home wins this round, y_map = home wins the map (final score)."""
import sys, json, pickle, bisect, collections
from cs2lib import *
S = pickle.load(open(sys.argv[1], 'rb')); P = json.load(open(sys.argv[2]))['pairs']; B = pickle.load(open(sys.argv[3], 'rb'))['book']
T = {k: [x[0] for x in v] for k, v in B.items()}
def mid(tk, t, maxage=30):
    ts = T.get(tk)
    if not ts: return None
    i = bisect.bisect_right(ts, t) - 1
    if i < 0 or t - ts[i] > maxage: return None
    return (B[tk][i][1] + B[tk][i][2]) / 2
samples = []; maps = {}
for key, v in S.items():
    rows = v['rows']; fin = v['meta']['final']
    if v['meta']['status'] not in (3, 8, 10) and False: pass
    # orientation: home side during first half = majority hs for rows with 1<=n<=11 (fallback n 13..23 flipped)
    cnt = collections.Counter(r['hs'] for r in rows if 1 <= r['ch'] + r['ca'] <= 11 and r['hs'] in (1, 2))
    if cnt: o = cnt.most_common(1)[0][0]
    else:
        c2 = collections.Counter(r['hs'] for r in rows if 13 <= r['ch'] + r['ca'] <= 23 and r['hs'] in (1, 2))
        if not c2: continue
        o = 3 - c2.most_common(1)[0][0]
    done = fin[0] >= 13 or fin[1] >= 13 or (fin[0] + fin[1] >= 24 and abs(fin[0] - fin[1]) >= 2)
    # finished map only if the last rows show a decided score
    y_map = 1 if fin[0] > fin[1] else 0
    # rounds are identified by the feed round-start epoch (tmr). Outcome = score change inside the tmr group (exactly +1 in total).
    groups = collections.OrderedDict()
    for r in rows:
        if r['tmr']: groups.setdefault(r['tmr'], []).append(r)
    outcome = {}; tmr_pre = {}; tmr_end = {}
    for tm, g in groups.items():
        f, l = g[0], g[-1]
        n0 = f['ch'] + f['ca']; dh, da = l['ch'] - f['ch'], l['ca'] - f['ca']
        tmr_pre[tm] = (f['ch'], f['ca'])
        if (dh, da) in ((1, 0), (0, 1)) and l['t'] - f['t'] < 200:
            outcome[tm] = 1 if dh else 0
            # first row where score changed = end of live round
            tmr_end[tm] = next(r['t'] for r in g if (r['ch'], r['ca']) != (f['ch'], f['ca']))
    rounds_info = [(tm, tmr_end[tm], sum(tmr_pre[tm]), home_is_T(o, sum(tmr_pre[tm])), outcome[tm]) for tm in outcome]
    p = P.get(key); pre = None; t_first = None
    if p:
        for r in rows:
            if r['tmr'] and r['ch'] + r['ca'] == 0 and r['al_h'] is not None and r['t'] - r['tmr'] >= 0:
                t_first = r['t']; break
        if t_first:
            pre = mid(p['tok_home'], t_first, 300)
            if pre is None:
                ts_ = T.get(p['tok_home'], []); i = bisect.bisect_left(ts_, t_first)
                if i < len(ts_) and ts_[i] - t_first < 300: pre = (B[p['tok_home']][i][1] + B[p['tok_home']][i][2]) / 2
    maps[key] = dict(o=o, final=fin, y_map=y_map, pre=pre, t0=rows[0]['t'], t1=rows[-1]['t'], paired=bool(p), outcome=outcome, rounds=rounds_info, complete=done, tourn=(p or {}).get('tournament'))
    last_t = {}; plant = {}; money0 = {}
    for r in rows:
        tm = r['tmr']
        if not tm or tm not in outcome: continue
        h0, a0 = tmr_pre[tm]; n = h0 + a0
        if (r['ch'], r['ca']) != (h0, a0): continue          # round already decided
        if 6 in r['tys']: plant.setdefault(tm, r['t'])
        if r['al_h'] is None: continue
        el = r['t'] - tm
        if tm not in money0 and 0 <= el <= 25: money0[tm] = (r['mo_h'] - r['mo_a'], r['mo_h'], r['mo_a'])
        if not (6 <= el <= 125): continue
        if r['t'] - last_t.get(tm, -1e9) < 5: continue
        last_t[tm] = r['t']
        pt = plant.get(tm)
        samples.append(dict(key=key, t=r['t'], tmr=tm, t_end=tmr_end[tm], n=n, h=h0, a=a0, el=el, al_h=r['al_h'], al_a=r['al_a'], hp_h=r['hp_h'], hp_a=r['hp_a'], adr_h=r['adr_h'], adr_a=r['adr_a'], k_h=r['k_h'], k_a=r['k_a'],
                            planted=1 if pt is not None else 0, tplant=(r['t'] - pt) if pt is not None else 0.0, mdiff=money0.get(tm, (0, 0, 0))[0], has_money=tm in money0,
                            homeT=home_is_T(o, n), y_round=outcome[tm], y_map=y_map))
print('maps', len(maps), 'paired', sum(1 for m in maps.values() if m['paired']), 'with pre-map price', sum(1 for m in maps.values() if m['pre'] is not None), 'samples', len(samples))
pickle.dump(dict(samples=samples, maps=maps), open(sys.argv[4], 'wb'))
