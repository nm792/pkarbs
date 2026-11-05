"""NFL upper bound on EVERY price move (any play: yards, downs, turnovers, scores), trade-only (5 Nov 2026).
Same method as tennis/hist/hist_delay.py (events = mid moves >= MOVE within 20 s, onset = first print covering 20% of
the move, ORACLE side, fills on prints <= 1% under our bid at mid x 0.975, 500-share cap, queue ignored, hold to
result). Delay is measured from the MARKET's move (onset), so 'delay 0' = we know the play the moment the price starts
to react. Seasons: 2025 (raw/us_nfl_hist, 268 games) and 2026 to 3 Nov (raw/us_nfl26_hist, 120 games).
Usage: python3 nfl/hist_moves.py"""
import sys, os, json, gzip, collections, datetime as dt
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, os.path.join(os.path.dirname(HERE), 'tennis', 'hist'))
import common as C
from common import RAW
import hist_delay as H
def ts(s): return dt.datetime.fromisoformat(s.replace('Z', '+00:00')).timestamp()
def load(sub):
    games = []; why = collections.Counter()
    for e in json.load(gzip.open(f'{RAW}/{sub}/gamma_events.json.gz')):
        for m in e['markets']:
            if m.get('sportsMarketType') != 'moneyline': continue
            fn = f"{RAW}/{sub}/trades/{m['conditionId']}.json.gz"
            if not os.path.exists(fn): why['no trades'] += 1; continue
            op = json.loads(m.get('outcomePrices') or '[]')
            if sorted(op) != ['0', '1']: why['unresolved/tie'] += 1; continue
            fs = m.get('feeSchedule') or {}; reb = float(fs.get('rebateRate') or 0) * float(fs.get('rate') or 0)
            t0 = ts(e['startTime']); pr = [p for p in C.prints(json.load(gzip.open(fn))) if p[0] >= t0]
            if len(pr) < 30: why['few in-play prints'] += 1; continue
            games.append(dict(slug=e['slug'], pr=pr, M=C.Mid(pr), win0=op[0] == '1', reb=reb, t0=t0, t1=pr[-1][0]))
    return games, why
out = {}
for sub, label in (('us_nfl26_hist', '2026'), ('us_nfl_hist', '2025')):
    games, why = load(sub)
    for g in games: g['E'] = H.events(g)
    n = len(games); ne = sum(len(g['E']) for g in games)
    print(label, 'games', n, dict(why), 'moves', ne, f'({ne / max(1, n):.0f}/game)', flush=True)
    rows = []
    for W in (30, 120):
        for lag in (-10, -5, 0, 2, 5, 10, 20, 30, 60):
            P = [H.run(g, lag, W) for g in games]; s = C.summarize(P); s = {k: ([float(x) for x in v] if isinstance(v, list) else v) for k, v in s.items()}
            r = dict(W=W, delay=lag, filled_per_game=round(s['usd'] / n, 1), result_per_game=round(s['net_result_usd'] / n, 2),
                     result_per_game_ci=[round(x / n, 2) for x in s['ci_result_usd']], **s); rows.append(r)
            print(f"{label} W{W:>3} d{lag:>3}s: ${r['filled_per_game']:6.1f} filled/game, 1min {s['net_1min_pct']}% {s['ci_1min']}, result {s['net_result_pct']}% "
                  f"= ${r['result_per_game']}/game {r['result_per_game_ci']}, ex-top5 {s['ex_top5_result_pct']}%", flush=True)
    out[label] = dict(games=n, why=dict(why), moves=ne, curve=rows)
json.dump(out, open(os.path.join(HERE, 'out_hist_moves.json'), 'w'), indent=1)
