# Reconciles pulled trades with gamma per-event volume; volume trend and timing. Inputs data/, rows.json.
import json,gzip,statistics as st,collections
ev=json.load(open("data/events.json")); rows={r["date"]:r for r in json.load(open("rows.json"))}
lines=["date\tn_trades\tshares_pulled\tgamma_volume\tratio\tusd_notional\tusd_before_T-60\tusd_T-60_to_T\tusd_after_T\tusd_at_price_0.05-0.95_T-60_to_T"]
mon=collections.defaultdict(lambda:[0,0,0,0])
for e in ev:
    tr=json.load(gzip.open(f"data/trades_{e['date']}.json.gz"))
    sh=sum(t["size"] for t in tr); usd=sum(t["size"]*t["price"] for t in tr); g=float(e["volume"] or 0)
    r=rows.get(e["date"]); a=b=c=m=0
    if r:
        T=r["T"]/1000
        for t in tr:
            x=t["size"]*t["price"]
            if t["timestamp"]<T-3600: a+=x
            elif t["timestamp"]<=T:
                b+=x
                if 0.05<=t["price"]<=0.95: m+=x
            else: c+=x
    lines.append(f"{e['date']}\t{len(tr)}\t{sh:.0f}\t{g:.0f}\t{(sh/g if g else 0):.4f}\t{usd:.0f}\t{a:.0f}\t{b:.0f}\t{c:.0f}\t{m:.0f}")
    k=e["date"][:7]; mon[k][0]+=1; mon[k][1]+=usd; mon[k][2]+=b; mon[k][3]+=g
open("reconcile.tsv","w").write("\n".join(lines)+"\n")
print("month\tevents\tusd_notional_per_event\tusd_T-60_to_T_per_event\tgamma_shares_per_event")
for k in sorted(mon): n,u,b,g=mon[k]; print(f"{k}\t{n}\t{u/n:.0f}\t{b/n:.0f}\t{g/n:.0f}")
