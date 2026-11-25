import json,urllib.request,time,sys,os
U='0x2005d16a84ceefa912d4e380cd32e7ff827875ea'
def get(q):
    u='https://data-api.polymarket.com/v2/trades?'+q
    for a in range(6):
        try: return json.load(urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'curl/8.5.0'}),timeout=60))
        except Exception as e: time.sleep(2*(a+1))
    raise SystemExit('fail '+u)
def pull(q,cid,cap=200):
    out=[];cur=None
    for i in range(cap):
        d=get(q+'&limit=500'+(f'&cursor={cur}' if cur else ''))
        for r in d['data']: assert r['condition_id']==cid,(r['condition_id'],cid)
        out+=d['data'];cur=d['pagination'].get('next_cursor')
        if not d['pagination'].get('has_more'): break
    return out
mk=json.load(open('mk3.json'));N=int(sys.argv[1])
os.makedirs('tapes',exist_ok=True)
for lg in ('cs2','sea','fl1'):
    for s,cid,pnl,vol,slug in [x for x in mk if x[0]==lg][:N]:
        f=f'tapes/{slug}.json'
        if os.path.exists(f): continue
        a=pull(f'user={U}&condition_id={cid}&taker_only=false',cid)
        t=pull(f'user={U}&condition_id={cid}&taker_only=true',cid)
        tape=pull(f'condition_id={cid}&taker_only=true',cid)
        json.dump({'slug':slug,'cid':cid,'pnl':pnl,'vol':vol,'all':a,'tk':t,'tape':tape},open(f,'w'))
        print(slug,len(a),len(t),len(tape),flush=True)
