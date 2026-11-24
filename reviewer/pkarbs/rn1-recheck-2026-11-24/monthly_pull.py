import json,urllib.request,time,sys
U='0x2005d16a84ceefa912d4e380cd32e7ff827875ea'
CUT=int(time.time())-62*86400
out=[]
for st in ['CLOSED','OPEN']:
    cur=None;n=0
    while True:
        u=f'https://data-api.polymarket.com/v2/positions?user={U}&limit=500&status={st}&sort_by=TIMESTAMP'+(f'&cursor={cur}' if cur else '')
        for a in range(5):
            try: d=json.load(urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'curl/8.5.0'}),timeout=60));break
            except Exception as e: time.sleep(2*(a+1))
        rows=d['data'];
        for r in rows:
            assert r['proxy_wallet'].lower()==U
            r.pop('profile_image',None);r.pop('icon',None)
        out+=rows;n+=1
        last=min(r['last_event_at'] for r in rows) if rows else 0
        cur=d['pagination'].get('next_cursor')
        if not d['pagination'].get('has_more') or last<CUT: break
    print(st,n,'pages',len(out),'last',last,file=sys.stderr)
json.dump(out,open('positions.json','w'))
