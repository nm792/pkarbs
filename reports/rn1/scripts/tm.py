import json,collections as C,datetime as dt,sys
from g import get
A=json.load(open(sys.argv[1])); T=[r for r in A if r["type"]=="TRADE"]
usd=C.Counter()
for r in T: usd[r["conditionId"]]+=r["usdcSize"]
top=[c for c,_ in usd.most_common(400)]
meta={}
for i in range(0,len(top),40):
    qs="&".join("condition_ids="+c for c in top[i:i+40])
    try:
        for m in get("https://gamma-api.polymarket.com/markets?limit=100&"+qs,retry=2):
            meta[m["conditionId"]]=m
    except Exception as e: print("err",e)
print("meta",len(meta),"of",len(top))
k=next(iter(meta.values())); print({x:k.get(x) for x in ["gameStartTime","startDate","endDate","sportsMarketType","negRisk","secondsDelay","clobRewards","rewardsMinSize","feeSchedule"]})
def P(s):
    if not s: return None
    s=s.replace("Z","+00:00").replace(" ","T")
    if len(s)>=22 and s[-3]!=":" and ("+" in s[19:] or "-" in s[19:]): s=s+":00"
    try: return dt.datetime.fromisoformat(s).timestamp()
    except: return None
bins=C.Counter(); tot=0; smt=C.Counter(); nr=C.Counter()
for r in T:
    m=meta.get(r["conditionId"])
    if not m: continue
    g=P(m.get("gameStartTime"))
    smt[m.get("sportsMarketType") or "none"]+=r["usdcSize"]; nr[str(m.get("negRisk"))]+=r["usdcSize"]
    if g is None: bins["no start"]+=r["usdcSize"]; continue
    d=(r["timestamp"]-g)/60
    b="pre >24h" if d<-1440 else "pre 1-24h" if d<-60 else "pre <1h" if d<0 else "in-play 0-1h" if d<60 else "in-play 1-2h" if d<120 else "in-play 2-4h" if d<240 else "after 4h+"
    bins[b]+=r["usdcSize"]; tot+=r["usdcSize"]
s=sum(bins.values())
print("timing by usdc %:",[(b,round(100*v/s,1)) for b,v in sorted(bins.items())])
s2=sum(smt.values()); print("sportsMarketType %:",[(b,round(100*v/s2,1)) for b,v in smt.most_common(10)])
print("negRisk %:",{b:round(100*v/s2,1) for b,v in nr.items()})
json.dump(meta,open("meta.json","w"))
