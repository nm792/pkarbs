import requests,json,time,concurrent.futures as cf
HL="https://api.hyperliquid.xyz/info";now=int(time.time()*1000)
h=json.load(open("hist.json"));syms=[s for s,v in h["fund"].items() if len(v)>=1440]
def f(coin):
    rows=[];st=now-208*86400000
    while st<now:
        e=min(now,st+30*86400000)
        for k in range(4):
            try: r=requests.post(HL,json={"type":"candleSnapshot","req":{"coin":coin,"interval":"1h","startTime":st,"endTime":e}},timeout=40).json();break
            except Exception: time.sleep(2);r=[]
        rows+=(r if isinstance(r,list) else []);st=e+1
    sp=None
    try:
        b=requests.post(HL,json={"type":"l2Book","coin":coin},timeout=20).json()["levels"]
        bid,ask=float(b[0][0]["px"]),float(b[1][0]["px"]);sp=(ask-bid)/((ask+bid)/2)*1e4/2
    except Exception: pass
    return coin,{x["t"]:[float(x["o"]),float(x["c"])] for x in rows},sp
out={};hs={}
with cf.ThreadPoolExecutor(4) as ex:
    for c,r,sp in ex.map(f,syms): out[c]=r;hs[c]=sp
json.dump(dict(candles=out,halfspread=hs),open("cand.json","w"))
print(len(out),sum(1 for v in out.values() if v))
