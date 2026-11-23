# Pull Polymarket perps SP500-USD 1 s marks over each SPY event window + prints for events after 18 Nov. Public, no keys.
import json,gzip,urllib.request,time,datetime as dt,os,concurrent.futures as cf
H="https://api.perpetuals.polymarket.com"
def get(u):
    for k in range(5):
        try: return json.load(urllib.request.urlopen(urllib.request.Request(u,headers={"user-agent":"research-reader"}),timeout=30))
        except Exception as e: err=e; time.sleep(1+k)
    raise err
ev=json.load(open("data/events.json"))
for d in ("2026-11-19","2026-11-20"):
    if any(e["date"]==d for e in ev): continue
    D=dt.date.fromisoformat(d); s=f"spy-up-or-down-on-{D.strftime('%B').lower()}-{D.day}-{D.year}"
    e=get("https://gamma-api.polymarket.com/events?slug="+s)[0]; m=e["markets"][0]
    ev.append(dict(date=d,slug=s,cond=m["conditionId"],tokens=json.loads(m["clobTokenIds"]),outcomes=json.loads(m["outcomes"]),final=json.loads(m["outcomePrices"]),closed=m.get("closed"),volume=m.get("volume"),fee=m.get("feeSchedule")))
    tr=[];cur=None
    while True:
        r=get(f"https://data-api.polymarket.com/v2/trades?condition={m['conditionId']}&limit=500"+(f"&cursor={cur}" if cur else "")); tr+=r.get("data",[])
        cur=r.get("pagination",{}).get("next_cursor")
        if not cur: break
    json.dump([{k:t[k] for k in ("side","token_id","size","price","timestamp","outcome","transaction_hash","proxy_wallet")} for t in tr],gzip.open(f"data/trades_{d}.json.gz","wt"))
json.dump(ev,open("data/events.json","w"),indent=0)
os.makedirs("data/perp1s",exist_ok=True)
def pull(e):
    d=e["date"]; out=f"data/perp1s/{d}.json.gz"
    if os.path.exists(out): return d,"cached"
    tr=json.load(gzip.open(f"data/trades_{d}.json.gz"))
    D=dt.date.fromisoformat(d)
    # close K: 16:00 America/New_York
    from zoneinfo import ZoneInfo
    K=int(dt.datetime(D.year,D.month,D.day,16,0,tzinfo=ZoneInfo("America/New_York")).timestamp())
    prev=D-dt.timedelta(days=3 if D.weekday()==0 else 1)
    Kp=int(dt.datetime(prev.year,prev.month,prev.day,16,0,tzinfo=ZoneInfo("America/New_York")).timestamp())
    s=min([t["timestamp"] for t in tr]+[Kp])-600; s=min(s,Kp-600)
    pts=[];t=s*1000
    while t<K*1000:
        r=get(f"{H}/v1/info/mark-history?instrument_id=1&interval=1s&start_timestamp={t}&end_timestamp={min(t+999000,K*1000)}")
        dd=r.get("data",[]); pts+= [[x[0]//1000,float(x[1])] for x in dd]
        t=(dd[-1][0]+1000) if dd else t+999000
    json.dump(dict(K=K,Kprev=Kp,pts=pts),gzip.open(out,"wt")); return d,len(pts)
todo=[e for e in ev if "2026-08-03"<=e["date"]<="2026-11-20"]
with cf.ThreadPoolExecutor(8) as ex:
    for d,n in ex.map(pull,todo): print(d,n,flush=True)
