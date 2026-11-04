"""Moneyline v2 trades for tennis matches seen on the server's Polymarket sports-WS log (2-4 Nov 2026)."""
import sys, os, json, gzip, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common import RAW, pull_trades
from concurrent.futures import ThreadPoolExecutor
G = json.load(gzip.open(f'{RAW}/tennis/gamma_tennis_events_2026-10-30_on.json.gz'))
W = set()
for l in gzip.open(os.path.join(os.path.dirname(RAW), '..', 'rn1/scores/cs2/server-2026-11/cs2_frames.jsonl.gz'), 'rt'):
    d = json.loads(l)
    if d.get('leagueAbbreviation') in ('atp', 'wta', 'challenger', 'wta challenger'): W.add(d['gameId'])
jobs = []
for e in G:
    if e['gameId'] not in W or not e.get('startTime'): continue
    t = dt.datetime.fromisoformat(e['startTime'].replace('Z', '+00:00')).timestamp()
    for m in e['markets']:
        if m.get('sportsMarketType') == 'moneyline': jobs.append((m['conditionId'], t))
with ThreadPoolExecutor(16) as ex: list(ex.map(lambda j: pull_trades(j[0], j[1] - 3600, j[1] + 10 * 3600, 'tennis/trades'), jobs))
print(len(jobs), 'markets')
