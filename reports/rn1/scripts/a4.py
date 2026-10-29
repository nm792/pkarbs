import json,collections as C,datetime as dt
A=json.load(open("act7d.json")); T=[r for r in A if r["type"]=="TRADE"]
meta=json.load(open("meta_all.json"))
def P(s):
    if not s: return None
    s=s.strip().replace("Z","+00:00").replace(" ","T")
    if s[-3]!=":" and s[-5] in "+-": s=s[:-2]+":"+s[-2:]
    if s[-3]==":" and s[-6] not in "+-" : pass
    try: return dt.datetime.fromisoformat(s if ("+" in s[10:] or s.count("-")>2) else s+"+00:00").timestamp()
    except Exception as e: return None
win={}; gst={}; typ={}
for c,m in meta.items():
    try: op=[float(x) for x in json.loads(m.get("outcomePrices") or "[]")]
    except: op=[]
    if len(op)==2 and sorted(op)==[0.0,1.0]: win[c]=op
    gst[c]=P(m.get("gameStartTime")); typ[c]=m.get("sportsMarketType") or "other"
print("conditions",len(set(r["conditionId"] for r in T)),"meta",len(meta),"resolved",len(win),"with start",sum(1 for v in gst.values() if v))
R=[r for r in T if r["conditionId"] in win]
usd_res=sum(r["usdcSize"] for r in R); usd=sum(r["usdcSize"] for r in T)
print("resolved share of buy usdc %.1f%%"%(100*usd_res/usd))
pnl=lambda r: r["size"]*win[r["conditionId"]][r["outcomeIndex"]]-r["usdcSize"]
tot=sum(pnl(r) for r in R); print("7d resolved fill P&L (pre-fee, pre-rebate) $%.0f on $%.0f bought = %.2f%%"%(tot,usd_res,100*tot/usd_res))
# matched vs excess
cond=C.defaultdict(lambda:{0:[0,0],1:[0,0]})
for r in R:
    x=cond[r["conditionId"]][r["outcomeIndex"]]; x[0]+=r["size"]; x[1]+=r["usdcSize"]
lock=0; dirp=0; dirusd=0; lockusd=0; neg_lock=0
percond=[]
for c,o in cond.items():
    w=win[c]; a,b=o[0],o[1]
    pa=a[1]/a[0] if a[0] else 0; pb=b[1]/b[0] if b[0] else 0
    m=min(a[0],b[0]); l=m*(1-pa-pb); lock+=l; lockusd+=m*(pa+pb)
    if l<0: neg_lock+=l
    ex=0
    for k,(s,u) in o.items():
        e=s-m; p=pa if k==0 else pb
        ex+=e*(w[k]-p); dirusd+=e*p
    dirp+=ex; percond.append((l+ex,c))
print("matched pairs: $%.0f on $%.0f cost (%.2f%%); of which conditions with avg cost>1 lose $%.0f"%(lock,lockusd,100*lock/lockusd,neg_lock))
print("one-sided excess: $%.0f on $%.0f cost (%.2f%%)"%(dirp,dirusd,100*dirp/dirusd))
percond.sort()
tp=sum(x for x,_ in percond)
top=sorted(percond,key=lambda x:-abs(x[0]))[:10]
print("top10 |pnl| conditions sum $%.0f"%sum(x for x,_ in top), [(round(x),meta[c]["question"][:45]) for x,c in top[:6]])
pos=sorted([x for x,_ in percond],reverse=True)
print("win cond share %.1f%%, top 1%% conds = $%.0f, bottom 1%% = $%.0f"%(100*sum(1 for x in pos if x>0)/len(pos),sum(pos[:len(pos)//100]),sum(pos[-len(pos)//100:])))
# timing
def tb(r):
    g=gst.get(r["conditionId"])
    if not g: return "no start time"
    d=(r["timestamp"]-g)/60
    return "1 pre >24h" if d<-1440 else "2 pre 1-24h" if d<-60 else "3 pre <1h" if d<0 else "4 in-play <1h" if d<60 else "5 in-play 1-2h" if d<120 else "6 in-play 2h+"
for name,f in [("timing",tb),("market type",lambda r:typ.get(r["conditionId"])),("category",lambda r:(r.get("eventSlug") or "").split("-")[0]),("price",lambda r:"%.1f-%.1f"%(min(9,int(r["price"]*10))/10,min(9,int(r["price"]*10))/10+.1))]:
    u=C.Counter(); p=C.Counter()
    for r in R: k=f(r); u[k]+=r["usdcSize"]; p[k]+=pnl(r)
    rows=sorted(u, key=lambda k:-u[k]) if name in ("category","market type") else sorted(u)
    print(name+":"); 
    for k in rows[:14]: print("   %-16s usdc %5.1f%%  pnl $%9.0f  margin %6.2f%%"%(k,100*u[k]/usd_res,p[k],100*p[k]/u[k]))
