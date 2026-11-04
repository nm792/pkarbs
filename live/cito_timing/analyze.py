"""Compare first-seen times of each score state: Cito WebSocket vs Polymarket sports WS.
Usage: python3 analyze.py <race.jsonl>   Prints per-sport lists of (PM time - Cito time) in seconds; +ve = Cito earlier."""
import json, sys, re, statistics as st
L = [json.loads(l) for l in open(sys.argv[1])]
def last(n): return n.strip().split()[-1].lower()
def team(n): return n.strip().split()[0].lower()
first = {}
def put(src, key, t):
    T0.setdefault(src, t)
    if t - T0[src] < 60: first.setdefault((src,) + key, None); return  # state already there at connect: no timing
    first.setdefault((src,) + key, t)
cs2_names = json.load(open(sys.argv[2])) if len(sys.argv) > 2 else {}  # matchId -> [team1, team2] from /cs2/live
T0 = {}
for x in L:
    s = x['src']
    if s == 'pm':
        try: g = json.loads(x['m'])
        except Exception: continue
        lg = g.get('leagueAbbreviation')
        if lg in ('wta', 'atp', 'challenger', 'itf'):
            a, b = last(g['homeTeam']), last(g['awayTeam'])
            sets = [re.sub(r'\(.*?\)', '', p).strip() for p in (g.get('score') or '').split(',') if p.strip()]
            try: sets = [tuple(map(int, p.split('-'))) for p in sets]
            except ValueError: continue
            if a > b: a, b = b, a; sets = [(y, z) for z, y in sets]
            put('pm', ('tennis', a, b, tuple(sets)), x['rt'])
        elif lg == 'cs2':
            try:
                r, ser, _ = g['score'].split('|'); ra, rb = map(int, r.split('-')); sa, sb = map(int, ser.split('-'))
            except Exception: continue
            a, b = team(g['homeTeam']), team(g['awayTeam'])
            if a > b: a, b, ra, rb, sa, sb = b, a, rb, ra, sb, sa
            put('pm', ('cs2', a, b, sa + sb, ra, rb), x['rt'])
    elif s == 'cito_tennis_ws':
        d = json.loads(x['m'])
        if d.get('type') != 'POINT_UPDATE' or 'data' not in d: continue
        dd = d['data']; a, b = last(dd['player1']['name']), last(dd['player2']['name'])
        sets = [tuple(map(int, p['score'].split('-'))) for p in dd.get('sets') or [] if re.fullmatch(r'\d+-\d+', p.get('score') or '')]
        if a > b: a, b = b, a; sets = [(y, z) for z, y in sets]
        put('cito', ('tennis', a, b, tuple(sets)), x['rt'])
    elif s == 'cito_cs2_ws':
        d = json.loads(x['m'])
        if d.get('type') != 'cs2.live.update': continue
        if d.get('team1Name'): cs2_names[d['matchId']] = (d['team1Name'], d['team2Name'])
        nm = cs2_names.get(d['matchId'])
        if not nm or d.get('team1Score') is None: continue
        a, b = team(nm[0]), team(nm[1]); ra, rb = d['team1Score'], d['team2Score']
        sa, sb = (d.get('series') or {}).get('team1', 0) or 0, (d.get('series') or {}).get('team2', 0) or 0
        if a > b: a, b, ra, rb = b, a, rb, ra
        put('cito', ('cs2', a, b, None, ra, rb), x['rt'])
for sport in ('cs2', 'tennis'):
    diffs = []
    for k, t in first.items():
        if t is None: continue
        if k[0] != 'cito' or k[1] != sport: continue
        for k2, t2 in first.items():
            if t2 is None or k2[0] != 'pm' or k2[1] != sport: continue
            if sport == 'tennis' and k2[2:] == k[2:]: diffs.append((k[2], k[3], k[4], round(t2 - t, 1)))
            if sport == 'cs2' and k2[2:4] == k[2:4] and k2[5:] == k[5:] and k[5:] != (0, 0): diffs.append((k[2], k[3], k[5:], round(t2 - t, 1)))
    d = [x[-1] for x in diffs]
    print(sport, 'n', len(d), 'median PM-Cito s', st.median(d) if d else None, 'min', min(d) if d else None, 'max', max(d) if d else None)
    for r in sorted(diffs): print('  ', r)
