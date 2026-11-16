import json,gzip,random,statistics as st,numpy as np
H=3600000;sg=lambda x:(x>0)-(x<0)
rows=[];h1={}
for src,d in (("/tmp/wp/rows.json","/tmp/wp/data/"),("/tmp/wp2/rows.json","/tmp/wp2/data/")):
    for r in json.load(open(src)):
        r["_d"]=d;rows.append(r)
def get(r):
    k=r["sym"];key=(r["_d"],k)
    if key not in h1:
        h1[key]={x["t"]:x for x in json.load(gzip.open(r["_d"]+f"hl_{k}.json.gz","rt"))["h1"]}
    return h1[key]
sel=[]
for r in rows:
    if abs(r["S"])<50: continue
    cs=(r["T"]-1800000)//H*H-H
    c=get(r).get(cs-12*H)
    r["L"]=None
    if c and r["P"]!=r["F"]: r["L"]=(r["P"]-float(c["c"]))/(r["P"]-r["F"])
    r["D"]=sg(r["S"])*(r["O"]-r["S"]);sel.append(r)
print("rows",len(rows),"sel",len(sel),"symbols",len(set((r["_d"],r["sym"]) for r in sel)),"weekends",len(set(r["monday"] for r in sel)),"L missing",sum(1 for r in sel if r["L"] is None))
rnd=random.Random(1)
def boot(cells,fn,lo=2.5,hi=97.5):
    wk={}
    for r in cells: wk.setdefault(r["monday"],[]).append(r)
    k=list(wk);bs=[]
    for _ in range(10000):
        v=[];[v.extend(wk[rnd.choice(k)]) for _ in k];bs.append(fn(v))
    bs.sort();return bs[int(len(bs)*lo/100)],bs[min(len(bs)-1,int(len(bs)*hi/100))]
mean=lambda v:float(np.mean([r["D"] for r in v]))
def wkcons(v):
    by={}
    for r in v:by.setdefault(r["monday"],[]).append(r["D"])
    ok=[np.mean(x)>0 for x in by.values() if len(x)>=3]
    return (sum(ok),len(ok))
def report(name,v):
    m=mean(v);a=boot(v,mean,2.5,97.5);b=boot(v,mean,0.25,99.75)
    pos,n=wkcons(v)
    print(f"{name:28s} n={len(v):4d} meanD={m:7.1f} med={np.median([r['D'] for r in v]):6.1f} CI95=[{a[0]:.1f},{a[1]:.1f}] CI99.5=[{b[0]:.1f},{b[1]:.1f}] wk_pos={pos}/{n}")
    return dict(name=name,n=len(v),mean=m,ci95=a,ci995=b,wk_pos=pos,wk_n=n)
out=[]
out.append(report("pooled |S|>=50",sel))
out.append(report("pooled |S|>=100",[r for r in sel if abs(r["S"])>=100]))
def terc(v,key,names):
    vals=sorted(key(r) for r in v);c1,c2=vals[len(vals)//3],vals[2*len(vals)//3]
    print("  cuts",round(c1,3),round(c2,3))
    g=[[r for r in v if key(r)<=c1],[r for r in v if c1<key(r)<=c2],[r for r in v if key(r)>c2]]
    for nm,x in zip(names,g): out.append(report(nm,x))
terc(sel,lambda r:r["S"],["S tercile1 (big down)","S tercile2 (middle)","S tercile3 (big up)"])
terc(sel,lambda r:abs(r["S"]),["|S| small","|S| mid","|S| large"])
terc(sel,lambda r:r["n_trades"] or 0,["liquidity low","liquidity mid","liquidity high"])
terc([r for r in sel if r["L"] is not None],lambda r:r["L"],["lateness early","lateness mid","lateness late"])
# regression R=a+bS
S=np.array([r["S"] for r in sel]);R=np.array([r["O"]-r["S"] for r in sel])
b=np.polyfit(S,R,1)[0]
def slope(v):return float(np.polyfit([r["S"] for r in v],[r["O"]-r["S"] for r in v],1)[0])
a95=boot(sel,slope);a995=boot(sel,slope,0.25,99.75)
print("slope b",b,"CI95",a95,"CI99.5",a995,"b*median|S|",b*np.median(abs(S)))
out.append(dict(name="slope",b=float(b),ci95=a95,ci995=a995,b_med=float(b*np.median(abs(S)))))
json.dump(out,open("overshoot_result.json","w"),indent=1,default=float)
import statistics as _s
print("median hurdle sel",_s.median([12+sg(r["S"])*r["fund_bp"] for r in sel]))
for nm,f in (("liq low",lambda r:(r["n_trades"] or 0)<=100),("|S| mid",lambda r:118.23<abs(r["S"])<=232.7)):
    v=[r for r in sel if f(r)];print(nm,"median hurdle",_s.median([12+sg(r["S"])*r["fund_bp"] for r in v]),"mean fund-adj hurdle",np.mean([12+sg(r["S"])*r["fund_bp"] for r in v]),"symbols",len(set(r["sym"] for r in v)),"top syms",__import__("collections").Counter(r["sym"] for r in v).most_common(5))
