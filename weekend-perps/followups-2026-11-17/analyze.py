import json,numpy as np,random,datetime,collections
H=3600000;h=json.load(open("hist.json"));c=json.load(open("cand.json"))
oi=h["oi"];F=h["fund"];C={k:{int(t):v for t,v in d.items()} for k,d in c["candles"].items()};HS=c["halfspread"]
syms=[s for s in F if len(F[s])>=1440 and oi.get(s,0)>0]
ois=sorted(oi[s] for s in syms);c1,c2=ois[len(ois)//3],ois[2*len(ois)//3]
tier=lambda s:"thin" if oi[s]<=c1 else ("mid" if oi[s]<=c2 else "liquid")
print("syms",len(syms),"OI cuts $m",round(c1/1e6,2),round(c2/1e6,2))
def sess(t):  # t = record time; the hour covered starts at t-1h
    d=datetime.datetime.fromtimestamp((t-H)/1000,datetime.UTC);wd=d.weekday();hr=d.hour
    if (wd==4 and hr>=22) or wd==5 or (wd==6 and hr<22): return "weekend"
    if wd<5 and 13<=hr<21: return "weekday-US"
    return "weekday-other"
rnd=random.Random(1)
agg=collections.defaultdict(lambda:dict(p=[],nxt=[],ar=[],fr=[],run=[]))
trades=collections.defaultdict(list)
for s in syms:
    rec=sorted((r[0]//H*H,r[1],r[2]) for r in F[s]);T=[r[0] for r in rec];P={r[0]:r[1]*1e4 for r in rec};FR={r[0]:r[2]*1e4 for r in rec}
    tr=tier(s);cs=C.get(s,{});hsp=HS.get(s) or 5.0;cost=2*(9+max(3*hsp,1.0))
    for t in T:
        k=(tr,sess(t));a=agg[k];p=P[t];a["p"].append(abs(p));a["fr"].append(abs(FR[t]))
        n=P.get(t+H)
        if abs(p)>=25 and n is not None:
            a["nxt"].append(1 if (np.sign(n)==np.sign(p) and abs(n)>=abs(p)/2) else 0)
        if n is not None: a["ar"].append((p,n))
        # reversion trade
        if abs(p)>=50 and n is not None:
            c0=cs.get(t-H);c1_=cs.get(t)
            if c0 and c1_:
                pos=-np.sign(p);g=pos*(c1_/c0-1)*1e4;f=-pos*FR[t+H] if (t+H) in FR else 0   # position pays pos*rate; received = -pos*rate
                trades[k].append((t//(7*86400000*1) , g+f-cost, g, f))
    # run lengths
    run=0;prev=0
    for t in T:
        p=P[t]
        if abs(p)>=25 and (prev==0 or np.sign(p)==prev): run+=1;prev=np.sign(p)
        else:
            if run: agg[(tr,sess(t))]["run"].append(run)
            run=1 if abs(p)>=25 else 0;prev=np.sign(p) if abs(p)>=25 else 0
def boot(v):
    wk=collections.defaultdict(list)
    for w,x,*_ in v: wk[w].append(x)
    k=list(wk);bs=[]
    for _ in range(3000):
        a=[];[a.extend(wk[rnd.choice(k)]) for _ in k];bs.append(np.mean(a))
    bs.sort();return round(bs[75],1),round(bs[2925],1)
out={}
print("tier session | hours | med|p| p90 p99 | %>=25 %>=50 | n25 notreverted | AR1 | med run | mean|fund|bp")
for tr in("thin","mid","liquid"):
    for se in("weekend","weekday-US","weekday-other"):
        a=agg[(tr,se)];p=np.array(a["p"])
        if len(p)<50:continue
        ar=np.corrcoef(*zip(*a["ar"]))[0,1] if len(a["ar"])>50 else float("nan")
        row=dict(tier=tr,session=se,hours=len(p),med=float(np.median(p)),p90=float(np.percentile(p,90)),p99=float(np.percentile(p,99)),s25=float((p>=25).mean()),s50=float((p>=50).mean()),n25=len(a["nxt"]),notrev=float(np.mean(a["nxt"])) if a["nxt"] else None,ar1=float(ar),run=float(np.median(a["run"])) if a["run"] else None,fund=float(np.mean(a["fr"])))
        tt=trades.get((tr,se),[])
        if tt:
            row.update(n_tr=len(tt),weeks=len(set(x[0] for x in tt)),gross=float(np.mean([x[2] for x in tt])),fund_rx=float(np.mean([x[3] for x in tt])),net=float(np.mean([x[1] for x in tt])),ci=boot(tt))
        out[f"{tr}|{se}"]=row
        print(f"{tr:6s}{se:14s}|{len(p):7d}| {row['med']:5.1f} {row['p90']:6.1f} {row['p99']:7.1f} | {row['s25']*100:5.1f} {row['s50']*100:5.1f} | {row['n25']:5d} {('%.0f%%'%(row['notrev']*100)) if row['notrev'] is not None else '-':>5s} | {row['ar1']:.2f} | {row['run']} | {row['fund']:.2f}")
        if tt:print(f"     reversion trade n={len(tt)} weeks={row['weeks']} gross={row['gross']:.1f} funding_rx={row['fund_rx']:.1f} net={row['net']:.1f} CI={row['ci']}")
json.dump(out,open("hist_result.json","w"),indent=1,default=float)
