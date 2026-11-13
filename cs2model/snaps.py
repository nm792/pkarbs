#!/usr/bin/env python3
"""Step 2b: per-map SNAPSHOT series (state at every feed message), robust to the ~12% of dropped events.
Per message: t, rn, c_h/c_a (map score), hside (1=T,2=CT for home team), alive_h/alive_a (None unless both rosters complete),
hp_h/hp_a, money_h/money_a, tmr (round start epoch from feed timer), plant (bomb planted seen in this round, from typeid 6), ev types seen.
Output pickle {mapkey: dict(meta, rows)}"""
import sys, json, gzip, collections, pickle
msgs = collections.defaultdict(list)
for l in gzip.open(sys.argv[1], 'rt'):
    r = json.loads(l); msgs[(r['mid'], r['map'])].append(r)
OUT = {}
for key, L in msgs.items():
    L.sort(key=lambda r: r['t'])
    rows = []
    for r in L:
        h, a = r['h'], r['a']
        full = len(h['pl']) == 5 and len(a['pl']) == 5 and all(len(q) >= 9 for q in h['pl'] + a['pl'])
        rows.append(dict(t=r['t'], rn=r['rn'], ch=h['c'], ca=a['c'], hs=h['side'],
            al_h=sum(1 for q in h['pl'] if q[3] > 0) if full else None, al_a=sum(1 for q in a['pl'] if q[3] > 0) if full else None,
            alf_h=sum(1 for q in h['pl'] if q[2]) if full else None, alf_a=sum(1 for q in a['pl'] if q[2]) if full else None,
            hp_h=sum(q[3] for q in h['pl']) if full else None, hp_a=sum(q[3] for q in a['pl']) if full else None,
            mo_h=sum(q[1] for q in h['pl']) if full else None, mo_a=sum(q[1] for q in a['pl']) if full else None,
            tmr=(r['tm'] or [None] * 3)[2], ph=(r['tm'] or [None])[0],
            adr_h=(sum(q[8] for q in h['pl']) / 5.0) if full else None, adr_a=(sum(q[8] for q in a['pl']) / 5.0) if full else None, k_h=sum(q[4] for q in h['pl']) if full else None, k_a=sum(q[4] for q in a['pl']) if full else None, d_h=sum(q[5] for q in h['pl']) if full else None, d_a=sum(q[5] for q in a['pl']) if full else None,
            tys=[e['typeid'] for e in r['ev']], st=r['st'], wp_h=[q[6] for q in h['pl']] if full else None, wp_a=[q[6] for q in a['pl']] if full else None))
    OUT['%s|%s' % key] = dict(meta=dict(mid=key[0], map=key[1], box=L[0]['box'], home_id=L[-1]['h']['id'], away_id=L[-1]['a']['id'], final=(L[-1]['h']['c'], L[-1]['a']['c']), status=L[-1]['st']), rows=rows)
pickle.dump(OUT, open(sys.argv[2], 'wb'))
print('maps', len(OUT), 'rows', sum(len(v['rows']) for v in OUT.values()))
