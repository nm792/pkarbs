import gzip,json,glob,numpy as np,random,collections
rnd=random.Random(1);NOT=1000.0
recs=[]
for f in sorted(glob.glob("out/*.jsonl.gz")):
    try:
        for l in gzip.open(f,"rt"):
            try:recs.append(json.loads(l))
            except Exception:break
    except Exception:pass
recs=[r for r in recs if "pm" in r and "hl" in r and r.get("books") is not None]
# keep only polls from the book-hot version onward is not needed; just use all
T=[r["t"] for r in recs];print("polls",len(recs),"span min",(T[-1]-T[0])/60 if T else 0)
sym=collections.defaultdict(list)
for r in recs:
    bk=r["books"]
    for x in r["pm"]:
        s,idx,mk,mid,last=x
        try:idx=float(idx);mid=float(mid)
        except Exception:continue
        sym[s].append((r["t"],(mid/idx-1)*1e4,bk.get(s)))
def vwap(levels,usd):
    need=usd;cost=0.0;qty=0.0
    for px,sz in levels:
        px=float(px);sz=float(sz);take=min(sz*px,need)
        cost+=take;qty+=take/px;need-=take
        if need<=1e-9:break
    return cost/qty if need<=1e-9 and qty>0 else None
def fill(book,side):  # side +1 buy -> asks ; -1 sell -> bids
    if not book or "asks" not in book:return None
    return vwap(book["asks"] if side>0 else book["bids"],NOT)
def run(s,series,entry_idx=None):
    pass
events=[];missed=0;nobook=0
for s,ser in sym.items():
    i=0
    while i<len(ser)-3:
        t,g,b=ser[i]
        if abs(g)>=25:
            pos=-1 if g>0 else 1   # sell if perp above index
            # entry at next sample
            t1,g1,b1=ser[i+1]
            if abs(g1)<15: missed+=1;i+=1;continue
            ep=fill(b1,pos)
            if ep is None: nobook+=1;i+=1;continue
            # exit trigger
            j=i+1;ex=None
            while j<len(ser)-1:
                tj,gj,bj=ser[j]
                if abs(gj)<5 or tj-t1>=300:
                    tx,gx,bx=ser[j+1];ex=fill(bx,-pos);break
                j+=1
            if ex is None:
                nobook+=1;i=j+1;continue
            gross=pos*(ex/ep-1)*1e4;net=gross-8
            events.append(dict(sym=s,t=t,day=int(t//86400),g=g,gross=gross,net=net,hold=ser[j+1][0]-t1))
            i=j+2
        else:i+=1
print("events",len(events),"missed (gap gone at entry)",missed,"no usable book",nobook)
if events:
    ne=np.array([e["net"] for e in events]);gr=np.array([e["gross"] for e in events])
    cl=collections.defaultdict(list)
    for e in events:cl[(e["sym"],int(e["t"]//3600))].append(e["net"])
    k=list(cl);bs=[]
    for _ in range(10000):
        a=[];[a.extend(cl[rnd.choice(k)]) for _ in k];bs.append(np.mean(a))
    bs.sort()
    print("gross mean",gr.mean().round(1),"median",np.median(gr).round(1),"net mean",ne.mean().round(1),"median",np.median(ne).round(1),"CI95",bs[250].round(1),bs[9749].round(1),"pos",(ne>0).mean().round(2),"median hold s",np.median([e["hold"] for e in events]),"days",len(set(e["day"] for e in events)))
    bysym=collections.defaultdict(list)
    for e in events:bysym[e["sym"]].append(e["net"])
    for s,v in sorted(bysym.items(),key=lambda kv:-len(kv[1])):print(" ",s,len(v),"net",round(float(np.mean(v)),1))
    # placebo: same number of random times with |g|<10, random direction, same exit rule
    pl=[]
    for e in events:
        ser=sym[e["sym"]];cand=[i for i in range(len(ser)-3) if abs(ser[i][1])<10 and ser[i+1][2] is not None]
        if not cand:continue
        i=rnd.choice(cand);pos=rnd.choice((-1,1));t1,g1,b1=ser[i+1];ep=fill(b1,pos)
        if ep is None:continue
        j=i+1;ex=None
        while j<len(ser)-1:
            if abs(ser[j][1])<5 or ser[j][0]-t1>=300:ex=fill(ser[j+1][2],-pos);break
            j+=1
        if ex:pl.append(pos*(ex/ep-1)*1e4-8)
    print("placebo n",len(pl),"mean net",np.mean(pl).round(1) if pl else None)
