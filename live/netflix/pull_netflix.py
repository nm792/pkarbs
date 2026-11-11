#!/usr/bin/env python3
"""Read-only pull for the Netflix test: (1) Netflix per-country weekly top 10, United States rows only;
(2) Kalshi trade history for the Netflix weekly series. Streams, single process, small output.
Usage: pull_netflix.py OUTDIR"""
import sys,os,json,gzip,time,urllib.request,urllib.parse,csv,io
UA={'User-Agent':'pkarbs-research/1.0'}
KALSHI='https://api.elections.kalshi.com/trade-api/v2'
SERIES=['KXNETFLIXRANKMOVIE','KXNETFLIXRANKSHOW','KXNETFLIXRANKMOVIERUNNERUP','KXNETFLIXRANKSHOWRUNNERUP',
 'KXNETFLIXRANKMOVIEGLOBAL','KXNETFLIXRANKSHOWGLOBAL','KXNETFLIXRANKMOVIEGLOBAL2','KXNETFLIXRANKSHOWGLOBAL2',
 'KXNETFLIXTOPVIEWSTV','KXNETFLIXTOPVIEWSMOVIE']
def get(url,tries=5):
    for a in range(tries):
        try: return urllib.request.urlopen(urllib.request.Request(url,headers=UA),timeout=60)
        except Exception as e:
            err=e; time.sleep(2+3*a)
    raise err
def us_rows(lines,country='United States'):
    """lines: iterable of str (TSV with header). Yields header then rows whose country_name==country."""
    it=iter(lines); head=next(it).rstrip('\n').split('\t'); yield head
    ci=head.index('country_name')
    for ln in it:
        p=ln.rstrip('\n').split('\t')
        if len(p)>ci and p[ci]==country: yield p
def pull_countries(out):
    r=get('https://www.netflix.com/tudum/top10/data/all-weeks-countries.tsv')
    n=0
    with open(os.path.join(out,'netflix_us_weekly.tsv'),'w') as f:
        for row in us_rows((l.decode('utf-8','replace') for l in r)):
            f.write('\t'.join(row)+'\n'); n+=1
    return n
def pull_kalshi(out,log):
    tot=0
    with gzip.open(os.path.join(out,'kalshi_netflix_trades.jsonl.gz'),'wt') as f, gzip.open(os.path.join(out,'kalshi_netflix_markets.jsonl.gz'),'wt') as fm:
        for s in SERIES:
            cur='';M=[]
            while True:
                u=f'{KALSHI}/markets?series_ticker={s}&limit=1000'+(f'&cursor={cur}' if cur else '')
                j=json.load(get(u)); M+=j.get('markets',[]); cur=j.get('cursor') or ''
                if not cur: break
                time.sleep(0.3)
            for m in M: fm.write(json.dumps({k:m.get(k) for k in('ticker','event_ticker','title','yes_sub_title','open_time','close_time','status','result','volume_fp','expiration_value')})+'\n')
            log.write(json.dumps({'ev':'series','s':s,'markets':len(M)})+'\n'); log.flush()
            for m in M:
                cur=''
                while True:
                    u=f"{KALSHI}/markets/trades?ticker={m['ticker']}&limit=1000"+(f'&cursor={cur}' if cur else '')
                    j=json.load(get(u))
                    for t in j.get('trades',[]):
                        f.write(json.dumps({'ticker':t['ticker'],'t':t['created_time'],'yes':t.get('yes_price_dollars',t.get('yes_price')),'no':t.get('no_price_dollars',t.get('no_price')),'n':t.get('count_fp',t.get('count')),'taker':t.get('taker_side')})+'\n'); tot+=1
                    cur=j.get('cursor') or ''
                    if not cur: break
                    time.sleep(0.2)
                time.sleep(0.2)
    return tot
if __name__=='__main__':
    out=sys.argv[1]; os.makedirs(out,exist_ok=True)
    with open(os.path.join(out,'log.jsonl'),'w') as log:
        n=pull_countries(out); log.write(json.dumps({'ev':'countries','us_rows':n})+'\n'); log.flush()
        t=pull_kalshi(out,log); log.write(json.dumps({'ev':'done','us_rows':n,'kalshi_trades':t})+'\n')
