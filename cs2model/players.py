#!/usr/bin/env python3
"""Step 11: per-player features from cs2msgs: (1) weapon-id price table estimated from money drops when a player's held weapon changes during a round's first 30 s
(median drop per weapon id, n>=8), (2) per-map player lines (name, team id, kills, deaths, adr at last full row) for rolling player ratings,
(3) per-(map, tmr) team equipment value = sum of price(weapon) over the five players at el=25-40 s (after buy phase) for rows with alive players.
Outputs players.json {wprice, plines, equip}."""
import sys, json, gzip, collections, statistics as st
msgs = collections.defaultdict(list)
for l in gzip.open(sys.argv[1], 'rt'):
    r = json.loads(l); msgs[(r['mid'], r['map'])].append(r)
drops = collections.defaultdict(list)
for key, L in msgs.items():
    L.sort(key=lambda r: r['t']); prev = {}
    for r in L:
        tm = (r['tm'] or [0, 0, 0])[2]
        if not tm: continue
        el = r['t'] - tm
        for team in ('h', 'a'):
            for q in r[team]['pl']:
                if len(q) < 10: continue
                name, money, alive, hp, k, d, wid, s6, adr, ast = q[:10]
                pk = (team, name)
                if pk in prev:
                    pm, pw, ptm = prev[pk]
                    if ptm == tm and 0 <= el <= 30 and wid and wid != pw and 150 <= pm - money <= 6500: drops[wid].append(pm - money)
                prev[pk] = (money, wid, tm)
wprice = {w: st.median(v) for w, v in drops.items() if len(v) >= 8}
print('weapon ids with price estimate', len(wprice), 'of', len(drops), 'seen; examples', sorted(((round(p), w[:6], len(drops[w])) for w, p in wprice.items()))[:6], '...', sorted(((round(p), w[:6], len(drops[w])) for w, p in wprice.items()))[-6:])
equip = {}; plines = {}
for key, L in msgs.items():
    L.sort(key=lambda r: r['t']); per = {}
    last_full = None
    for r in L:
        tm = (r['tm'] or [0, 0, 0])[2]
        if len(r['h']['pl']) == 5 and len(r['a']['pl']) == 5 and all(len(q) >= 10 for q in r['h']['pl'] + r['a']['pl']): last_full = r
        if not tm or tm in per: continue
        el = r['t'] - tm
        if 28 <= el <= 45 and len(r['h']['pl']) == 5 and len(r['a']['pl']) == 5 and all(len(q) >= 10 for q in r['h']['pl'] + r['a']['pl']):
            eh = sum(wprice.get(q[6], 0) for q in r['h']['pl'] if q[3] > 0); ea = sum(wprice.get(q[6], 0) for q in r['a']['pl'] if q[3] > 0)
            known = sum(1 for q in r['h']['pl'] + r['a']['pl'] if q[6] in wprice)
            per[tm] = (eh, ea, known)
    equip['%s|%s' % key] = {str(k): v for k, v in per.items()}
    if last_full:
        plines['%s|%s' % key] = dict(home=[(q[0], q[4], q[5], q[8]) for q in last_full['h']['pl']], away=[(q[0], q[4], q[5], q[8]) for q in last_full['a']['pl']], t=last_full['t'])
json.dump(dict(wprice=wprice, plines=plines, equip=equip), open(sys.argv[2], 'w'))
print('maps with equip', sum(1 for v in equip.values() if v), 'rounds with equip', sum(len(v) for v in equip.values()))
