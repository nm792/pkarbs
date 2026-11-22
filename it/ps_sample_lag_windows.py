import sys,json,gzip,glob,bisect,statistics as st
sys.path.insert(0,"it"); import ps_chart_samples as C
for f in sorted(glob.glob("scratch/ps_samples/ps_sample_*.jsonl.gz")):
    msgs=[json.loads(l) for l in gzip.open(f,"rt")]
    p0=next(m["payload"] for m in reversed(msgs) if m["payload"].get("home_team"))
    h,a=p0["home_team"]["team_name"],p0["away_team"]["team_name"]; t0,t1=msgs[0]["recv_ns"]/1e9,msgs[-1]["recv_ns"]/1e9
    ev=C.events(msgs); mk=C.find_markets(h,a,t0)
    for q,cid,o in mk:
        tr=[x for x in C.trades(cid) if t0-60<=x["timestamp"]<=t1+60 and x.get("outcome_index")==0]
        if len(tr)<30: continue
        tr.sort(key=lambda x:x["timestamp"]); ts=[x["timestamp"] for x in tr]; pr=[x["price"] for x in tr]
        def px(t):
            i=bisect.bisect_right(ts,t)-1; return pr[i] if i>=0 else None
        print("==",h,a,q[:60],"trades",len(tr),"span s",round(t1-t0))
        for kind in "TKB":
            E=[e for e in ev if e[1]==kind]
            win=[(-30,-15),(-15,0),(0,15),(15,30)]; out=[]
            for lo,hi in win:
                d=[abs(px(t+hi)-px(t+lo)) for t,_,_ in E if px(t+hi) is not None and px(t+lo) is not None]
                out.append(round(st.mean(d)*100,2) if d else None)
            base=[abs(px(t+15)-px(t)) for t in [t0+ (t1-t0)*i/200 for i in range(5,195)] if px(t) and px(t+15)]
            print(kind,"n",len(E),"mean |dP| cents by window",dict(zip(["-30:-15","-15:0","0:+15","+15:+30"],out)),"| random-time 15s mean",round(st.mean(base)*100,2))
