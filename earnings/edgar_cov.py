import json,urllib.request,urllib.parse,time,re,collections,datetime as dt
H={'User-Agent':'research-script/1.0'}
def g(u):
    for a in range(5):
        try:return json.load(urllib.request.urlopen(urllib.request.Request(u,headers=H),timeout=40))
        except Exception as e:time.sleep(2*(a+1))
hits={}
for q in ['"prepared remarks"','"earnings call transcript"','"conference call transcript"','"call transcript"']:
    for (a,b) in [('2025-02-01','2025-07-31'),('2025-08-01','2025-12-31'),('2026-01-01','2026-04-30'),('2026-05-01','2026-08-15'),('2026-08-16','2026-11-10')]:
        frm=0
        while frm<1000:
            r=g('https://efts.sec.gov/LATEST/search-index?q=%s&forms=8-K&dateRange=custom&startdt=%s&enddt=%s&from=%d'%(urllib.parse.quote(q),a,b,frm))
            if not r:break
            hs=r['hits']['hits']
            for h in hs:
                s=h['_source'];hits[h['_id']]=(q,s['file_date'],s['display_names'][0] if s['display_names'] else '',h['_id'])
            frm+=len(hs)
            if len(hs)<100 or frm>=r['hits']['total']['value']:break
            time.sleep(0.2)
    print(q,len(hits),flush=True)
json.dump(list(hits.values()),open('edgar_hits.json','w'))
