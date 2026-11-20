# DATA PREP, NOT TESTED: pulls all six markets of every US gas event 16 Oct-19 Nov (Gamma + data-api /v2/trades) into all_markets.json (the tape the backtest reads).
import json,subprocess,datetime as dt,sys
from concurrent.futures import ThreadPoolExecutor
def get(u):
    for _ in range(3):
        o=subprocess.run(['curl','-s','--compressed','-m','30','-A','Mozilla/5.0',u],capture_output=True,text=True).stdout
        try: return json.loads(o)
        except: pass
def trades(cid):
    out=[];cur=None
    for _ in range(40):
        j=get(f"https://data-api.polymarket.com/v2/trades?conditionId={cid}&limit=500"+(f"&cursor={cur}" if cur else ""))
        if not j: break
        d=j['data'] if isinstance(j,dict) else j; out+=d
        cur=(j.get('pagination') or {}).get('next_cursor') if isinstance(j,dict) else None
        if not cur or not d: break
    return out
evs=[]
d=dt.date(2026,10,16)
while d<=dt.date(2026,11,19):
    s='us-gas-price-on-%s-%d-2026'%(d.strftime('%B').lower(),d.day)
    j=get('https://gamma-api.polymarket.com/events?slug='+s)
    if j: evs.append((d.isoformat(),j[0]))
    d+=dt.timedelta(1)
jobs=[(dd,m) for dd,e in evs for m in e['markets']]
def work(x):
    dd,m=x
    return dict(date=dd,q=m['question'],cid=m['conditionId'],created=m['createdAt'],tokens=json.loads(m['clobTokenIds']),tr=[(t['timestamp'],t['outcome'],t['side'],t['price'],t['size']) for t in trades(m['conditionId'])])
with ThreadPoolExecutor(4) as ex: res=list(ex.map(work,jobs))
json.dump(res,open('all_markets.json','w')); print(len(evs),len(res),sum(len(r['tr']) for r in res))
