# Build per-minute training rows from raw/frames + raw/matches.json.
# Winner of each game = side with more (towers + inhibitors) in the 'finished' frame
# (checked against the official series score in check_winners()).
import json, glob, os, datetime as dt, math
import pandas as pd
def ts(s): return dt.datetime.fromisoformat(s[:19]+'+00:00').timestamp()
DR = ('ocean','cloud','infernal','mountain','hextech','chemtech')
def feat(f, t0, hist):
    b, r = f['blueTeam'], f['redTeam']
    bd = [d for d in b['dragons'] if d != 'elder']; rd = [d for d in r['dragons'] if d != 'elder']
    T = ts(f['t'])
    # baron buff proxy: baron count rose within the last 180 s
    def recent(side):
        cur = f[side]['barons']
        for (tt, bb) in hist[side]:
            if T - tt <= 180 and bb < cur: return 1
        return 0
    lv = lambda s: sum(p[1] for p in f[s]['p']); cs = lambda s: sum(p[4] for p in f[s]['p'])
    return dict(t=(T - t0)/60, gd=(b['totalGold']-r['totalGold'])/1000, kd=b['totalKills']-r['totalKills'],
        td=b['towers']-r['towers'], ihd=b['inhibitors']-r['inhibitors'], bnd=b['barons']-r['barons'],
        dd=len(bd)-len(rd), eld=b['dragons'].count('elder')-r['dragons'].count('elder'),
        soul=(len(bd)>=4)-(len(rd)>=4), bbuf=recent('blueTeam')-recent('redTeam'),
        lvd=lv('blueTeam')-lv('redTeam'), csd=(cs('blueTeam')-cs('redTeam'))/10)
def winner(fin):
    b, r = fin['blueTeam'], fin['redTeam']
    sb, sr = b['towers']+b['inhibitors'], r['towers']+r['inhibitors']
    if sb == sr: return None
    return 1 if sb > sr else 0
def build():
    M = json.load(open('raw/matches.json'))
    g2m = {g['id']:(m,g) for m in M for g in m.get('games',[])}
    rows, games = [], []
    EL = json.load(open('elo_pre.json')) if os.path.exists('elo_pre.json') else {}
    for p in glob.glob('raw/frames/*.json'):
        d = json.load(open(p))
        if 'frames' not in d: continue
        fr = [f for f in d['frames']]
        fin = [f for f in fr if f['state']=='finished']
        ing = [f for f in fr if f['state']=='in_game']
        if not fin or len(ing) < 10: continue
        w = winner(fin[-1])
        m, g = g2m.get(d['gid'], (None,None))
        if w is None or m is None: continue
        t0 = ts(ing[0]['t'])
        e = EL.get(m['match_id'], {}); elo = math.log(10) * (e.get(d['meta']['blue'], 1500) - e.get(d['meta']['red'], 1500)) / 400
        games.append(dict(gid=d['gid'], match=m['match_id'], league=m['league'], start=m['start'], blue_won=w,
                          blue=d['meta']['blue'], red=d['meta']['red'], patch=d['patch'], n=len(ing)))
        hist = {'blueTeam':[], 'redTeam':[]}
        for f in ing:
            x = feat(f, t0, hist); x.update(elo=elo, gid=d['gid'], match=m['match_id'], league=m['league'], start=m['start'], y=w)
            rows.append(x)
            for s in hist: hist[s].append((ts(f['t']), f[s]['barons']))
    return pd.DataFrame(rows), pd.DataFrame(games)
def check_winners(G):
    """Per match: predicted wins per team must equal official gameWins."""
    M = {m['match_id']:m for m in json.load(open('raw/matches.json'))}
    ok = bad = 0
    for mid, gg in G.groupby('match'):
        m = M[mid]; code = m['team_ids']
        if len(gg) != len(m['games']): continue
        wins = {}
        for _, r in gg.iterrows():
            wid = r.blue if r.blue_won else r.red
            wins[code.get(wid)] = wins.get(code.get(wid), 0) + 1
        off = {c:w for c,w in m['teams']}
        if all(wins.get(c,0) == (w or 0) for c,w in off.items()): ok += 1
        else: bad += 1
    return ok, bad
if __name__ == '__main__':
    R, G = build()
    R.to_parquet('rows.parquet') if False else R.to_csv('rows.csv.gz', index=False)
    G.to_csv('games.csv', index=False)
    print('games', len(G), 'rows', len(R), 'blue win rate', round(G.blue_won.mean(),3))
    print('winner check (matches fully pulled): ok/bad', check_winners(G))
