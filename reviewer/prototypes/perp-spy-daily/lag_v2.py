# Scores LAG-RULE-v2.md. Inputs: data/events.json, data/trades_*.json.gz, data/perp1s/*.json.gz, result.json, data/yahoo_SP500.json.gz.
import json,gzip,math,bisect,random,statistics as st,datetime as dt,os,glob,collections
N=lambda x:0.5*(1+math.erf(x/math.sqrt(2))); fee=lambda a:0.04*a*(1-a)
r=json.load(open("result.json")); SG={int(k):v/1e4 for k,v in r["sigma_bp"].items()}; MU={int(k):v/1e4 for k,v in r["mu_bp"].items()}
def itp(tab,tau):
    if tau>23: return tab[23]*math.sqrt(tau/23) if tab is SG else tab[23]
    tau=max(tau,1.0); a=int(tau); b=min(a+1,23); w=tau-a; return tab[a]*(1-w)+tab[b]*w
ev={e["date"]:e for e in json.load(open("data/events.json"))}
y=json.load(gzip.open("data/yahoo_SP500.json.gz")); yc={dt.datetime.fromtimestamp(t,dt.UTC).date().isoformat():c for t,c in zip(y["timestamp"],y["indicators"]["quote"][0]["close"])}
rnd=random.Random(1)
def analyse(d,plant=False,null=False,lagfair=0):
    e=ev[d]; p=json.load(gzip.open(f"data/perp1s/{d}.json.gz")); K=p["K"]; pts=p["pts"]
    pt=[x[0] for x in pts]; pv=[x[1] for x in pts]
    def perp(t):  # last mark strictly before t
        i=bisect.bisect_left(pt,t)-1; return pv[i] if i>=0 and t-pt[i]<=10 else None
    C0=perp(p["Kprev"]+1)
    if C0 is None: return None
    def fair(t,lf=None):
        P=perp(t-(lagfair if lf is None else lf))
        if P is None: return None
        tau=(K-t)/3600; return N((math.log(P/C0)+itp(MU,tau))/itp(SG,tau))
    tr=sorted(json.load(gzip.open(f"data/trades_{d}.json.gz")),key=lambda t:t["timestamp"])
    pr=[(t["timestamp"],t["price"] if t["outcome"]=="Up" else 1-t["price"],t) for t in tr if t["timestamp"]<=K]
    t_first=pr[0][0] if pr else K
    moves=[];skip=0
    cand=range(max(t_first,pt[0]+60),K-60)
    for t in cand:
        if t<skip: continue
        a,b=perp(t-60),perp(t)
        if a is None or b is None or abs(math.log(b/a))<0.001: continue
        skip=t+600; fa,fb=fair(t-60,0),fair(t,0)
        if fa is None or fb is None: continue
        moves.append((t,math.log(b/a),fb-fa))
    if null:
        nd=st.median([abs(m[2]) for m in moves]) if moves else 0.03
        moves=[(rnd.randrange(max(t_first,pt[0]+60),K-60),0.0,nd*rnd.choice((-1,1))) for _ in moves]
    tp=[x[0] for x in pr]; res=[]
    for t,mv,dp in moves:
        pre=[x[1] for x in pr if t-600<=x[0]<=t-60]
        if not pre: res.append(dict(t=t,mv=mv,dp=dp,measurable=False)); continue
        L=st.median(pre); tgt=L+dp/2; lag=None; gap=None
        seq=pr[bisect.bisect_left(tp,t):]
        if plant: seq=sorted(seq+[(t+30,L+dp,None)],key=lambda x:x[0])
        for x in seq:
            if x[0]>t+1800: break
            if gap is None: gap=x[0]-t
            if (dp>0 and x[1]>=tgt) or (dp<0 and x[1]<=tgt): lag=x[0]-t; break
        res.append(dict(t=t,mv=mv,dp=dp,measurable=True,pre=L,lag=lag,gap=gap,abs_dp=abs(dp)))
    stale=[]
    for ts_,ip,t in pr:
        if t["side"]!="BUY": continue
        f=fair(ts_)
        if f is None: continue
        j=0 if t["outcome"]=="Up" else 1; fj=f if j==0 else 1-f
        if t["price"]<fj-fee(t["price"])-0.01:
            sh=t["size"]; stale.append(dict(ts=ts_,usd=sh*t["price"],pnl=(float(e["final"][j])-t["price"]-fee(t["price"]))*sh,gap_c=fj-t["price"]))
    buy_usd=sum(t["size"]*t["price"] for t in tr if t["side"]=="BUY" and t["timestamp"]<=K)
    return dict(date=d,C0=C0,C0_yahoo_prev=None,moves=res,stale_n=len(stale),stale_usd=sum(s["usd"] for s in stale),stale_pnl=sum(s["pnl"] for s in stale),buy_usd=buy_usd,n_prints=len(pr))
days=sorted(os.path.basename(f)[:10] for f in glob.glob("data/perp1s/*.json.gz"))
def run(**kw): return [x for x in (analyse(d,**kw) for d in days) if x]
def lagstats(R):
    m=[x for E in R for x in E["moves"]]; me=[x for x in m if x["measurable"]]
    lags=sorted(x["lag"] for x in me if x["lag"] is not None); cens=sum(1 for x in me if x["lag"] is None)
    allv=lags+[10**9]*cens; allv.sort()
    q=lambda f:(allv[int(f*(len(allv)-1))] if allv else None)
    gaps=sorted(x["gap"] for x in me if x["gap"] is not None)
    return dict(moves=len(m),measurable=len(me),caught_up=len(lags),censored_30m=cens,
       lag_p25=q(.25),lag_median=q(.5),lag_p75=q(.75),within_10s=sum(l<=10 for l in lags),within_60s=sum(l<=60 for l in lags),within_300s=sum(l<=300 for l in lags),
       share_within_300s=(sum(l<=300 for l in lags)/len(me) if me else None),first_print_gap_median=(st.median(gaps) if gaps else None))
def boot(v,B=10000):
    rr=random.Random(1);n=len(v);xs=sorted(sum(v[rr.randrange(n)] for _ in range(n)) for _ in range(B)); return [xs[int(.025*B)],xs[int(.975*B)]]
R=run(); RP=run(plant=True); RN=run(null=True); RS=run(lagfair=1800)
c0chk=[abs(math.log(E["C0"]/yc[pd]))*1e4 for E in R for pd in [max([k for k in yc if k<E["date"]],default=None)] if pd and E["date"]<="2026-11-13"]
by_m=collections.defaultdict(lambda:[0,0.0,0.0,0.0])
for E in R:
    k=E["date"][:7]; by_m[k][0]+=1; by_m[k][1]+=E["buy_usd"]; by_m[k][2]+=E["stale_usd"]; by_m[k][3]+=E["stale_pnl"]
out=dict(rule="LAG-RULE-v2.md",events=len(R),C0_vs_yahoo_prev_close_bp=dict(n=len(c0chk),median=st.median(c0chk) if c0chk else None,p90=sorted(c0chk)[int(.9*(len(c0chk)-1))] if c0chk else None),
  lag=lagstats(R),plant_30s=lagstats(RP),null_times=lagstats(RN),
  lag_by_size={b:lagstats([dict(moves=[x for x in E["moves"] if f(x)]) for E in R]) for b,f in (("abs_dp<0.05",lambda x:x.get("abs_dp",abs(x["dp"]))<0.05),("abs_dp>=0.05",lambda x:x.get("abs_dp",abs(x["dp"]))>=0.05))},
  stale=dict(n=sum(E["stale_n"] for E in R),usd=sum(E["stale_usd"] for E in R),pnl=sum(E["stale_pnl"] for E in R),buy_usd=sum(E["buy_usd"] for E in R),
     pnl_ci_by_event=boot([E["stale_pnl"] for E in R]),usd_per_event=sum(E["stale_usd"] for E in R)/len(R),pnl_per_event=sum(E["stale_pnl"] for E in R)/len(R)),
  stale_placebo_fair_30min_old=dict(n=sum(E["stale_n"] for E in RS),usd=sum(E["stale_usd"] for E in RS),pnl=sum(E["stale_pnl"] for E in RS),pnl_ci_by_event=boot([E["stale_pnl"] for E in RS])),
  by_month={k:dict(events=v[0],taker_buy_usd_per_event=round(v[1]/v[0]),stale_usd_per_event=round(v[2]/v[0]),stale_pnl_per_event=round(v[3]/v[0])) for k,v in sorted(by_m.items())},
  per_event=[dict(date=E["date"],prints=E["n_prints"],buy_usd=round(E["buy_usd"]),stale_n=E["stale_n"],stale_usd=round(E["stale_usd"]),stale_pnl=round(E["stale_pnl"],2)) for E in R])
json.dump(out,open("lag_v2_result.json","w"),indent=1)
print(json.dumps({k:v for k,v in out.items() if k!="per_event"},indent=1))
