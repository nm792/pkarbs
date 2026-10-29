import json,datetime as dt
p=json.load(open("pnl.json"))["data"]["points"]
K=["economic_pnl","trade_pnl","fees_paid","maker_rebate","taker_rebate","reward_income","volume_usdc","trade_count","unrealized_pnl"]
def d(t): return dt.datetime.fromtimestamp(t,dt.timezone.utc)
prev={k:0 for k in K}; rows=[]
bym={}
for x in p: bym[d(x["timestamp"]).strftime("%Y-%m")]=x
print("month "+" ".join(f"{k[:10]:>11}" for k in K)+"  margin%")
for m,x in bym.items():
    dd={k:(x[k] or 0)-prev[k] for k in K}; prev={k:x[k] or 0 for k in K}
    mg=100*dd["economic_pnl"]/dd["volume_usdc"] if dd["volume_usdc"] else 0
    print(m+" "+" ".join(f"{dd[k]:11.0f}" for k in K)+f"  {mg:.2f}")
# daily stats last 60 days
ds=[]
for a,b in zip(p[:-1],p[1:]):
    ds.append((d(b["timestamp"]).date(), b["economic_pnl"]-a["economic_pnl"], b["volume_usdc"]-a["volume_usdc"]))
import statistics as st
for n in [30,90,len(ds)]:
    v=[x[1] for x in ds[-n:]]
    print(n,"days: mean/day %.0f median %.0f sd %.0f neg days %d min %.0f max %.0f"%(st.mean(v),st.median(v),st.pstdev(v),sum(1 for y in v if y<0),min(v),max(v)))
# drawdown
peak=-1e18;mdd=0
for x in p:
    e=x["economic_pnl"]; peak=max(peak,e); mdd=min(mdd,e-peak)
print("max drawdown",mdd)
print("last 10 days",[(str(a),round(b),round(c)) for a,b,c in ds[-10:]])
