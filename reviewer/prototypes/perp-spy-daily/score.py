# Scores LOCKED-RULE.md (perp vs PM SPY daily Up/Down). Inputs: data/. Outputs: result.json, trades.json, reconcile.tsv.
import json,gzip,math,random,statistics as st,datetime as dt,collections
D="data/"; H=3600
N=lambda x:0.5*(1+math.erf(x/math.sqrt(2))); fee=lambda a:0.04*a*(1-a)
ev={e["date"]:e for e in json.load(open(D+"events.json"))}
hl={c["T"]+1:float(c["c"]) for c in json.load(gzip.open(D+"hl_SP500.json.gz"))["h1"]}
y=json.load(gzip.open(D+"yahoo_SP500.json.gz")); ts=y["timestamp"]; q=y["indicators"]["quote"][0]
day=lambda t:dt.datetime.fromtimestamp(t,dt.UTC).date().isoformat()
# reconciliation
rec=["date\tn_trades\tshares_pulled\tgamma_volume\tratio\tusd_notional"]; mon=collections.defaultdict(lambda:[0,0.0,0.0])
TR={}
for d,e in sorted(ev.items()):
    tr=json.load(gzip.open(D+f"trades_{d}.json.gz")); TR[d]=tr
    sh=sum(t["size"] for t in tr); usd=sum(t["size"]*t["price"] for t in tr); g=float(e["volume"] or 0)
    rec.append(f"{d}\t{len(tr)}\t{sh:.0f}\t{g:.0f}\t{(sh/g if g else 0):.4f}\t{usd:.0f}")
    mon[d[:7]][0]+=1; mon[d[:7]][1]+=usd; mon[d[:7]][2]+=g
open("reconcile.tsv","w").write("\n".join(rec)+"\n")
cps=[];excl=collections.Counter();days=[]
for i in range(1,len(ts)):
    d=day(ts[i])
    if d<"2026-04-22" or d>"2026-11-13": continue
    if d not in ev: excl["no PM event"]+=1; continue
    if q["close"][i] is None or q["close"][i-1] is None: excl["no yahoo close"]+=1; continue
    days.append(d); e=ev[d]; K=ts[i]+int(6.5*H); C0=q["close"][i-1]; Y=math.log(q["close"][i]/C0)
    buys=[[t for t in TR[d] if t["token_id"]==tok and t["side"]=="BUY"] for tok in e["tokens"]]
    for k in range(1,24):
        t=K-k*H; P=hl.get(t*1000)
        if P is None: excl["no candle at checkpoint"]+=1; continue
        c=dict(date=d,k=k,t=t,x=math.log(P/C0),Y=Y,final=[float(v) for v in e["final"]])
        for j in (0,1):
            w=sorted([b for b in buys[j] if t-300<=b["timestamp"]<=t],key=lambda b:b["timestamp"])
            c[f"ask{j}"]=w[-1]["price"] if w else None
            c[f"dep{j}"]=sum(b["size"]*b["price"] for b in buys[j] if t-H<=b["timestamp"]<=t)
        cps.append(c)
train=[c for c in cps if c["date"]<"2026-08-01"]; test=[c for c in cps if c["date"]>="2026-08-01"]
dtr=[d for d in days if d<"2026-08-01"]; dte=[d for d in days if d>="2026-08-01"]
mu={};sg={}
for k in range(1,24):
    r=[c["Y"]-c["x"] for c in train if c["k"]==k]; mu[k]=st.mean(r); sg[k]=st.stdev(r)
for c in cps: c["p0"]=N((c["x"]+mu[c["k"]])/sg[c["k"]]); c["p1"]=1-c["p0"]
def solve(p):
    lo,hi=0.0,1.0
    for _ in range(60):
        m=(lo+hi)/2
        if p-m-fee(m)>0.05: lo=m
        else: hi=m
    return lo
def run(cs,flip=False,plant=None):
    out=[]
    for c in cs:
        best=None
        for j in (0,1):
            a=c[f"ask{j}"]
            if a is None: continue
            p=c[f"p{1-j if flip else j}"]
            if plant=="edge5": a=solve(p)
            if plant=="null": a=p
            if a<=0.001: continue
            ed=p-a-fee(a)
            if ed>=0.03 and (best is None or ed>best[1]): best=(j,ed,a)
        if best:
            j,ed,a=best; pnl=c["final"][j]-a-fee(a); n=0.1*c[f"dep{j}"]
            out.append(dict(date=c["date"],k=c["k"],side=j,ask=a,edge=ed,pnl=pnl,notional=n,usd=pnl*n/a,fee_usd=fee(a)*n/a))
    return out
def boot(v,f,B=10000):
    rnd=random.Random(1);n=len(v);xs=sorted(f([v[rnd.randrange(n)] for _ in range(n)]) for _ in range(B)); return [xs[int(.025*B)],xs[int(.975*B)]]
def summ(tr,dd):
    if not tr: return dict(trades=0)
    byd=collections.defaultdict(float); bydn=collections.defaultdict(float)
    for t in tr: byd[t["date"]]+=t["usd"]; bydn[t["date"]]+=t["notional"]
    daily=[byd.get(d,0.0) for d in dd]
    # per-share CI clustered by day
    g=collections.defaultdict(list)
    for t in tr: g[t["date"]].append(t["pnl"])
    cl=list(g.values())
    return dict(trades=len(tr),trade_days=len(g),days=len(dd),hit=sum(t["pnl"]>0 for t in tr)/len(tr),mean_ask=st.mean(t["ask"] for t in tr),
        mean_edge_exante=st.mean(t["edge"] for t in tr),mean_pnl_share=st.mean(t["pnl"] for t in tr),
        ci_pnl_share=boot(cl,lambda s:sum(sum(x) for x in s)/sum(len(x) for x in s)) if len(cl)>1 else None,
        tradeable_usd_per_day=sum(bydn.values())/len(dd),usd_per_day=sum(daily)/len(dd),ci_usd_day=boot(daily,st.mean),
        rebate_usd_day=0.25*sum(t["fee_usd"] for t in tr)/len(dd))
res=dict(rule_commit="803825d7",n_days=len(days),n_train_days=len(dtr),n_test_days=len(dte),n_checkpoints=len(cps),excluded=dict(excl),
         sigma_bp={k:round(sg[k]*1e4,1) for k in sg},mu_bp={k:round(mu[k]*1e4,1) for k in mu},
         usd_per_event_by_month={m:round(v[1]/v[0]) for m,v in sorted(mon.items())},gamma_shares_per_event_by_month={m:round(v[2]/v[0]) for m,v in sorted(mon.items())})
for name,cs,dd in (("train",train,dtr),("test",test,dte)):
    R=dict(checkpoints=len(cs),with_ask_up=sum(c["ask0"] is not None for c in cs),with_ask_down=sum(c["ask1"] is not None for c in cs))
    for band,f in (("session_k<=6",lambda c:c["k"]<=6),("overnight_k>=7",lambda c:c["k"]>=7)):
        b=[c for c in cs if f(c) and c["final"][0]!=0.5]
        R["calib_"+band]=dict(brier=st.mean((c["p0"]-c["final"][0])**2 for c in b),sign_hit=st.mean(float((c["p0"]>0.5)==(c["final"][0]>0.5)) for c in b),
            mean_abs_p_minus_ask_up=st.mean(abs(c["p0"]-c["ask0"]) for c in b if c["ask0"] is not None))
    R["yahoo_spx_vs_pm_agree"]=st.mean(float((c["Y"]>0)==(c["final"][0]>0.5)) for c in cs if c["k"]==1 and c["final"][0]!=0.5)
    P=run(cs); R["primary"]=summ(P,dd)
    R["primary_session"]=summ([t for t in P if t["k"]<=6],dd); R["primary_overnight"]=summ([t for t in P if t["k"]>=7],dd)
    R["placebo_flip"]=summ(run(cs,flip=True),dd); R["plant_edge5"]=summ(run(cs,plant="edge5"),dd); R["plant_null"]=summ(run(cs,plant="null"),dd)
    res[name]=R
    if name=="test": json.dump(P,open("trades_test.json","w"),indent=0)
t=res["test"];p=t["primary"]
if t["plant_null"].get("trades",0)!=0 or abs(t["plant_edge5"].get("mean_edge_exante",0)-0.05)>1e-6: v="INVALID"
elif p.get("trades",0)<20: v="UNDERPOWERED"
elif p["ci_pnl_share"][0]>0 and p["ci_usd_day"][0]>=200 and t["placebo_flip"].get("mean_pnl_share",1)<0: v="PASS"
else: v="FAIL"
res["verdict"]=v
json.dump(res,open("result.json","w"),indent=1); print(json.dumps(res,indent=1))
