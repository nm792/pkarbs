import json,urllib.request,sys,collections
W="0x2005d16a84ceefa912d4e380cd32e7ff827875ea"
U="https://api.goldsky.com/api/public/project_cl6mb8i9h0003e201j6li0diw/subgraphs/orderbook-subgraph/0.0.1/gn"
def q(s):
    r=urllib.request.Request(U,data=json.dumps({"query":s}).encode(),headers={"Content-Type":"application/json","User-Agent":"curl/8"})
    return json.load(urllib.request.urlopen(r,timeout=60))
for role in ["maker","taker"]:
    d=q('{orderFilledEvents(first:1000,orderBy:timestamp,orderDirection:desc,where:{%s:"%s"}){timestamp maker taker makerAssetId takerAssetId makerAmountFilled takerAmountFilled fee}}'%(role,W))
    if "errors" in d: print(d); continue
    ev=d["data"]["orderFilledEvents"]
    print(role,len(ev), ev[0]["timestamp"] if ev else None, ev[-1]["timestamp"] if ev else None)
    c=collections.Counter(e["taker"] if role=="maker" else e["maker"] for e in ev)
    print(" counterparties top:",c.most_common(4))
    fees=sum(int(e["fee"]) for e in ev)/1e6; print(" fee sum",fees)
    json.dump(ev,open(f"gs_{role}.json","w"))
    print(ev[:2])
