import json
from g import get
W="0x2005d16a84ceefa912d4e380cd32e7ff827875ea"
res={}
for t in ["true","false"]:
    rows=[]
    for off in range(0,3000,500):
        try: b=get(f"https://data-api.polymarket.com/trades?user={W}&limit=500&offset={off}&takerOnly={t}",retry=2)
        except Exception as e: print(t,off,e); break
        rows+=b
        if len(b)<500: break
    res[t]=rows
    ts=[r["timestamp"] for r in rows]
    print(t,len(rows),min(ts),max(ts))
lo=max(min(r["timestamp"] for r in res[t]) for t in res)
for t in res:
    s=[r for r in res[t] if r["timestamp"]>=lo]
    print("takerOnly",t,"since",lo,"n",len(s),"usdc",round(sum(r["size"]*r["price"] for r in s)), "sides",{x:sum(1 for r in s if r["side"]==x) for x in ["BUY","SELL"]})
json.dump(res,open("mt.json","w"))
print(res["true"][0])
