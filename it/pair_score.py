import gzip,json,sys,bisect,collections,glob,os,io
FEE=0.05
def fee(p): return FEE*p*(1-p)
def lines(d):
    """books.jsonl.gz (old layout) or books-*.jsonl[.gz] hourly files (slim layout, pmcs2/pmdota/pm_mece_books); multi-member gzip ok."""
    for f in sorted(glob.glob(d+"/books*.jsonl*")):
        if f.endswith(".tmp"): continue
        try:
            h=gzip.open(f,"rt") if f.endswith(".gz") else open(f)
            for l in h: yield l
        except EOFError: pass
def load(d):
    mk={}
    mf=d+"/markets.jsonl.gz" if os.path.exists(d+"/markets.jsonl.gz") else d+"/markets.jsonl"
    for l in (gzip.open(mf,"rt") if mf.endswith(".gz") else open(mf)):
        try:r=json.loads(l)
        except:continue
        if len(r.get("tokens",[]))==2: mk[r["cond"]]=r
    tok2m={t:(c,i) for c,m in mk.items() for i,t in enumerate(m["tokens"])}
    ser=collections.defaultdict(lambda:[[],[]])  # cond -> per token list of (ms, asks, bids)
    for l in lines(d):
        try:r=json.loads(l)
        except:continue
        if r["asset"] not in tok2m: continue
        c,i=tok2m[r["asset"]]
        a=sorted((float(x["price"]),float(x["size"])) for x in r["asks"] if float(x["size"])>0)
        b=sorted(((float(x["price"]),float(x["size"])) for x in r["bids"] if float(x["size"])>0),reverse=True)
        ser[c][i].append((r["recv_ms"],a,b))
    return mk,ser
_c={}
def at(lst,t):
    ts=_c.get(id(lst))
    if ts is None: ts=_c[id(lst)]=[x[0] for x in lst]
    k=bisect.bisect_right(ts,t)-1
    return lst[k] if k>=0 else None
def walk_buy(aA,aB):
    # buy equal shares of both tokens walking asks; return (shares, net profit) maximizing profit while marginal >0
    iA=iB=0; ra=aA[0][1] if aA else 0; rb=aB[0][1] if aB else 0; sh=0; prof=0
    aA=[list(x) for x in aA]; aB=[list(x) for x in aB]
    while iA<len(aA) and iB<len(aB):
        pa,sa=aA[iA]; pb,sb=aB[iB]
        m=1-pa-pb-fee(pa)-fee(pb)
        if m<=0: break
        q=min(sa,sb); sh+=q; prof+=q*m; aA[iA][1]-=q; aB[iB][1]-=q
        if aA[iA][1]<=1e-9: iA+=1
        if aB[iB][1]<=1e-9: iB+=1
    return sh,prof
def walk_sell(bA,bB):  # mint $1 set, sell both at bids
    iA=iB=0; bA=[list(x) for x in bA]; bB=[list(x) for x in bB]; sh=0; prof=0
    while iA<len(bA) and iB<len(bB):
        pa,sa=bA[iA]; pb,sb=bB[iB]
        m=pa+pb-1-fee(pa)-fee(pb)
        if m<=0: break
        q=min(sa,sb); sh+=q; prof+=q*m; bA[iA][1]-=q; bB[iB][1]-=q
        if bA[iA][1]<=1e-9: iA+=1
        if bB[iB][1]<=1e-9: iB+=1
    return sh,prof
def run(d,delay):
    _c.clear(); mk,ser=load(d); out=[]; nm=0; nobs=0; mins=[]
    for c,(A,B) in ser.items():
        if not A or not B: continue
        nm+=1
        times=sorted(set([x[0] for x in A]+[x[0] for x in B]))
        for side in ("buy","sell"):
            last=None
            for t in times:
                a=at(A,t); b=at(B,t)
                if not a or not b: continue
                nobs+=1
                if side=="buy" and a[1] and b[1]: mins.append(a[1][0][0]+b[1][0][0])
                # detect at t, fill at t+delay
                da=at(A,t+delay); db=at(B,t+delay)
                if side=="buy":
                    det=a[1] and b[1] and 1-a[1][0][0]-b[1][0][0]-fee(a[1][0][0])-fee(b[1][0][0])>0
                else:
                    det=a[2] and b[2] and a[2][0][0]+b[2][0][0]-1-fee(a[2][0][0])-fee(b[2][0][0])>0
                if not det: continue
                if delay>0 and (not da or not db): continue
                f=walk_buy(da[1],db[1]) if side=="buy" else walk_sell(da[2],db[2])
                out.append((c,(mk[c].get("title") or mk[c].get("q") or c),side,t,f[0],f[1]))
    return nm,nobs,out,mins
if __name__=="__main__":
    for d in sys.argv[1:]:
        for delay in (0,1000):
            nm,nobs,out,mins=run(d,delay)
            runs=[]; 
            for o in out:   # collapse detections within 10 s per market/side into one run (max profit)
                if runs and runs[-1][0]==o[0] and runs[-1][2]==o[2] and o[3]-runs[-1][3]<10000:
                    if o[5]>runs[-1][5]: runs[-1]=o[:3]+(runs[-1][3],o[4],o[5])
                    else: runs[-1]=runs[-1][:3]+(o[3],)+runs[-1][4:]
                else: runs.append(o)
            pos=[r for r in runs if r[5]>0.0]
            print(d,"delay",delay,"mkts",nm,"obs",nobs,"min askA+askB",round(min(mins),4) if mins else None,"detections",len(out),"runs",len(runs),"net$",round(sum(r[5] for r in runs),2),"shares",round(sum(r[4] for r in runs),1))
            for r in sorted(runs,key=lambda r:-r[5])[:4]: print("   ",r[1][:40],r[2],r[3],round(r[4],1),round(r[5],2))
