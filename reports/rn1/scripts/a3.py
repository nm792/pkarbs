import json,collections as C,statistics as st,sys
A=json.load(open(sys.argv[1]))
print("rows",len(A))
tc=C.Counter(r["type"] for r in A); print("types",tc)
tu=C.defaultdict(float)
for r in A: tu[r["type"]]+=r.get("usdcSize") or 0
print("type usdc",{k:round(v) for k,v in tu.items()})
T=[r for r in A if r["type"]=="TRADE"]
ts=[r["timestamp"] for r in T]; print("trade span h",(max(ts)-min(ts))/3600)
sd=C.Counter(r["side"] for r in T); su=C.defaultdict(float)
for r in T: su[r["side"]]+=r["usdcSize"]
print("side n",sd,"usdc",{k:round(v) for k,v in su.items()})
def cat(r):
    s=r.get("eventSlug") or r.get("slug") or ""
    p=s.split("-")[0]
    return p
cu=C.defaultdict(float)
for r in T: cu[cat(r)]+=r["usdcSize"]
tot=sum(cu.values())
print("category share by usdc:",[(k,round(100*v/tot,1)) for k,v in sorted(cu.items(),key=lambda x:-x[1])[:25]])
sz=sorted(r["usdcSize"] for r in T)
q=lambda f:sz[int(f*(len(sz)-1))]
print("trade usdc p10 %.1f p50 %.1f p90 %.1f p99 %.0f max %.0f mean %.1f"%(q(.1),q(.5),q(.9),q(.99),sz[-1],st.mean(sz)))
pb=[r["price"] for r in T if r["side"]=="BUY"]
hb=C.Counter(min(9,int(p*10)) for p in pb); print("buy price deciles",sorted(hb.items()))
# per condition both-sides
cond=C.defaultdict(lambda: C.defaultdict(lambda:[0.0,0.0,0.0,0.0]))  # outcomeIndex->[buysh,buyusd,sellsh,sellusd]
title={}
for r in T:
    x=cond[r["conditionId"]][r["outcomeIndex"]]
    if r["side"]=="BUY": x[0]+=r["size"]; x[1]+=r["usdcSize"]
    else: x[2]+=r["size"]; x[3]+=r["usdcSize"]
    title[r["conditionId"]]=r["title"]
nb=0;usd_both=0;usd_all=0;matched=0;mcost=0;combs=[]
for c,o in cond.items():
    b=sum(v[1] for v in o.values()); usd_all+=b
    if len(o)==2 and all(v[0]>0 for v in o.values()):
        nb+=1; usd_both+=b
        a0,a1=o[0],o[1]
        p0=a0[1]/a0[0]; p1=a1[1]/a1[0]; m=min(a0[0],a1[0])
        matched+=m; mcost+=m*(p0+p1); combs.append((p0+p1,m,c))
print("conditions",len(cond),"with buys on both outcomes",nb,"share of buy usdc in those %.1f%%"%(100*usd_both/usd_all))
print("matched pairs shares %.0f, avg combined cost of matched %.4f"%(matched,mcost/matched if matched else 0))
w=sorted(combs); 
import bisect
cs=[x[0] for x in w]
print("combined avg cost dist (by condition) p10 %.3f p50 %.3f p90 %.3f, share <1: %.1f%%"%(cs[len(cs)//10],cs[len(cs)//2],cs[9*len(cs)//10],100*sum(1 for x in cs if x<1)/len(cs)))
# share-weighted fraction of bought shares that are matched
tb=sum(v[0] for o in cond.values() for v in o.values())
print("bought shares %.0f, matched both sides %.0f (%.1f%% of bought shares are in hedged pairs x2)"%(tb,matched,100*2*matched/tb))
# unhedged directional remainder: shares bought on one side beyond the match
json.dump({c:{str(k):v for k,v in o.items()} for c,o in cond.items()},open("cond.json","w")); json.dump(title,open("title.json","w"))
