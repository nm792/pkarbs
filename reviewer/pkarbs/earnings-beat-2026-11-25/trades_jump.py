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
    def py(x): return x["price"] if x["token_id"]==r["yes_token"] else 1-x["price"]
    tape=sorted((x["timestamp"],round(py(x),4),round(x["size"]*x["price"],2)) for x in rows)
    # report (jump) time J: first trade after which every YES price is >=0.97 or every one <=0.03, i.e. the outcome is known
    J=None; y=1 if r["final"]==["1","0"] else 0
    for i in range(len(tape)):
        rest=[p for _,p,_ in tape[i:]]
        if (y==1 and min(rest)>=0.97) or (y==0 and max(rest)<=0.03): J=tape[i][0]; break
    T=(J-1800) if J else ts(r["start"])
    pre=sorted([x for x in rows if x["timestamp"]<T],key=lambda x:x["timestamp"])
    win=[x for x in pre if x["timestamp"]>=T-86400]
    usd=sum(x["size"]*x["price"] for x in win)
    vw=(sum(py(x)*x["size"]*x["price"] for x in win)/usd) if usd else None
    return dict(J=J,tape_n=len(tape),slug=r["slug"],y=1 if r["final"]==["1","0"] else 0,vol=r["vol"],start=r["start"],n_all=len(rows),n_pre=len(pre),
                last_pre=py(pre[-1]) if pre else None,last_pre_age_h=(T-pre[-1]["timestamp"])/3600 if pre else None,vwap24=vw,usd24=usd,fee=r.get("feeSchedule"))
with cf.ThreadPoolExecutor(6) as ex: out=[x for x in ex.map(one,d) if x]
json.dump(out,open("pre_jump.json","w")); print(len(out), sum(1 for x in out if x.get("last_pre") is not None), sum(1 for x in out if "err" in x))
