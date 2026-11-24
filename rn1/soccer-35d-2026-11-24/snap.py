import json,urllib.request,gzip,re,datetime,sys,time
out=[]
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
def gj(u):
    b=urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'x','Accept-Encoding':'gzip'}),timeout=40).read()
    try: b=gzip.decompress(b)
    except: pass
    return json.loads(b)
for lg,sid in (('fl1',10195),('sea',10203),('epl',10188),('lal',10193)):
    ev=[]
    for off in range(0,1500,50):
        d=gj(f'https://gamma-api.polymarket.com/events?series_id={sid}&closed=false&limit=50&offset={off}'); ev+=d
        if len(d)<50: break
    rx=re.compile(r'^[a-z0-9]+-[a-z0-9]+-[a-z0-9]+-\d{4}-\d\d-\d\d$')
    for e in ev:
        if not rx.match(e['slug']) or e.get('ended'): continue
        for m in e['markets']:
            if m.get('sportsMarketType')!='moneyline': continue
            toks=json.loads(m['clobTokenIds']); oc=json.loads(m['outcomes'])
            for t,o in zip(toks,oc):
                try: b=gj('https://clob.polymarket.com/book?token_id='+t)
                except Exception as ex: out.append({'lg':lg,'slug':e['slug'],'err':str(ex)[:80]}); continue
                if b.get('asset_id')!=t: raise SystemExit('book for wrong token')
                bids=sorted([(float(x['price']),float(x['size'])) for x in b['bids']],reverse=True); asks=sorted([(float(x['price']),float(x['size'])) for x in b['asks']])
                out.append({'lg':lg,'slug':e['slug'],'q':m['question'],'outcome':o,'t_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
                  'bb':bids[0][0] if bids else None,'bb_sz':bids[0][1] if bids else None,'ba':asks[0][0] if asks else None,'ba_sz':asks[0][1] if asks else None,
                  'bid_depth_usd_top3':sum(p*s for p,s in bids[:3]),'bid_depth_usd_5c':sum(p*s for p,s in bids if bids and p>=bids[0][0]-0.05),'nbids':len(bids)})
json.dump(out,open('snap.json','w'))
print(len(out))
