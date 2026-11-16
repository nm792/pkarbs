import json,urllib.request,urllib.parse,time,datetime,gzip
H="https://api.perpetuals.polymarket.com"
def get(p,**q):
    u=H+p+("?"+urllib.parse.urlencode(q) if q else "")
    for k in range(4):
        try:
            return json.load(urllib.request.urlopen(urllib.request.Request(u,headers={"user-agent":"data-logger"}),timeout=30))
        except Exception as e: err=e;time.sleep(1.5)
    raise err
ins={i["symbol"]:i["instrument_id"] for i in json.load(open("/tmp/wp/pm_instruments.json"))}
MAP={"SP500":"SP500-USD","XYZ100":"NAS100-USD","NVDA":"NVDA-USD","SNDK":"SNDK-USD","MU":"MU-USD","AMD":"AMD-USD","GOOGL":"GOOG-USD"}
rows=json.load(open("/tmp/wp/rows.json"))
out=[];nof=0
for r in rows:
    if r["sym"] not in MAP: continue
    T=r["T"]; iid=ins[MAP[r["sym"]]]
    if T< 1785542400000+86400000: continue   # PM live from 1 Aug 2026
    t=T-1800000
    d=get("/v1/info/mark-history",instrument_id=iid,interval="1s",start_timestamp=t-120000,end_timestamp=t+1000)
    pts=[x for x in d.get("data",[]) if x[0]<=t]
    if not pts: nof+=1;continue
    out.append(dict(r,pm_mark=float(pts[-1][1]),pm_ts=pts[-1][0]))
print("PM cells",len(out),"no data",nof)
json.dump(out,open("/tmp/wp/pm_rows.json","w"))
