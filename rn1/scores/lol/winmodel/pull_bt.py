# For matched PM game markets: 10 s livestats frames (full window frames, slimmed) + all data-api trades.
# Output raw/bt/<gid>/frames.json.gz, trades.json.gz
import json, gzip, os, sys, datetime as dt
from concurrent.futures import ThreadPoolExecutor
from pull_frames import jget, slim
def pull(x):
    gid = x['gid']; od = f'raw/bt/{gid}'
    if os.path.exists(f'{od}/trades.json.gz'): return gid, 'cached'
    os.makedirs(od, exist_ok=True)
    c, w = jget(f'https://feed.lolesports.com/livestats/v1/window/{gid}')
    if c != 200 or not w or not w.get('frames'): return gid, f'noframes {c}'
    t = dt.datetime.fromisoformat(w['frames'][0]['rfc460Timestamp'][:19] + '+00:00'); t -= dt.timedelta(seconds=t.second % 10)
    t0 = t; fr = {f['rfc460Timestamp'][:19]: f for f in w['frames']}; miss = 0; fin = False
    tend = None
    if os.path.exists(f'raw/frames/{gid}.json'):
        z = json.load(open(f'raw/frames/{gid}.json')).get('frames') or []
        fz = [f['t'] for f in z if f['state'] == 'finished']
        if fz: tend = dt.datetime.fromisoformat(fz[0][:19] + '+00:00')
    while not fin and (t - t0).total_seconds() < 3 * 3600 and ((tend is not None and t <= tend + dt.timedelta(seconds=30)) or (tend is None and miss < 60)):
        t += dt.timedelta(seconds=10)
        c, w2 = jget(f'https://feed.lolesports.com/livestats/v1/window/{gid}', {'startingTime': t.strftime('%Y-%m-%dT%H:%M:%SZ')})
        ff = (w2 or {}).get('frames') or []
        if not ff: miss += 1; continue
        miss = 0
        for f in ff:
            fr.setdefault(f['rfc460Timestamp'][:19], f)   # first frame of each second
            if f['gameState'] == 'finished': fin = True
    frames = [slim(fr[k]) for k in sorted(fr)]
    json.dump(frames, gzip.open(f'{od}/frames.json.gz', 'wt'))
    ts = lambda z: int(dt.datetime.fromisoformat(z[:19] + '+00:00').timestamp())
    p = {'condition': x['condition'], 'limit': 500, 'start': ts(frames[0]['t']) - 1800, 'end': ts(frames[-1]['t']) + 600}
    allt = []; cur = None
    for _ in range(400):
        if cur: p['cursor'] = cur
        c, d = jget('https://data-api.polymarket.com/v2/trades', p)
        if c != 200 or not d: break
        allt += [{k: z[k] for k in ('timestamp', 'outcome', 'outcome_index', 'side', 'price', 'size', 'proxy_wallet', 'transaction_hash')} for z in d['data']]
        cur = d['pagination'].get('next_cursor')
        if not d['pagination'].get('has_more') or not cur: break
    json.dump(allt, gzip.open(f'{od}/trades.json.gz', 'wt'))
    return gid, len(frames), len(allt), fin
if __name__ == '__main__':
    X = json.load(open('raw/pm/pm_game_markets_matched.json'))
    X.sort(key=lambda x: x['start'], reverse=True)
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 150
    with ThreadPoolExecutor(int(sys.argv[2]) if len(sys.argv) > 2 else 24) as ex:
        for i, r in enumerate(ex.map(pull, X[:n])): print(i, *r, flush=True)
