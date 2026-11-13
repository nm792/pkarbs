"""ESPN scoreboard/summary pulls for US sports, slimmed to the score timeline (wallclock, period, clock, home, away)."""
import sys, os, json, gzip, re, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common import jget, RAW
PATH = {'nba': 'basketball/nba', 'nfl': 'football/nfl', 'cfb': 'football/college-football', 'nhl': 'hockey/nhl', 'cbb': 'basketball/mens-college-basketball'}
PLEN = {'nba': 720, 'nfl': 900, 'cfb': 900, 'nhl': 1200, 'cbb': 1200}     # regulation period length, s
NPER = {'nba': 4, 'nfl': 4, 'cfb': 4, 'nhl': 3, 'cbb': 2}
def clk(s):
    m = re.match(r'(\d+):(\d+)(?:\.(\d+))?', s or '')
    if m: return int(m.group(1)) * 60 + int(m.group(2))
    m = re.match(r'([\d.]+)', s or '')
    return float(m.group(1)) if m else None
def scoreboard(sport, day):
    p = {'dates': day, 'limit': 500}
    if sport == 'cfb': p['groups'] = 80
    if sport == 'cbb': p['groups'] = 50
    c, d = jget(f'https://site.api.espn.com/apis/site/v2/sports/{PATH[sport]}/scoreboard', p)
    return (d or {}).get('events', [])
def summary(sport, eid, sub):
    fn = f'{RAW}/{sub}/{sport}/{eid}.json.gz'
    if os.path.exists(fn): return json.load(gzip.open(fn))
    c, d = jget(f'https://site.api.espn.com/apis/site/v2/sports/{PATH[sport]}/summary', {'event': eid})
    if not d: return None
    hd = d['header']['competitions'][0]
    comp = {c['homeAway']: dict(id=c['team']['id'], name=c['team'].get('displayName'), abbr=c['team'].get('abbreviation'), score=c.get('score'), winner=c.get('winner')) for c in hd['competitors']}
    plays = d.get('plays') or [p for dr in (d.get('drives') or {}).get('previous', []) for p in dr.get('plays', [])]
    tl = []; last = None
    for p in plays:
        w = p.get('wallclock'); per = (p.get('period') or {}).get('number'); c_ = clk((p.get('clock') or {}).get('displayValue'))
        hs, as_ = p.get('homeScore'), p.get('awayScore')
        if w is None or per is None or c_ is None or hs is None: continue
        row = [w, per, c_, int(hs), int(as_)]
        if last is None or row[3:] != last[3:] or row[1] != last[1]: tl.append(row); last = row
        else: tl.append(row); last = row
    # thin: keep score changes, period changes, and one row per ~30 s of wallclock
    th = []; lw = None
    for r in tl:
        t = dt.datetime.fromisoformat(r[0].replace('Z', '+00:00')).timestamp()
        if not th or r[3:] != th[-1][3:] or r[1] != th[-1][1] or t - lw >= 30: th.append(r); lw = t
    pc = d.get('pickcenter') or []
    odds = [dict(spread=x.get('spread'), total=x.get('overUnder'), details=x.get('details'), hml=(x.get('homeTeamOdds') or {}).get('moneyLine'), aml=(x.get('awayTeamOdds') or {}).get('moneyLine')) for x in pc[:1]]
    out = dict(id=eid, date=hd.get('date'), comp=comp, completed=hd['status']['type'].get('completed'), tl=th, odds=odds)
    os.makedirs(os.path.dirname(fn), exist_ok=True); json.dump(out, gzip.open(fn, 'wt'))
    return out
