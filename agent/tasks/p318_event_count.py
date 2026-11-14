import gzip, json, os, time, collections
D="/mnt/HC_Volume_107257520/pkarbs"
pay=os.path.join(D,"goalserve","esports_payloads")
files=[f for f in sorted(os.listdir(pay)) if f.endswith(".gz")]
matches={}; moves=0; rows=0; nonempty=0; scorech=0; per_file=collections.Counter()
prev={}
def ip(v):
    try: f=float(v)
    except Exception: return None
    if f<=0 or f>=1: return None
    return 1.0/f
for fn in files:
    with gzip.open(os.path.join(pay,fn),"rt",errors="replace") as fh:
        for line in fh:
            rows+=1
            try: r=json.loads(line)
            except Exception: continue
            b=r.get("body")
            if not b: continue
            try: b=json.loads(b)
            except Exception: continue
            evs=b.get("events") or {}
            if evs: nonempty+=1
            for mid,ev in evs.items():
                if not isinstance(ev,dict): continue
                m=matches.setdefault(mid,{"name":str(ev.get("t1"))+" v "+str(ev.get("t2")),"first":r["recv_ns"],"last":r["recv_ns"],"moves":0,"score":0})
                m["last"]=max(m["last"],r["recv_ns"]); m["first"]=min(m["first"],r["recv_ns"])
                for o in (ev.get("odds") or []):
                    v=o.get("v")
                    if v is None: continue
                    p=ip(v)
                    if p is None: continue
                    key=(mid,str(o.get("id")),str(o.get("nm")))
                    old=prev.get(key); prev[key]=p
                    if old is not None and abs(p-old)>=0.02:
                        moves+=1; m["moves"]+=1
                st=ev.get("st") or ev.get("score") or {}
                if isinstance(st,dict):
                    for k,v2 in st.items():
                        cur=json.dumps(v2,sort_keys=True) if isinstance(v2,(dict,list)) else v2
                        old=m.setdefault("_st",{}).get(k)
                        m["_st"][k]=cur
                        if old is not None and old!=cur:
                            scorech+=1; m["score"]+=1; per_file[fn]+=1
res={"files":files,"rows":rows,"rows_with_events":nonempty,"matches":len(matches),
     "odds_moves_ge2c":moves,"score_field_changes":scorech,"score_changes_per_file":dict(per_file),
     "per_match":{k:{"name":v["name"],"first":time.strftime("%Y-%m-%d %H:%M:%SZ",time.gmtime(v["first"]/1e9)),
                     "last":time.strftime("%Y-%m-%d %H:%M:%SZ",time.gmtime(v["last"]/1e9)),
                     "moves":v["moves"],"score_changes":v["score"]} for k,v in matches.items()}}
# pandascore
pk=collections.Counter(); pm={}
with gzip.open(os.path.join(D,"pandascore","events.jsonl.gz"),"rt",errors="replace") as fh:
    for line in fh:
        try: r=json.loads(line)
        except Exception: continue
        pk[r.get("kind")]+=1
        if r.get("kind")=="task_started" and r.get("match_id"):
            pm[r["match_id"]]={"label":r.get("label"),"slug":r.get("slug"),"opens_at":r.get("opens_at"),"first_seen":r.get("t")}
res["pandascore"]={"kinds":dict(pk),"matches":len(pm),"match_list":pm,
                   "state_events":sum(v for k,v in pk.items() if k in ("event","kill","round","round_score","score","alive"))}
json.dump(res,open("/tmp/p318-a.json","w"),indent=1,default=str)
print(json.dumps({k:v for k,v in res.items() if k not in("per_match","match_list")},indent=1))
print("matches:",json.dumps(res["per_match"],indent=1)[:1500])
print("ps match list:",json.dumps(res["pandascore"]["match_list"],indent=1)[:1200])
