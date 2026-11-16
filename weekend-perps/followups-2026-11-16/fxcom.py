import json,requests,time,datetime,calendar,numpy as np,random,urllib.parse
H=3600000;UA={"user-agent":"Mozilla/5.0"}
HL="https://api.hyperliquid.xyz/info";PM="https://api.perpetuals.polymarket.com"
U=[("xyz","GOLD","GC=F"),("xyz","SILVER","SI=F"),("xyz","COPPER","HG=F"),("xyz","PLATINUM","PL=F"),("xyz","PALLADIUM","PA=F"),("xyz","CL","CL=F"),("xyz","BRENTOIL","BZ=F"),("xyz","NATGAS","NG=F"),("xyz","CORN","ZC=F"),("xyz","WHEAT","ZW=F"),("xyz","ALUMINIUM","ALI=F"),("xyz","EUR","EURUSD=X"),("xyz","JPY","JPY=X"),("xyz","GBP","GBPUSD=X"),("xyz","DXY","DX-Y.NYB"),
("flx","OIL","CL=F"),("flx","GAS","NG=F"),("flx","COPPER","HG=F"),("flx","GOLD","GC=F"),("flx","SILVER","SI=F"),("flx","PLATINUM","PL=F"),("flx","PALLADIUM","PA=F"),
("pm","GOLD-USD","GC=F"),("pm","SILVER-USD","SI=F"),("pm","WTIOIL-USD","CL=F"),("pm","BRENTOIL-USD","BZ=F")]
now=int(time.time()*1000);start=calendar.timegm((2026,4,15,0,0,0))*1000
def hlpost(b):
    for k in range(5):
        try: return requests.post(HL,json=b,timeout=40).json()
        except Exception: time.sleep(2)
oi={}
for d in ("xyz","flx"):
    m,c=hlpost({"type":"metaAndAssetCtxs","dex":d})
    for u,x in zip(m["universe"],c): oi[(d,u["name"].split(":")[1])]=float(x["openInterest"])*float(x["markPx"])
ins={i["symbol"]:i["instrument_id"] for i in json.load(open("/tmp/wp/pm_instruments.json"))}
for t in (lambda r:r["data"] if isinstance(r,dict) else r)(requests.get(PM+"/v1/info/tickers",timeout=30).json()):
    oi[("pm",t["symbol"])]=float(t["open_interest"])*float(t["mark_price"])
yc={}
def yh(y):
    if y not in yc:
        d=requests.get(f"https://query1.finance.yahoo.com/v8/finance/chart/{urllib.parse.quote(y)}?interval=1h&range=2y",headers=UA,timeout=60).json()["chart"]["result"]
        if not d: yc[y]=None
        else:
            d=d[0];q=d["indicators"]["quote"][0];ts=d["timestamp"]
            yc[y]=[(ts[i]*1000,q["open"][i],q["close"][i],(q.get("volume") or [None]*len(ts))[i]) for i in range(len(ts)) if q["open"][i] is not None and q["close"][i] is not None]
    return yc[y]
def perp(d,s):
    if d in("xyz","flx"):
        rows=[];st=start
        while st<now:
            e=min(now,st+30*86400000)
            rows+=hlpost({"type":"candleSnapshot","req":{"coin":f"{d}:{s}","interval":"1h","startTime":st,"endTime":e}});st=e+1
        return {x["t"]:(float(x["o"]),float(x["c"])) for x in rows}
    rows=[];st=calendar.timegm((2026,8,1,0,0,0))*1000
    while st<now:
        e=min(now,st+25*86400000)
        r=requests.get(PM+"/v1/info/klines",params=dict(instrument_id=ins[s],interval="1h",start_timestamp=st,end_timestamp=e),timeout=40).json()
        rows+=r.get("data",[]);st=e+1
    return {x[0]:(float(x[1]),float(x[4])) for x in rows}
rnd=random.Random(1)
def bootci(vals_by_wk,fn=np.mean):
    k=list(vals_by_wk);bs=[]
    for _ in range(10000):
        v=[];[v.extend(vals_by_wk[rnd.choice(k)]) for _ in k];bs.append(fn(v))
    bs.sort();return bs[249],bs[9749]
sg=lambda x:(x>0)-(x<0)
res=[]
for d,s,y in U:
    key=f"{d}:{s}"
    try:
        ref=yh(y)
        if not ref: res.append(dict(sym=key,err="no yahoo"));continue
        P=perp(d,s)
        if not P: res.append(dict(sym=key,err="no perp"));continue
    except Exception as ex_: res.append(dict(sym=key,err=str(ex_)[:80]));continue
    refd={t:(o,c,v) for t,o,c,v in ref}
    has_vol=any((v or 0)>0 for _,_,_,v in ref)
    common=[t for t,_,_,_ in ref if t in P]
    if len(common)<50: res.append(dict(sym=key,err=f"few common hours {len(common)}"));continue
    f=common[:20]
    inv=np.median([abs(np.log(refd[t][1]*P[t][1])) for t in f])<np.median([abs(np.log(refd[t][1]/P[t][1])) for t in f])
    pr=lambda t,i:(1/P[t][i] if inv else P[t][i])
    # weekday TE
    te=[];ra=[];rb=[]
    prev=None
    for t,o,c,v in ref:
        if prev is not None and t-prev>2*H: skipuntil=t+2*H
        else: skipuntil=skipuntil if prev is not None else 0
        prev=t
        wd=datetime.datetime.fromtimestamp(t/1000,datetime.UTC).weekday()
        if t<skipuntil or wd>4 or t not in P: continue
        if has_vol and v is not None and v==0: continue
        a=(pr(t,1)/pr(t,0)-1)*1e4;b=(c/o-1)*1e4
        ra.append(a);rb.append(b);te.append(abs(a-b))
    # weekend cells
    cells=[]
    for i in range(1,len(ref)):
        if ref[i][0]-ref[i-1][0]>36*H:
            T=ref[i][0];F=ref[i-1][2];O=ref[i][1];Tend_prev=ref[i-1][0]+H
            cs=(T-1800000)//H*H-H
            if cs not in P: continue
            Pp=pr(cs,1)
            S=(Pp-F)/F*1e4
            fp_t=Tend_prev-H
            Sown=None
            if fp_t in P: Sown=(Pp/pr(fp_t,1)-1)*1e4
            Oo=(O-F)/F*1e4
            cells.append(dict(T=T,S=S,Sown=Sown,O=Oo))
    r=dict(sym=key,ref=y,oi_usd=oi.get((d,s)),inv=bool(inv),n_hours=len(te),med_abs_e=float(np.median(te)) if te else None,p90_abs_e=float(np.percentile(te,90)) if te else None,corr=float(np.corrcoef(ra,rb)[0,1]) if len(te)>10 else None,n_wk=len(cells))
    if cells:
        R=[c["O"]-c["S"] for c in cells];r["med_abs_R"]=float(np.median(np.abs(R)));r["med_abs_S"]=float(np.median([abs(c["S"]) for c in cells]))
        sel=[c for c in cells if abs(c["S"])>=50];r["n_sig"]=len(sel)
        if len(sel)>=5:
            by={}
            for c in sel: by.setdefault(c["T"]//(7*86400000),[]).append(sg(c["S"])*(c["O"]-c["S"]))
            allv=[x for v in by.values() for x in v];r["meanD"]=float(np.mean(allv));r["D_ci"]=bootci(by)
            r["hit"]=sum(1 for c in sel if sg(c["S"])==sg(c["O"]))/len(sel)
        Ro=[c["O"]-c["Sown"] for c in cells if c["Sown"] is not None]
        if Ro: r["med_abs_R_ownclose"]=float(np.median(np.abs(Ro)));r["med_abs_Sown"]=float(np.median([abs(c["Sown"]) for c in cells if c["Sown"] is not None]))
        so=[c for c in cells if c["Sown"] is not None and abs(c["Sown"])>=50];r["n_sig_own"]=len(so)
        if len(so)>=5:
            by={}
            for c in so: by.setdefault(c["T"]//(7*86400000),[]).append(sg(c["Sown"])*(c["O"]-c["Sown"]))
            allv=[x for v in by.values() for x in v];r["meanD_own"]=float(np.mean(allv));r["D_own_ci"]=bootci(by);r["hit_own"]=sum(1 for c in so if sg(c["Sown"])==sg(c["O"]))/len(so)
        if len(cells)>=8: r["slope_R_on_S"]=float(np.polyfit([c["S"] for c in cells],R,1)[0])
    res.append(r);print(r,flush=True)
json.dump(res,open("fxcom_result.json","w"),indent=1,default=float)
# spearman OI vs median |e|
ok=[r for r in res if r.get("med_abs_e") is not None and r.get("oi_usd")]
def rank(x):
    o=np.argsort(x);rk=np.empty(len(x));rk[o]=np.arange(len(x));return rk
a=rank([r["oi_usd"] for r in ok]);b=rank([r["med_abs_e"] for r in ok])
print("spearman OI vs med|e|",np.corrcoef(a,b)[0,1],"n",len(ok))
