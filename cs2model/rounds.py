#!/usr/bin/env python3
"""Step 2: from cs2msgs.jsonl.gz build per-map round tables.  Output rounds.json: {mapkey: {meta, rounds:[...]}}
Round record: n, t_start (receive), tmr_start (feed epoch), home_side (1=T,2=CT; side at that round), score_h/score_a before round,
 money_h/money_a (sum, from latest message at/before first kill or +20s of round start, only if 5 players listed),
 kills [(t_recv, killer_side, victim_side, victim_name, hs)], plant t, defuse t, end (t_recv, winner_side, wintype), winner_home(bool)."""
import sys, json, gzip, collections
msgs = collections.defaultdict(list)
for l in gzip.open(sys.argv[1], 'rt'):
    r = json.loads(l); msgs[(r['mid'], r['map'])].append(r)
OUT = {}
for key, L in msgs.items():
    L.sort(key=lambda r: r['t'])
    evs = {}
    for r in L:
        for e in r['ev']:
            ix = e['index']
            if ix not in evs: evs[ix] = (r['t'], e, r['rn'], r['tm'])
    ordered = sorted(evs.items())
    rounds = collections.OrderedDict()
    cur = None
    # build rounds from events: typeid 1 starts a round; use msg round_num as label of message carrying event
    for ix, (t, e, rn, tm) in ordered:
        ty = e['typeid']
        if rn is None: continue
        R = rounds.setdefault(rn, dict(n=rn, kills=[], plant=None, defuse=None, start=None, end=None, tmr=tm[2] if tm else None))
        if ty == 1 and R['start'] is None: R['start'] = t
        elif ty == 8: R['kills'].append((t, e['killerside'], e['victimside'], e['victimname'], e.get('headshot', 0)))
        elif ty == 3 and R['plant'] is None: R['plant'] = t
        elif ty == 4 and R['defuse'] is None: R['defuse'] = t
        elif ty == 2 and R['end'] is None: R['end'] = (t, e['winner_side'], e['wintype'], e['t_score'], e['ct_score'])
    # score/side/money per round from messages: take last message whose rn==n before round-end; scores at that moment are pre-round
    info = {}
    for r in L:
        rn = r['rn']
        if rn is None: continue
        d = info.setdefault(rn, dict(first=r, pre=None))
        # money snapshot: message within first 25 s of the round's start with 5 players each
    meta = dict(mid=key[0], map=key[1], box=L[0]['box'], n_msgs=len(L), t0=L[0]['t'], t1=L[-1]['t'], status=L[-1]['st'],
                final=(L[-1]['h']['c'], L[-1]['a']['c']))
    # per round: first message of that round -> pre-round score + sides; money from messages with full rosters
    for rn, R in rounds.items():
        msgs_r = [r for r in L if r['rn'] == rn]
        if not msgs_r: continue
        f = msgs_r[0]
        R['score_h'], R['score_a'] = f['h']['c'], f['a']['c']
        R['home_side'] = f['h']['side']
        R['t_first_msg'] = f['t']
        # money: last message before first kill (or first 30s) that lists 5+5 players
        tcut = (R['kills'][0][0] if R['kills'] else (R['end'][0] if R['end'] else f['t'] + 30)) - 0.5
        best = None
        for r in msgs_r:
            if r['t'] > tcut: break
            if len(r['h']['pl']) == 5 and len(r['a']['pl']) == 5 and all(len(q) >= 6 for q in r['h']['pl'] + r['a']['pl']):
                best = r
        if best:
            R['money_h'] = sum(q[1] for q in best['h']['pl']); R['money_a'] = sum(q[1] for q in best['a']['pl'])
            R['money_t'] = best['t']
    OUT['%s|%s' % key] = dict(meta=meta, rounds=list(rounds.values()))
json.dump(OUT, open(sys.argv[2], 'w'))
nm = len(OUT); nr = sum(len(v['rounds']) for v in OUT.values())
nmoney = sum(1 for v in OUT.values() for R in v['rounds'] if 'money_h' in R)
print('maps', nm, 'rounds', nr, 'rounds with money', nmoney, 'with end', sum(1 for v in OUT.values() for R in v['rounds'] if R['end']))
