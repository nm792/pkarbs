import json,urllib.request,urllib.parse,calendar,time,gzip,datetime,sys
OUT="/tmp/wp/data/"
COINS=["JP225","SP500","XYZ100","NVDA","SNDK","MU","AMD","GOOGL"]
CASH={"JP225":"^N225","SP500":"^GSPC","XYZ100":"^NDX","NVDA":"NVDA","SNDK":"SNDK","MU":"MU","AMD":"AMD","GOOGL":"GOOGL"}
def post(b):
    for k in range(4):
        try:
            r=urllib.request.Request("https://api.hyperliquid.xyz/info",json.dumps(b).encode(),{"content-type":"application/json","user-agent":"data-logger"})
            return json.load(urllib.request.urlopen(r,timeout=40))
        except Exception as e:
            err=e; time.sleep(2)
    raise err
now=int(time.time()*1000)
start=calendar.timegm((2026,4,15,0,0,0))*1000
meta={"fetched_utc":datetime.datetime.now(datetime.UTC).isoformat()}
for c in COINS:
    coin="xyz:"+c
    rows=[];s=start
    while s<now:
        e=min(now,s+30*86400000)
        r=post({"type":"candleSnapshot","req":{"coin":coin,"interval":"1h","startTime":s,"endTime":e}})
        rows+=r
        s=e+1
    seen={};[seen.__setitem__(x["t"],x) for x in rows]; rows=[seen[k] for k in sorted(seen)]
    m1=post({"type":"candleSnapshot","req":{"coin":coin,"interval":"1m","startTime":now-5000*60000,"endTime":now}})
    fr=[];s=start
    while True:
        r=post({"type":"fundingHistory","coin":coin,"startTime":s})
        if not r: break
        fr+=r
        if len(r)<500: break
        s=r[-1]["time"]+1
    seen={};[seen.__setitem__(x["time"],x) for x in fr]; fr=[seen[k] for k in sorted(seen)]
    json.dump({"coin":coin,"h1":rows,"m1":m1,"funding":fr},gzip.open(OUT+f"hl_{c}.json.gz","wt"))
    f=lambda t: datetime.datetime.fromtimestamp(t/1000,datetime.UTC).strftime("%Y-%m-%d %H:%M")
    print(coin,"h1",len(rows),f(rows[0]["t"]) if rows else None,f(rows[-1]["t"]) if rows else None,"m1",len(m1),"funding",len(fr),flush=True)
for c,ys in CASH.items():
    u=f"https://query1.finance.yahoo.com/v8/finance/chart/{urllib.parse.quote(ys)}?interval=1d&range=2y"
    r=urllib.request.Request(u,headers={"user-agent":"Mozilla/5.0"})
    d=json.load(urllib.request.urlopen(r,timeout=40))["chart"]["result"][0]
    json.dump(d,gzip.open(OUT+f"yahoo_{c}.json.gz","wt"))
    print("yahoo",ys,len(d["timestamp"]),flush=True)
json.dump(meta,open(OUT+"meta.json","w"))
