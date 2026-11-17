import json,numpy as np,random,collections,datetime
H=3600000;h=json.load(open("hist.json"));c=json.load(open("cand.json"))
oi=h["oi"];F=h["fund"];C={k:{int(t):v for t,v in d.items()} for k,d in c["candles"].items()};HS=c["halfspread"]
syms=[s for s in F if len(F[s])>=1440 and (oi.get(s,0)>0 or s.split(":")[0] in ("flx","km")) and s in C]
ois=sorted(oi[s] for s in syms if oi[s]>0);c1,c2=ois[len(ois)//3],ois[2*len(ois)//3]
tier=lambda s:"thin" if (oi[s]<=c1 or oi[s]==0) else ("mid" if oi[s]<=c2 else "liquid")
grp=lambda s:"flx+km" if s.split(":")[0] in("flx","km") else "xyz"
rnd=random.Random(1);WK=7*86400000
def boot(v):
    wk=collections.defaultdict(list)
    for w,x in v: wk[w].append(x)
    k=list(wk);bs=[]
    for _ in range(5000):
        a=[];[a.extend(wk[rnd.choice(k)]) for _ in k];bs.append(np.mean(a))
    bs.sort();return round(bs[125],1),round(bs[4875],1)
sg=np.sign
def series(s):
    rec=sorted((r[0]//H*H,r[1]*1e4,r[2]*1e4) for r in F[s]);return {t:p for t,p,f in rec},{t:f for t,p,f in rec}
S={s:series(s) for s in syms}
# ---------- Test 2
def carry(k,persist=False):
    out=collections.defaultdict(list)
    for s in syms:
        P,FR=S[s];cs=C[s];hs=HS.get(s) or 5.0;cost=2*(9+max(3*hs,1.0));free=0
        for t in sorted(P):
            if t<free or abs(P[t])<50: continue
            if persist and not all((t-i*H) in P and abs(P[t-i*H])>=100 and sg(P[t-i*H])==sg(P[t]) for i in range(3)): continue
            x0=cs.get(t-H);x1=cs.get(t+(k-1)*H)
            if not x0 or not x1: continue
            pos=-sg(P[t]);g=pos*(x1/x0-1)*1e4
            fr=sum(-pos*FR.get(t+i*H,0) for i in range(1,k+1))
            net=g+fr-cost;free=t+k*H
            for key in((grp(s),tier(s)),("all",tier(s)),(grp(s),"all"),("all","all")): out[key].append((t//WK,net,g,fr))
    return out
for k,pers in((6,False),(6,True),(3,False),(12,False)):
    o=carry(k,pers);print(f"== carry k={k} persistent={pers}")
    for key in sorted(o):
        v=o[key]
        if len(v)<10:continue
        print(f"{key[0]:7s}{key[1]:7s} n={len(v):5d} weeks={len(set(x[0] for x in v)):2d} gross={np.mean([x[2] for x in v]):7.1f} funding={np.mean([x[3] for x in v]):6.1f} net={np.mean([x[1] for x in v]):7.1f} CI={boot([(x[0],x[1]) for x in v])}")
# ---------- Test 3
eps=[]
for s in syms:
    P,FR=S[s];cs=C[s];ts=sorted(P);i=0
    while i<len(ts):
        t=ts[i]
        if abs(P[t])>=100:
            j=i
            while j+1<len(ts) and ts[j+1]==ts[j]+H and abs(P[ts[j+1]])>=100 and sg(P[ts[j+1]])==sg(P[t]): j+=1
            n=j-i+1
            if n>=3:
                nxt=ts[j+1] if j+1<len(ts) and ts[j+1]==ts[j]+H else None
                reset=nxt is not None and abs(P[nxt])<25
                eps.append(dict(s=s,start=t,n=n,last=ts[j],p=P[ts[j]],sign=sg(P[t]),nxt=nxt,reset=reset,end_kind=("reset" if reset else ("gap" if nxt is None else "partial"))))
            i=j+1
        else: i+=1
print("episodes",len(eps),"by end",collections.Counter(e["end_kind"] for e in eps))
for gname in("xyz","flx+km"):
    for tn in("thin","mid","liquid"):
        v=[e for e in eps if grp(e["s"])==gname and tier(e["s"])==tn]
        if v:print(gname,tn,"episodes",len(v),"median run",np.median([e["n"] for e in v]),"p90 run",np.percentile([e["n"] for e in v],90),"median |p| before end",round(float(np.median([abs(e["p"]) for e in v])),0))
# hazard
print("hazard: run length n -> P(reset next hour) , P(partial exit), episodes at risk")
for n in range(3,13):
    risk=[e for e in eps if e["n"]>=n];
    if len(risk)<10:break
    end=[e for e in risk if e["n"]==n]
    print(n,len(risk),round(sum(1 for e in end if e["end_kind"]=="reset")/len(risk),3),round(sum(1 for e in end if e["end_kind"]=="partial")/len(risk),3))
# jump size at reset
y=[];x=[];tr=[]
for e in eps:
    if not e["reset"]:continue
    s=e["s"];cs=C[s];tr_=e["nxt"];c1_=cs.get(tr_-H);c0_=cs.get(tr_-2*H)
    if c0_ and c1_:
        mv=(c1_/c0_-1)*1e4*(-e["sign"]);y.append(mv);x.append(abs(e["p"]))
        # ex-post trade: enter after 3rd hour of episode, exit at reset hour close
        t3=e["start"]+2*H;ent=cs.get(t3-H);ex=c1_;FR=S[s][1]
        if ent:
            pos=-e["sign"];g=pos*(ex/ent-1)*1e4
            fr=sum(-pos*FR.get(t,0) for t in range(t3+H,tr_+1,H));hs=HS.get(s) or 5.0
            tr.append((e["start"]//WK,g+fr-2*(9+max(3*hs,1.0)),g,fr,grp(s),tier(s)))
print("reset episodes with candles",len(y))
if len(y)>5:
    y=np.array(y);x=np.array(x)
    print("move toward oracle in reset hour (bp): mean",y.mean().round(1),"median",np.median(y).round(1),"mean |premium| before",x.mean().round(1),"slope",np.polyfit(x,y,1)[0].round(3),"corr",np.corrcoef(x,y)[0,1].round(3))
    print("ex-post bound trade: n",len(tr),"gross",np.mean([a[2] for a in tr]).round(1),"funding",np.mean([a[3] for a in tr]).round(1),"net",np.mean([a[1] for a in tr]).round(1),"CI",boot([(a[0],a[1]) for a in tr]),"weeks",len(set(a[0] for a in tr)))
    for gname in("xyz","flx+km"):
        v=[a for a in tr if a[4]==gname]
        if len(v)>=5:print("  ",gname,len(v),"net",np.mean([a[1] for a in v]).round(1),boot([(a[0],a[1]) for a in v]))
# predictability: numpy logistic (IRLS), last 30% of weeks out of sample
rows=[]
for e in eps:
    for n in range(3,e["n"]+1):
        t=e["start"]+(n-1)*H;P=S[e["s"]][0];nxt=t+H
        if nxt not in P: continue
        d=datetime.datetime.fromtimestamp(nxt/1000,datetime.UTC)
        wkend=1 if ((d.weekday()==4 and d.hour>=22) or d.weekday()==5 or (d.weekday()==6 and d.hour<22)) else 0
        rows.append((t,[1,n,abs(P[t])/100,wkend,1 if grp(e["s"])=="flx+km" else 0],1 if (n==e["n"] and e["reset"]) else 0))
rows.sort();cut=int(len(rows)*0.7);tr_=rows[:cut];te=rows[cut:]
Xtr=np.array([r[1] for r in tr_],float);ytr=np.array([r[2] for r in tr_],float);Xte=np.array([r[1] for r in te],float);yte=np.array([r[2] for r in te],float)
w=np.zeros(Xtr.shape[1])
for _ in range(50):
    p=1/(1+np.exp(-Xtr@w));W=p*(1-p)+1e-6;w=w+np.linalg.solve(Xtr.T@(Xtr*W[:,None])+1e-3*np.eye(len(w)),Xtr.T@(ytr-p))
sc=Xte@w
def auc(y,s_):
    pos=s_[y==1];neg=s_[y==0]
    return float(np.mean([(p>neg).mean()+0.5*(p==neg).mean() for p in pos])) if len(pos) and len(neg) else None
print("logistic rows",len(rows),"train resets",int(ytr.sum()),"test resets",int(yte.sum()),"AUC out-of-sample",auc(yte,sc),"coefs [const,run,|p|/100,weekend,flx/km]",w.round(2))
