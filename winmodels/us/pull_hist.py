"""History for fitting (games BEFORE the backtest window): every 2nd day of the previous season."""
import sys, datetime as dt
from concurrent.futures import ThreadPoolExecutor
from espn import scoreboard, summary
RNG = {'nba': ('2025-10-21', '2026-04-12'), 'nfl': ('2025-09-04', '2026-01-05'), 'cfb': ('2025-08-30', '2025-12-07'), 'nhl': ('2025-10-07', '2026-04-16')}
sport = sys.argv[1]; step = int(sys.argv[2]) if len(sys.argv) > 2 else 2
a, b = [dt.date.fromisoformat(x) for x in RNG[sport]]
days = [(a + dt.timedelta(days=k)).strftime('%Y%m%d') for k in range(0, (b - a).days + 1, step if sport not in ('nfl',) else 1)]
with ThreadPoolExecutor(8) as ex: evs = [e for L in ex.map(lambda d: scoreboard(sport, d), days) for e in L]
ids = sorted({e['id'] for e in evs if e['competitions'][0]['status']['type'].get('completed')})
print(sport, 'games', len(ids), flush=True)
with ThreadPoolExecutor(12) as ex: n = sum(1 for s in ex.map(lambda i: summary(sport, i, 'us_hist'), ids) if s)
print(sport, 'summaries', n)
