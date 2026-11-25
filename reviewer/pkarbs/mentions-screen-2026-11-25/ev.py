import json,urllib.request
H={"User-Agent":"Mozilla/5.0"}
def get(u): return json.load(urllib.request.urlopen(urllib.request.Request(u,headers=H),timeout=30))
ev=[];off=0
while True:
    r=get(f"https://gamma-api.polymarket.com/events?tag_slug=mention-markets&closed=false&limit=50&offset={off}")
    if not r: break
    ev+=r; off+=50
    if off>1000: break
json.dump(ev,open("open_events.json","w"))
print(len(ev))
tot=0
for e in sorted(ev,key=lambda e:-float(e.get("volume") or 0))[:15]:
    print(round(float(e.get("volume") or 0)), round(float(e.get("volume1mo") or 0)), len(e.get("markets",[])), e.get("endDate","")[:16], e["slug"][:60])
print("sum vol",round(sum(float(e.get("volume") or 0) for e in ev)),"sum 1mo",round(sum(float(e.get("volume1mo") or 0) for e in ev)))
