"""Forward test ARM 2 scorer (pre-registered 11 Nov 2026, see PREREG-forward-arm2-2026-11-11.md).
Every Kalshi Mentions-category series except the 10 arm-1 series; same frozen 3c rule; eligibility is decided mechanically per event
(>=10 earlier resolved events in the series that had settled before this event opened). Uses exponential backoff on HTTP 429.
Usage: python3 mm_forward2.py            # score (prints P&L stats)
       python3 mm_forward2.py --count    # events/eligibility counts only, no P&L"""
import json,sys,time,math,re,datetime as dt,collections,statistics as S,urllib.request,urllib.error,concurrent.futures as cf
from math import log,sqrt,erf
B='https://api.elections.kalshi.com/trade-api/v2/'
FREEZE=dt.datetime(2026,11,11,10,0,tzinfo=dt.timezone.utc).timestamp()   # events opened at or after this
ARM1={'KXVANCEMENTION','KXNFLMENTION','KXNBAMENTION','KXWCMENTION','KXMAMDANIMENTION','KXBERNIEMENTION','KXSECPRESSMENTION','KXTRUMPMENTIONB','KXTRUMPSAY','KXTRUMPMENTION'}
THR=.03;ALPHA=2.0;PMIN=.05;PMAX=.95;MIN_HIST=10;MIN_MARKETS=3;WINDOW=3600
def ts(s):return dt.datetime.fromisoformat(s.replace('Z','+00:00')).timestamp()
def norm(s):return re.sub(r'[^a-z]','',(s or '').lower())
def g(u):
    for a in range(9):
        try:return json.load(urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'x'}),timeout=60))
        except urllib.error.HTTPError as e:
            if e.code in(400,404):return None
            time.sleep(min(60,2**a)+(int(e.headers.get('Retry-After',0)) if e.code==429 else 0))
        except Exception:time.sleep(min(30,2**a))
    raise RuntimeError('gave up '+u)
def pull_series(s):
    out={}
    for base in('markets','historical/markets'):
        cur=None
        while True:
            r=g(f"{B}{base}?series_ticker={s}&limit=1000"+(f'&cursor={cur}' if cur else ''))
            if not r:break
            for m in r.get('markets',[]):out[m['ticker']]=m
            cur=r.get('cursor')
            if not cur:break
    return s,list(out.values())
def trades(m):
    o=int(ts(m['open_time']));out=[]
    for base in('markets/trades','historical/trades'):
        cur=None
        for _ in range(10):
            r=g(f"{B}{base}?ticker={m['ticker']}&min_ts={o}&max_ts={o+WINDOW}&limit=1000"+(f'&cursor={cur}' if cur else ''))
            if not r:break
            out+=[(ts(x['created_time']),x['taker_side'],float(x['yes_price_dollars']),float(x['no_price_dollars']),float(x['count_fp'])) for x in r.get('trades',[])]
            cur=r.get('cursor')
            if not cur:break
        if out:break
    return sorted(out)
def fee(p,sz):return math.ceil(100*0.07*sz*p*(1-p)-1e-9)/100
def tstat(v):
    if len(v)<3:return 0.0
    sd=S.stdev(v);return 0.0 if sd==0 else S.mean(v)/sd*sqrt(len(v))
def main():
    count_only='--count' in sys.argv
    ser=[s['ticker'] for s in g(B+'series?category=Mentions')['series']];ser=sorted(set(ser)-ARM1)
    with cf.ThreadPoolExecutor(6) as ex:data=dict(ex.map(pull_series,ser))
    units=[];ne=0;nelig=0;npend=0;stats=collections.Counter()
    for s,ms in data.items():
        ev=collections.defaultdict(list)
        for m in ms:ev[m['event_ticker']].append(m)
        E=[]
        for et,L in ev.items():
            res=all(m['result'] in('yes','no') for m in L)
            E.append(dict(et=et,L=L,t0=min(ts(m['open_time']) for m in L),res=res and len(L)>=MIN_MARKETS,
                K=max(min(ts(m['close_time']),ts(m['settlement_ts']) if m.get('settlement_ts') else 9e18) for m in L)))
        for e in E:
            if e['t0']<FREEZE or len(e['L'])<MIN_MARKETS:continue
            ne+=1
            if not e['res']:npend+=1;continue
            hist=[h for h in E if h['res'] and h['K']<e['t0']]
            if len(hist)<MIN_HIST:continue
            nelig+=1;stats[s]+=1
            if count_only:continue
            wh=collections.defaultdict(lambda:[0,0]);tot=[0,0]
            for h in hist:
                for m in h['L']:
                    k=wh[norm(m['yes_sub_title'])];k[0]+=1;k[1]+=1 if m['result']=='yes' else 0;tot[0]+=1;tot[1]+=1 if m['result']=='yes' else 0
            gp=tot[1]/tot[0];fills=[];cand=[];LS=[]
            for m in e['L']:
                w=1 if m['result']=='yes' else 0;h=wh[norm(m['yes_sub_title'])];q=(h[1]+ALPHA*gp)/(h[0]+ALPHA)
                pr=[x for x in trades(m) if e['t0']<=x[0]<=e['t0']+WINDOW and x[4]>0]
                if pr:
                    mk=min(max(pr[0][2],.01),.99);qq=min(max(q,.01),.99)
                    LS.append((w*log(qq)+(1-w)*log(1-qq))-(w*log(mk)+(1-w)*log(1-mk)))
                for (t,side,yp,np_,sz) in pr:
                    oi,p=(0,yp) if side=='yes' else (1,np_)
                    if not(PMIN<=p<=PMAX):continue
                    fills.append((oi,p,sz,w));edge=(q-p) if oi==0 else ((1-q)-p)
                    if edge>=THR:cand.append((t,oi,p,sz,w))
            bet=None
            if cand:t,oi,p,sz,w=min(cand);bet=dict(oi=oi,p=p,sz=sz,w=w)
            units.append(dict(id=e['et'],s=s,bet=bet,fills=fills,LS=LS,wk=dt.datetime.fromtimestamp(e['t0']).strftime('%G-%V')))
    print(f'forward events (open >= freeze, >={MIN_MARKETS} markets): {ne}; unresolved {npend}; eligible+resolved {nelig}; series with scored events {len(stats)}')
    if count_only:return
    pnl=lambda b:((b['w'] if b['oi']==0 else 1-b['w'])-b['p'])*b['sz']
    bets=[u for u in units if u['bet']];print('events with a bet',len(bets))
    if not bets:return
    real=[pnl(u['bet']) for u in bets];fees=sum(fee(u['bet']['p'],u['bet']['sz']) for u in bets);tot=sum(real)
    d=[]
    for u in bets:
        b=u['bet'];f=[x for x in u['fills'] if x[0]==b['oi']]
        if f:d.append(pnl(b)-S.mean(((x[3] if x[0]==0 else 1-x[3])-x[1])*b['sz'] for x in f))
    cl=collections.defaultdict(float)
    for u in units:cl[u['wk']]+=pnl(u['bet']) if u['bet'] else 0
    srt=sorted(real,reverse=True);top3=sum(srt[:3])
    LS=[x for u in units for x in u['LS']]
    t_p=tstat(d);t_c=tstat(list(cl.values()));ls=S.mean(LS) if LS else float('nan')
    net=tot-fees
    print(f'gross ${tot:.2f} fees ${fees:.2f} net ${net:.2f} on stake ${sum(u["bet"]["p"]*u["bet"]["sz"] for u in bets):.2f}; paired t vs same-side placebo {t_p:.2f}; cluster(week) t {t_c:.2f}; top3 share {top3/tot if tot>0 else float("nan"):.2f}; log score vs first print {ls:.4f}')
    n=len(bets)
    if n>=100:
        if net>0 and t_p>=2 and ls>0 and tot>0 and top3<.5*tot and t_c>1.5:print('DECISION: PASS')
        elif net<=0 or (ls<0 and t_p<1):print('DECISION: FAIL')
        else:print('DECISION: UNKNOWN, continue to 200')
    else:print(f'DECISION: not yet ({n}/100 events with a bet)')
if __name__=='__main__':main()
