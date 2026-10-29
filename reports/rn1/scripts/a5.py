import json,collections as C,bisect
A=json.load(open("act7d.json")); T=[r for r in A if r["type"]=="TRADE"]
by=C.defaultdict(lambda:{0:[],1:[]})
for r in T: by[r["conditionId"]][r["outcomeIndex"]].append((r["timestamp"],r["price"],r["usdcSize"]))
for c in by:
    for k in (0,1): by[c][k].sort()
bins=C.Counter(); tot=0
lim=[(5,"<=5s"),(60,"5-60s"),(600,"1-10m"),(3600,"10-60m"),(1e9,">1h or none")]
for c,o in by.items():
    for k in (0,1):
        opp=[t for t,_,_ in o[1-k]]
        for t,p,u in o[k]:
            if opp:
                i=bisect.bisect_left(opp,t); d=min(abs(opp[j]-t) for j in (i-1,i) if 0<=j<len(opp))
            else: d=1e12
            for L,n in lim:
                if d<=L: bins[n]+=u; break
            tot+=u
print("USDC by gap to nearest opposite-outcome fill:",[(n,round(100*bins[n]/tot,1)) for _,n in lim])
# taker fills from mt.json
M=json.load(open("mt.json"))
tk=M["true"]; lo=min(r["timestamp"] for r in M["false"]); tk=[r for r in tk if r["timestamp"]>=lo]
alls=M["false"]
pa=C.defaultdict(list)
for r in alls: pa[(r["conditionId"],r["outcomeIndex"])].append((r["timestamp"],r["price"]))
n=0;u=0;arb=0;arbu=0
for r in tk:
    o=pa.get((r["conditionId"],1-r["outcomeIndex"]),[])
    near=[p for t,p in o if abs(t-r["timestamp"])<=5]
    uu=r["size"]*r["price"]; u+=uu
    if near:
        n+=1
        if r["price"]+min(near)<1: arb+=1; arbu+=uu
print("taker fills in window",len(tk),"usdc",round(u),"with opposite fill within 5s",n,"of which combined<1:",arb,"usdc",round(arbu))
cnt=C.Counter((r["eventSlug"] or "").split("-")[0] for r in tk); print("taker cats",cnt.most_common(6))
print("taker price mean %.3f"%(sum(r["price"] for r in tk)/len(tk)))
