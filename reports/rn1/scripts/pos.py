import json
from g import get
W="0x2005d16a84ceefa912d4e380cd32e7ff827875ea"
B="https://data-api.polymarket.com"
for sb in ["REALIZEDPNL"]:
  for d in ["DESC","ASC"]:
    try:
        r=get(f"{B}/closed-positions?user={W}&limit=25&sortBy={sb}&sortDirection={d}")
        print(sb,d,len(r))
        for x in r[:15]: print(round(x.get("realizedPnl",0)),round(x.get("totalBought",0)),x.get("avgPrice"),x.get("curPrice"),x.get("outcome"),x.get("title")[:60],x.get("endDate"))
    except Exception as e: print(sb,d,e)
p=get(f"{B}/positions?user={W}&limit=500&sizeThreshold=1")
print("open positions",len(p),"value",round(sum(x["currentValue"] for x in p)),"cost",round(sum(x["initialValue"] for x in p)))
for x in sorted(p,key=lambda x:-x["currentValue"])[:10]: print(round(x["currentValue"]),x["outcome"],x["avgPrice"],x["curPrice"],x["title"][:60])
json.dump(p,open("pos.json","w"))
