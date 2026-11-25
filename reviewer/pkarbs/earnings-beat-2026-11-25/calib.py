# Calibration of the pre-report YES price (last trade >=30 min before the outcome jump J) vs realised beat.
import json, math, random
d=[x for x in json.load(open("pre_jump.json")) if x.get("last_pre") is not None and x.get("J")]
print("markets with jump found", len(d))
d=[x for x in d if x["last_pre_age_h"]<=24 and 0.03<x["last_pre"]<0.97]
n=len(d); print("usable (pre trade within 24h, price 3-97c)", n, "YES rate %.3f mean price %.3f" % (sum(x["y"] for x in d)/n, sum(x["last_pre"] for x in d)/n))
B=[0,.2,.4,.5,.6,.7,.8,.9,1.0]
rows=[]
for a,b in zip(B,B[1:]):
    s=[x for x in d if a<=x["last_pre"]<b]
    if not s: continue
    k=len(s); y=sum(x["y"] for x in s)/k; p=sum(x["last_pre"] for x in s)/k; se=math.sqrt(max(y*(1-y),1e-9)/k)
    rows.append((a,b,k,p,y)); print(f"{a:.1f}-{b:.1f} n={k:4d} price={p:.3f} realised={y:.3f} diff={y-p:+.3f} +-{1.96*se:.3f}")
# simple rules at the last pre-report print, fee rate*p*(1-p) taker (rate 0.01 where listed, else 0), $ per $1 staked
def pnl(rule):
    out=[]
    for x in d:
        p=x["last_pre"]; f=(x["fee"] or {}).get("rate",0) or 0
        side=rule(p)
        if side=="Y": out.append((x["y"]-p-f*p*(1-p))/p)
        elif side=="N": out.append(((1-x["y"])-(1-p)-f*p*(1-p))/(1-p))
    return out
def boot(v,B=5000):
    if not v: return (0,0,0)
    m=sum(v)/len(v); bs=sorted(sum(random.choice(v) for _ in v)/len(v) for _ in range(B)); return (m,bs[int(.025*B)],bs[int(.975*B)])
random.seed(1)
for name,rule in [("buy YES p>=0.8",lambda p:"Y" if p>=0.8 else None),("buy NO p<0.2",lambda p:"N" if p<0.2 else None),
                  ("buy YES all",lambda p:"Y"),("buy NO 0.6-0.8",lambda p:"N" if 0.6<=p<0.8 else None),("buy YES 0.4-0.6",lambda p:"Y" if 0.4<=p<0.6 else None)]:
    v=pnl(rule); m,lo,hi=boot(v); print(f"{name:18s} n={len(v):4d} return/$ {m:+.3f} [{lo:+.3f},{hi:+.3f}]")
# MC type 1: random side on the same markets
v=[]
for _ in range(2000):
    r=pnl(lambda p:random.choice("YN")); v.append(sum(r)/len(r))
v.sort(); print("MC type 1 (random side, same data): 95th pct return/$ %+.3f" % v[int(.95*len(v))])
# Rule of interest found in the calibration table: buy YES when p < 0.5. Null = prices are calibrated (MC type 2: y ~ Bernoulli(p), same markets).
def ret_yes(x,y):
    p=x["last_pre"]; f=(x["fee"] or {}).get("rate",0) or 0; return (y-p-f*p*(1-p))/p
S=[x for x in d if x["last_pre"]<0.5]
obs=sum(ret_yes(x,x["y"]) for x in S)/len(S)
null=sorted(sum(ret_yes(x,1 if random.random()<x["last_pre"] else 0) for x in S)/len(S) for _ in range(5000))
pv=sum(1 for v in null if v>=obs)/len(null)
m,lo,hi=boot([ret_yes(x,x["y"]) for x in S])
print(f"buy YES p<0.5: n={len(S)} return/$ {obs:+.3f} [{lo:+.3f},{hi:+.3f}]; MC type 2 calibrated-price null 95th pct {null[int(.95*len(null))]:+.3f}, p={pv:.4f}")
# split by time (first half vs second half of markets by jump time) to check stability
S2=sorted(S,key=lambda x:x["J"]); h=len(S2)//2
for nm,part in (("earlier half",S2[:h]),("later half",S2[h:])):
    v=[ret_yes(x,x["y"]) for x in part]; m,lo,hi=boot(v); print(f"  {nm}: n={len(v)} return/$ {m:+.3f} [{lo:+.3f},{hi:+.3f}]")
usd=sorted(x["usd24"] for x in S); print("  24h pre-report $ traded per market: median %.0f, p75 %.0f" % (usd[len(usd)//2], usd[3*len(usd)//4]))
