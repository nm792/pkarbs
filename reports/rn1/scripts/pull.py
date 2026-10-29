import json,sys,time,urllib.error
from g import get
W="0x2005d16a84ceefa912d4e380cd32e7ff827875ea"
hours=float(sys.argv[1]); out=sys.argv[2]; CAP=int(sys.argv[3]) if len(sys.argv)>3 else 3000
now=int(time.time()); start=now-int(hours*3600)
rows={}; log=open(out+".log","w")
def win(a,b):
    u=f"https://data-api.polymarket.com/activity?user={W}&limit=500&start={a}&end={b}&sortBy=TIMESTAMP&sortDirection=DESC"
    got=[];off=0
    while True:
        try: bb=get(u+f"&offset={off}",retry=2)
        except urllib.error.HTTPError as e:
            bb=None
        if bb is None or (len(bb)==500 and off+500>=CAP):
            if bb: got+=bb
            if b-a<=1: break
            m=(a+b)//2; win(a,m); win(m+1,b); return
        got+=bb
        if len(bb)<500: break
        off+=500
    for r in got:
        rows[(r["transactionHash"],r.get("asset"),r["type"],r.get("size"),r.get("side"),r["timestamp"],r.get("price"))]=r
    print(a,b,len(got),file=log,flush=True)
step=3600
for b in range(now,start,-step):
    win(max(start,b-step+1),b)
    json.dump(list(rows.values()),open(out,"w"))
print(len(rows))
