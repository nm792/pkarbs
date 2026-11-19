import requests,json,time,concurrent.futures as cf
HL="https://api.hyperliquid.xyz/info";now=int(time.time()*1000)
dexs=["xyz","flx","km"]
syms=[];oi={}
for d in dexs:
    m,c=requests.post(HL,json={"type":"metaAndAssetCtxs","dex":d},timeout=30).json()
    for u,x in zip(m["universe"],c):
        n=u["name"];syms.append(n);oi[n]=float(x["openInterest"])*float(x["markPx"])
def f(coin):
    rows=[];st=now-420*86400000
    for _ in range(40):
        for k in range(4):
            try:
                r=requests.post(HL,json={"type":"fundingHistory","coin":coin,"startTime":st},timeout=40).json();break
            except Exception: time.sleep(2);r=[]
        if not r:break
        rows+=r
        if len(r)<500:break
        st=r[-1]["time"]+1
    return coin,[(x["time"],float(x["premium"]),float(x["fundingRate"])) for x in rows]
out={}
with cf.ThreadPoolExecutor(4) as ex:
    for c,r in ex.map(f,syms): out[c]=r
json.dump(dict(oi=oi,fund=out),open("hist.json","w"))
print(len(out),sum(1 for v in out.values() if len(v)>=1440))
