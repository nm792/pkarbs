"""Full ADV table (total + in-play $/day) per league and per sport, 20 Oct - 4 Nov 2026 (15 days), gamma closed events.
In-play share: data-api v2 trades on sampled events (40 per league for the top 12, else 12); see inplay_share.py."""
import json, gzip, collections, os, re
H = os.path.dirname(os.path.abspath(__file__)); RAW = os.path.join(H, '..', 'raw', 'inplay')
E = json.load(gzip.open(f'{RAW}/events_2026-10-20_11-04.json.gz')); S = json.load(gzip.open(f'{RAW}/gamma_sports_2026-11-04.json.gz'))
NAME = {s['sport']: s.get('name') or s['sport'] for s in S}
SH = {}
for f in ('inplay_share_rest.json', 'inplay_share_lol_cs2_dota2.json', 'inplay_share_2026-10-20_11-04.json', 'inplay_share_top40.json'):
    for k, v in json.load(open(f'{H}/{f}'))['summary'].items(): SH[k] = (v['strat_inplay_share'], v['events'])
def sport(lg, nm):
    n = (nm or '').lower(); l = lg.lower()
    if l in ('nba', 'wnba', 'cbb', 'cwbb', 'euroleague', 'bkcba', 'bkfr1', 'bkkbl', 'bknbl') or 'basket' in n or l.startswith('bk'): return 'Basketball'
    if l in ('nfl', 'cfb', 'ufl', 'cfl'): return 'American football'
    if l in ('atp', 'wta', 'itf', 'atp-doubles', 'wta-doubles', 'challenger') or 'tennis' in n: return 'Tennis'
    if l in ('lol', 'cs2', 'dota2', 'val', 'mlbb', 'r6siege', 'codmw', 'rl', 'ow', 'sc2', 'pubg', 'hok', 'wildrift', 'fifa', 'apex') or 'esport' in n or 'league of legends' in n: return 'Esports'
    if l.startswith(('cric', 'crint')) or 'cricket' in n: return 'Cricket'
    if l in ('nhl', 'khl', 'shl', 'ahl', 'liiga', 'del') or 'hockey' in n: return 'Ice hockey'
    if l in ('mlb', 'npb', 'kbo', 'lmp', 'lidom', 'abl') or 'baseball' in n: return 'Baseball'
    if l in ('ufc', 'pfl', 'boxing', 'mma') or 'ufc' in n or 'box' in n: return 'MMA / boxing'
    if 'rugby' in n or l.startswith('rug') or l in ('nrl', 'sr', 'top14', 'prem'): return 'Rugby'
    if l in ('afl',) or 'aussie' in n: return 'AFL'
    if l in ('f1', 'nascar', 'indycar', 'motogp') or 'formula' in n: return 'Motorsport'
    if 'golf' in n or l in ('pga', 'lpga', 'liv'): return 'Golf'
    if 'table tennis' in n or l.startswith('tt'): return 'Table tennis'
    if 'darts' in n: return 'Darts'
    if 'volley' in n: return 'Volleyball'
    if 'handball' in n: return 'Handball'
    return 'Soccer'
V = collections.Counter(); N = collections.Counter()
for e in E: V[e['league']] += e['volume']; N[e['league']] += 1
D = 15; rows = []
for lg, v in V.most_common():
    sh, ne = SH.get(lg, (None, 0)); rows.append(dict(league=lg, name=NAME.get(lg, lg), sport=sport(lg, NAME.get(lg)), total=v / D, inplay=None if sh is None else v / D * sh, share=sh, sampled=ne))
SP = collections.defaultdict(lambda: dict(total=0, inplay=0, meas_total=0, leagues=0))
for r in rows:
    s = SP[r['sport']]; s['total'] += r['total']; s['leagues'] += 1
    if r['inplay'] is not None: s['inplay'] += r['inplay']; s['meas_total'] += r['total']
tot = sum(r['total'] for r in rows)
L = [f'# Polymarket sports ADV, 20 Oct - 4 Nov 2026 (15 days)\n', f'All {len(rows)} leagues with closed events: ${tot/1e6:.1f}M/day total. Gamma event volume (closed events ending in the window) / 15.',
     'In-play = volume traded after gameStartTime, measured from data-api v2 trades on sampled events (40 per league for the top 12 leagues, 12 for others), stratified by event size.',
     'In-play for a sport counts only leagues where it was measured; "measured" = share of that sport\'s total in measured leagues.\n',
     '## By sport\n', '| # | Sport | Total $/day | In-play $/day (measured leagues) | In-play share | Leagues | Measured |', '|---|---|---|---|---|---|---|']
for i, (k, s) in enumerate(sorted(SP.items(), key=lambda x: -x[1]['total']), 1):
    shr = s['inplay'] / s['meas_total'] if s['meas_total'] else None
    L.append(f"| {i} | {k} | ${s['total']/1e6:.2f}M | ${s['inplay']/1e6:.2f}M | {'' if shr is None else f'{shr:.0%}'} | {s['leagues']} | {s['meas_total']/max(1,s['total']):.0%} |")
L += ['\n## By league (every league >= $0.1M/day; full list in adv_by_league.json)\n', '| # | League | Sport | Total $/day | In-play $/day | In-play share | Events sampled |', '|---|---|---|---|---|---|---|']
for i, r in enumerate([r for r in rows if r['total'] >= 1e5], 1):
    L.append(f"| {i} | {r['name']} ({r['league']}) | {r['sport']} | ${r['total']/1e6:.2f}M | {'' if r['inplay'] is None else f'${r[chr(105)+chr(110)+chr(112)+chr(108)+chr(97)+chr(121)]/1e6:.2f}M'} | {'' if r['share'] is None else f'{r[chr(115)+chr(104)+chr(97)+chr(114)+chr(101)]:.0%}'} | {r['sampled'] or ''} |")
open(f'{H}/ADV-2026-10-20_11-04.md', 'w').write('\n'.join(L) + '\n')
json.dump(rows, open(f'{H}/adv_by_league.json', 'w'), indent=0)
print('\n'.join(L))
