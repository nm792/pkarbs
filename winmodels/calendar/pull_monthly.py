"""Measured Polymarket volume per league per month, Nov 2025 - Oct 2026 (gamma events by series, closed, by end date)."""
import sys, os, json, gzip, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common import jget, RAW
from concurrent.futures import ThreadPoolExecutor
S = {s['sport']: s for s in json.load(gzip.open(f'{RAW}/rank/gamma_sports.json.gz'))}
L = {'LoL': ['lol'], 'CS2': ['cs2'], 'Dota 2': ['dota2'], 'NFL': ['nfl'], 'NHL': ['nhl'], 'Tennis (ATP+WTA)': ['atp', 'wta'],
     'Cricket (intl)': ['crint'], 'Cricket (IPL)': ['cricipl', 'ipl'], 'Rugby': [k for k in S if k.startswith('ru') and k not in ('rus', 'rus1')], 'NBA': ['nba']}
months = [(dt.date(2025 + (10 + k) // 12, (10 + k) % 12 + 1, 1)) for k in range(12)]
def nxt(d): return dt.date(d.year + (d.month == 12), d.month % 12 + 1, 1)
def pull(job):
    name, lg, m = job; tot = 0.0; n = 0
    for ser in str(S.get(lg, {}).get('series') or '').split(','):
        if not ser: continue
        off = 0
        while off < 5000:
            c, d = jget('https://gamma-api.polymarket.com/events', {'series_id': ser, 'closed': 'true', 'end_date_min': f'{m}T00:00:00Z', 'end_date_max': f'{nxt(m)}T00:00:00Z', 'limit': 100, 'offset': off})
            if c != 200 or not d: break
            tot += sum(float(e.get('volume') or 0) for e in d); n += len(d); off += 100
            if len(d) < 100: break
    return name, lg, str(m)[:7], tot, n
jobs = [(name, lg, m) for name, lgs in L.items() for lg in lgs if lg in S for m in months]
with ThreadPoolExecutor(16) as ex: R = list(ex.map(pull, jobs))
json.dump(R, open('monthly_volume_2025-11_2026-10.json', 'w'), indent=0)
agg = {}
for name, lg, m, v, n in R: agg.setdefault(name, {}).setdefault(m, [0, 0]); agg[name][m][0] += v; agg[name][m][1] += n
ms = [str(m)[:7] for m in months]
print(f"{'$M by month':18}" + ''.join(f'{m[2:]:>8}' for m in ms))
for name in agg: print(f'{name:18}' + ''.join(f"{agg[name].get(m, [0])[0]/1e6:>8.1f}" for m in ms))
print('rugby leagues:', L['Rugby'])
