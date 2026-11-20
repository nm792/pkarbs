# Rerun of LOCKED-RULE-metals-brent-reopen-oos-2026-11-16 at the sourced cost table (LOCKED-RULE-cost-table-2026-11-17: xyz growth-mode taker 0.9 bp).
# Logic copied verbatim from weekend-perps/followups-2026-11-16/oos.py (trades/boot/rep); only change: cells come from oos_cells.json (no refetch, no new data) and fee list from argv.
import json,sys,random,numpy as np
CELLS=sys.argv[1];FEES=[float(x) for x in sys.argv[2].split(",")]
SYMS={"SILVER":("SI=F",-1,1.0),"COPPER":("HG=F",-1,4.9),"PLATINUM":("PL=F",-1,6.2),"BRENTOIL":("BZ=F",1,1.0)}
res=json.load(open(CELLS))
rnd=random.Random(1)
sg=lambda x:(x>0)-(x<0)
def trades(sample,fee):
    out=[]
    for s,(y,pos,hs) in SYMS.items():
        for c in res[s][sample]:
            if abs(c["S"])<50: continue
            g=pos*sg(c["S"])*(c["ext"]/c["ent"]-1)*1e4
            cost=2*(fee+max(hs,1.0))
            out.append(dict(sym=s,wk=c["T"]//(7*86400000),T=c["T"],S=c["S"],gross=g,net=g-cost))
    return out
def boot(v):
    wk={}
    for x in v:wk.setdefault(x["wk"],[]).append(x["net"])
    k=list(wk);bs=[]
    for _ in range(10000):
        a=[];[a.extend(wk[rnd.choice(k)]) for _ in k];bs.append(np.mean(a))
    bs.sort();return round(bs[249],1),round(bs[9749],1)
def rep(name,v):
    if not v:print(f"{name:34s} n=0");return None
    wk={}
    for x in v:wk.setdefault(x["wk"],[]).append(x)
    right=np.mean([np.mean([y["gross"] for y in l])>0 for l in wk.values()])
    tot=sum(x["net"] for x in v);sh={w:sum(y["net"] for y in l) for w,l in wk.items()}
    mx=max(sh.values())/tot if tot>0 else None
    print(f"{name:34s} n={len(v):3d} wk={len(wk):2d} gross={np.mean([x['gross'] for x in v]):7.1f} net={np.mean([x['net'] for x in v]):7.1f} med_net={np.median([x['net'] for x in v]):7.1f} CI={boot(v)} wk_right={right:.0%} max_wk_share={mx if mx is None else round(mx,2)}")
    return v
for fee in FEES:
    print("===== fee",fee,"bp per side")
    for sample in("disc1","coarse","held"):
        metals=[t for t in trades(sample,fee) if t["sym"]!="BRENTOIL"]
        rep(f"{sample} metals pooled",metals)
        for s in("SILVER","COPPER","PLATINUM"):rep(f"  {sample} {s}",[t for t in metals if t["sym"]==s])
        rep(f"{sample} BRENT",[t for t in trades(sample,fee) if t["sym"]=="BRENTOIL"])
