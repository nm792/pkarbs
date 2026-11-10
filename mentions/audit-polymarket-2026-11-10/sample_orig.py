import json,random,collections
E=json.load(open('pm_mm_events.json'))
def fam(e):
    t=(e.get('title') or '').lower()
    if 'trump' in t and 'week' in t:return 'trump-weekly'
    if 'trump' in t:return 'trump-event'
    if 'earnings' in t:return 'earnings-call'
    if 'nfl' in t or 'announcer' in t or 'nba' in t or 'game' in t:return 'sports-announcers'
    return 'other'
def start(e):return min((m.get('startDate') or e.get('startDate') or '') for m in e['markets'])
def ok(e):
    r=0
    for m in e['markets']:
        try:p=json.loads(m['outcomePrices'])
        except Exception:return False
        if max(float(x) for x in p)<.99:return False
    return len(e['markets'])>=3
E=[e for e in E if ok(e)]
fams=collections.defaultdict(list)
for e in E:fams[fam(e)].append(e)
el=[]
for f,L in fams.items():
    L.sort(key=start);b=max(10,int(.3*len(L)));el+=L[b:]
    print(f,len(L),'post-burn',len(L)-b)
random.seed(7);S=random.sample(el,min(300,len(el)))
json.dump({e['id']:e for e in S},open('pm_mm_sample.json','w'))
print('sample',len(S),'markets',sum(len(e['markets']) for e in S))
json.dump([ (e['id'],fam(e),start(e)) for e in E],open('pm_mm_order.json','w'))
