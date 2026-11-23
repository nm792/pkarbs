# One live read: perp marks + both SPY tokens' books at the same moment. Read-only. Usage: python3 -I live_read.py 2026-11-23
import json,sys,math,urllib.request,datetime as dt,time
from zoneinfo import ZoneInfo
def get(u,data=None):
    h={"user-agent":"research-reader"}
    if data: h["content-type"]="application/json"
    return json.load(urllib.request.urlopen(urllib.request.Request(u,data=data,headers=h),timeout=20))
d=sys.argv[1]; D=dt.date.fromisoformat(d)
e=get(f"https://gamma-api.polymarket.com/events?slug=spy-up-or-down-on-{D.strftime('%B').lower()}-{D.day}-{D.year}")[0]; m=e["markets"][0]; tok=json.loads(m["clobTokenIds"])
NY=ZoneInfo("America/New_York"); K=int(dt.datetime(D.year,D.month,D.day,16,0,tzinfo=NY).timestamp())
prev=D-dt.timedelta(days=3 if D.weekday()==0 else 1); Kp=int(dt.datetime(prev.year,prev.month,prev.day,16,0,tzinfo=NY).timestamp())
c0=get(f"https://api.perpetuals.polymarket.com/v1/info/mark-history?instrument_id=1&interval=1s&start_timestamp={(Kp-60)*1000}&end_timestamp={Kp*1000}")["data"][-1]
t0=time.time()
now=int(t0); pm=get(f"https://api.perpetuals.polymarket.com/v1/info/mark-history?instrument_id=1&interval=1s&start_timestamp={(now-30)*1000}&end_timestamp={now*1000}")["data"]
hl=get("https://api.hyperliquid.xyz/info",json.dumps({"type":"allMids","dex":"xyz"}).encode())["xyz:SP500"]
books=[get("https://clob.polymarket.com/book?token_id="+t) for t in tok]
t1=time.time()
r=json.load(open("result.json")); SG={int(k):v/1e4 for k,v in r["sigma_bp"].items()}; MU={int(k):v/1e4 for k,v in r["mu_bp"].items()}
tau=(K-now)/3600
def itp(tab):
    if tau>23: return tab[23]*math.sqrt(tau/23) if tab is SG else tab[23]
    a=max(1,int(tau)); b=min(a+1,23); w=max(0,tau-a); return tab[a]*(1-w)+tab[b]*w
P=float(pm[-1][1]); C0=float(c0[1]); N=lambda x:0.5*(1+math.erf(x/math.sqrt(2)))
pu=N((math.log(P/C0)+itp(MU))/itp(SG)); fee=lambda a:0.04*a*(1-a)
out=dict(read_utc=dt.datetime.fromtimestamp(t0,dt.UTC).isoformat(),read_seconds=round(t1-t0,2),event=e["slug"],hours_to_close=round(tau,2),
  C0_perp_at_prev_close=C0,C0_ts=c0[0],pm_perp_mark=P,pm_perp_ts=pm[-1][0],hl_xyz_sp500_mid=float(hl),move_bp=round(math.log(P/C0)*1e4,1),fair_up=round(pu,4))
for k,(name,b) in enumerate(zip(("Up","Down"),books)):
    asks=sorted(b["asks"],key=lambda x:float(x["price"]))[:5]; bids=sorted(b["bids"],key=lambda x:-float(x["price"]))[:5]
    f=pu if k==0 else 1-pu; a=float(asks[0]["price"]) if asks else None
    out[name]=dict(book_ts=b.get("timestamp"),best_ask=a,ask_size=asks[0]["size"] if asks else None,best_bid=bids[0]["price"] if bids else None,
       fair=round(f,4),edge_at_ask=round(f-a-fee(a),4) if a else None,top5_ask_usd=round(sum(float(x["price"])*float(x["size"]) for x in asks),2))
fn=f"LIVE-READ-{d}-{dt.datetime.fromtimestamp(t0,dt.UTC).strftime('%H%M')}.json"; json.dump(out,open(fn,"w"),indent=1); print(fn); print(json.dumps(out,indent=1))
