# Pull closed Polymarket earnings-beat events (tag_slug=earnings), one market each; record outcome, volume, end date.
import json, urllib.request, time
out=[]; off=0
while True:
    u=f"https://gamma-api.polymarket.com/events?tag_slug=earnings&closed=true&limit=50&offset={off}&order=endDate&ascending=false"
    d=json.load(urllib.request.urlopen(urllib.request.Request(u,headers={"Accept":"application/json"})))
    if not d: break
    for e in d:
        for m in e.get("markets",[]):
            if "quarterly-earnings" not in (m.get("slug") or ""): continue
            try: op=json.loads(m.get("outcomePrices") or "[]"); oc=json.loads(m.get("outcomes") or "[]"); tk=json.loads(m.get("clobTokenIds") or "[]")
            except Exception: continue
            if len(op)!=2: continue
            out.append(dict(slug=m["slug"],cid=m.get("conditionId"),start=e.get("startTime"),q=m.get("question"),end=m.get("endDate"),closed=m.get("closedTime"),vol=float(m.get("volume") or 0),
                            outcomes=oc,final=op,yes_token=tk[0] if tk else None,feeSchedule=m.get("feeSchedule")))
    off+=50; time.sleep(0.2)
    if off>6000: break
json.dump(out,open("closed.json","w"))
print(len(out))
