import json, gzip, sys, time, urllib.request, urllib.parse
W='0x2005d16a84ceefa912d4e380cd32e7ff827875ea'
mode=sys.argv[1]            # all | taker
days=int(sys.argv[2]); out=sys.argv[3]
cutoff=time.time()-days*86400
def get(p):
    for a in range(6):
        try:
            r=urllib.request.Request('https://data-api.polymarket.com/v2/trades?'+urllib.parse.urlencode(p),headers={'User-Agent':'Mozilla/5.0'})
            return json.load(urllib.request.urlopen(r,timeout=40))
        except Exception as e:
            time.sleep(2*(a+1)); err=e
    raise err
cur=None; n=0; oldest=None
with gzip.open(out,'wt') as f:
    while True:
        p={'user':W,'limit':500}
        if mode=='taker': p['taker_only']='true'
        else: p['taker_only']='false'
        if cur: p['cursor']=cur
        d=get(p); rows=d.get('data') or []
        for r in rows:
            if r.get('proxy_wallet','').lower()!=W: raise SystemExit('WRONG WALLET ROW (param ignored?) '+str(r.get('proxy_wallet')))
            f.write(json.dumps(r,separators=(',',':'))+'\n'); n+=1
            oldest=r['timestamp'] if oldest is None else min(oldest,r['timestamp'])
        pg=d.get('pagination') or {}
        if n%5000<500: print(mode,n,oldest,flush=True)
        if not rows or not pg.get('has_more') or not pg.get('next_cursor') or oldest<=cutoff: break
        cur=pg['next_cursor']
print('DONE',mode,n,oldest,time.time()-oldest,flush=True)
