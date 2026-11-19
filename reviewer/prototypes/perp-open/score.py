# Scores LOCKED-RULE.md exactly. Inputs: data/ only. Output: result.json, rows.json.
import json,gzip,math,random,statistics as st,datetime as dt,sys
D="data/"
N=lambda x:0.5*(1+math.erf(x/math.sqrt(2)))
fee=lambda a:0.04*a*(1-a)
ev={e["date"]:e for e in json.load(open(D+"events.json"))}
hl={c["T"]+1:float(c["c"]) for c in json.load(gzip.open(D+"hl_SP500.json.gz"))["h1"]}  # key = candle end (ms)
y=json.load(gzip.open(D+"yahoo_SP500.json.gz")); ts=y["timestamp"]; q=y["indicators"]["quote"][0]
day=lambda t:dt.datetime.fromtimestamp(t,dt.UTC).date().isoformat()
rows=[];excl={}
def ex(r): excl[r]=excl.get(r,0)+1
for i in range(1,len(ts)):
    d=day(ts[i])
    if d<"2026-04-22" or d>"2026-11-13": continue
    if d not in ev: ex("no PM event"); continue
    T=ts[i]*1000; C=q["close"][i-1]; O=q["open"][i]
    P=hl.get(T-1800000)
    if P is None: ex("no perp candle ending T-30"); continue
    e=ev[d]; tr=json.load(gzip.open(D+f"trades_{d}.json.gz"))
    r=dict(date=d,T=T,C=C,O=O,P=P,S=(P-C)/C,R=(O-C)/C-(P-C)/C,final=[float(x) for x in e["final"]],outcomes=e["outcomes"])
    for k,tok in enumerate(e["tokens"]):
        b=[t for t in tr if t["token_id"]==tok and t["side"]=="BUY"]
        w1=sorted([t for t in b if T/1000-2100<=t["timestamp"]<=T/1000-1800],key=lambda t:t["timestamp"])
        w2=sorted([t for t in b if T/1000-1800<=t["timestamp"]<=T/1000-1500],key=lambda t:t["timestamp"])
        r[f"ask{k}"]=w1[-1]["price"] if w1 else None
        r[f"ask2_{k}"]=w2[0]["price"] if w2 else None
        r[f"depth{k}"]=sum(t["size"]*t["price"] for t in b if T/1000-3600<=t["timestamp"]<=T/1000)
    rows.append(r)
train=[r for r in rows if r["date"]<"2026-08-01"]; test=[r for r in rows if r["date"]>="2026-08-01"]
mu=st.mean(r["R"] for r in train); sg=st.stdev(r["R"] for r in train)
for r in rows:
    r["p0"]=N((r["S"]+mu)/sg); r["p1"]=1-r["p0"]
def run(rs,askkey="ask",flip=False,plant=None):
    out=[]
    for r in rs:
        best=None
        for k in (0,1):
            p=r[f"p{1-k if flip else k}"]
            a=r.get(f"{askkey}{k}") if askkey=="ask" else r.get(f"ask2_{k}")
            if plant=="edge5":
                if r.get(f"ask{k}") is None: continue
                lo,hi=0.0,1.0
                for _ in range(60):
                    m=(lo+hi)/2
                    if p-m-fee(m)>0.05: lo=m
                    else: hi=m
                a=lo
                if a<=0.001: continue
            elif plant=="null":
                if r.get(f"ask{k}") is None: continue
                a=p
            if a is None: continue
            edge=p-a-fee(a)
            if edge>=0.03 and (best is None or edge>best[1]): best=(k,edge,a)
        if best:
            k,edge,a=best; pay=r["final"][k]; pnl=pay-a-fee(a)
            notional=0.1*r[f"depth{k}"]; shares=notional/a if a>0 else 0
            out.append(dict(date=r["date"],k=k,ask=a,edge=edge,p=r[f"p{k}"],pnl=pnl,usd=pnl*shares,notional=notional,fee_usd=fee(a)*shares))
    return out
def boot(vals,n,f,B=10000):
    rnd=random.Random(1); xs=[]
    for _ in range(B):
        s=[vals[rnd.randrange(n)] for _ in range(n)]; xs.append(f(s))
    xs.sort(); return [xs[int(.025*B)],xs[int(.975*B)]]
def summ(tr,ndays):
    if not tr: return dict(trades=0)
    pnl=[t["pnl"] for t in tr]
    daily=[t["usd"] for t in tr]+[0.0]*(ndays-len(tr))
    return dict(trades=len(tr),days=ndays,hit=sum(1 for t in tr if t["pnl"]>0)/len(tr),mean_ask=st.mean(t["ask"] for t in tr),
        mean_edge_exante=st.mean(t["edge"] for t in tr),mean_pnl_share=st.mean(pnl),ci_pnl_share=boot(pnl,len(pnl),st.mean) if len(pnl)>1 else None,
        median_notional=st.median(t["notional"] for t in tr),usd_per_day=sum(daily)/ndays,ci_usd_day=boot(daily,ndays,st.mean),
        rebate_usd_day=0.25*sum(t["fee_usd"] for t in tr)/ndays)
res=dict(rule_commit="47889d5b",mu_bp=mu*1e4,sigma_bp=sg*1e4,n_rows=len(rows),n_train=len(train),n_test=len(test),excluded=excl)
for name,rs in (("train",train),("test",test)):
    res[name]=dict(
      asks_available=dict(up=sum(r["ask0"] is not None for r in rs),down=sum(r["ask1"] is not None for r in rs),both=sum(r["ask0"] is not None and r["ask1"] is not None for r in rs)),
      calib=dict(brier=st.mean((r["p0"]-(r["final"][0]))**2 for r in rs),hit_sign=st.mean(1.0 if (r["p0"]>0.5)==(r["final"][0]>0.5) else 0.0 for r in rs if r["final"][0]!=0.5),
                 yahoo_vs_pm_agree=st.mean(1.0 if (r["O"]>r["C"])==(r["final"][0]>0.5) else 0.0 for r in rs if r["final"][0]!=0.5)),
      primary=summ(run(rs),len(rs)), secondary_delayed=summ(run(rs,"ask2"),len(rs)),
      placebo_flip=summ(run(rs,flip=True),len(rs)), plant_edge5=summ(run(rs,plant="edge5"),len(rs)), plant_null=summ(run(rs,plant="null"),len(rs)))
    # sanity: asks vs model, no threshold
    both=[r for r in rs if r["ask0"] is not None and r["ask1"] is not None]
    res[name]["ask_sum_mean"]=st.mean(r["ask0"]+r["ask1"] for r in both) if both else None
    res[name]["mean_abs_p_minus_ask_up"]=st.mean(abs(r["p0"]-r["ask0"]) for r in rs if r["ask0"] is not None)
t=res["test"]; p=t["primary"]
if t["plant_null"].get("trades",0)!=0 or abs(t["plant_edge5"].get("mean_edge_exante",0)-0.05)>1e-6: v="INVALID"
elif p.get("trades",0)<20: v="UNDERPOWERED"
elif p["ci_pnl_share"][0]>0 and p["ci_usd_day"][0]>=200 and t["placebo_flip"].get("mean_pnl_share",1)<0: v="PASS"
else: v="FAIL"
res["verdict"]=v
json.dump(res,open("result.json","w"),indent=1); json.dump(rows,open("rows.json","w"))
print(json.dumps(res,indent=1))
