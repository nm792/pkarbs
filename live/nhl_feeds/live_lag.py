"""NHL live: how late is each feed vs the Polymarket PRICE on goals (5 Nov 2026). Input: capture.py output dirs.
Per goal: price onset from 1 s books of the scoring team's token (first snapshot whose mid has moved >= 20% of the
(ref-120 s -> ref+120 s) move; ref = ESPN wallclock), half-move time, and recv time of each feed:
  nhl_play  first NHL api-web play-by-play 'goal' play (cache-busted 1 s poll)
  nhl_score first NHL api-web score change in the game state
  espn      first ESPN summary scoring play (2 s poll); espn_wall = ESPN's own wallclock stamp
  pm_ws     first Polymarket sports-WS frame with the new total
Also: share of the price move already done when each feed arrives, and bid depth at mid-2.5% on the scoring side then.
Usage: python3 live_lag.py DIR [DIR ...] > report"""
import sys, os, json, gzip, bisect, collections, re, datetime as dt
import numpy as np
def rd(d, n):
    for fn in (f'{d}/{n}.jsonl', f'{d}/{n}.jsonl.gz'):
        if os.path.exists(fn):
            with (gzip.open(fn, 'rt') if fn.endswith('gz') else open(fn)) as f: return [json.loads(l) for l in f if l.strip()]
    return []
def ts(s): return dt.datetime.fromisoformat(s.replace('Z', '+00:00')).timestamp()
def nz(s): return re.sub(r'[^a-z0-9]', '', (s or '').lower())
rows = []
for D in sys.argv[1:]:
    mk = {}; [mk.__setitem__(m['slug'], m) for m in rd(D, 'markets')]
    sch = {}; [sch.__setitem__(s['id'], s) for s in rd(D, 'sched')]
    book = collections.defaultdict(list)
    for b in rd(D, 'books'):
        bids = [(float(x['price']), float(x['size'])) for x in b['bids'] or []]; asks = [(float(x['price']), float(x['size'])) for x in b['asks'] or []]
        if not bids or not asks: continue
        bb = max(p for p, s in bids); ba = min(p for p, s in asks)
        book[b['asset']].append((b['recv_ms'] / 1000, (bb + ba) / 2, bb, ba, bids))
    for v in book.values(): v.sort(key=lambda x: x[0])
    nhl = rd(D, 'nhl'); espn = rd(D, 'espn'); ws = rd(D, 'sports')
    for gid, s in sch.items():
        # PM market for this NHL game: title "Away vs. Home" with nicknames
        m = None
        for x in mk.values():
            t = nz(x['title'])
            if nz(s['away_name']) in t and nz(s['home_name']) in t and abs(ts(x['start']) - ts(s['start'])) < 3 * 3600: m = x
        if not m: continue
        o = [nz(z) for z in m['outcomes']]; tok_home = m['tokens'][0 if nz(s['home_name']) in o[0] or o[0] in nz(s['home_name']) else 1]
        tok_away = [t for t in m['tokens'] if t != tok_home][0]
        goals = {}
        for r in nhl:
            if r['id'] != gid or r['kind'] != 'play' or r['play']['typeDescKey'] != 'goal': continue
            dd = r['play']['details']; k = (dd.get('awayScore'), dd.get('homeScore'))
            goals.setdefault(k, {})['nhl_play'] = r['recv_ms'] / 1000
            goals[k]['period'] = r['play']['periodDescriptor']['number']; goals[k]['tip'] = r['play']['timeInPeriod']
        last = None
        for r in nhl:
            if r['id'] != gid or r['kind'] != 'state': continue
            k = (r['away'], r['home'])
            if last is not None and k != last and sum(k) > sum(last): goals.setdefault(k, {}).setdefault('nhl_score', r['recv_ms'] / 1000)
            last = k
        for r in espn:
            if r['id'] != gid or r['kind'] != 'play' or not r['play'].get('scoringPlay'): continue
            k = (r['play'].get('awayScore'), r['play'].get('homeScore'))
            g = goals.setdefault(k, {}); g.setdefault('espn', r['recv_ms'] / 1000)
            if r['play'].get('wallclock'): g.setdefault('espn_wall', ts(r['play']['wallclock']))
        pm = [w for w in ws if w.get('homeTeam') and str(w.get('gameId')) == str(m['gid'])]; lastt = None
        for w in pm:
            try: tot = sum(int(z) for z in w['score'].split('-'))
            except Exception: continue
            if lastt is not None and tot > lastt:
                for k, g in goals.items():
                    if sum(k) == tot: g.setdefault('pm_ws', w['recv_ms'] / 1000)
            lastt = tot
        for k, g in sorted(goals.items(), key=lambda z: sum(z[0])):
            if sum(k) == 0: continue
            home_scored = None
            prevs = [kk for kk in goals if sum(kk) == sum(k) - 1]
            if prevs: home_scored = k[1] > prevs[0][1]
            elif sum(k) == 1: home_scored = k[1] == 1
            if home_scored is None: continue
            tok = tok_home if home_scored else tok_away; B = book.get(tok, [])
            feeds = [g[x] for x in ('nhl_play', 'nhl_score', 'espn', 'pm_ws') if x in g]
            ref = g.get('espn_wall') or (min(feeds) if feeds else None)
            if ref is None or not B: continue
            bt = [b[0] for b in B]
            def mid(T):
                i = bisect.bisect_right(bt, T) - 1; return B[i][1] if i >= 0 else None
            pa, pb = mid(ref - 120), mid(ref + 120)
            row = dict(dir=os.path.basename(D.rstrip('/')), game=m['slug'], score=f'{k[0]}-{k[1]}', home_scored=home_scored, period=g.get('period'), tip=g.get('tip'),
                       **{x: g.get(x) for x in ('nhl_play', 'nhl_score', 'espn', 'espn_wall', 'pm_ws')})
            if pa is None or pb is None or pb - pa < 0.02:
                row['note'] = 'price move < 2c or no book'; rows.append(row); continue
            on = half = None
            for b in B[bisect.bisect_left(bt, ref - 120):bisect.bisect_right(bt, ref + 120)]:
                x = (b[1] - pa) / (pb - pa)
                if on is None and x >= 0.2: on = b[0]
                if x >= 0.5: half = b[0]; break
            row.update(pre=round(pa, 3), post=round(pb, 3), onset=on, half=half)
            for x in ('nhl_play', 'nhl_score', 'espn', 'espn_wall', 'pm_ws'):
                if g.get(x) and on:
                    row[f'{x}_minus_onset'] = round(g[x] - on, 1)
                    mm = mid(g[x]); row[f'{x}_moved'] = round((mm - pa) / (pb - pa), 2) if mm is not None else None
                    i = bisect.bisect_right(bt, g[x]) - 1
                    if i >= 0:
                        bid = round(B[i][1] * 0.975, 3); row[f'{x}_depth_at_bid'] = round(sum(sz for p, sz in B[i][4] if p >= bid - 1e-9))
            rows.append(row)
out = dict(rows=rows, summary={})
for x in ('nhl_play', 'nhl_score', 'espn', 'espn_wall', 'pm_ws'):
    v = np.array([r[f'{x}_minus_onset'] for r in rows if r.get(f'{x}_minus_onset') is not None])
    mv = np.array([r[f'{x}_moved'] for r in rows if r.get(f'{x}_moved') is not None])
    if len(v): out['summary'][x] = dict(n=len(v), median=float(np.median(v)), p10=float(np.percentile(v, 10)), p90=float(np.percentile(v, 90)),
                                         moved_median=float(np.median(mv)) if len(mv) else None)
print(json.dumps(out['summary'], indent=1))
for r in rows: print({k: (round(v, 1) if isinstance(v, float) and v > 1e9 else v) for k, v in r.items()})
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out_live_lag.json'), 'w'), indent=1)
