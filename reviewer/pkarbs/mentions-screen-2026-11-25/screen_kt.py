import json,sys,urllib.request,concurrent.futures as cf
sys.path.insert(0,'code'); import mentions_pm_daily_scorer as S
S.KEEP_THRESHOLD=True
H={"User-Agent":"Mozilla/5.0"}
def get(u): return json.load(urllib.request.urlopen(urllib.request.Request(u,headers=H),timeout=30))
st=json.load(open('st/events.json')); closed=[e for e in (st['events'] if isinstance(st,dict) and 'events' in st else st.values() if isinstance(st,dict) else st)]
closed=[e for e in closed if isinstance(e,dict) and S.resolved(e)]
for e in closed:
    for m in e['markets']: m['word']=S.wkey(m.get('label'))
op=[S.slim(e) for e in json.load(open('open_events.json'))]
raw={e['id']:e for e in json.load(open('open_events.json'))}
def book(t):
    try: return get(f"https://clob.polymarket.com/book?token_id={t}")
    except Exception as x: return None
rows=[]
for ev in op:
    hist=[h for h in closed if h['fam']==ev['fam']]
    for m in ev['markets']:
        if m['closed'] or len(m['toks'])<2: continue
        q=S.q_for(hist,ev,m)
        for side,t,fair in (("YES",m['toks'][0],q),("NO",m['toks'][1],1-q)):
            rows.append((ev,m,side,t,fair,len(hist)))
with cf.ThreadPoolExecutor(8) as ex: bks=list(ex.map(lambda r: book(r[3]), rows))
out=[]
for (ev,m,side,t,fair,nh),b in zip(rows,bks):
    asks=sorted(((float(a['price']),float(a['size'])) for a in (b or {}).get('asks',[])))
    best=asks[0][0] if asks else None
    edge_usd=sum(p*s for p,s in asks if p<=fair-0.10 and p>=0.05)
    full=sum(p*s for p,s in asks)
    out.append(dict(event=raw[ev['id']]['slug'][:60],fam=ev['fam'],word=m['label'],side=side,fair=round(fair,3),best_ask=best,edge_priced_usd=round(edge_usd,2),ladder_usd=round(full),hist_events=nh,ev_vol=round(float(raw[ev['id']].get('volume') or 0)),end=raw[ev['id']].get('endDate','')[:16]))
json.dump(out,open('screen_open_kt.json','w'),indent=1)
hit=[o for o in out if o['edge_priced_usd']>0]
print(len(out),"tokens;",len(hit),"with edge-priced asks; total edge-priced $",round(sum(o['edge_priced_usd'] for o in hit)))
for o in sorted(hit,key=lambda o:-o['edge_priced_usd'])[:25]: print(o)
