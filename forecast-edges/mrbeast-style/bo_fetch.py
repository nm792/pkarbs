import json,re,urllib.request,time,concurrent.futures as cf
E_=json.load(open('allev.json'))
ids=[e['id'] for e in E_.values() if re.search(r'weekend box office|opening weekend|box office:',e['title'].lower()) and e.get('closed')]
print(len(ids),flush=True)
def get(i):
    for a in range(4):
        try: return json.load(urllib.request.urlopen(urllib.request.Request(f'https://gamma-api.polymarket.com/events/{i}',headers={'User-Agent':'x'}),timeout=40))
        except Exception: time.sleep(1+a)
out={}
with cf.ThreadPoolExecutor(10) as ex:
    for i,r in zip(ids,ex.map(get,ids)):
        if r: out[i]=r
json.dump(out,open('bo_events.json','w')); print(len(out))
