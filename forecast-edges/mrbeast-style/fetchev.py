import json,urllib.request,time,sys,concurrent.futures as cf
sys.path.insert(0,'/tmp/w')
from classify import fam
E=json.load(open('allev.json'))
want=sys.argv[1].split('|')
ids=[e['id'] for e in E.values() if fam(e['title']) in want]
print(len(ids))
def get(i):
    for a in range(4):
        try: return json.load(urllib.request.urlopen(urllib.request.Request(f'https://gamma-api.polymarket.com/events/{i}',headers={'User-Agent':'x'}),timeout=40))
        except Exception: time.sleep(1+a)
out={}
with cf.ThreadPoolExecutor(10) as ex:
    for i,r in zip(ids,ex.map(get,ids)):
        if r: out[i]=r
json.dump(out,open(sys.argv[2],'w'))
print(len(out))
