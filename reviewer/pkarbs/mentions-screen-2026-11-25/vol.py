import json,urllib.request,collections,datetime as dt
H={"User-Agent":"Mozilla/5.0"}
def get(u): return json.load(urllib.request.urlopen(urllib.request.Request(u,headers=H),timeout=30))
ev=[];off=0
while True:
    r=get(f"https://gamma-api.polymarket.com/events?tag_slug=mention-markets&closed=true&end_date_min=2026-10-26T00:00:00Z&limit=50&offset={off}")
    if not r: break
    ev+=r; off+=50
    if off>3000: break
json.dump(ev,open("closed30.json","w"))
def fam(s):
    s=s.lower()
    for k,f in [("trump","Trump"),("announcer","Sports announcers"),("earnings","Earnings calls"),("powell","Fed/Powell"),("vance","Vance"),("leavitt","Press sec"),("musk","Musk"),("mrbeast","Creators"),("stream","Creators")]:
        if k in s: return f
    return "Other"
c=collections.defaultdict(lambda:[0,0.0])
for e in ev:
    f=fam(e["slug"]); c[f][0]+=1; c[f][1]+=float(e.get("volume") or 0)
tot=sum(v[1] for v in c.values())
print(len(ev),"events, total $",round(tot))
for f,(n,v) in sorted(c.items(),key=lambda x:-x[1][1]): print(f,n,round(v),f"{v/tot:.0%}")
for e in sorted(ev,key=lambda e:-float(e.get("volume") or 0))[:12]: print(round(float(e.get("volume") or 0)),e.get("endDate","")[:10],e["slug"][:70])
