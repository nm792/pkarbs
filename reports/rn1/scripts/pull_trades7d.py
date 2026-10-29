# Pulls /trades for both takerOnly flags in 1 h windows (run in Composio sandbox, 29 Oct 03:05Z). Uses get() from g.py.
import json,time,os
from concurrent.futures import ThreadPoolExecutor
from g import get
W="0x2005d16a84ceefa912d4e380cd32e7ff827875ea"
S,E=1792634632,1793239431
OUT="trades7d"; os.makedirs(OUT,exist_ok=True)
def win(t,a,b,acc,log):
    u=f"https://data-api.polymarket.com/trades?user={W}&takerOnly={t}&limit=500&start={a}&end={b}"
    off=0; got=[]
    while True:
        try: bb=get(u+f"&offset={off}",retry=3)
        except Exception as e: log.append((a,b,off,"ERR "+str(e))); return
        got+=bb
        if len(bb)<500: break
        off+=500
        if off>=10000:
            log.append((a,b,off,"cap-split")); m=(a+b)//2; win(t,a,m,acc,log); win(t,m+1,b,acc,log); return
    acc.extend(got); log.append((a,b,len(got),"ok"))
def hour(t,a):
    fn=f"{OUT}/{t}_{a}.json"
    if os.path.exists(fn): return 0
    acc=[];log=[]; win(t,a,min(E,a+3599),acc,log)
    if any("ERR" in str(x[3]) for x in log): return -1
    json.dump({"start":a,"end":min(E,a+3599),"takerOnly":t,"pulled_at":int(time.time()),"log":log,"rows":acc},open(fn,"w")); return len(acc)
jobs=[(t,a) for t in ["true","false"] for a in range(S,E+1,3600)]
with ThreadPoolExecutor(8) as ex: print(list(ex.map(lambda j:hour(*j),jobs)).count(-1),"errors")
