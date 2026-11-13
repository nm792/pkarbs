#!/usr/bin/env python3
"""Free daily Netflix signal + Polymarket Netflix books, recorder. Read-only. Single process.
Usage: record_netflix.py OUTDIR [--once]
 - every run: fetch what's-on-netflix.com daily top-10 page for today and yesterday (robots.txt allows /most-popular/), parse to JSON
 - every run: snapshot best bid/ask and top 5 levels for every market of every open Polymarket 'Netflix ... this week' event
Run from cron/timer every 30 minutes. Output: OUTDIR/wn_daily.jsonl, OUTDIR/books.jsonl.gz"""
import sys,os,re,json,gzip,time,datetime,urllib.request,urllib.parse
UA={'User-Agent':'pkarbs-research/1.0 (low-rate)'}
def parse_wn(h):
    d=re.findall(r'<time class="won-mp-chart-date" datetime="(\d{4}-\d\d-\d\d)"',h)
    if not d: return None
    out={'date':d[0],'global':{'movie':[],'tv':[]},'country':{}}
    # global table: rows with points
    gi=h.find('Global charts'); ci=h.find('Most popular by country')
    g=h[gi:ci] if gi>=0 else ''
    # each row: rank, movie title, points, prior, tv title, points, prior
    for tr in re.findall(r'<tr[^>]*>(.*?)</tr>',g,re.S):
        tds=re.findall(r'<td[^>]*>(.*?)</td>',tr,re.S)
        if len(tds)<5: continue
        rk=re.sub('<[^>]+>','',tds[0]).strip()
        if not rk.isdigit(): continue
        def title(x):
            m=re.search(r'data-won-mp-trend-title="([^"]*)"',x); return m.group(1) if m else re.sub('<[^>]+>','',x).strip()
        def pts(x):
            t=re.sub('<[^>]+>','',x).strip(); return int(t) if t.isdigit() else None
        out['global']['movie'].append((int(rk),title(tds[1]),pts(tds[2])))
        out['global']['tv'].append((int(rk),title(tds[4]),pts(tds[5])))
    # country sections
    for m in re.finditer(r'<h4 class="won-mp-chart-title" id="won-mp-country-([A-Z]+)">(.*?)</h4>(.*?)(?=<h4 class="won-mp-chart-title" id="won-mp-country-|$)',h,re.S):
        cc,_,body=m.groups()
        # two blocks: TV series then Movies
        for blk in re.split(r'<div class="won-mp-chart-banner">',body)[1:]:
            kind='tv' if re.search(r'TV series',blk[:200]) else 'movie'
            rows=re.findall(r'<td class="won-mp-rank-col">(\d+)</td>\s*<td><div class="won-mp-cell-main"><button[^>]*data-won-mp-trend-title="([^"]*)"',blk)
            out['country'].setdefault(cc,{})[kind]=[(int(a),b) for a,b in rows]
    return out

def get(url,tries=4):
    for a in range(tries):
        try: return urllib.request.urlopen(urllib.request.Request(url,headers=UA),timeout=60).read().decode('utf-8','replace')
        except Exception as e: err=e; time.sleep(2+3*a)
    raise err
def wn_day(d):
    u='https://www.whats-on-netflix.com/most-popular/?dateselect='+d.strftime('%m/%d/%Y')
    return parse_wn(get(u))
def open_events():
    out=[];off=0
    j=json.loads(get('https://gamma-api.polymarket.com/public-search?q=Netflix%20this%20week&limit_per_type=50&events_status=active'))
    for e in j.get('events',[]):
        if re.search(r'Netflix',e['title']) and re.search(r'this week',e['title']) and not e.get('closed'): out.append(e['id'])
    return out
def snap_books(out):
    now=datetime.datetime.utcnow().isoformat()+'Z'; n=0
    with gzip.open(os.path.join(out,'books.jsonl.gz'),'at') as f:
        for eid in open_events():
            e=json.loads(get('https://gamma-api.polymarket.com/events/'+eid))
            for m in e.get('markets',[]):
                if m.get('closed'): continue
                toks=json.loads(m.get('clobTokenIds') or '[]')
                if not toks: continue
                try: b=json.loads(get('https://clob.polymarket.com/book?token_id='+toks[0]))
                except Exception: continue
                f.write(json.dumps({'t':now,'event':eid,'title':e['title'],'market':m.get('groupItemTitle'),'cond':m['conditionId'],
                    'bids':b.get('bids',[])[-5:],'asks':b.get('asks',[])[:5]})+'\n'); n+=1; time.sleep(0.15)
    return n
if __name__=='__main__':
    out=sys.argv[1]; os.makedirs(out,exist_ok=True)
    today=datetime.datetime.utcnow().date()
    with open(os.path.join(out,'wn_daily.jsonl'),'a') as f:
        for d in (today-datetime.timedelta(days=1),today):
            try:
                p=wn_day(d)
                if p: f.write(json.dumps({'fetched':datetime.datetime.utcnow().isoformat()+'Z',**p})+'\n')
            except Exception as ex: f.write(json.dumps({'error':str(ex),'date':d.isoformat()})+'\n')
            time.sleep(3)
    n=snap_books(out)
    print(json.dumps({'ev':'done','books':n}))
