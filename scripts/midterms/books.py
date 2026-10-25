import json,re,glob
def load_books(files):
    B={}
    for f in files:
        d=json.load(open(f))
        for r in d['results']:
            if '/book?' not in r['url']: continue
            t=r["text"].replace("\\_","_").strip().strip("`").strip()
            if not t.strip(): print("EMPTY",r["url"][-12:]); continue
            b=json.loads(t)
            asks=sorted((float(x['price']),float(x['size'])) for x in b['asks'])
            bids=sorted(((float(x['price']),float(x['size'])) for x in b['bids']),reverse=True)
            B[b['asset_id']]=dict(asks=asks,bids=bids,ts=int(b['timestamp']))
    return B
def cost_curve(asks,n):
    "cost of buying n shares walking asks"
    c=0;left=n
    for p,s in asks:
        q=min(s,left); c+=q*p; left-=q
        if left<=1e-9: return c
    return None
