import gzip,json,numpy as np,collections
rows=[json.loads(l) for l in gzip.open("sample.jsonl.gz","rt")]
by=collections.defaultdict(list)
for r in rows: by[(r["v"],r.get("d",""),r["s"])].append(r)
T0=rows[0]["t"];print("rows",len(rows),"span min",(rows[-1]["t"]-T0)/60)
print("sym | n | oracle moved? (std oracle bp) | med|mark-oracle| | max | share>=25 | longest>=25 (s) | reverted<5bp after >=25?")
res={}
for k,v in sorted(by.items()):
    mk=np.array([(x["mark"]/x["oracle"]-1)*1e4 for x in v]);orc=np.array([x["oracle"] for x in v]);ts=np.array([x["t"] for x in v])
    mid=np.array([(x["mid"]/x["oracle"]-1)*1e4 if x.get("mid") else np.nan for x in v])
    use=mid if not np.all(np.isnan(mid)) else mk
    ex=np.abs(use)>=25;best=0;st=None;rev=None
    for i,e in enumerate(ex):
        if e:
            if st is None: st=ts[i]
            best=max(best,ts[i]-st+5)
        else:
            if st is not None and abs(use[i])<5: rev=True
            st=None
    osd=float(np.std(np.diff(np.log(orc)))*1e4) if len(orc)>2 else 0
    res["/".join(k)]=dict(n=len(v),med=float(np.nanmedian(np.abs(use))),mx=float(np.nanmax(np.abs(use))),share=float(ex.mean()),run=float(best),oracle_changes=int((np.diff(orc)!=0).sum()),using="mid" if use is mid else "mark")
    print(k,len(v),"oracle changes",int((np.diff(orc)!=0).sum()),"| med",round(res["/".join(k)]["med"],1),"max",round(res["/".join(k)]["mx"],1),"share>=25",round(float(ex.mean()),2),"longest",round(best),"s")
json.dump(res,open("sample_result.json","w"),indent=1)
