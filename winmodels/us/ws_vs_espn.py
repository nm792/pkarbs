"""NBA feed delay: Polymarket sports WS score message receipt time vs ESPN play wallclock (true event time).
Input: raw WS capture jsonl files (recv_ms, data); ESPN summaries in raw/us_bt/nba. Score string may be away-home;
we try both orders and keep the one that matches more changes."""
import sys, os, json, glob, datetime as dt, collections, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.dirname(HERE))
from espn import scoreboard, summary
files = sys.argv[1:] or sorted(glob.glob('/mnt/project-files/winmodels/raw/wscap/*.jsonl'))
ws = collections.defaultdict(list); days = set()
for f in files:
    for l in open(f):
        r = json.loads(l)
        if 'data' in r:
            try: d = json.loads(r['data'])
            except Exception: continue
        elif 'leagueAbbreviation' in r: d = r          # server logger frame format
        else: continue
        if d.get('leagueAbbreviation') == 'nba' and d.get('score'):
            ws[frozenset((d['homeTeam'], d['awayTeam']))].append((r['recv_ms'] / 1000, d['score']))
            t = dt.datetime.fromtimestamp(r['recv_ms'] / 1000, dt.timezone.utc)
            for back in (0, 1): days.add((t - dt.timedelta(hours=6 + 24 * back)).strftime('%Y%m%d'))
AB = {'GS': 'GSW', 'NY': 'NYK', 'SA': 'SAS', 'NO': 'NOP', 'UTAH': 'UTA', 'WSH': 'WAS'}
allds = []; per = {}; gap_med = {}
for day in sorted(days):
    for e in scoreboard('nba', day):
        s = summary('nba', e['id'], 'us_bt')
        if not s: continue
        k = frozenset(AB.get(s['comp'][x]['abbr'], s['comp'][x]['abbr']) for x in ('home', 'away'))
        if k not in ws: continue
        first = {}
        for r in s['tl']:
            for key in ((r[3], r[4]), (r[4], r[3])):
                first.setdefault(key, dt.datetime.fromisoformat(r[0].replace('Z', '+00:00')).timestamp())
        seen = set(); ds = []
        for t, sc in ws[k]:
            try: a, b = [int(x) for x in sc.split('-')]
            except Exception: continue
            if (a, b) in seen: continue
            seen.add((a, b))
            if (a, b) in first: ds.append(t - first[(a, b)])
        per[e['id']] = ds; allds += ds
        gaps = np.diff([t for t, _ in ws[k]]); gap_med[e['id']] = float(np.median(gaps)) if len(gaps) else None
        if ds: print(e['id'], sorted(k), 'n', len(ds), 'median', round(float(np.median(ds)), 1), 's; range', round(min(ds), 1), round(max(ds), 1), '; median gap between WS msgs', round(gap_med[e['id']] or 0, 1), 's')
if allds:
    a = np.array(allds); print(f'ALL: n {len(a)}, median {np.median(a):.1f} s, p10 {np.percentile(a,10):.1f}, p90 {np.percentile(a,90):.1f}')
    json.dump(dict(per_game=per, gap_median=gap_med, n=len(a), median=float(np.median(a)), p10=float(np.percentile(a,10)), p90=float(np.percentile(a,90))),
              open(os.path.join(HERE, 'out_ws_vs_espn.json'), 'w'), indent=1)
