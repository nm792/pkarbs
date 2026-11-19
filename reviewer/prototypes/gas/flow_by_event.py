import json, time, gzip, sys
# usage: python3 flow_by_event.py raw/events_trades-<stamp>.json.gz
from collections import defaultdict
D=json.load(gzip.open(sys.argv[1], "rt"))
def ts(s):
    import datetime; return datetime.datetime.fromisoformat(s.replace("Z","+00:00")).timestamp() if s else None
print("slug | series | start | end | gamma vol | trades $ | $ at 0.05-0.95 | taker-buy $ 0.05-0.95 | n trades | days live")
agg=defaultdict(lambda: defaultdict(float))
for slug,e in D.items():
    gv=float(e.get("volume") or 0); tot=q=qb=0; n=0
    for m in e["markets"]:
        for t in m["_trades"]:
            x=t["price"]*t["size"]; tot+=x; n+=1
            if 0.05<=t["price"]<=0.95:
                q+=x
                if t["side"]=="BUY": qb+=x
    s0,s1=ts(e.get("startDate")),ts(e.get("endDate")); days=max((min(s1,time.time())-s0)/86400,0.01)
    a=agg[e["_series"]]; a["gv"]+=gv; a["tot"]+=tot; a["q"]+=q; a["qb"]+=qb; a["days"]+=days; a["n"]+=1
    print(f"{slug[:45]} | {e['_series']} | {e.get('startDate','')[:10]} | {e.get('endDate','')[:10]} | {gv:,.0f} | {tot:,.0f} | {q:,.0f} | {qb:,.0f} | {n} | {days:.1f}")
print()
for s,a in agg.items(): print(s, {k:round(v) for k,v in a.items()})
