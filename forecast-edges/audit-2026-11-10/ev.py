import requests,json,re
S=requests.Session(); out=[]
off=0
while True:
    r=S.get("https://gamma-api.polymarket.com/events",params=dict(tag_slug="tweets-markets",closed="true",limit=100,offset=off,order="endDate",ascending="true"),timeout=60).json()
    if not r: break
    out+=r; off+=100
    if len(r)<100: break
print(len(out))
json.dump(out,open('events_all.json','w'))
import collections
c=collections.Counter(e['title'].split(' #')[0][:30] for e in out); print(c.most_common(12))
el=[e for e in out if e['title'].startswith('Elon Musk # tweets')]
print(len(el),el[0]['endDate'],el[-1]['endDate'])
