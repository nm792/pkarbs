# Scores CATCHUP-RULE.md (historical). Inputs as lag_v2.py. Output catchup_result.json.
import json,gzip,math,bisect,random,statistics as st,datetime as dt,os,glob,collections
from zoneinfo import ZoneInfo
N_=lambda x:0.5*(1+math.erf(x/math.sqrt(2))); fee=lambda a:0.04*a*(1-a)
r=json.load(open("result.json")); SG={int(k):v/1e4 for k,v in r["sigma_bp"].items()}; MU={int(k):v/1e4 for k,v in r["mu_bp"].items()}
def itp(tab,tau):
    if tau>23: return tab[23]*math.sqrt(tau/23) if tab is SG else tab[23]
    tau=max(tau,1.0); a=int(tau); b=min(a+1,23); w=tau-a; return tab[a]*(1-w)+tab[b]*w
ev={e["date"]:e for e in json.load(open("data/events.json"))}; NY=ZoneInfo("America/New_York")
days=sorted(os.path.basename(f)[:10] for f in glob.glob("data/perp1s/*.json.gz"))
def load(d):
    p=json.load(gzip.open(f"data/perp1s/{d}.json.gz")); pt=[x[0] for x in p["pts"]]; pv=[x[1] for x in p["pts"]]
    tr=sorted([t for t in json.load(gzip.open(f"data/trades_{d}.json.gz")) if t["timestamp"]<=p["K"]],key=lambda t:t["timestamp"])
    return p,pt,pv,tr
DATA={d:load(d) for d in days}
def sim(d,N=60,S=900,null=False,rnd=None):
    p,pt,pv,tr=DATA[d]; K=p["K"]; e=ev[d]
    def perp(t):
        i=bisect.bisect_left(pt,t)-1; return pv[i] if i>=0 and t-pt[i]<=10 else None
    C0=perp(p["Kprev"]+1)
    if C0 is None or not tr: return []
    def fair(t):
        P=perp(t); tau=(K-t)/3600
        return None if P is None else N_((math.log(P/C0)+itp(MU,tau))/itp(SG,tau))
    pr=[(t["timestamp"],t["price"] if t["outcome"]=="Up" else 1-t["price"],t) for t in tr]; tp=[x[0] for x in pr]
    lo=max(tr[0]["timestamp"],pt[0]+60); moves=[]; skip=0
    for t in range(lo,K-60):
        if t<skip: continue
        a,b=perp(t-60),perp(t)
        if a is None or b is None or abs(math.log(b/a))<0.001: continue
        fa,fb=fair(t-60),fair(t)
        if fa is None or fb is None: continue
        skip=t+600; moves.append((t,math.log(b/a),fb-fa))
    if null: 
        nd=st.median([abs(m[2]) for m in moves]) if moves else 0.03
        moves=[(rnd.randrange(lo,K-60),0.0,0.0) for _ in moves]; moves=[(t,0.0,nd*rnd.choice((-1,1))) for t,_,_ in moves]
    out=[]
    for t,mv,dp in moves:
        pre=[x[1] for x in pr if t-600<=x[0]<=t-60]
        if not pre: continue
        L=st.median(pre); up=dp>0; j=0 if up else 1; q0=L if up else 1-L; tgt=q0+abs(dp)/2
        tok=e["tokens"][j]
        i0=bisect.bisect_left(tp,t+1); ent=None
        for x in pr[i0:]:
            if x[0]>t+N: break
            tt=x[2]
            if tt["token_id"]==tok and tt["side"]=="BUY":
                if tt["price"]<=tgt: ent=tt
                break
        if not ent: continue
        sh=min(5.0,ent["size"]); ex=None; how=None
        for x in pr[bisect.bisect_right(tp,ent["timestamp"]):]:
            tt=x[2]
            if tt["token_id"]!=tok or tt["side"]!="SELL": continue
            if tt["price"]>=tgt: ex=tt; how="caught_up"; break
            if tt["timestamp"]>=ent["timestamp"]+S: ex=tt; how="time_stop"; break
        if ex: xp=ex["price"]; pnl=xp-ent["price"]-fee(ent["price"])-fee(xp); xt=ex["timestamp"]
        else: xp=float(e["final"][j]); pnl=xp-ent["price"]-fee(ent["price"]); how="resolution"; xt=K
        loc=dt.datetime.fromtimestamp(t,NY); sess=(loc.hour,loc.minute)>=(9,30) and loc.hour<16 and loc.weekday()<5
        out.append(dict(date=d,move_utc=dt.datetime.fromtimestamp(t,dt.UTC).strftime("%Y-%m-%d %H:%M:%S"),move_bp=round(mv*1e4,1),dp=round(dp,3),side="Up" if up else "Down",
          q0=round(q0,3),entry=ent["price"],entry_delay_s=ent["timestamp"]-t,exit=xp,exit_how=how,hold_s=xt-ent["timestamp"],shares=sh,pnl_share=round(pnl,4),pnl_usd=round(pnl*sh,3),session=sess))
    return out
def boot_ev(T,B=10000,add=0.0):
    g=collections.defaultdict(list)
    for x in T: g[x["date"]].append(x["pnl_share"]+add)
    cl=list(g.values()); n=len(cl)
    if n<2: return None
    rr=random.Random(1); xs=sorted((lambda s:sum(map(sum,s))/sum(map(len,s)))([cl[rr.randrange(n)] for _ in range(n)]) for _ in range(B)); return [round(xs[int(.025*B)],4),round(xs[int(.975*B)],4)]
def summ(T):
    if not T: return dict(trades=0)
    return dict(trades=len(T),events=len(set(x["date"] for x in T)),mean_pnl_share=round(st.mean(x["pnl_share"] for x in T),4),ci=boot_ev(T),
       hit=round(sum(x["pnl_share"]>0 for x in T)/len(T),3),mean_entry=round(st.mean(x["entry"] for x in T),3),usd_total=round(sum(x["pnl_usd"] for x in T),2),
       exits=dict(collections.Counter(x["exit_how"] for x in T)),median_hold_s=st.median(x["hold_s"] for x in T))
res={}
for N in (30,60,120):
    for S in (300,900):
        T=[x for d in days for x in sim(d,N,S)]; res[f"N{N}_S{S}"]=summ(T)
        if (N,S)==(60,900): P=T
rnd=random.Random(1); NT=[x for d in days for x in sim(d,60,900,null=True,rnd=rnd)]
out=dict(rule="CATCHUP-RULE.md",events=len(days),grid=res,primary=summ(P),
  null_random_times=summ(NT),
  planted_3c=dict(mean=round(st.mean(x["pnl_share"] for x in P)+0.03,4) if P else None,ci=boot_ev(P,add=0.03),detects=(boot_ev(P,add=0.03) or [0])[0]>0),
  by_move=dict(small_10_20bp=summ([x for x in P if abs(x["move_bp"])<20]),big_20bp_plus=summ([x for x in P if abs(x["move_bp"])>=20])),
  by_time=dict(us_session=summ([x for x in P if x["session"]]),outside=summ([x for x in P if not x["session"]])),
  by_entry_delay={k:summ([x for x in P if f(x["entry_delay_s"])]) for k,f in (("<=10s",lambda s:s<=10),("10-30s",lambda s:10<s<=30),("30-60s",lambda s:s>30))},
  usd_per_day_at_5_shares=round(sum(x["pnl_usd"] for x in P)/len(days),2) if P else 0,
  examples=P[:: max(1,len(P)//15)][:15])
json.dump(dict(out,trades=P),open("catchup_result.json","w"),indent=1)
print(json.dumps(out,indent=1))
