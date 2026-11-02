import json, subprocess, sys, datetime as dt, glob, os, csv
from concurrent.futures import ThreadPoolExecutor
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
K = "0TvQnueqKa5mxJntVWt0w4LpLfEkrV1Ta8rQBb9Z"
def get(url, params=None, headers=None):
    cmd = ['curl','-sS','-m','30','-A',UA,'-G',url]
    for k,v in (params or {}).items(): cmd += ['--data-urlencode', f'{k}={v}']
    for k,v in (headers or {}).items(): cmd += ['-H', f'{k}: {v}']
    return subprocess.run(cmd+['-w','\n%{http_code}'],capture_output=True,text=True).stdout
def jget(url, params=None, headers=None):
    o = get(url, params, headers); body, code = o.rsplit('\n',1)
    return int(code), (json.loads(body) if code=='200' else None)
m = json.load(open('matched.json'))
mid = sys.argv[1]; idx = [x['match_id'] for x in m].index(mid); info = m[idx]
c, d = jget("https://esports-api.lolesports.com/persisted/gw/getEventDetails", {'hl':'en-US','id':mid}, {'x-api-key':K})
games = [g for g in d['data']['event']['match']['games'] if g['state']=='completed' and g.get('number')==1]
gid = games[0]['id']
st = dt.datetime.fromisoformat(info['start'].replace('Z','+00:00'))
# find game start: probe every 2 min from -60 to +60 min
probes = [st + dt.timedelta(minutes=2*i-60) for i in range(0,61)]
def probe(t):
    c, w = jget(f"https://feed.lolesports.com/livestats/v1/window/{gid}", {'startingTime': t.strftime('%Y-%m-%dT%H:%M:%SZ')})
    return t, c
with ThreadPoolExecutor(8) as ex: res = list(ex.map(probe, probes))
ok = [t for t,c in res if c==200]
if not ok: print('NO FRAMES', mid); sys.exit(0)
start = ok[0] - dt.timedelta(minutes=2)
times = [start + dt.timedelta(seconds=10*i) for i in range(0, 360)]
def cap(t):
    c, w = jget(f"https://feed.lolesports.com/livestats/v1/window/{gid}", {'startingTime': t.strftime('%Y-%m-%dT%H:%M:%SZ')})
    return w['frames'] if c==200 and w else []
with ThreadPoolExecutor(8) as ex: chunks = list(ex.map(cap, times))
fr = {}
for ch in chunks:
    for x in ch: fr[x['rfc460Timestamp']] = x
frames = [fr[t] for t in sorted(fr)]
out_dir = f"out/{mid}"; os.makedirs(out_dir, exist_ok=True)
json.dump(frames, open(f"{out_dir}/frames.json",'w'))
ends = [f for f in frames if f['gameState']=='finished']
print(mid, gid, info['teams'], 'frames', len(frames), frames[0]['rfc460Timestamp'] if frames else None, frames[-1]['rfc460Timestamp'] if frames else None, 'finished' if ends else 'NOT finished')
# trades
cid = info['condition']
allt = []; off = 0
while True:
    c, t = jget("https://data-api.polymarket.com/trades", {'market': cid, 'limit': 500, 'offset': off})
    if c!=200 or not t: break
    allt += t
    if len(t) < 500 or off >= 10000: break
    off += 500
json.dump(allt, open(f"{out_dir}/trades.json",'w'))
print('trades', len(allt))
