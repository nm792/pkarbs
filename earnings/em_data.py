"""PM earnings-call mention markets -> rows (company, word, threshold, outcome, event time, trades)."""
import json,re,collections,datetime as dt
E=json.load(open('/mnt/project-files/mrbeast-markets/mentions/pm_mm_events.json'))
TR=json.load(open('pm_trades.json'))
def ts(s):
    s=s.replace(' ','T').replace('Z','+00:00')
    if re.search(r'[+-]\d\d$',s):s+=':00'
    return dt.datetime.fromisoformat(s).timestamp()
def norm(s):return re.sub(r'[^a-z0-9]','',(s or '').lower())
def company(e):
    t=e['title']
    for pat in [r'What will (?:be said|(?:Elon Musk|Michael Saylor) say) during (.+?) Q\d',r'What will (.+?) say during',r'Will (.+?) CEO say',r'What will be said during (.+?) earnings']:
        m=re.search(pat,t)
        if m:
            c=m.group(1);c=re.sub(r'\(.*?\)','',c);return norm(c.replace('Inc.',''))
    return norm(t)
def parse(m):
    q=m['question'];w=re.search(r'say "(.+?)"',q) or re.search(r'"(.+?)"',q)
    word=norm(w.group(1)) if w else norm(m.get('groupItemTitle'))
    k=re.search(r'(\d+)\+\s*times',q);k=int(k.group(1)) if k else 1
    return word,k
def res(m):
    p=json.loads(m['outcomePrices']);return 1 if float(p[0])>.5 else 0
def rows():
    out=[]
    for e in E:
        if 'earnings' not in (e.get('title') or '').lower():continue
        try:
            if not all(max(float(x) for x in json.loads(m['outcomePrices']))>=.99 for m in e['markets']):continue
        except Exception:continue
        t0=min(ts(m.get('startDate') or e['startDate']) for m in e['markets']);c=company(e)
        for m in e['markets']:
            w,k=parse(m);out.append(dict(eid=e['id'],comp=c,word=w,k=k,y=res(m),t0=t0,cond=m['conditionId'],q=m['question'],tr=TR.get(m['conditionId'],[])))
    return out
if __name__=='__main__':
    R=rows();print(len(R),len({r['eid'] for r in R}),len({r['comp'] for r in R}))
    ev=collections.defaultdict(set)
    for r in R:ev[r['comp']].add(r['eid'])
    print(sorted(((len(v),c) for c,v in ev.items()),reverse=True)[:25]);print(sum(1 for v in ev.values() if len(v)>=2),'companies with >=2 events')
    print(sum(r['y'] for r in R)/len(R),sum(1 for r in R if any(t[0]<=r['t0']+3600 for t in r['tr'])))
