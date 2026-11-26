import json,collections,glob,datetime as dt
from families import classify
out=json.load(open("scan_out.json"))
ev={}
for f in glob.glob("events_*.json"):
    for e in json.load(open(f)): ev[e["id"]]=e
now=dt.datetime(2026,11,26,tzinfo=dt.timezone.utc); pm=collections.Counter()
for e in ev.values():
    f=classify(e["title"])
    if f and e["closed"] and e["end"]:
        d=dt.datetime.fromisoformat(e["end"].replace("Z","+00:00"))
        if 0<=(now-d).days<=180: pm[f]+=1/6
by=collections.defaultdict(list)
for r in out: by[r["family"]].append(r)
rows=[]
for f,l in by.items():
    n=len(l)
    for tier in ("calendar","onset"):
        sub=[r for r in l if r.get("R") and r["anchor"]==tier]
        if not sub: continue
        mult=pm[f]*len(sub)/n/len(sub)   # = events/month * share of scanned events in tier, per tier-event
        d={}
        for L in ("0","2","5","15"):
            d[L]=sum(r["stats"][L]["edge"] for r in sub)*mult/30
        e5=sorted([r["stats"]["5"]["edge"] for r in sub],reverse=True); t5=sum(e5)
        rows.append(dict(f=f,tier=tier,n=n,ts=len(sub),ev_m=pm[f],hit=sum(1 for r in sub if r["stats"]["5"]["n"]>0),
            d=d,top1=(e5[0]/t5 if t5 else 0),paid5=sum(r["stats"]["5"]["paid"] for r in sub)/len(sub),
            prints5=sum(r["stats"]["5"]["n"] for r in sub)))
rows.sort(key=lambda r:-r["d"]["5"])
L=["| rank | family | R source | events/mo (listed, 180d) | scanned | tier events | with >=1 print at L=5 | prints L=5 | $ paid/event (cap $200/trade) | floor edge $/day L=0 | L=2 | **L=5** | L=15 | top event share | stack layer |","|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|"]
for i,r in enumerate(rows,1):
    d=r["d"]; stack=("YES" if (d["5"]>=1 and r["hit"]>=5 and r["top1"]<0.5) else ("UNPROVEN" if d["5"]>=0.3 else "no")) if r["tier"]=="calendar" else ("UNPROVEN (needs trigger source)" if d["5"]>=0.3 else "no")
    src="calendar clock (snap to scheduled time)" if r["tier"]=="calendar" else "ONSET (price jump; hindsight, NOT a floor)"
    L.append(f"| {i} | {r['f']} | {src} | {r['ev_m']:.1f} | {r['n']} | {r['ts']} | {r['hit']} | {r['prints5']} | {r['paid5']:.0f} | {d['0']:.1f} | {d['2']:.1f} | **{d['5']:.1f}** | {d['15']:.1f} | {r['top1']:.0%} | {stack} |")
open("TABLE.md","w").write("\n".join(L)); print("\n".join(L))
