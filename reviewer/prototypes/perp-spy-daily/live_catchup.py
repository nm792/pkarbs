# Live version of CATCHUP-RULE.md on logger files. Usage: python3 -I live_catchup.py FILE [FILE...]
import json,sys,math,bisect,statistics as st,datetime as dt
from zoneinfo import ZoneInfo
N_=lambda x:0.5*(1+math.erf(x/math.sqrt(2))); phi=lambda x:math.exp(-x*x/2)/math.sqrt(2*math.pi); fee=lambda a:0.04*a*(1-a)
r=json.load(open("result.json")); SG={int(k):v/1e4 for k,v in r["sigma_bp"].items()}; MU={int(k):v/1e4 for k,v in r["mu_bp"].items()}
def itp(tab,tau):
    if tau>23: return tab[23]*math.sqrt(tau/23) if tab is SG else tab[23]
    tau=max(tau,1.0); a=int(tau); b=min(a+1,23); w=tau-a; return tab[a]*(1-w)+tab[b]*w
NY=ZoneInfo("America/New_York"); C0S={"2026-11-23":6925.8,"2026-11-24":7237.8}   # perp mark at prior close (20 Nov: LIVE-READ-2026-11-23-1351.json; 23 Nov 21:00Z: mark-history ts 1795467599000)
out={}
for f in sys.argv[1:]:
    d=f.split("_")[1]; D=dt.date.fromisoformat(d); K=int(dt.datetime(D.year,D.month,D.day,16,tzinfo=NY).timestamp())
    R=[x for x in map(json.loads,open(f)) if "error" not in x and x.get("perp") and x["up"]["ask"] is not None and x["up"]["bid"] is not None and x["dn"]["ask"] is not None and x["dn"]["bid"] is not None]
    T=[x["t"] for x in R]; P=[float(x["perp"][1]) for x in R]
    def at(t): i=bisect.bisect_right(T,t)-1; return i
    def fair_dp(i0,i1):
        tau=(K-R[i1]["t"])/3600
        if d in C0S:
            C0=C0S[d]; g=lambda p:N_((math.log(p/C0)+itp(MU,tau))/itp(SG,tau)); return g(P[i1])-g(P[i0]),"model"
        return phi(0)*math.log(P[i1]/P[i0])/itp(SG,tau+24),"at-the-money approx (C0 unknown)"
    def run(plant=False):
        trades=[];lags=[];skip=0;moves=0
        for i,x in enumerate(R):
            t=x["t"]
            if t<skip: continue
            j=at(t-60)
            if j<0 or t-R[j]["t"]>65: continue
            if abs(math.log(P[i]/P[j]))<0.001: continue
            skip=t+600; moves+=1; dp,how=fair_dp(j,i); up=P[i]>P[j]; k="up" if up else "dn"
            pre=R[i-1][k]; q0=(pre["ask"]+pre["bid"])/2; tgt=q0+abs(dp)/2
            # quote lag: first poll where stale token mid >= tgt
            ql=None
            for y in R[i:]:
                if y["t"]>t+1800: break
                m=(y[k]["ask"]+y[k]["bid"])/2
                if plant and y["t"]>=t+30: m=q0+abs(dp)
                if m>=tgt: ql=round(y["t"]-t,1); break
            lags.append(ql)
            e=next((y for y in R[i:] if y["t"]>=t+0.25),None)
            if not e: continue
            a=e[k]["ask"] if not plant else q0; sh=min(5.0,e[k]["asz"] or 0) if not plant else 5.0
            if a>tgt or sh<=0: trades.append(dict(move_utc=dt.datetime.fromtimestamp(t,dt.UTC).strftime("%H:%M:%S"),skipped="ask already caught up",ask=a,q0=round(q0,3),tgt=round(tgt,3))); continue
            ex=None
            for y in R[R.index(e)+1:]:
                b=y[k]["bid"]
                if plant and y["t"]>=t+30: b=q0+abs(dp)
                if b>=tgt: ex=(y,b,"caught_up"); break
                if y["t"]>=e["t"]+900: ex=(y,b,"time_stop"); break
            if not ex: ex=(R[-1],R[-1][k]["bid"],"log_end")
            y,b,hw=ex; pnl=b-a-fee(a)-fee(b)
            trades.append(dict(move_utc=dt.datetime.fromtimestamp(t,dt.UTC).strftime("%H:%M:%S"),move_bp=round(math.log(P[i]/P[j])*1e4,1),dp=round(dp,3),dp_method=how,side=k,q0=round(q0,3),
              entry_ask=a,ask_size=e[k]["asz"],shares=sh,entry_delay_s=round(e["t"]-t,2),exit_bid=b,exit_how=hw,hold_s=round(y["t"]-e["t"],1),pnl_share=round(pnl,4),pnl_usd=round(pnl*sh,3)))
        done=[x for x in trades if "pnl_share" in x]
        return dict(rows=len(R),span_min=round((T[-1]-T[0])/60,1),moves=moves,quote_lags_s=lags,trades=len(done),skipped=len(trades)-len(done),
            mean_pnl_share=round(st.mean(x["pnl_share"] for x in done),4) if done else None,usd_total=round(sum(x["pnl_usd"] for x in done),3),detail=trades)
    out[f]=dict(real=run(),planted_30s=run(plant=True))
json.dump(out,open("live_catchup_result.json","w"),indent=1); print(json.dumps(out,indent=1)[:6000])
