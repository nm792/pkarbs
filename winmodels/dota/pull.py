"""Pull OpenDota match details + Polymarket trades for matched Dota 2 games (top N by volume)."""
import json, gzip, os, sys, time, urllib.request
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, '..'); import common as C
N = int(sys.argv[1]) if len(sys.argv) > 1 else 150
M = sorted(json.load(open('matched.json')), key=lambda r: -r['vol'])[:N]
os.makedirs(f'{C.RAW}/dota/od', exist_ok=True)
def od(mid):
    fn = f'{C.RAW}/dota/od/{mid}.json.gz'
    if os.path.exists(fn): return
    for t in range(4):
        try:
            d = json.load(urllib.request.urlopen(urllib.request.Request(f'https://api.opendota.com/api/matches/{mid}', headers={'User-Agent': 'pkarbs-research/1.0'}), timeout=60))
            keep = {k: d.get(k) for k in ('match_id', 'start_time', 'duration', 'radiant_win', 'pre_game_duration', 'objectives', 'teamfights', 'radiant_gold_adv', 'radiant_xp_adv', 'radiant_score', 'dire_score', 'version', 'replay_url')}
            keep['kills'] = [(p.get('isRadiant'), k['time']) for p in d.get('players', []) for k in (p.get('kills_log') or [])]
            json.dump(keep, gzip.open(fn, 'wt')); return
        except Exception as ex: time.sleep(5 * (t + 1))
for r in M: od(r['match_id']); time.sleep(1.05)
with ThreadPoolExecutor(12) as ex: list(ex.map(lambda r: C.pull_trades(r['cond'], r['gst'] - 7200, r['gst'] + 8 * 3600, 'dota/trades'), M))
print('done', N)
