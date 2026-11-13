import sys; sys.path.insert(0,'/home/user/pkarbs/scan')
import volume_first_scan as v, time, random, re, numpy as np
from collections import defaultdict
random.seed(7)
now=time.time(); since=now-60*86400
d=v.get(v.KAL+"/series",{"limit":1000},sleep=0.4)
tick=[s['ticker'] for s in d['series'] if s['ticker'].startswith('KXAAAGAS')]
def fam(t):
    if re.fullmatch(r"KXAAAGASD[A-Z]{2}",t): return "state daily (KXAAAGASD??)"
    if t.startswith("KXAAAGASCD"): return "state CD (KXAAAGASCD??)"
    return t
fams=defaultdict(list)
for t in tick: fams[fam(t)].append(t)
rows=[]
for f,ts in sorted(fams.items()):
    evs=defaultdict(list)
    for t in ts:
        cur=None
        for _ in range(4):
            p={"series_ticker":t,"status":"settled","min_close_ts":int(since),"limit":1000}
            if cur:p["cursor"]=cur
            r=v.get(v.KAL+"/markets",p,sleep=0.35)
            if not r:break
            for m in r.get('markets',[]):
                if m.get('result') in('yes','no'): evs[m['event_ticker']].append((t,m))
            cur=r.get('cursor')
            if not cur:break
    if not evs: continue
    vol=sum(float(m.get('volume_fp',0)) for l in evs.values() for _,m in l)*0.5
    pool=[]
    for et,l in evs.items():
        multi=len(l)>=3
        for t,m in l:
            if multi and m['result']!='yes': continue
            try:
                ct=time.mktime(time.strptime(m['close_time'][:19],"%Y-%m-%dT%H:%M:%S"))-time.timezone
                ot=time.mktime(time.strptime(m['open_time'][:19],"%Y-%m-%dT%H:%M:%S"))-time.timezone
            except Exception: continue
            pool.append({"id":m['ticker'],"series":t,"y":int(m['result']=='yes'),"close":ct,"open":ot})
    random.shuffle(pool); fs=[]
    for m in pool[:40]:
        r=v.kal_winner_stats(m)
        if r: fs.append(r[0])
    if len(fs)<3: 
        print(f,"too few paths",len(pool),len(fs)); continue
    fs=np.array(fs)
    rows.append((f,vol/60,len(pool),len(evs),len(fs),float((fs>0.7).mean()),float(fs.mean())))
    print(rows[-1],flush=True)
print("\n| series | volume $/day | resolved winners (events) | measured | share after 70% | mean emergence |")
for r in sorted(rows,key=lambda r:-r[1]): print(f"| {r[0]} | ${r[1]:,.0f} | {r[2]} ({r[3]}) | {r[4]} | {r[5]*100:.0f}% | {r[6]:.2f} |")
