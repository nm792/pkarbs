"""Snapshot every Polymarket gas event (series us-gas-price-daily, gas-price-hits-weekly, gas-price-hits) with all trades (data-api v2). Public data, no orders. Needs raw/series_<slug>.json from gamma /series?slug=."""
import json, urllib.request, time, sys
def get(u):
    for i in range(4):
        try:
            return json.load(urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent":"research-client"}), timeout=30))
        except Exception as ex:
            err=ex; time.sleep(2*(i+1))
    raise err
out={}
for s in ["us-gas-price-daily","gas-price-hits-weekly","gas-price-hits"]:
    ser=json.load(open(f"raw/series_{s}.json"))[0]
    for e in ser["events"]:
        ev=get(f"https://gamma-api.polymarket.com/events?slug={e['slug']}")[0]
        ev["_series"]=s
        for m in ev["markets"]:
            trades=[]; cur=None
            for _ in range(200):
                u=f"https://data-api.polymarket.com/v2/trades?condition={m['conditionId']}&limit=500"+(f"&cursor={cur}" if cur else "")
                d=get(u)
                trades+=[{k:z[k] for k in ("side","token_id","size","price","timestamp","outcome_index","proxy_wallet")} for z in d["data"]]
                cur=d["pagination"].get("next_cursor")
                if not d["pagination"].get("has_more") or not cur: break
            m["_trades"]=trades
        out[e["slug"]]=ev
        print(s, e["slug"], len(ev["markets"]), sum(len(m["_trades"]) for m in ev["markets"]), flush=True)
json.dump(out, open("raw/events_trades.json","w"))  # then gzip to raw/events_trades-<stamp>.json.gz
