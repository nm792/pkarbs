"""Rank in-play sports leagues by Polymarket volume vs rn1's share (22 Oct 02Z - 2 Nov 06Z 2026)."""
import sys, os, json, gzip, collections
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common import RAW
E = json.load(gzip.open(f'{RAW}/rank/gamma_events_by_league_2026-10-22_11-02.json.gz'))
vol = collections.Counter(); nev = collections.Counter(); games = collections.Counter()
for e in E:
    p = e['slug'].split('-')[0]; vol[p] += e['volume']; nev[p] += 1; games[p] += 1 if e.get('gameId') else 0
rn = collections.Counter(); T0, T1 = 1792634632, 1793599200
A = json.load(gzip.open('/mnt/project-files/rn1/raw/act7d.json.gz'))
A += [json.loads(l) for f in ('rn1_activity_2026-10-29T02Z_to_2026-11-02T06Z.jsonl.gz',) for l in gzip.open(f'/home/user/pkarbs/rn1/decomp/raw/{f}', 'rt')]
seen = set()
for a in A:
    if a.get('type') != 'TRADE' or not (T0 <= a['timestamp'] < T1): continue
    tx = a.get('transactionHash') or a.get('transaction_hash'); k = (tx, a.get('asset') or a.get('token_id'), a['size'], a['timestamp'])
    if k in seen: continue
    seen.add(k); rn[(a.get('eventSlug') or a.get('event_slug') or a.get('slug') or '').split('-')[0]] += float(a.get('usdcSize') or a.get('usdc_size') or a['size'] * a['price'])
rows = []
for p in set(vol) | set(rn):
    if vol[p] < 2e5: continue
    rows.append(dict(prefix=p, events=nev[p], with_live_feed=games[p], pm_volume_m=round(vol[p] / 1e6, 2), rn1_bought_m=round(rn[p] / 1e6, 3),
                     rn1_share_pct=round(100 * rn[p] / vol[p], 2), volume_without_rn1_m=round((vol[p] - rn[p]) / 1e6, 2)))
rows.sort(key=lambda r: -r['pm_volume_m'])
json.dump(rows, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'rank_2026-10-22_11-02.json'), 'w'), indent=0)
print(f"{'league':10}{'events':>7}{'w/feed':>7}{'PM vol $M':>10}{'rn1 $M':>8}{'rn1 %':>7}")
for r in rows[:70]: print(f"{r['prefix']:10}{r['events']:>7}{r['with_live_feed']:>7}{r['pm_volume_m']:>10}{r['rn1_bought_m']:>8}{r['rn1_share_pct']:>7}")
print('total PM', round(sum(vol.values()) / 1e6, 1), 'rn1', round(sum(rn.values()) / 1e6, 1))
