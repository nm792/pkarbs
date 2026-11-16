import json,requests,time,datetime,random,numpy as np,concurrent.futures as cf,urllib.parse
B="https://api.perpetuals.polymarket.com"
ins=json.load(open("/tmp/wp/pm_instruments.json"))
EXC={"SKHY","SKHYNIX","SAMSUNG","CXMT","UNITREE","SPCX","CBRS","ANT"}
ydm={"SP500":"^GSPC","NAS100":"^NDX","GOOG":"GOOG"}
L=[]
for i in ins:
    if i["category"] in("equity","index"):
        b=i["base_asset"]
        if b in EXC: continue
        L.append((i["instrument_id"],i["symbol"],ydm.get(b,b),i["category"]))
S_=requests.Session()
def get(p,**q):
    for k in range(5):
        try:
            r=S_.get(B+p,params=q,timeout=30)
            if r.status_code==200: return r.json()
            time.sleep(1.5)
        except Exception: time.sleep(1.5)
    return None
def yahoo(y):
    u=f"https://query1.finance.yahoo.com/v8/finance/chart/{urllib.parse.quote(y)}?interval=1d&range=6mo"
    try:
        d=requests.get(u,headers={"user-agent":"Mozilla/5.0"},timeout=40).json()["chart"]["result"][0]
        q=d["indicators"]["quote"][0];ts=d["timestamp"]
        return [(ts[i],q["open"][i],q["close"][i]) for i in range(len(ts)) if q["open"][i] is not None and q["close"][i] is not None]
    except Exception: return None
LIVE=datetime.date(2026,8,3)
cells=[];nodata=[]
for iid,sym,y,cat in L:
    bars=yahoo(y)
    if not bars: nodata.append(sym);continue
    for i in range(1,len(bars)):
        t0,_,c0=bars[i-1];t1,o1,_=bars[i]
        d0=datetime.datetime.fromtimestamp(t0,datetime.UTC).date();d1=datetime.datetime.fromtimestamp(t1,datetime.UTC).date()
        if d1<LIVE or d1.weekday()>4: continue
        gap=(d1-d0).days
        wk=d1.weekday()==0
        if (wk and gap!=3) or ((not wk) and gap!=1): continue
        cells.append(dict(iid=iid,sym=sym,cat=cat,date=str(d1),wk=wk,T=t1*1000,F=c0,open=o1))
print("cells",len(cells),"nodata",nodata,flush=True)
def sig(c):
    t=c["T"]-1800000
    d=get("/v1/info/mark-history",instrument_id=c["iid"],interval="1s",start_timestamp=t-120000,end_timestamp=t+1000)
    pts=[x for x in (d or {}).get("data",[]) if x[0]<=t]
    if not pts: c["S"]=None;return c
    c["mark"]=float(pts[-1][1]);c["S"]=(c["mark"]-c["F"])/c["F"]*1e4;return c
with cf.ThreadPoolExecutor(6) as ex: cells=list(ex.map(sig,cells))
sigc=[c for c in cells if c["S"] is not None and abs(c["S"])>=100]
print("with S",sum(1 for c in cells if c["S"] is not None),"signals",len(sigc),"weekend",sum(c["wk"] for c in sigc),flush=True)
def trades(iid,a,b):
    out=[];cur_end=b
    for _ in range(10):
        d=get("/v1/info/trades",instrument_id=iid,start_timestamp=a,end_timestamp=cur_end,limit=1000)
        data=(d or {}).get("data",[])
        out+=data
        if len(data)<1000: break
        cur_end=min(x["timestamp"] for x in data)-1
    return sorted(out,key=lambda x:x["timestamp"])
def trade(c):
    s=1 if c["S"]>0 else -1;T=c["T"]
    ent=trades(c["iid"],T-29*60000,T-20*60000)
    ex_=trades(c["iid"],T+5*60000,T+10*60000)
    es="long" if s>0 else "short";xs="short" if s>0 else "long"
    e=[x for x in ent if x["side"]==es];x_=[x for x in ex_ if x["side"]==xs]
    if not e or not x_: c["ok"]=False;return c
    c["ok"]=True;c["entry"]=float(e[0]["price"]);c["entry_t"]=e[0]["timestamp"]-T;c["exit"]=float(x_[0]["price"]);c["exit_t"]=x_[0]["timestamp"]-T
    c["entry_notional"]=float(e[0]["price"])*float(e[0]["quantity"]);c["exit_notional"]=float(x_[0]["price"])*float(x_[0]["quantity"])
    c["gross"]=s*(c["exit"]-c["entry"])/c["entry"]*1e4;c["net"]=c["gross"]-8
    # spread proxy: nearest opposite-side trade within 10 s of the entry trade
    opp=[x for x in ent if x["side"]!=es and abs(x["timestamp"]-e[0]["timestamp"])<=10000]
    if opp:
        o=min(opp,key=lambda x:abs(x["timestamp"]-e[0]["timestamp"]));c["spread_bp"]=abs(c["entry"]-float(o["price"]))/c["entry"]*1e4
    return c
with cf.ThreadPoolExecutor(6) as ex: sigc=list(ex.map(trade,sigc))
json.dump(sigc,open("pm_drift_cells.json","w"),default=float)
print("done",flush=True)
