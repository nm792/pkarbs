# Pull Polymarket "SPX Opens Up or Down on <date>" events (gamma) and all their trades (data-api v2). Public, no keys.
import json,urllib.request,datetime,time,sys,os
def get(u):
    for k in range(4):
        try: return json.load(urllib.request.urlopen(urllib.request.Request(u,headers={"user-agent":"research-reader"}),timeout=30))
        except Exception as e: err=e; time.sleep(1.5)
    raise err
os.makedirs("data",exist_ok=True)
d=datetime.date(2026,4,20); end=datetime.date(2026,11,18); ev=[]
while d<=end:
    if d.weekday()<5:
        s=f"spx-opens-up-or-down-on-{d.strftime('%B').lower()}-{d.day}-{d.year}"
        r=get("https://gamma-api.polymarket.com/events?slug="+s)
        if r:
            e=r[0]; m=e["markets"][0]
            ev.append(dict(date=str(d),slug=s,cond=m["conditionId"],tokens=json.loads(m["clobTokenIds"]),outcomes=json.loads(m["outcomes"]),
                 final=json.loads(m["outcomePrices"]),closed=m.get("closed"),volume=m.get("volume"),fee=m.get("feeSchedule"),feesEnabled=m.get("feesEnabled")))
    d+=datetime.timedelta(days=1)
print("events",len(ev))
for e in ev:
    tr=[];cur=None;pages=0
    while True:
        u=f"https://data-api.polymarket.com/v2/trades?condition={e['cond']}&limit=500"+(f"&cursor={cur}" if cur else "")
        r=get(u); tr+=r.get("data",[]); pages+=1
        cur=r.get("pagination",{}).get("next_cursor")
        if not cur or pages>=200: break
    e["n_trades"]=len(tr)
    json.dump([{k:t[k] for k in ("side","token_id","size","price","timestamp","outcome","transaction_hash","proxy_wallet")} for t in tr],open(f"data/trades_{e['date']}.json","w"))
    print(e["date"],len(tr),e["volume"],flush=True)
json.dump(ev,open("data/events.json","w"),indent=0)
