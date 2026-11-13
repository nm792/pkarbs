import json,sys,collections,datetime as dt,statistics as S,re,subprocess,os,concurrent.futures as cf
sys.path.insert(0,'.')
from lockstat import lockstat
from math import log
SER=['KXVANCEMENTION','KXNFLMENTION','KXNBAMENTION','KXWCMENTION','KXMAMDANIMENTION','KXBERNIEMENTION','KXSECPRESSMENTION','KXTRUMPMENTIONB','KXTRUMPSAY']
def ts(s):return dt.datetime.fromisoformat(s.replace('Z','+00:00')).timestamp()
def norm(s):return re.sub(r'[^a-z]','',s.lower())
def prep(s):
    if not os.path.exists(f'mm_{s}_markets.json'):subprocess.run(['python3','-I','gas_pull.py',s,f'mm_{s}_markets.json'],check=True)
    if not os.path.exists(f'mm_{s}_trades.json'):
        src=open('tm_trades.py').read().replace("tm_markets.json",f"mm_{s}_markets.json").replace("tm_trades.json",f"mm_{s}_trades.json")
        open(f'_tmp_{s}.py','w').write(src);subprocess.run(['python3','-I',f'_tmp_{s}.py'],check=True,stdout=subprocess.DEVNULL)
def run(s,thr,freeze_ts,alpha=2.0,pmin=.05,pmax=.95):
    M=json.load(open(f'mm_{s}_markets.json'));TR=json.load(open(f'mm_{s}_trades.json'))
    ev=collections.defaultdict(list)
    for m in M:
        if m['result'] in('yes','no'):ev[m['event_ticker']].append(m)
    order=sorted(ev,key=lambda t:min(ts(x['open_time']) for x in ev[t]))
    hist=collections.defaultdict(lambda:[0,0]);U=[];LS=[]
    for i,et in enumerate(order):
        ms=ev[et];t0=min(ts(x['open_time']) for x in ms);t1=t0+3600
        if t0>=freeze_ts:
            fills=[];cand=[]
            gp=sum(h[1] for h in hist.values())/max(1,sum(h[0] for h in hist.values()))
            for m in ms:
                w=1 if m['result']=='yes' else 0;h=hist[norm(m['yes_sub_title'])]
                q=(h[1]+alpha*gp)/(h[0]+alpha)
                pr=[(ts(c[0]),c) for c in TR.get(m['ticker'],[]) if t0<=ts(c[0])<=t1 and c[4]>0]
                if pr:
                    mk=min(pr,key=lambda x:x[0])[1][2];mk=min(max(mk,.01),.99);qq=min(max(q,.01),.99)
                    LS.append((w*log(qq)+(1-w)*log(1-qq))-(w*log(mk)+(1-w)*log(1-mk)))
                for tt,c in pr:
                    oi,p=(0,c[2]) if c[1]=='yes' else (1,c[3])
                    if not(pmin<=p<=pmax):continue
                    fills.append((oi,p,c[4],w))
                    edge=(q-p) if oi==0 else ((1-q)-p)
                    if edge>=thr:cand.append((tt,oi,p,c[4],w))
            bet=None
            if cand:
                tt,oi,p,cnt,w=min(cand);bet=dict(oi=oi,p=p,sz=cnt,w=w)
            U.append(dict(id=s+et,bet=bet,fills=fills,cluster=dt.datetime.fromtimestamp(t0).strftime('%Y-%m')))
        for m in ms:
            h=hist[norm(m['yes_sub_title'])];h[0]+=1;h[1]+=1 if m['result']=='yes' else 0
    return U,LS,len(order)

FREEZE='2026-11-10T15:00:00+00:00'   # rule frozen; events opened at or after this are the forward sample
if __name__=='__main__':
    import math
    thr=.03;fz=ts(FREEZE) if len(sys.argv)<2 else ts(sys.argv[1])
    allU=[];allLS=[]
    ALL=SER+['KXTRUMPMENTION']
    with cf.ThreadPoolExecutor(3) as ex:list(ex.map(prep,ALL))
    for s in ALL:
        U,LS,n=run(s,thr,fz);allU+=U;allLS+=LS
        lockstat(U,f'{s} forward 3c',nvar=1)
    lockstat(allU,'POOLED forward 3c',nvar=1,logscore=(round(S.mean(allLS),4),round(S.mean(allLS)/S.stdev(allLS)*len(allLS)**.5,2),len(allLS)) if len(allLS)>2 else None)
    bets=[u['bet'] for u in allU if u['bet']]
    fee=sum(math.ceil(100*0.07*b['sz']*b['p']*(1-b['p'])-1e-9)/100 for b in bets)
    print('events scored',len(allU),'bets',len(bets),'taker fees $',round(fee,2))
