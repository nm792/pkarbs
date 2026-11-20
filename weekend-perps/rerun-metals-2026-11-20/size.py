# Stack-layer sizing. All inputs cited; ESTIMATE, not a measured P&L.
# signals/week: RESULT-metals-brent-oos-2026-11-16.md capacity section (discovery rates). book capacity within 5 bp per side: same file (live l2Book 16 Nov ~15:30Z).
# net bp: out/rerun_fee0.9.txt (disc1 = 1h discovery, held = held-out 4h).
rate={"SILVER":0.4,"COPPER":0.4,"PLATINUM":0.3,"BRENTOIL":0.7}
cap={"SILVER":1.0e6,"COPPER":18e3,"PLATINUM":20e3,"BRENTOIL":340e3}   # low end of stated range
net={"disc1":{"SILVER":26.3,"COPPER":38.6,"PLATINUM":34.2,"BRENTOIL":3.3},
     "held":{"SILVER":-29.2,"COPPER":87.2,"PLATINUM":0.5,"BRENTOIL":41.9}}
for label,size in (("book capacity (5 bp impact)",None),("$20k per trade (flat)",20e3),("$100k per trade, capped at book",1e5)):
    for smp in ("disc1","held"):
        tot=0;rows=[]
        for s in rate:
            sz=cap[s] if size is None else min(size,cap[s]) if size!=20e3 else min(size,cap[s])
            d=rate[s]*sz*net[smp][s]/1e4/7
            rows.append(f"{s}:{d:6.2f}");tot+=d
        print(f"{label:34s} {smp:5s} total ${tot:7.2f}/day  "+" ".join(rows))
# metals only (ex Brent)
