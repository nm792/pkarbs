# Pull rn1 activity (v2 data-api) in 1h windows, cursor paging. Usage: start_ts end_ts out.jsonl
import sys,json,urllib.request,urllib.parse,time
W='0x2005d16a84ceefa912d4e380cd32e7ff827875ea'
s,e,out=int(sys.argv[1]),int(sys.argv[2]),sys.argv[3]
f=open(out,'w');n=0
def get(p):
  for i in range(5):
    try:
      r=urllib.request.Request('https://data-api.polymarket.com/v2/activity?'+urllib.parse.urlencode(p),headers={'User-Agent':'Mozilla/5.0'})
      return json.load(urllib.request.urlopen(r,timeout=30))
    except Exception as ex: print('retry',ex,file=sys.stderr); time.sleep(2**i)
t=s
while t<e:
  p=dict(user=W,limit=500,start=t,end=min(t+3600,e)-1); cur=None
  while True:
    if cur: p['cursor']=cur
    d=get(p)
    for x in d['data']: f.write(json.dumps(x)+'\n'); n+=1
    cur=d['pagination'].get('next_cursor')
    if not d['pagination'].get('has_more') or not cur: break
  t+=3600
print(n)
