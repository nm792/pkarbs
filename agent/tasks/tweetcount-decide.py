#!/usr/bin/env python3
"""Decision generator for the tiny live test of the weekly Elon tweet-count rule (NO ORDERS PLACED HERE; stdlib only).
Locked rule (backtest 'weekly, 24h, 5c edge'; k=0.439, bias=0.003 fitted on the first 48 weekly events, never re-fit):
  at T = window end - 24 h (run within 10 minutes after T):
    so_far = posts in [window start, T) from xtracker   (resolution source)
    rem    = sum over remaining hours of the 21-day UTC hour-of-day posting rate
    mu = so_far + rem*(1+0.003); sd = max(0.439*rem, sqrt(max(rem,1)))
    p_model(bracket) = Phi((hi+.5-mu)/sd) - Phi((lo-.5-mu)/sd)
  Candidates: BUY YES at the live best ask if p_model - ask_yes > 0.05 ; BUY NO at the live best No ask if (1-p_model) - ask_no > 0.05.
  Skip prices <= 0.02 or >= 0.98. ONE bracket per window only: the single largest edge (model - ask) over all YES and NO candidates. Size = min(shares at that ask level, $5/price).
Output: JSON list (at most one) of taker order intents (token_id, side=BUY, outcome, limit_price=ask, shares, usd). Hermes places it as a marketable FOK/IOC order, never resting.
Usage: python3 tweetcount-decide.py --slug elon-musk-of-tweets-november-6-november-13-2026 [--force] [--ts-file posts.json]
"""
import argparse, bisect, calendar, json, math, re, sys, time, urllib.request, urllib.parse
UA={"User-Agent":"Mozilla/5.0 (compatible; research)"}
K,B,TH=0.439,0.003,0.05
CAP_WINDOW=5.0  # ONE bracket per window, the single largest edge, max $5
def j(u):
    with urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=30) as r: return json.loads(r.read().decode('utf-8','replace'))
def Phi(x): return .5*(1+math.erf(x/math.sqrt(2)))
def bucket(t):
    m=re.match(r'<(\d+)',t)
    if m: return (0,int(m.group(1))-1)
    m=re.match(r'(\d+)\+',t)
    if m: return (int(m.group(1)),10**9)
    m=re.match(r'(\d+)-(\d+)',t)
    if m: return (int(m.group(1)),int(m.group(2)))
def posts(start_iso,end_iso):
    d=j("https://xtracker.polymarket.com/api/users/elonmusk/posts?startDate=%s&endDate=%s"%(start_iso,end_iso))["data"]
    return sorted(calendar.timegm(time.strptime(p["createdAt"][:19],"%Y-%m-%dT%H:%M:%S")) for p in d)
def book(tok):
    b=j("https://clob.polymarket.com/book?token_id="+tok)
    asks=sorted((float(x["price"]),float(x["size"])) for x in b.get("asks",[]))
    return asks[0] if asks else None
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--slug",required=True); ap.add_argument("--force",action="store_true"); ap.add_argument("--ts-file")
    a=ap.parse_args()
    ev=j("https://gamma-api.polymarket.com/events?slug="+a.slug)[0]
    end=calendar.timegm(time.strptime(ev["endDate"][:19],"%Y-%m-%dT%H:%M:%S")); T=end-24*3600; now=time.time()
    start=end-7*86400
    if not a.force and not (T<=now<=T+600): print(json.dumps({"skip":"outside decision window [T, T+10min]","T":T,"now":now})); return
    if "tweets" not in ev["title"] or not ev["title"].startswith("Elon"): print(json.dumps({"skip":"not an Elon tweets window"})); return
    iso=lambda t: time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime(t))
    TS=json.load(open(a.ts_file)) if a.ts_file else posts(iso(T-21*86400),iso(T))
    so=bisect.bisect_left(TS,T)-bisect.bisect_left(TS,start)
    c=[0]*24
    for x in TS[bisect.bisect_left(TS,T-21*86400):bisect.bisect_left(TS,T)]: c[int((x%86400)//3600)]+=1
    prof=[v/21 for v in c]
    rem=0;x=T
    while x<end:
        nx=min(end,(x//3600+1)*3600); rem+=prof[int((x%86400)//3600)]*(nx-x)/3600; x=nx
    mu=so+rem*(1+B); sd=max(K*rem,math.sqrt(max(rem,1)))
    cand=[]
    for mk in ev["markets"]:
        bk=bucket(mk.get("groupItemTitle") or "")
        if not bk: continue
        pm=Phi((bk[1]+.5-mu)/sd)-Phi((bk[0]-.5-mu)/sd)
        toks=json.loads(mk["clobTokenIds"])
        for side,tok,pmodel in (("Yes",toks[0],pm),("No",toks[1],1-pm)):
            try: ask=book(tok)
            except Exception: continue
            if not ask: continue
            p,sz=ask
            if p<=0.02 or p>=0.98 or pmodel-p<=TH: continue
            usd=min(CAP_WINDOW,sz*p)
            if usd<1: continue
            cand.append((pmodel-p,{"bracket":mk["groupItemTitle"],"token_id":tok,"side":"BUY","outcome":side,"limit_price":p,"shares":round(usd/p,2),"usd":round(usd,2),"p_model":round(pmodel,3),"edge":round(pmodel-p,3)}))
    out=[max(cand,key=lambda x:x[0])[1]] if cand else []
    spent=sum(o["usd"] for o in out)
    print(json.dumps({"slug":a.slug,"T":T,"so_far":so,"rem_pred":round(rem,1),"mu":round(mu,1),"sd":round(sd,1),"orders":out,"total_usd":round(spent,2)},indent=1))
main()
