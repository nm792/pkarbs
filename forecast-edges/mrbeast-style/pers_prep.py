import json,re,collections,datetime,sys
sys.path.insert(0,'/tmp/w')
from classify import fam
D=json.load(open('/tmp/w/other_events.json'))
def ts(s): return datetime.datetime.fromisoformat(s.replace('Z','+00:00')).timestamp()
def skey(t):
    if re.search(r'Netflix',t) and re.search(r'this week',t) and not re.search(r'How many|say',t):
        rk='#2' if '#2' in t else 'top'
        reg='US' if re.search(r'\bUS\b',t) else 'global'
        typ='movie' if re.search(r'[Mm]ovie',t) else 'show'
        return f'netflix|{rk}|{reg}|{typ}'
    if re.search(r'Spotify',t) and re.search(r'song',t) and re.search(r'this week',t) and re.search(r'#[12]',t):
        rk='#2' if '#2' in t else '#1'
        reg='US' if re.search(r'\bUS\b',t) else 'global'
        return f'spotify|{rk}|{reg}'
    if re.search(r'App Store',t) and re.search(r'#[12] (Free|Paid) App',t) and not re.search(r'by|out as|back in|Big AI',t):
        m=re.search(r'#([12]) (Free|Paid)',t); return f'appstore|{m.group(1)}|{m.group(2)}'
    if re.search(r'Billboard',t) and re.search(r'#[12] (Song|Album)',t) and re.search(r'Week of',t):
        m=re.search(r'(Hot 100|200) #([12]) (Song|Album)',t)
        if m: return f'billboard|{m.group(1)}|{m.group(2)}'
    if re.search(r'OpenRouter',t): 
        m=re.search(r'#(\d)',t); return f'openrouter|{m.group(1)}'
    return None
S=collections.defaultdict(list)
for e in D.values():
    k=skey(e['title'])
    if not k or not e.get('closedTime'): continue
    ws=[m for m in e['markets'] if (json.loads(m.get('outcomePrices') or '["0","0"]')[0]=='1')]
    if len(ws)!=1: continue
    S[k].append(dict(id=e['id'],start=ts(e['startDate']),close=ts(e['closedTime']),win=ws[0]['groupItemTitle'],vol=e.get('volume') or 0,
      mk={m['groupItemTitle']:(m['conditionId'],(json.loads(m.get('outcomePrices') or '["0","0"]')[0]=='1')) for m in e['markets']},title=e['title']))
for k in S: S[k].sort(key=lambda r:r['close'])
print({k:(len(v),round(sum(x['vol'] for x in v)/1e6,2)) for k,v in S.items()})
tg={}
rows=[]
for k,v in S.items():
    for i in range(1,len(v)):
        r=v[i];prev=v[i-1]
        if prev['close']>r['start']+3600: 
            # find latest prior closed before T
            c=[x for x in v[:i] if x['close']<=r['start']+3600]
            if not c: continue
            prev=c[-1]
        if prev['win'] in r['mk']:
            cid,won=r['mk'][prev['win']]
            tg[cid]=dict(markets=[dict(conditionId=cid,groupItemTitle=prev['win'])])
            rows.append(dict(key=k,id=r['id'],start=r['start'],close=r['close'],T=r['start']+3600,cid=cid,won=won,prevwin=prev['win'],title=r['title']))
print(len(rows),'rows')
json.dump({c:{'markets':v['markets']} for c,v in tg.items()},open('pers_events.json','w'))
json.dump(rows,open('pers_rows.json','w'))
