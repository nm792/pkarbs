#!/usr/bin/env python3
"""Step 2 (v2): per-map round tables from cs2msgs.jsonl.gz, splitting rounds by the event sequence (typeid 1 = live start,
8 = kill, 6 = bomb plant (carries alive counts), 2 = round end), not by the message round_num.
A round is 'clean' when every one of its events was first seen in a message carrying <=3 events (real-time arrival, not a backlog dump).
Output JSON: {mapkey: {meta, rounds}}; round = n, t0 (receive time of start), pre-score h/a, home_side(1=T,2=CT), money_h/a (cash after buys, at start),
kills [(t, killer_side, victim_side, victim)], plant (t, ct_alive, t_alive) , end (t, winner_side, wintype), clean."""
import sys, json, gzip, collections
msgs = collections.defaultdict(list)
for l in gzip.open(sys.argv[1], 'rt'):
    r = json.loads(l); msgs[(r['mid'], r['map'])].append(r)
OUT = {}
for key, L in msgs.items():
    L.sort(key=lambda r: r['t'])
    first = {}
    for r in L:
        for e in r['ev']:
            if e['index'] not in first: first[e['index']] = (r['t'], e, r, len(r['ev']))
    seq = [first[i] for i in sorted(first)]
    rounds = []; cur = None
    for t, e, r, ne in seq:
        ty = e['typeid']
        if ty == 1:
            if cur: rounds.append(cur)
            cur = dict(n=len(rounds) + 1, t0=t, pre_h=r['h']['c'], pre_a=r['a']['c'], home_side=r['h']['side'], kills=[], plant=None, end=None, clean=(ne <= 3),
                       tmr=(r['tm'] or [None] * 3)[2], rn=r['rn'])
            # money snapshot: latest message at/before t+20s with full rosters, first message after start
            cur['_t'] = t
        elif cur is None: continue
        elif ty == 8:
            cur['kills'].append((t, e['killerside'], e['victimside'], e['victimname'])); cur['clean'] &= (ne <= 3)
        elif ty == 6 and cur['plant'] is None:
            cur['plant'] = (t, e['ctplayers'], e['tplayers']); cur['clean'] &= (ne <= 3)
        elif ty == 2 and cur['end'] is None:
            cur['end'] = (t, e['winner_side'], e['wintype']); cur['clean'] &= (ne <= 3)
    if cur: rounds.append(cur)
    # money at start per round
    Lt = [r['t'] for r in L]
    import bisect
    for R in rounds:
        i = bisect.bisect_left(Lt, R['t0'] - 1.0)
        best = None
        for r in L[i:i + 40]:
            if r['t'] > R['t0'] + 15: break
            if r['rn'] == R['rn'] and len(r['h']['pl']) == 5 and len(r['a']['pl']) == 5 and all(len(q) >= 7 for q in r['h']['pl'] + r['a']['pl']):
                best = r; break
        if best:
            R['money_h'] = sum(q[1] for q in best['h']['pl']); R['money_a'] = sum(q[1] for q in best['a']['pl'])
            R['alive_h0'] = sum(1 for q in best['h']['pl'] if q[2]); R['alive_a0'] = sum(1 for q in best['a']['pl'] if q[2])
            R['wpn_h'] = [q[6] for q in best['h']['pl']]; R['wpn_a'] = [q[6] for q in best['a']['pl']]
            R['kd_h'] = [(q[4], q[5]) for q in best['h']['pl']]; R['kd_a'] = [(q[4], q[5]) for q in best['a']['pl']]
        R.pop('_t', None)
    f = L[-1]
    OUT['%s|%s' % key] = dict(meta=dict(mid=key[0], map=key[1], box=L[0]['box'], n_msgs=len(L), t0=L[0]['t'], t1=L[-1]['t'], status=f['st'],
        home_id=f['h']['id'], away_id=f['a']['id'], final=(f['h']['c'], f['a']['c'])), rounds=rounds)
json.dump(OUT, open(sys.argv[2], 'w'))
print('maps', len(OUT), 'rounds', sum(len(v['rounds']) for v in OUT.values()), 'with end', sum(1 for v in OUT.values() for R in v['rounds'] if R['end']),
      'clean+end', sum(1 for v in OUT.values() for R in v['rounds'] if R['end'] and R['clean']), 'with money', sum(1 for v in OUT.values() for R in v['rounds'] if 'money_h' in R))
