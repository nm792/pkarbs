"""Live NBA feed delay from poll.py output: for each score change, receive time minus NBA official timeActual,
for the NBA liveData S3 feed and ESPN summary. Rows seen in a game's first poll (backlog) are dropped.
Usage: python3 live_delay.py OUTDIR [OUTDIR...]"""
import sys, json, os, datetime as dt, collections, numpy as np
def ts(s): return dt.datetime.fromisoformat(s.replace('Z', '+00:00')).timestamp()
AB = {'GS': 'GSW', 'NY': 'NYK', 'SA': 'SAS', 'NO': 'NOP', 'UTAH': 'UTA', 'WSH': 'WAS'}
res = collections.defaultdict(list); per = {}
for D in sys.argv[1:]:
    log = [json.loads(l) for l in open(f'{D}/log.jsonl')]
    nb = {}; es = {}
    for r in log:
        p = r['msg'].split()
        if p[:2] == ['nba', 'start']: nb[p[2]] = frozenset(p[3].split('@'))
        if p[:2] == ['espn', 'start']: es[p[2]] = frozenset(AB.get(x, x) for x in (p[3], p[5]))
    A = [json.loads(l) for l in open(f'{D}/nba_actions.jsonl')]
    E = [json.loads(l) for l in open(f'{D}/espn_plays.jsonl')]
    first_n = {}; first_e = {}
    for a in A: first_n.setdefault(a['gid'], a['recv_ms'])
    for e in E: first_e.setdefault(e['eid'], e['recv_ms'])
    for gid, teams in nb.items():
        eid = next((k for k, v in es.items() if v == teams), None)
        acts = sorted([a for a in A if a['gid'] == gid and a['t']], key=lambda a: a['n'])
        tA = {}; dn = []; last = None
        for a in acts:
            sc = (int(a['h']), int(a['a']))
            if sc != last and sc not in tA:
                tA[sc] = ts(a['t'])
                if a['recv_ms'] != first_n[gid]: dn.append(a['recv_ms'] / 1000 - tA[sc])
            last = sc
        de = []
        if eid:
            seen = set()
            for e in E:
                if e['eid'] != eid or e['h'] is None: continue
                sc = (int(e['h']), int(e['a']))
                if sc in seen: continue
                seen.add(sc)
                if e['recv_ms'] != first_e[eid] and sc in tA: de.append(e['recv_ms'] / 1000 - tA[sc])
        key = f'{D}:{gid}'
        per[key] = dict(teams=sorted(teams), nba_n=len(dn), nba_med=float(np.median(dn)) if dn else None, espn_n=len(de), espn_med=float(np.median(de)) if de else None)
        res['nba'] += dn; res['espn'] += de
        print(key, sorted(teams), 'NBA S3 n', len(dn), 'median', round(per[key]['nba_med'] or -1, 1), '| ESPN n', len(de), 'median', round(per[key]['espn_med'] or -1, 1))
for k, v in res.items():
    v = np.array(v)
    if len(v): print(f'ALL {k}: n {len(v)} median {np.median(v):.1f} s p10 {np.percentile(v,10):.1f} p25 {np.percentile(v,25):.1f} p75 {np.percentile(v,75):.1f} p90 {np.percentile(v,90):.1f}')
json.dump(dict(per_game=per, **{k: dict(n=len(v), median=float(np.median(v)), p10=float(np.percentile(v, 10)), p90=float(np.percentile(v, 90))) for k, v in res.items() if len(v)}),
          open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out_live_delay.json'), 'w'), indent=1)
