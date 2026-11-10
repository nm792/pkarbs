"""Per-company word-history model for earnings-call mention markets (Polymarket, resolved outcomes only; no transcripts).
Causal features at each event: company-word-threshold history (shrunk to global word-threshold rate), fitted on the first half of events (time order), frozen, tested on the second half."""
import sys,math,collections,statistics as S,numpy as np
import em_data as D
from lockstat import lockstat
def lg(p):p=min(max(p,.02),.98);return math.log(p/(1-p))
def sg(x):return 1/(1+math.exp(-x))
R=D.rows()
ends={}
for e in D.E:
    for m in e['markets']:ends[m['conditionId']]=D.ts(m.get('endDate') or e['endDate'])
ev=collections.defaultdict(list)
for r in R:ev[r['eid']].append(r)
order=sorted(ev,key=lambda i:ev[i][0]['t0'])
def endt(i):return max(ends[r['cond']] for r in ev[i])
# causal features
hist_cw=collections.defaultdict(list);hist_w=collections.defaultdict(list);hist_k=collections.defaultdict(list);hist_c=collections.defaultdict(list);allh=[]
done=[]  # (end time, rows) applied when t0 passes
pending=[]
for i in order:
    t0=ev[i][0]['t0']
    still=[]
    for (te,rows) in pending:
        if te<t0:
            for r in rows:
                hist_cw[(r['comp'],r['word'],r['k'])].append(r['y']);hist_w[(r['word'],r['k'])].append(r['y']);hist_k[r['k']].append(r['y']);hist_c[r['comp']].append(r['y']);allh.append(r['y'])
        else:still.append((te,rows))
    pending=still
    gp=(sum(allh)+1)/(len(allh)+2)
    for r in ev[i]:
        kk=hist_k[r['k']];pk=(sum(kk)+3*gp)/(len(kk)+3)
        hw=hist_w[(r['word'],r['k'])];pw=(sum(hw)+3*pk)/(len(hw)+3)
        hc=hist_c[r['comp']];pc=(sum(hc)+3*gp)/(len(hc)+3)
        h=hist_cw[(r['comp'],r['word'],r['k'])];n=len(h)
        qcw=(sum(h)+3*pw)/(n+3)
        r['f']=[lg(qcw),lg(pw),lg(pc),n];r['ncw']=n
    pending.append((endt(i),ev[i]))
half=len(order)//2;train=set(order[:half]);test=order[half:]
# fit logistic (ridge) on train rows with features [lg qcw, lg pw, lg pc]
def fit(X,y,l2=1.0,it=300):
    X=np.c_[np.ones(len(X)),X];w=np.zeros(X.shape[1])
    for _ in range(it):
        p=1/(1+np.exp(-X@w));g=X.T@(p-y)+l2*np.r_[0,w[1:]];H=(X.T*(p*(1-p)))@X+l2*np.eye(len(w));w-=np.linalg.solve(H,g)
    return w
tr=[r for i in order[:half] for r in ev[i]]
w=fit(np.array([r['f'][:3] for r in tr]),np.array([r['y'] for r in tr]))
print('train events',half,'test events',len(test),'weights',np.round(w,3))
def mq(r):return sg(w[0]+w[1]*r['f'][0]+w[2]*r['f'][1]+w[3]*r['f'][2])
def first_prints(r):
    e=ends[r['cond']];return [t for t in sorted(r['tr']) if t[1]=='BUY' and r['t0']<=t[0]<=e and t[4]>0]
# log score vs market first print (YES-price equivalent)
def yes_price(t):return t[3] if t[2]==0 else 1-t[3]
LS=[];LSbase=[];per=collections.defaultdict(list)
for i in test:
    for r in ev[i]:
        fp=[t for t in first_prints(r) if 0.03<=yes_price(t)<=0.97]
        if not fp:continue
        pm=min(max(yes_price(fp[0]),.01),.99);q=min(max(mq(r),.01),.99);y=r['y']
        d=(y*math.log(q)+(1-y)*math.log(1-q))-(y*math.log(pm)+(1-y)*math.log(1-pm));LS.append(d);per[i].append(d)
ec=[sum(v) for v in per.values()]
print('markets',len(LS),'mean log score model-market %.4f (market-level t %.2f; event-cluster t %.2f)'%(S.mean(LS),S.mean(LS)/S.stdev(LS)*len(LS)**.5,S.mean(ec)/S.stdev(ec)*len(ec)**.5))
# does history add to price?  y ~ logit(price)+logit(model)
rows=[(lg(yes_price([t for t in first_prints(r) if 0.03<=yes_price(t)<=0.97][0])),lg(mq(r)),r['y'],i) for i in test for r in ev[i] if [t for t in first_prints(r) if 0.03<=yes_price(t)<=0.97]]
X=np.array([[a,b] for a,b,_,_ in rows]);Y=np.array([c for _,_,c,_ in rows]);w2=fit(X,Y,l2=0.01);print('y~price+model (in-sample on test, descriptive): ',np.round(w2,3))
# fill test
def units(thr,pmin=.05,pmax=.95):
    U=[]
    for i in test:
        fills=[];cand=[]
        for r in ev[i]:
            q=mq(r);y=r['y'];seen=False
            for t in first_prints(r):
                oi=t[2];p=t[3]
                if not(pmin<=p<=pmax):continue
                fills.append((oi,p,t[4],y))
                if not seen:
                    seen=True;edge=(q-p) if oi==0 else ((1-q)-p)
                    if edge>=thr:cand.append((t[0],oi,p,t[4],y))
        bet=None
        if cand:
            tt,oi,p,sz,y=min(cand);bet=dict(oi=oi,p=p,sz=sz,w=y)
        U.append(dict(id=i,bet=bet,fills=fills,cluster=ev[i][0]['comp']))
    return U
for thr in(.03,.05,.10):
    lockstat(units(thr),f'EARN-HIST test thr={thr}',nvar=3,logscore=(round(S.mean(LS),4),round(S.mean(LS)/S.stdev(LS)*len(LS)**.5,2),len(LS)))

# ---- Variant 2: price + history, fitted on the first half's first-print prices, frozen
def fp0(r):
    f=[t for t in first_prints(r) if 0.03<=yes_price(t)<=0.97];return yes_price(f[0]) if f else None
tr2=[(r,fp0(r)) for i in order[:half] for r in ev[i] if fp0(r) is not None]
w3=fit(np.array([[lg(p),r['f'][0],r['f'][1]] for r,p in tr2]),np.array([r['y'] for r,p in tr2]),l2=1.0)
print('\nVARIANT 2 (price+history) train markets',len(tr2),'weights [b,price,cw,word]',np.round(w3,3))
def mq2(r):
    p=fp0(r);return sg(w3[0]+w3[1]*lg(p)+w3[2]*r['f'][0]+w3[3]*r['f'][1])
LS2=[];per2=collections.defaultdict(list)
for i in test:
    for r in ev[i]:
        p=fp0(r)
        if p is None:continue
        pm=min(max(p,.01),.99);q=min(max(mq2(r),.01),.99);y=r['y']
        d=(y*math.log(q)+(1-y)*math.log(1-q))-(y*math.log(pm)+(1-y)*math.log(1-pm));LS2.append(d);per2[i].append(d)
ec2=[sum(v) for v in per2.values()]
print('V2 markets',len(LS2),'mean log score minus market %.4f (market t %.2f; event-cluster t %.2f)'%(S.mean(LS2),S.mean(LS2)/S.stdev(LS2)*len(LS2)**.5,S.mean(ec2)/S.stdev(ec2)*len(ec2)**.5))
def units2(thr,pmin=.05,pmax=.95):
    U=[]
    for i in test:
        fills=[];cand=[]
        for r in ev[i]:
            if fp0(r) is None:continue
            y=r['y'];seen=False
            for t in first_prints(r):
                oi=t[2];p=t[3]
                if not(pmin<=p<=pmax):continue
                fills.append((oi,p,t[4],y))
                if not seen:
                    seen=True;q=mq2(r);edge=(q-p) if oi==0 else ((1-q)-p)
                    if edge>=thr:cand.append((t[0],oi,p,t[4],y))
        bet=None
        if cand:
            tt,oi,p,sz,y=min(cand);bet=dict(oi=oi,p=p,sz=sz,w=y)
        U.append(dict(id=i,bet=bet,fills=fills,cluster=ev[i][0]['comp']))
    return U
for thr in(.03,.05,.10):
    lockstat(units2(thr),f'EARN V2 test thr={thr}',nvar=6,logscore=(round(S.mean(LS2),4),round(S.mean(LS2)/S.stdev(LS2)*len(LS2)**.5,2),len(LS2)))
