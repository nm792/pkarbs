"""ESPN 'all soccer' scoreboards 15 Jul - 20 Oct 2026 (before the backtest window): goal/red-card minutes for fitting."""
import sys, os, json, gzip, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common import jget, RAW
from concurrent.futures import ThreadPoolExecutor
days = [(dt.date(2026, 7, 15) + dt.timedelta(days=k)).strftime('%Y%m%d') for k in range(98)]
def sb(day):
    c, d = jget('https://site.api.espn.com/apis/site/v2/sports/soccer/all/scoreboard', {'dates': day, 'limit': 1000})
    out = []
    for e in (d or {}).get('events', []):
        cp = e['competitions'][0]
        if not cp['status']['type'].get('completed'): continue
        out.append(dict(id=e['id'], date=e['date'], league=(e.get('season') or {}).get('slug'),
                        comp=[(c['homeAway'], c['team']['id'], c.get('score')) for c in cp['competitors']],
                        det=[(x['clock']['value'], x['clock']['displayValue'], x['team']['id'], bool(x.get('scoringPlay')), bool(x.get('redCard')), bool(x.get('ownGoal')), bool(x.get('shootout'))) for x in cp.get('details', [])]))
    return out
with ThreadPoolExecutor(8) as ex: H = [e for L in ex.map(sb, days) for e in L]
H = list({e['id']: e for e in H}.values())
json.dump(H, gzip.open(f'{RAW}/soccer/espn_hist_2026-07-15_10-20.json.gz', 'wt'))
print(len(H))
