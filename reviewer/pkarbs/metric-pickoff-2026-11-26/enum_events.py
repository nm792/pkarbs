# Enumerate Gamma events per candidate tag slug (open + closed). Output: events_<tag>.json (compact). Volume = SHARES-ish gamma figure, NOT $.
import json, sys, time, requests
TAGS=sys.argv[1:]
S=requests.Session()
def page(tag, closed, off):
    r=S.get("https://gamma-api.polymarket.com/events",params=dict(tag_slug=tag,closed=str(closed).lower(),limit=50,offset=off,order="endDate",ascending="false"),headers={"Accept-Encoding":"gzip"},timeout=40)
    r.raise_for_status(); return r.json()
for tag in TAGS:
    out={}
    for closed in (True,False):
        off=0
        while off<8000:
            try: d=page(tag,closed,off)
            except Exception as e: print(tag,"ERR",off,str(e)[:80]); break
            if not d: break
            for e in d:
                out[e["id"]]=dict(id=e["id"],slug=e.get("slug"),title=e.get("title"),start=e.get("startTime"),end=e.get("endDate"),closed=e.get("closed"),vol=e.get("volume"),
                    tags=[t["slug"] for t in e.get("tags",[])],
                    markets=[dict(slug=m.get("slug"),q=m.get("question"),cid=m.get("conditionId"),tok=m.get("clobTokenIds"),op=m.get("outcomePrices"),outs=m.get("outcomes"),vol=m.get("volume"),end=m.get("endDate"),closedTime=m.get("closedTime"),fee=m.get("feeSchedule")) for m in e.get("markets",[])])
            off+=50
            time.sleep(0.15)
    json.dump(list(out.values()),open(f"events_{tag}.json","w"))
    print(tag,len(out),"events",sum(len(v["markets"]) for v in out.values()),"markets",flush=True)
