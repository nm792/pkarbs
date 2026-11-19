# Exploratory (19 Nov 2026): on rule-selected days, first YES prints after listing and bid fill by price. Run from the data folder with pm_hist.json, pm_trades.json, aaa_prints.json, dgasnyh.csv, dgasgulf.csv.
import json, sys, datetime as dt, numpy as np
sys.path.insert(0,'.'); import nowcast as n
H=json.load(open("pm_hist.json")); T=json.load(open("pm_trades.json")); P=n.load_prints(); ny=n.load_spot("dgasnyh.csv"); gu=n.load_spot("dgasgulf.csv")
sel=[]
for s,r in sorted(H.items(),key=lambda kv:kv[1]["end"]):
    d=dt.datetime.strptime(r["end"][:10],"%Y-%m-%d").date(); mk=r["mk"]; win=[i for i,m in enumerate(mk) if json.loads(m["res"])[0]=="1"][0]
    bs=[n.bucket_bounds(m["q"]) for m in mk]; L=min(x["t"] for m in mk for x in m["hist"]); nc=n.oos_predict(P,ny,gu,d,2,dt.date(2026,3,26),10.0)
    if not nc: continue
    prev=P[d-dt.timedelta(days=1)]; mean=prev+nc[0]/100; sd=nc[1]/100
    pr=np.array(n.bucket_probs(mean,sd,bs)); pr/=pr.sum(); i=int(pr.argmax()); lo,hi=bs[i]
    marg=(hi-mean)*100 if lo<-1e8 else ((mean-lo)*100 if hi>1e8 else min(mean-lo,hi-mean)*100)
    if marg<0.5: continue
    tr=[x for x in T.get(mk[i]["cond"],[]) if x["outcome_index"]==0 and x["timestamp"]>=L]
    sel.append((s[-17:],float(pr[i]),i==win,L,sorted(tr,key=lambda x:x["timestamp"])))
for s,p,w,L,tr in sel: print(s,f"p_model={p:.2f}",f"first print {tr[0]['price']:.3f} {tr[0]['side']} lag {(tr[0]['timestamp']-L)/60:.0f}m" if tr else "no prints",f"won={w}")
for b in (0.5,0.6,0.7,0.8,0.9):
    f10=sum(1 for *_,L,tr in sel if any(x["side"]=="SELL" and x["price"]<=b and x["timestamp"]<L+600 for x in tr))
    f60=sum(1 for *_,L,tr in sel if any(x["side"]=="SELL" and x["price"]<=b and x["timestamp"]<L+3600 for x in tr))
    print(f"bid {b:.2f}: days with a SELL print at/below within 10m {f10}/{len(sel)}, 1h {f60}/{len(sel)}")
