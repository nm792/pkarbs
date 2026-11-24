# Live read-only logger: PM perp SP500 mark + both SPY tokens' best bid/ask every ~2 s. No orders. Usage: python3 -I book_logger.py 2026-11-23 SECONDS
import json,sys,urllib.request,datetime as dt,time
def get(u):
    return json.load(urllib.request.urlopen(urllib.request.Request(u,headers={"user-agent":"research-reader"}),timeout=10))
d=sys.argv[1]; dur=int(sys.argv[2]); D=dt.date.fromisoformat(d)
m=get(f"https://gamma-api.polymarket.com/events?slug=spy-up-or-down-on-{D.strftime('%B').lower()}-{D.day}-{D.year}")[0]["markets"][0]; tok=json.loads(m["clobTokenIds"])
out=open(f"live_{d}_book.jsonl","a"); end=time.time()+dur; err=0
while time.time()<end:
    t0=time.time()
    try:
        now=int(t0)
        pm=get(f"https://api.perpetuals.polymarket.com/v1/info/mark-history?instrument_id=1&interval=1s&start_timestamp={(now-5)*1000}&end_timestamp={now*1000}")["data"]
        bk=[get("https://clob.polymarket.com/book?token_id="+t) for t in tok]
        row=dict(t=round(t0,2),t1=round(time.time(),2),perp=pm[-1] if pm else None)
        for n,b in zip(("up","dn"),bk):
            a=min(b["asks"],key=lambda x:float(x["price"])) if b["asks"] else None; bi=max(b["bids"],key=lambda x:float(x["price"])) if b["bids"] else None
            row[n]=dict(ts=b.get("timestamp"),ask=a and float(a["price"]),asz=a and float(a["size"]),bid=bi and float(bi["price"]),bsz=bi and float(bi["size"]))
        out.write(json.dumps(row)+"\n"); out.flush()
    except Exception as e:
        err+=1; out.write(json.dumps(dict(t=round(t0,2),error=str(e)[:200]))+"\n"); out.flush()
    time.sleep(max(0,2-(time.time()-t0)))
