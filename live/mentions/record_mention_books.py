"""Record order books for NEW mention markets on Kalshi and Polymarket during their first 3 hours.
Run every 5 minutes (cron). One process, read-only public endpoints, no keys, no orders.
  python3 record_mention_books.py OUTDIR
Writes OUTDIR/books_YYYYMMDD.jsonl.gz, one line per market per snapshot:
 {t, venue, event, market, word, open_time, age_s, book}  book = raw bids/asks as returned."""
import json,sys,os,time,gzip,re,datetime as dt,urllib.request
KALSHI='https://api.elections.kalshi.com/trade-api/v2/'
SERIES=['KXTRUMPMENTION','KXTRUMPMENTIONB','KXTRUMPSAY','KXVANCEMENTION','KXNFLMENTION','KXNBAMENTION','KXWCMENTION','KXMAMDANIMENTION','KXBERNIEMENTION','KXSECPRESSMENTION']
WINDOW=3*3600
def get(u):
    for a in range(3):
        try:return json.load(urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'x'}),timeout=30))
        except Exception as e:
            if hasattr(e,'code') and e.code in(400,404):return None
            time.sleep(1+a)
def ts(s):
    s=s.replace(' ','T').replace('Z','+00:00')
    if re.search(r'[+-]\d\d$',s):s+=':00'
    return dt.datetime.fromisoformat(s).timestamp()
def young(open_time,now):
    try:age=now-ts(open_time)
    except Exception:return None
    return age if 0<=age<=WINDOW else None
def kalshi_targets(now):
    out=[]
    for s in SERIES:
        r=get(f'{KALSHI}markets?series_ticker={s}&status=open&limit=1000')
        for m in (r or {}).get('markets',[]):
            age=young(m.get('open_time') or '',now)
            if age is not None:out.append(dict(venue='kalshi',event=m['event_ticker'],market=m['ticker'],word=m.get('yes_sub_title'),open_time=m['open_time'],age_s=int(age),url=f"{KALSHI}markets/{m['ticker']}/orderbook"))
    return out
def pm_targets(now):
    out=[];r=get('https://gamma-api.polymarket.com/events?tag_slug=mention-markets&closed=false&limit=100&order=startDate&ascending=false') or []
    for e in r:
        for m in e.get('markets',[]):
            st=m.get('startDate') or e.get('startDate') or ''
            age=young(st,now)
            if age is None or not m.get('acceptingOrders'):continue
            try:tok=json.loads(m['clobTokenIds'])[0]
            except Exception:continue
            out.append(dict(venue='polymarket',event=e['slug'],market=m['conditionId'],word=m.get('groupItemTitle'),open_time=st,age_s=int(age),url=f'https://clob.polymarket.com/book?token_id={tok}'))
    return out
def main(outdir):
    os.makedirs(outdir,exist_ok=True);now=time.time()
    T=kalshi_targets(now)+pm_targets(now);n=0
    fn=os.path.join(outdir,'books_'+dt.datetime.utcnow().strftime('%Y%m%d')+'.jsonl.gz')
    with gzip.open(fn,'at') as f:
        for t in T:
            b=get(t['url'])
            if b is None:continue
            f.write(json.dumps(dict(t=int(time.time()),venue=t['venue'],event=t['event'],market=t['market'],word=t['word'],open_time=t['open_time'],age_s=t['age_s'],book=b))+'\n');n+=1
            time.sleep(0.15)
    print(json.dumps({'ev':'done','targets':len(T),'books':n,'file':fn}))
if __name__=='__main__':main(sys.argv[1] if len(sys.argv)>1 else 'out')
