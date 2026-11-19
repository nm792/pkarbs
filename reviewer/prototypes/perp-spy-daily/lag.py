import json,gzip,math,bisect,datetime as dt,statistics as st
N=lambda x:0.5*(1+math.erf(x/math.sqrt(2))); fee=lambda a:0.04*a*(1-a)
r=json.load(open("result.json")); SG={int(k):v/1e4 for k,v in r["sigma_bp"].items()}; MU={int(k):v/1e4 for k,v in r["mu_bp"].items()}
m=json.load(gzip.open("data/hl_SP500.json.gz"))["m1"]; mt=[c["T"]//1000+1 for c in m]; mc=[float(c["c"]) for c in m]
y=json.load(gzip.open("data/yahoo_SP500.json.gz")); ts=y["timestamp"]; cl=y["indicators"]["quote"][0]["close"]
ev={e["date"]:e for e in json.load(open("data/events.json"))}
def interp(tab,tau):
    if tau>23: return tab[23]*math.sqrt(tau/23) if tab is SG else tab[23]
    tau=max(tau,1.0); a=int(math.floor(tau)); b=min(a+1,23); w=tau-a; return tab[a]*(1-w)+tab[b]*w
def perp(t):
    i=bisect.bisect_right(mt,t)-1; return mc[i] if i>=0 and t-mt[i]<=120 else None
out={}
for d,K,C0 in (("2026-11-13",None,None),("2026-11-16",None,None)):
    i=[j for j,t in enumerate(ts) if dt.datetime.fromtimestamp(t,dt.UTC).date().isoformat()==d][0] if d!="2026-11-16" else None
    if d=="2026-11-13": K=ts[i]+int(6.5*3600); C0=cl[i-1]
    else: K=int(dt.datetime(2026,11,16,21,0,tzinfo=dt.UTC).timestamp()); C0=cl[-1]  # 13 Nov close = last Yahoo bar
    e=ev[d]; tr=sorted(json.load(gzip.open(f"data/trades_{d}.json.gz")),key=lambda t:t["timestamp"])
    fair=lambda t:(lambda P:None if P is None else N((math.log(P/C0)+interp(MU,(K-t)/3600))/interp(SG,(K-t)/3600)))(perp(t))
    pr=[(t["timestamp"],t["price"] if t["outcome"]=="Up" else 1-t["price"],t) for t in tr if perp(t["timestamp"]) is not None]
    tp=[p[0] for p in pr]
    moves=[];skip=0;nomeas=0
    for t in range(mt[0]+300,min(mt[-1],K),60):
        if t<skip: continue
        a,b=perp(t-300),perp(t)
        if a is None or b is None or abs(math.log(b/a))<0.001: continue
        skip=t+600; dp=fair(t)-fair(t-300)
        pre=[p[1] for p in pr if t-900<=p[0]<=t-300]
        if not pre: nomeas+=1; moves.append(dict(t=t,move_bp=round(math.log(b/a)*1e4,1),dp=round(dp,3),lag_s=None,why="no PM prints before")); continue
        L=st.median(pre); tgt=L+dp/2; lag=None
        for p in pr[bisect.bisect_left(tp,t):]:
            if p[0]>t+1800: break
            if (dp>0 and p[1]>=tgt) or (dp<0 and p[1]<=tgt): lag=p[0]-t; break
        moves.append(dict(t=t,utc=dt.datetime.fromtimestamp(t,dt.UTC).strftime("%d %H:%M"),move_bp=round(math.log(b/a)*1e4,1),dp=round(dp,3),pm_pre=round(L,3),lag_s=lag))
    stale=[];
    for ts_,ip,t in pr:
        if t["side"]!="BUY": continue
        f=fair(ts_-60)
        if f is None: continue
        fj=f if t["outcome"]=="Up" else 1-f
        if t["price"]<fj-fee(t["price"])-0.01:
            j=0 if t["outcome"]=="Up" else 1
            stale.append(dict(utc=dt.datetime.fromtimestamp(ts_,dt.UTC).strftime("%d %H:%M:%S"),outcome=t["outcome"],price=t["price"],fair=round(fj,3),usd=round(t["size"]*t["price"],2),pnl_share=round(float(e["final"][j])-t["price"]-fee(t["price"]),3)))
    allbuy=sum(t["size"]*t["price"] for t in tr if t["side"]=="BUY" and perp(t["timestamp"]) is not None)
    out[d]=dict(prints_with_perp=len(pr),moves=moves,moves_measurable=sum(1 for x in moves if "why" not in x),
        lags_s=sorted(x["lag_s"] for x in moves if x.get("lag_s") is not None),censored_30min=sum(1 for x in moves if "why" not in x and x["lag_s"] is None),
        taker_buy_usd_covered=round(allbuy),stale_buy_usd=round(sum(s["usd"] for s in stale),2),stale_n=len(stale),
        stale_pnl_usd=round(sum(s["pnl_share"]*s["usd"]/s["price"] for s in stale),2),stale=stale)
json.dump(out,open("lag_result.json","w"),indent=1)
for d,o in out.items(): print(d,{k:v for k,v in o.items() if k not in ("moves","stale")}); [print("  ",x) for x in o["moves"]]; [print("  S",s) for s in o["stale"][:40]]
