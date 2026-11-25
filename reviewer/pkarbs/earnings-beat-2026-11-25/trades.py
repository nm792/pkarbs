# Pre-report YES price per closed earnings-beat market from Data API v2 trades (condition filter, asserted per row).
import json, subprocess, datetime, concurrent.futures as cf
d=json.load(open("closed.json"))
def ts(s): return datetime.datetime.fromisoformat(s.replace("Z","+00:00")).timestamp()
def get(q):
    o=subprocess.run(["curl","-s","--max-time","30","https://data-api.polymarket.com/v2/trades?"+q],capture_output=True,text=True).stdout
    return json.loads(o)
def one(r):
    if not r.get("cid") or not r.get("start") or not r.get("yes_token"): return None
    rows=[]; cur=None; pages=0
    while True:
        try: j=get(f"condition={r['cid']}&limit=500"+(f"&cursor={cur}" if cur else ""))
        except Exception as e: return dict(slug=r["slug"],err=str(e)[:60])
        if "data" not in j: return dict(slug=r["slug"],err=str(j)[:80])
        b=j["data"]; assert all(x["condition_id"]==r["cid"] for x in b), r["slug"]
        rows+=b; pages+=1; cur=(j.get("pagination") or {}).get("next_cursor")
        if not cur or pages>=20: break
    T=ts(r["start"])
    def py(x): return x["price"] if x["token_id"]==r["yes_token"] else 1-x["price"]
    pre=sorted([x for x in rows if x["timestamp"]<T],key=lambda x:x["timestamp"])
    win=[x for x in pre if x["timestamp"]>=T-86400]
    usd=sum(x["size"]*x["price"] for x in win)
    vw=(sum(py(x)*x["size"]*x["price"] for x in win)/usd) if usd else None
    return dict(slug=r["slug"],y=1 if r["final"]==["1","0"] else 0,vol=r["vol"],start=r["start"],n_all=len(rows),n_pre=len(pre),
                last_pre=py(pre[-1]) if pre else None,last_pre_age_h=(T-pre[-1]["timestamp"])/3600 if pre else None,vwap24=vw,usd24=usd,fee=r.get("feeSchedule"))
with cf.ThreadPoolExecutor(6) as ex: out=[x for x in ex.map(one,d) if x]
json.dump(out,open("pre.json","w")); print(len(out), sum(1 for x in out if x.get("last_pre") is not None), sum(1 for x in out if "err" in x))
