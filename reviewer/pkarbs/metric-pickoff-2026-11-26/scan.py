"""Stale-ask pickoff scan on historical prints (Data API v2 /trades). PRINTS ONLY: a FLOOR, not own-book depth.
Rule under test: at R+L the winning token of each market is known; count BUY prints on the winner's OWN token at price < 0.95
in [R+L, R+60 s]. Winner = settlement outcome (oracle proxy for the printed number; measurement only).
Timestamps are whole seconds (API resolution)."""
import json, os, gzip, time, hashlib, statistics, datetime as dt
from zoneinfo import ZoneInfo
import requests

CACHE="cache"; os.makedirs(CACHE,exist_ok=True)
S=requests.Session()
LS=(0,2,5,15)           # latency scenarios, seconds
WIN=60                  # window length after R, seconds
CAP_TRADE=200.0; CAP_DAY=2000.0; PMAX=0.95

def fetch_trades(cid, max_pages=30):
    fn=f"{CACHE}/{cid}.json.gz"
    if os.path.exists(fn): return json.load(gzip.open(fn,"rt"))
    rows=[]; cur=None; pages=0; seen_low=False
    while pages<max_pages:
        p=dict(condition=cid,limit=500)
        if cur: p["cursor"]=cur
        for k in range(4):
            try:
                r=S.get("https://data-api.polymarket.com/v2/trades",params=p,timeout=40)
                if r.status_code==429: time.sleep(2+k*2); continue
                r.raise_for_status(); j=r.json(); break
            except Exception as e:
                if k==3: raise
                time.sleep(1+k)
        b=j.get("data") or []
        assert all(x["condition_id"]==cid for x in b)
        rows+=[dict(ts=x["timestamp"],tok=x["token_id"],side=x["side"],p=x["price"],sz=x["size"]) for x in b]
        pages+=1; cur=(j.get("pagination") or {}).get("next_cursor")
        if not cur or not b: break
        # stop once we are >3 days older than the newest print and have seen a low-priced print
        if min(r_["p"] for r_ in rows)<0.5 and rows[-1]["ts"]<rows[0]["ts"]-3*86400: break
    json.dump(rows,gzip.open(fn,"wt")); return rows

def winner_token(m):
    try: op=[float(x) for x in json.loads(m["op"]) if True] if isinstance(m["op"],str) else [float(x) for x in m["op"]]
    except Exception: return None
    tk=m["tok"]; tk=json.loads(tk) if isinstance(tk,str) else tk
    if not tk or len(tk)!=2 or len(op)!=2: return None
    if op==[1.0,0.0]: return tk[0]
    if op==[0.0,1.0]: return tk[1]
    return None

def jump_time(series):
    """first ts after which every winner-token print is >=0.6, preceded by a print <=0.5 (a real jump). None if no jump."""
    s=sorted(series)  # (ts,p)
    last_low=None
    for i,(t,p) in enumerate(s):
        if p<0.6: last_low=i
    if last_low is None or last_low==len(s)-1: return None
    low=[x for x in s[:last_low+1] if x[1]<=0.5]
    if not low: return None
    return s[last_low+1][0]

def tzclock(tz,hh,mm,day):  # UTC epoch of local clock time on a given UTC date +-1
    return int(dt.datetime(day.year,day.month,day.day,hh,mm,tzinfo=ZoneInfo(tz)).timestamp())
CLOCKS={  # family -> [(tz,hh,mm)] scheduled release clocks (public calendars)
 "macro":[("America/New_York",8,30),("America/New_York",10,0),("Europe/London",7,0),("Europe/Berlin",11,0)],
 "fed":[("America/New_York",14,0)],
 "cb":[("Europe/Berlin",14,15),("Europe/London",12,0),("Europe/Moscow",13,30),("America/New_York",9,45),("Australia/Sydney",14,30),("Europe/Zurich",9,30),("America/New_York",14,0)],
}
FAMCLOCK={"fed_decision":"fed","ecb_boj_boe_bor":"cb","cpi_inflation":"macro","jobs_unemp":"macro","gdp":"macro","eggs_prices":"macro"}
def snap(family,j0):
    ck=FAMCLOCK.get(family)
    if not ck: return None
    d0=dt.datetime.fromtimestamp(j0,dt.timezone.utc).date()
    best=None
    for dd in (-1,0,1):
        day=d0+dt.timedelta(days=dd)
        for tz,hh,mm in CLOCKS[ck]:
            t=tzclock(tz,hh,mm,day)
            if j0-600<=t<=j0 and (best is None or t>best): best=t
    return best

def scan_market(rows, wtok, R, Ls=LS, win=WIN):
    """BUY prints on winner token, price<PMAX, ts in [R+L, R+win]. returns dict L->list of (ts,p,sz)."""
    out={}
    for L in Ls:
        out[L]=[(r["ts"],r["p"],r["sz"]) for r in rows if r["tok"]==wtok and r["side"]=="BUY" and r["p"]<PMAX and R+L<=r["ts"]<=R+win]
    return out

def day_cap(prints):
    """apply $200 per trade, $2000 per UTC day on paid notional; return (paid, edge)."""
    by={}
    paid=edge=0.0
    for ts,p,sz in sorted(prints):
        d=ts//86400
        n=min(p*sz,CAP_TRADE); n=min(n,CAP_DAY-by.get(d,0.0))
        if n<=0: continue
        by[d]=by.get(d,0.0)+n; paid+=n; edge+=n*(1-p)/p
    return paid,edge
