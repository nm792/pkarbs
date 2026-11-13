import json,urllib.request,urllib.parse,time,sys
Q=sys.argv[1:]
def get(u):
    for a in range(4):
        try: return json.load(urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'x'}),timeout=30))
        except Exception as e: time.sleep(1+a)
allev={}
try: allev=json.load(open('enum.json'))
except: pass
for q in Q:
    for st in ('true','false'):
        for pg in range(1,15):
            u='https://gamma-api.polymarket.com/public-search?'+urllib.parse.urlencode({'q':q,'limit_per_type':50,'page':pg,'events_status':'closed' if st=='true' else 'active','keep_closed_markets':1})
            j=get(u)
            if not j: break
            ev=j.get('events') or []
            for e in ev: allev[e['id']]=dict(id=e['id'],title=e['title'],slug=e.get('slug'),vol=e.get('volume'),end=e.get('endDate'),closed=e.get('closed'),nm=len(e.get('markets') or []))
            if not j.get('pagination',{}).get('hasMore'): break
    print(q,len(allev),flush=True)
json.dump(allev,open('enum.json','w'))
