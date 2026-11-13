# Pull one livestats frame per STEP seconds for each game (feed.lolesports.com, no key).
# Keeps team-level state + per-player gold/level/kills/deaths/cs. Output: raw/frames/<gid>.json
import json, subprocess, sys, os, datetime as dt, random
from concurrent.futures import ThreadPoolExecutor
UA="Mozilla/5.0"; STEP=60
import threading, requests
_tl=threading.local()
def jget(url, params=None):
    if not hasattr(_tl,'s'):
        _tl.s=requests.Session(); _tl.s.headers['User-Agent']=UA
        _tl.s.verify=os.environ.get('REQUESTS_CA_BUNDLE') or '/root/.ccr/ca-bundle.crt'
    for _ in range(3):
        try:
            r=_tl.s.get(url,params=params,timeout=30)
            return r.status_code,(r.json() if r.status_code==200 and r.content.strip() else None)
        except Exception: continue
    return 0,None
def slim(f):
    out={'t':f['rfc460Timestamp'],'state':f['gameState']}
    for side in ('blueTeam','redTeam'):
        T=f[side]; out[side]={k:T[k] for k in ('totalGold','inhibitors','towers','barons','totalKills','dragons')}
        out[side]['p']=[[p['totalGold'],p['level'],p['kills'],p['deaths'],p['creepScore']] for p in T['participants']]
    return out
def pull(gid):
    path=f'raw/frames/{gid}.json'
    if os.path.exists(path): return gid,'cached'
    c,w=jget(f'https://feed.lolesports.com/livestats/v1/window/{gid}')
    if c!=200 or not w or not w.get('frames'): json.dump({'gid':gid,'err':c},open(path,'w')); return gid,f'nodata {c}'
    meta=w['gameMetadata']
    t0=dt.datetime.fromisoformat(w['frames'][0]['rfc460Timestamp'][:19]+'+00:00')
    t0=t0-dt.timedelta(seconds=t0.second%10)
    frames=[slim(w['frames'][0])]; t=t0; miss=0
    while True:
        t+=dt.timedelta(seconds=STEP)
        c,w2=jget(f'https://feed.lolesports.com/livestats/v1/window/{gid}',{'startingTime':t.strftime('%Y-%m-%dT%H:%M:%SZ')})
        fr=(w2 or {}).get('frames') or []
        if not fr:
            miss+=1
            if miss>=5 or (t-t0).total_seconds()>4*3600: break
            continue
        miss=0; f=slim(fr[0]); frames.append(f)
        if any(x['gameState']=='finished' for x in fr):
            frames.append(slim([x for x in fr if x['gameState']=='finished'][-1])); break
    json.dump({'gid':gid,'meta':{s:meta[s+'TeamMetadata']['esportsTeamId'] for s in ('blue','red')},
               'patch':meta.get('patchVersion'),'frames':frames},open(path,'w'))
    return gid,len(frames)
if __name__=='__main__':
    os.makedirs('raw/frames',exist_ok=True)
    gids=[l.strip() for l in open(sys.argv[1]) if l.strip()]
    with ThreadPoolExecutor(int(sys.argv[2]) if len(sys.argv)>2 else 8) as ex:
        for i,r in enumerate(ex.map(pull,gids)):
            print(i,*r,flush=True)
