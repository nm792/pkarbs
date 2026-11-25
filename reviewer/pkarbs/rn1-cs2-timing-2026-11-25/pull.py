import json,urllib.request,time,sys
U="0x2005d16a84ceefa912d4e380cd32e7ff827875ea"; T0=int(sys.argv[1]); out={}
for tk in ("true","false"):
    cur=None; n=0
    while True:
        url=f"https://data-api.polymarket.com/v2/trades?user={U}&limit=500&taker_only={tk}"+(f"&cursor={cur}" if cur else "")
        d=json.load(urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0"}),timeout=30))
        rows=d.get("data",[]); stop=False
        for r in rows:
            assert r["proxy_wallet"].lower()==U
            if r["timestamp"]<T0: stop=True; break
            out.setdefault(tk,[]).append(r)
        cur=(d.get("pagination") or {}).get("next_cursor"); n+=1
        if stop or not cur or not rows or n>200: break
json.dump(out,open("rn1_since.json","w"))
for tk,v in out.items():
    cs=[r for r in v if any(k in (r.get("event_slug") or r.get("slug") or "").lower() for k in ("cs2","counter-strike","csgo"))]
    print(tk,len(v),"cs2",len(cs))
    import collections; c=collections.Counter(time.strftime("%Y-%m-%d %HZ",time.gmtime(r["timestamp"])) for r in cs); print(sorted(c.items()))
    print(collections.Counter((r.get("event_slug") or "")[:40] for r in cs).most_common(8))
