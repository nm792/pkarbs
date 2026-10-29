import json
A=json.load(open("act7d.json")); M=json.load(open("mt.json"))
tk=M["true"]; lo=min(r["timestamp"] for r in tk); hi=max(r["timestamp"] for r in tk)
act=[r for r in A if r["type"]=="TRADE" and lo<=r["timestamp"]<=hi]
tu=sum(r["size"]*r["price"] for r in tk); au=sum(r["usdcSize"] for r in act)
print("window h %.1f taker fills %d usdc %.0f ; all activity fills %d usdc %.0f ; taker share usdc %.1f%%"%((hi-lo)/3600,len(tk),tu,len(act),au,100*tu/au))
