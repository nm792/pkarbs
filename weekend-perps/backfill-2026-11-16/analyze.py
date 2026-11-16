import json,gzip,datetime,random,math,sys,statistics as st
D="/tmp/wp/data/"
COINS=["JP225","SP500","XYZ100","NVDA","SNDK","MU","AMD","GOOGL"]
HOUR=3600000
def load(p): return json.load(gzip.open(p,"rt"))
def iso(t): return datetime.datetime.fromtimestamp(t,datetime.UTC)
rows=[];skipped={"holiday_or_nonstandard":0,"no_candle":0,"no_perp_history":0}
funding_by={};h1_by={}
for c in COINS:
    hl=load(D+f"hl_{c}.json.gz")
    h1_by[c]={x["t"]:x for x in hl["h1"]}
    funding_by[c]=[(x["time"],float(x["fundingRate"])) for x in hl["funding"]]
    y=load(D+f"yahoo_{c}.json.gz")
    ts=y["timestamp"];q=y["indicators"]["quote"][0]
    bars=[(ts[i],q["open"][i],q["close"][i]) for i in range(len(ts)) if q["open"][i] is not None]
    first_h1=min(h1_by[c]) if h1_by[c] else None
    for i in range(1,len(bars)):
        t0,o0,c0=bars[i-1];t1,o1,c1=bars[i]
        d0=iso(t0).date();d1=iso(t1).date()
        if d1.weekday()!=0: continue          # Monday open bar only
        if (d1-d0).days!=3 or d0.weekday()!=4:
            skipped["holiday_or_nonstandard"]+=1;continue
        if c0 is None: continue
        T=t1*1000                              # Monday bar timestamp = official open
        if first_h1 is None or T-HOUR*2<first_h1:
            skipped["no_perp_history"]+=1;continue
        cs=(T-1800000)//HOUR*HOUR-HOUR         # start of last 1h candle ending <= T-30min
        cd=h1_by[c].get(cs)
        if cd is None or cd["o"] is None:
            skipped["no_candle"]+=1;continue
        P=float(cd["c"]);F=c0;O=o1
        fri_close_ms=calendar_ms=int(datetime.datetime(d0.year,d0.month,d0.day,21,0,tzinfo=datetime.UTC).timestamp()*1000)
        fsum=sum(r for tt,r in funding_by[c] if fri_close_ms<=tt<T)
        rows.append(dict(sym=c,monday=str(d1),T=T,F=F,open=O,P=P,
            S=(P-F)/F*1e4,O=(O-F)/F*1e4,fund_bp=fsum*1e4,n_trades=cd.get("n")))
json.dump(rows,open("/tmp/wp/rows.json","w"))
rnd=random.Random(1)
sgn=lambda x:(x>0)-(x<0)
def metrics(sel):
    n=len(sel)
    hit=[1 if (sgn(r["S"])==sgn(r["O"]) and r["O"]!=0) else 0 for r in sel]
    C=[sgn(r["S"])*r["O"] for r in sel]
    C2=[sgn(r["S"])*(r["O"]-r["S"]) for r in sel]
    hurdle=[12+sgn(r["S"])*r["fund_bp"] for r in sel]
    return hit,C,C2,hurdle
def binom_p(k,n,p=0.5):  # one-sided P(X>=k)
    return sum(math.comb(n,i)*p**i*(1-p)**(n-i) for i in range(k,n+1)) if n else float("nan")
out={"n_rows_all":len(rows),"skipped":skipped,"weekend_dates":sorted(set(r["monday"] for r in rows))}
for name,thr in (("primary",100),("secondary",50)):
    sel=[r for r in rows if abs(r["S"])>=thr]
    wk=sorted(set(r["monday"] for r in sel))
    hit,C,C2,hurdle=metrics(sel)
    n=len(sel);k=sum(hit)
    res={"threshold_bp":thr,"n_signals":n,"n_weekends_with_signal":len(wk),"hits":k,"hit_rate":k/n if n else None,"binom_p_one_sided_pooled":binom_p(k,n)}
    if n:
        by_w={}
        for r,h in zip(sel,hit): by_w.setdefault(r["monday"],[]).append(h)
        keys=list(by_w);bs=[]
        for _ in range(10000):
            s=0;m=0
            for _ in keys:
                v=by_w[rnd.choice(keys)];s+=sum(v);m+=len(v)
            bs.append(s/m)
        bs.sort();res["hit_rate_ci95_weekend_bootstrap"]=[bs[249],bs[9749]]
        res["mean_C_bp"]=st.mean(C);res["median_C_bp"]=st.median(C)
        res["mean_C2_bp"]=st.mean(C2);res["median_C2_bp"]=st.median(C2)
        res["median_hurdle_bp"]=st.median(hurdle)
        res["mean_C_over_2x_median_hurdle"]=st.mean(C)>2*st.median(hurdle)
        pm=[]
        for _ in range(10000):
            s=[rnd.choice((-1,1))*r["O"] for r in sel] if False else None
            # shuffle signs within bucket
            signs=[sgn(r["S"]) for r in sel];rnd.shuffle(signs)
            pm.append(st.mean([sg*r["O"] for sg,r in zip(signs,sel)]))
        res["placebo_mean_C_bp"]=st.mean(pm);res["placebo_sd"]=st.pstdev(pm)
        res["placebo_z"]=(st.mean(C)-st.mean(pm))/st.pstdev(pm) if st.pstdev(pm)>0 else None
        res["metric2_median_absO_minus_absO_minus_S_bp"]=st.median([abs(r["O"]) for r in sel])-st.median([abs(r["O"]-r["S"]) for r in sel])
        wsum={w:sum(c for c,r in zip(C,sel) if r["monday"]==w) for w in wk}
        tot=sum(wsum.values());res["total_C_bp"]=tot
        res["max_weekend_share_of_total_C"]=(max(wsum.values())/tot) if tot>0 else None
        res["top3_weekend_share"]=(sum(sorted(wsum.values(),reverse=True)[:3])/tot) if tot>0 else None
        res["share_of_signal_rows_with_zero_trades_in_S_candle"]=sum(1 for r in sel if (r["n_trades"] or 0)==0)/n
        cells={}
        for r,h in zip(sel,hit): cells.setdefault(r["sym"],[0,0]);cells[r["sym"]][0]+=h;cells[r["sym"]][1]+=1
        ncell=2*len(COINS)
        res["by_symbol"]={s:{"hits":a,"n":b,"p_one_sided":binom_p(a,b),"flag_after_bonferroni":binom_p(a,b)<0.05/ncell} for s,(a,b) in cells.items()}
    out[name]=res
p=out["primary"]
chk={}
chk["weekends_with_signal>=20"]=p["n_weekends_with_signal"]>=20
chk["hit_rate>=0.70"]=bool(p["n_signals"]) and p["hit_rate"]>=0.70
chk["lower95>0.55"]=bool(p["n_signals"]) and p["hit_rate_ci95_weekend_bootstrap"][0]>0.55
chk["mean_C>2x_hurdle"]=bool(p["n_signals"]) and p["mean_C_over_2x_median_hurdle"]
chk["placebo_z>=2"]=bool(p["n_signals"]) and (p.get("placebo_z") or 0)>=2
chk["no_weekend>40%"]=bool(p["n_signals"]) and (p.get("max_weekend_share_of_total_C") is not None) and p["max_weekend_share_of_total_C"]<=0.40
out["pass_checks"]=chk
out["verdict"]="unknown (N too small)" if not chk["weekends_with_signal>=20"] else ("PASS (provisional, backfill)" if all(chk.values()) else "fail")
json.dump(out,open("/tmp/wp/result.json","w"),indent=1)
print(json.dumps(out,indent=1))
