"""Polymarket mention-markets forward scorer (frozen rule). Usage:
  python3 pm_forward.py [FREEZE_ISO]   # default 2026-11-10T15:00:00+00:00
Steps: enumerate closed events (tag mention-markets) via gamma, pull /v2/trades for events started at/after FREEZE,
score with the frozen per-word base rate (alpha=2, 5c..95c prices, first-hour BUY prints, hold to resolution) at edge 10c (primary) and 3c, 5c.
History for base rates = ALL earlier closed events in the same family. Needs lockstat.py next to it."""
import json,sys,re,time,collections,datetime as dt,statistics as S,urllib.request,concurrent.futures as cf,os
sys.path.insert(0,'.')
from lockstat import lockstat
from math import log
FREEZE=sys.argv[1] if len(sys.argv)>1 else '2026-11-10T15:00:00+00:00'
def g(u):
    for a in range(5):
        try:return json.load(urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'x'}),timeout=60))
        except Exception:time.sleep(2*(a+1))
def ts(s):
    s=s.replace(' ','T').replace('Z','+00:00')
    if re.search(r'[+-]\d\d$',s):s+=':00'
    return dt.datetime.fromisoformat(s).timestamp()
def norm(s):return re.sub(r'[^a-z]','',(s or '').lower())
def fam(e):
    t=(e.get('title') or '').lower()
    if 'trump' in t and 'week' in t:return 'trump-weekly'
    if 'trump' in t:return 'trump-event'
    if 'earnings' in t:return 'earnings-call'
    if 'nfl' in t or 'announcer' in t or 'nba' in t or 'game' in t:return 'sports-announcers'
    return 'other'
def start(e):return min((m.get('startDate') or e.get('startDate') or '') for m in e['markets'])
def ok(e):
    try:
        for m in e['markets']:
            if max(float(x) for x in json.loads(m['outcomePrices']))<.99:return False
    except Exception:return False
    return len(e['markets'])>=3
def enum():
    ev={};d=dt.date(2024,6,1)
    while d<dt.date.today()+dt.timedelta(days=2):
        e=d+dt.timedelta(days=15);off=0
        while True:
            r=g(f'https://gamma-api.polymarket.com/events?tag_slug=mention-markets&closed=true&end_date_min={d}&end_date_max={e}&limit=100&offset={off}')
            for x in r:ev[x['id']]=x
            if len(r)<100:break
            off+=100
        d=e
    return [e for e in ev.values() if ok(e)]
def pull(c):
    out=[];cur=None
    for _ in range(150):
        r=g(f"https://data-api.polymarket.com/v2/trades?condition={c}&limit=500"+(f'&cursor={cur}' if cur else ''))
        if r is None:return c,None
        out+=[(x['timestamp'],x['side'],x['price'],x['size'],x['outcome_index']) for x in r['data']]
        p=r['pagination']
        if not p.get('has_more'):break
        cur=p.get('next_cursor')
        if not cur:break
    return c,out
def res(m):return 1 if float(json.loads(m['outcomePrices'])[0])>.5 else 0
if __name__=='__main__':
    fz=ts(FREEZE);E=enum();print('events',len(E))
    fwd=[e for e in E if ts(start(e))>=fz];print('forward events',len(fwd))
    cond=[m['conditionId'] for e in fwd for m in e['markets']]
    with cf.ThreadPoolExecutor(10) as ex:TR=dict(ex.map(pull,cond))
    for thr in(.10,.03,.05):
        U=[];LS=[];byf=collections.defaultdict(list)
        for e in E:byf[fam(e)].append(e)
        for f,L in byf.items():
            L.sort(key=start);hist=collections.defaultdict(lambda:[0,0])
            for e in L:
                ms=e['markets'];t0=ts(start(e))
                if t0>=fz:
                    fills=[];cand=[]
                    tot=sum(h[0] for h in hist.values());gp=sum(h[1] for h in hist.values())/max(1,tot)
                    for m in ms:
                        w=res(m);h=hist[norm(m.get('groupItemTitle') or m['question'])];q=(h[1]+2*gp)/(h[0]+2)
                        pr=sorted([(t[0],t) for t in (TR.get(m['conditionId']) or []) if t0<=t[0]<=t0+3600 and t[1]=='BUY' and t[3]>0],key=lambda z:z[0])
                        if pr:
                            t=pr[0][1];mk=t[2] if t[4]==0 else 1-t[2];mk=min(max(mk,.01),.99);qq=min(max(q,.01),.99)
                            LS.append((w*log(qq)+(1-w)*log(1-qq))-(w*log(mk)+(1-w)*log(1-mk)))
                        for tt,t in pr:
                            oi,p=t[4],t[2]
                            if not(.05<=p<=.95):continue
                            fills.append((oi,p,t[3],w));edge=(q-p) if oi==0 else ((1-q)-p)
                            if edge>=thr:cand.append((tt,oi,p,t[3],w))
                    bet=None
                    if cand:
                        tt,oi,p,sz,w=min(cand);bet=dict(oi=oi,p=p,sz=sz,w=w)
                    U.append(dict(id=e['id'],bet=bet,fills=fills,cluster=dt.datetime.fromtimestamp(t0).strftime('%Y-%m')))
                for m in ms:
                    h=hist[norm(m.get('groupItemTitle') or m['question'])];h[0]+=1;h[1]+=res(m)
        ls=(round(S.mean(LS),4),round(S.mean(LS)/S.stdev(LS)*len(LS)**.5,2),len(LS)) if len(LS)>2 else None
        lockstat(U,f'PM forward thr={thr}',nvar=1,logscore=ls)
