import json,gzip,sys,time,urllib.request,urllib.parse,threading
from concurrent.futures import ThreadPoolExecutor
conds=json.load(open('comp_conds.json'))
def get(p):
    for a in range(6):
        try:
            r=urllib.request.Request('https://data-api.polymarket.com/v2/trades?'+urllib.parse.urlencode(p),headers={'User-Agent':'Mozilla/5.0'})
            return json.load(urllib.request.urlopen(r,timeout=40))
        except Exception as e: time.sleep(2*(a+1)); err=e
    raise err
lock=threading.Lock(); f=gzip.open('comp.jsonl.gz','wt'); done=[0]; trunc=[0]
def work(c):
    for mode in ('false','true'):
        cur=None
        for pg in range(60):
            p={'condition_id':c,'limit':500,'taker_only':mode}
            if cur: p['cursor']=cur
            d=get(p); rows=d.get('data') or []
            out=[]
            for r in rows:
                if r['condition_id'].lower()!=c.lower(): raise SystemExit('WRONG MARKET ROW')
                out.append(json.dumps({'m':mode,'c':c,'w':r['proxy_wallet'],'s':r['side'],'t':r['token_id'],'z':r['size'],'p':r['price'],'ts':r['timestamp'],'h':r['transaction_hash'],'e':r['event_slug']},separators=(',',':')))
            with lock:
                for o in out: f.write(o+'\n')
            pgn=d.get('pagination') or {}
            if not rows or not pgn.get('has_more') or not pgn.get('next_cursor'): break
            cur=pgn['next_cursor']
        else:
            trunc[0]+=1
    with lock:
        done[0]+=1
        if done[0]%100==0: print('done',done[0],'trunc',trunc[0],flush=True)
with ThreadPoolExecutor(12) as ex: list(ex.map(work,conds))
f.close(); print('DONE',done[0],'trunc',trunc[0],flush=True)
