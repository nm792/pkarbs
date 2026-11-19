import requests,json,time,gzip
HL="https://api.hyperliquid.xyz/info";PM="https://api.perpetuals.polymarket.com/v1/info/tickers"
HLS={"xyz":["GOLD","SILVER","CL","BRENTOIL","SP500","XYZ100","NVDA","EUR","COPPER","PLATINUM","PALLADIUM","URNM","BIRD"],"flx":["OIL","COPPER","GAS","SILVER"],"km":["BMNR","RTX"]}
PMS=["SP500-USD","NAS100-USD","GOLD-USD","SILVER-USD","WTIOIL-USD","BRENTOIL-USD","NVDA-USD","MU-USD","AMD-USD","TSLA-USD"]
S=requests.Session();end=time.time()+1800
out=gzip.open("sample.jsonl.gz","wt")
while time.time()<end:
    t0=time.time()
    try:
        for d,names in HLS.items():
            m,c=S.post(HL,json={"type":"metaAndAssetCtxs","dex":d},timeout=10).json()
            for u,x in zip(m["universe"],c):
                n=u["name"].split(":")[1]
                if n in names: out.write(json.dumps(dict(t=t0,v="hl",d=d,s=n,mark=float(x["markPx"]),oracle=float(x["oraclePx"]),mid=float(x["midPx"]) if x.get("midPx") else None))+"\n")
        for x in S.get(PM,timeout=10).json():
            if x["symbol"] in PMS: out.write(json.dumps(dict(t=t0,v="pm",s=x["symbol"],mark=float(x["mark_price"]),oracle=float(x["index_price"]),mid=float(x["mid_price"]) if x.get("mid_price") else None,last=float(x["last_price"])))+"\n")
        out.flush()
    except Exception as e: pass
    time.sleep(max(0,5-(time.time()-t0)))
out.close();print("done")
