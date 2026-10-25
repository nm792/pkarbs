import json
S=json.load(open('k_events_store.json'))
P={e['slug']:e for e in json.load(open('pm_midterms.json'))}
st={'TX':'texas','MI':'michigan','ME':'maine','NC':'north-carolina','GA':'georgia','IA':'iowa','AK':'alaska','NE':'nebraska','KS':'kansas','MN':'minnesota','NH':'new-hampshire','OH':'ohio','NV':'nevada','AZ':'arizona','WI':'wisconsin','FL':'florida'}
def kf(p): return 0.07*p*(1-p)
rows=[]
for k,e in S.items():
    if not k.endswith('-26'): continue
    if k.startswith('SENATE') and k[6:8] in st: slug=f"{st[k[6:8]]}-senate-election-winner"
    elif k.startswith('GOVPARTY') and k[8:10] in st: slug=f"{st[k[8:10]]}-governor-winner-2026"
    else: continue
    pe=P.get(slug)
    if not pe: print('NO PM',k,slug); continue
    pms=[m for m in pe['markets'] if not m.get('closed') and float(m.get('bestBid') or 0)>0.001]
    for km in e['markets']:
        if km.get('status')!='active': continue
        name=(km.get('yes_sub_title') or '').split()[-1].lower()
        pm=[m for m in pms if name in (m.get('groupItemTitle') or '').lower()]
        if not pm: print('nomatch',k,km.get('yes_sub_title'),[m.get('groupItemTitle') for m in pms]); continue
        pm=pm[0]
        ka=float(km['yes_ask_dollars']); kb=float(km['yes_bid_dollars'])
        pa=float(pm['bestAsk']); pb=float(pm['bestBid'])
        # pair A: buy K yes(name) + buy PM NO(name) at 1-pb  ; pair B: buy PM yes + K NO at 1-kb
        A=ka+(1-pb)+kf(ka); Bc=pa+(1-kb)+kf(1-kb)
        rows.append((round(min(A,Bc),4),k,km.get('yes_sub_title'),'K',kb,ka,'PM',pb,pa,round(A,4),round(Bc,4),pm['groupItemTitle'],round(float(pm.get('liquidityNum') or 0))))
rows.sort()
for r in rows: print(r)
