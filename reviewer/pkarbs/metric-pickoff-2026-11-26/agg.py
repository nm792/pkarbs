import json,collections,glob,datetime as dt
from families import classify
out=json.load(open("scan_out.json"))
# events per month by family over closed events with end in last 180d (all events enumerated, not only scanned)
ev={}
for f in glob.glob("events_*.json"):
    for e in json.load(open(f)): ev[e["id"]]=e
now=dt.datetime(2026,11,26,tzinfo=dt.timezone.utc)
per_month={}
for e in ev.values():
    f=classify(e["title"])
    if not f or not e["closed"] or not e["end"]: continue
    d=dt.datetime.fromisoformat(e["end"].replace("Z","+00:00"))
    if (now-d).days<=180 and d<=now: per_month[f]=per_month.get(f,0)+1
for f in per_month: per_month[f]/=6.0
rows=[]
by=collections.defaultdict(list)
for r in out: by[r["family"]].append(r)
for f,l in by.items():
    n=len(l); withR=[r for r in l if r.get("R")]
    cal=[r for r in withR if r["anchor"]=="calendar"]
    def agg(sub,L):
        paid=sum(r["stats"][str(L)]["paid"] for r in sub); edge=sum(r["stats"][str(L)]["edge"] for r in sub)
        npr=sum(r["stats"][str(L)]["n"] for r in sub); hit=sum(1 for r in sub if r["stats"][str(L)]["n"]>0)
        return paid,edge,npr,hit
    # scanned events are the most recent N; scale by events/month actually listed
    for L in (0,5):
        for tier,sub in (("calendar",cal),("onset",[r for r in withR if r["anchor"]=="onset"])):
            if not sub: continue
            paid,edge,npr,hit=agg(sub,L)
            pe=paid/len(sub); ee=edge/len(sub)
            # per-event mean over ALL scanned events with R of this tier; monthly rate = events/month * fraction of events in this tier
            frac=len(sub)/n
            pm=per_month.get(f,0)
            rows.append(dict(family=f,tier=tier,L=L,scanned=n,with_jump=len(withR),tier_n=len(sub),events_per_month=round(pm,1),
                prints=npr,events_with_print=hit,paid_per_event=round(pe,1),edge_per_event=round(ee,2),
                month_paid=round(pe*pm*frac,0),month_edge=round(ee*pm*frac,1),day_edge=round(ee*pm*frac/30,2)))
rows.sort(key=lambda r:(-r["month_edge"]))
json.dump(rows,open("agg.json","w"),indent=1)
print("fam tier L scanned jumps tier_n ev/mo prints evHit paid/ev edge/ev month$paid month$edge day$edge")
for r in rows:
    if r["L"]==0: print(*[r[k] for k in ("family","tier","L","scanned","with_jump","tier_n","events_per_month","prints","events_with_print","paid_per_event","edge_per_event","month_paid","month_edge","day_edge")])
print()
for r in rows:
    if r["L"]==5: print(r["family"],r["tier"],"L5 prints",r["prints"],"edge/ev",r["edge_per_event"],"day",r["day_edge"])
