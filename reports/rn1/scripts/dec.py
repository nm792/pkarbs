import json,collections as C,datetime as dt,sys,time
from g import get
A=json.load(open("act7d.json")); T=[r for r in A if r["type"]=="TRADE"]
conds=sorted(set(r["conditionId"] for r in T))
try: meta=json.load(open("meta_all.json"))
except: meta={}
t0=time.time()
todo=[c for c in conds if c not in meta]
for i in range(0,len(todo),40):
    if time.time()-t0>150: break
    qs="&".join("condition_ids="+c for c in todo[i:i+40])
    for closed in ["true","false"]:
        try:
            for m in get(f"https://gamma-api.polymarket.com/markets?limit=100&closed={closed}&"+qs,retry=2): meta[m["conditionId"]]=m
        except Exception as e: print("err",e)
json.dump(meta,open("meta_all.json","w"))
print("meta",len(meta),"of",len(conds))
