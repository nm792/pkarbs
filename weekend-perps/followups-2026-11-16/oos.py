import json,requests,time,datetime,calendar,urllib.parse,numpy as np,random
H=3600000;HL="https://api.hyperliquid.xyz/info";UA={"user-agent":"Mozilla/5.0"}
now=int(time.time()*1000);CUT=calendar.timegm((2026,4,22,0,0,0))*1000
SYMS={"SILVER":("SI=F",-1,1.0),"COPPER":("HG=F",-1,4.9),"PLATINUM":("PL=F",-1,6.2),"BRENTOIL":("BZ=F",1,1.0)}
def post(b):
    for k in range(5):
        try:return requests.post(HL,json=b,timeout=40).json()
        except Exception:time.sleep(2)
def candles(coin,iv,start):
    rows=[];st=start;step=30*86400000 if iv=="1h" else 400*86400000
    while st<now:
        e=min(now,st+step);rows+=post({"type":"candleSnapshot","req":{"coin":coin,"interval":iv,"startTime":st,"endTime":e}});st=e+1
    return {x["t"]:float(x["c"]) for x in rows}
def yh(y):
    d=requests.get(f"https://query1.finance.yahoo.com/v8/finance/chart/{urllib.parse.quote(y)}?interval=1h&range=2y",headers=UA,timeout=60).json()["chart"]["result"][0]
    q=d["indicators"]["quote"][0];ts=d["timestamp"]
    return [(ts[i]*1000,q["open"][i],q["close"][i]) for i in range(len(ts)) if q["open"][i] is not None and q["close"][i] is not None]
sg=lambda x:(x>0)-(x<0)
rnd=random.Random(1)
def cells(ref,P,Rh):
    out=[]
    for i in range(1,len(ref)):
        if ref[i][0]-ref[i-1][0]<=36*H: continue
        T=ref[i][0];lastend=ref[i-1][0]+H
        ps=(lastend//Rh)*Rh-Rh;es=((T-1800000)//Rh)*Rh-Rh
        xs=-((-(T+H-Rh))//Rh)*Rh
        if ps not in P or es not in P or xs not in P: continue
        out.append(dict(T=T,S=(P[es]/P[ps]-1)*1e4,ent=P[es],ext=P[xs]))
    return out
res={}
for s,(y,pos,hs) in SYMS.items():
    ref=yh(y)
    p1=candles(f"xyz:{s}","1h",calendar.timegm((2026,4,15,0,0,0))*1000)
    p4=candles(f"xyz:{s}","4h",now-1200*86400000)
    res[s]=dict(disc1=[c for c in cells(ref,p1,H) if c["T"]>=CUT],coarse=[c for c in cells(ref,p4,4*H) if c["T"]>=CUT],held=[c for c in cells(ref,p4,4*H) if c["T"]<CUT])
    print(s,{k:len(v) for k,v in res[s].items()},flush=True)
def trades(sample,fee):
    out=[]
    for s,(y,pos,hs) in SYMS.items():
        for c in res[s][sample]:
            if abs(c["S"])<50: continue
            g=pos*sg(c["S"])*(c["ext"]/c["ent"]-1)*1e4
            cost=2*(fee+max(3*hs/ (1) if False else hs,1.0))
            out.append(dict(sym=s,wk=c["T"]//(7*86400000),T=c["T"],S=c["S"],gross=g,net=g-cost))
    return out
def boot(v):
    wk={}
    for x in v:wk.setdefault(x["wk"],[]).append(x["net"])
    k=list(wk);bs=[]
    for _ in range(10000):
        a=[];[a.extend(wk[rnd.choice(k)]) for _ in k];bs.append(np.mean(a))
    bs.sort();return round(bs[249],1),round(bs[9749],1)
def rep(name,v):
    if not v:print(f"{name:34s} n=0");return None
    wk={}
    for x in v:wk.setdefault(x["wk"],[]).append(x)
    right=np.mean([np.mean([y["gross"] for y in l])>0 for l in wk.values()])
    tot=sum(x["net"] for x in v);sh={w:sum(y["net"] for y in l) for w,l in wk.items()}
    mx=max(sh.values())/tot if tot>0 else None
    print(f"{name:34s} n={len(v):3d} wk={len(wk):2d} gross={np.mean([x['gross'] for x in v]):7.1f} net={np.mean([x['net'] for x in v]):7.1f} med_net={np.median([x['net'] for x in v]):7.1f} CI={boot(v)} wk_right={right:.0%} max_wk_share={mx if mx is None else round(mx,2)}")
    return v
for fee,lab in((9,"fee9"),(4.5,"fee4.5")):
    print("=====",lab)
    for sample in("disc1","coarse","held"):
        metals=[t for t in trades(sample,fee) if t["sym"]!="BRENTOIL"]
        rep(f"{sample} metals pooled",metals)
        for s in("SILVER","COPPER","PLATINUM"):rep(f"  {sample} {s}",[t for t in metals if t["sym"]==s])
        rep(f"{sample} BRENT",[t for t in trades(sample,fee) if t["sym"]=="BRENTOIL"])
json.dump({s:{k:v for k,v in d.items()} for s,d in res.items()},open("oos_cells.json","w"))
