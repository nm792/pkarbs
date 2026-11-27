import json, glob, sys, time, datetime as dt, collections, concurrent.futures as cf
from families import classify
import scan
MACRO={"fed_decision","ecb_boj_boe_bor","cpi_inflation","jobs_unemp","gdp","eggs_prices"}
NMAX=int(sys.argv[1]) if len(sys.argv)>1 else 40
ev={}
for f in glob.glob("events_*.json"):
    for e in json.load(open(f)): ev[e["id"]]=e
fam=collections.defaultdict(list)
for e in ev.values():
    f=classify(e["title"])
    if f and e["closed"] and e["markets"]: fam[f].append(e)
for f in fam: fam[f].sort(key=lambda e:e["end"] or "",reverse=True)
sel=[]
for f,l in fam.items():
    # exclude ambiguous non-scheduled macro titles (e.g. "BLS delays CPI", "how low will yield")
    if f in MACRO: sel+= [(f,e) for e in l[:max(NMAX,80)]]
    else: sel+=[(f,e) for e in l[:NMAX]]
print("events selected",len(sel),"markets",sum(len(e["markets"]) for _,e in sel),flush=True)
def do_event(fe):
    f,e=fe; res=dict(family=f,id=e["id"],title=e["title"],end=e["end"],n_mk=len(e["markets"]),err=0)
    mk=[]
    for m in sorted(e["markets"],key=lambda m:-float(m.get("vol") or 0))[:20]:
        w=scan.winner_token(m)
        if not w or not m.get("cid"): continue
        try: rows=scan.fetch_trades(m["cid"])
        except Exception as ex: res["err"]+=1; continue
        mk.append((m,w,rows))
    res["n_resolved_mk"]=len(mk)
    # jump time from winner-token series of YES-winning markets (clean jumps); fall back to all winners
    js=[]
    for m,w,rows in mk:
        s=[(r["ts"],r["p"]) for r in rows if r["tok"]==w]
        j=scan.jump_time(s) if s else None
        if j: js.append(j)
    if not js: res["R"]=None; return res
    j0=sorted(js)[len(js)//2]
    Rc=scan.snap(f,j0)
    res["j0"]=j0; res["lag"]=(j0-Rc) if Rc else None; res["R"]=Rc if Rc else j0; res["anchor"]="calendar" if Rc else "onset"
    R=res["R"]; res["stats"]={}
    allp={L:[] for L in scan.LS}
    for m,w,rows in mk:
        o=scan.scan_market(rows,w,R)
        for L in scan.LS: allp[L]+=o[L]
    for L in scan.LS:
        paid,edge=scan.day_cap(allp[L])
        res["stats"][L]=dict(n=len(allp[L]),paid=paid,edge=edge,raw_usd=sum(p*s for _,p,s in allp[L]))
    return res
t0=time.time(); out=[]
with cf.ThreadPoolExecutor(10) as ex:
    for i,r in enumerate(ex.map(do_event,sel)):
        out.append(r)
        if i%25==0: print(i,len(sel),round(time.time()-t0),flush=True); json.dump(out,open("scan_out.json","w"))
json.dump(out,open("scan_out.json","w")); print("done",round(time.time()-t0))
