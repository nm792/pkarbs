import json,re,glob,os,sys
TD='/root/.claude/projects/-home-user/d45618f0-e206-59c9-89ab-a81c1c4790c7/tool-results/'
STORE='/tmp/w/wn_daily.json'
def parse(h):
    d=re.findall(r'<time class="won-mp-chart-date" datetime="(\d{4}-\d\d-\d\d)"',h)
    if not d: return None
    out={'date':d[0],'global':{'movie':[],'tv':[]},'country':{}}
    # global table: rows with points
    gi=h.find('Global charts'); ci=h.find('Most popular by country')
    g=h[gi:ci] if gi>=0 else ''
    # each row: rank, movie title, points, prior, tv title, points, prior
    for tr in re.findall(r'<tr[^>]*>(.*?)</tr>',g,re.S):
        tds=re.findall(r'<td[^>]*>(.*?)</td>',tr,re.S)
        if len(tds)<5: continue
        rk=re.sub('<[^>]+>','',tds[0]).strip()
        if not rk.isdigit(): continue
        def title(x):
            m=re.search(r'data-won-mp-trend-title="([^"]*)"',x); return m.group(1) if m else re.sub('<[^>]+>','',x).strip()
        def pts(x):
            t=re.sub('<[^>]+>','',x).strip(); return int(t) if t.isdigit() else None
        out['global']['movie'].append((int(rk),title(tds[1]),pts(tds[2])))
        out['global']['tv'].append((int(rk),title(tds[4]),pts(tds[5])))
    # country sections
    for m in re.finditer(r'<h4 class="won-mp-chart-title" id="won-mp-country-([A-Z]+)">(.*?)</h4>(.*?)(?=<h4 class="won-mp-chart-title" id="won-mp-country-|$)',h,re.S):
        cc,_,body=m.groups()
        # two blocks: TV series then Movies
        for blk in re.split(r'<div class="won-mp-chart-banner">',body)[1:]:
            kind='tv' if re.search(r'TV series',blk[:200]) else 'movie'
            rows=re.findall(r'<td class="won-mp-rank-col">(\d+)</td>\s*<td><div class="won-mp-cell-main"><button[^>]*data-won-mp-trend-title="([^"]*)"',blk)
            out['country'].setdefault(cc,{})[kind]=[(int(a),b) for a,b in rows]
    return out
def ingest():
    store=json.load(open(STORE)) if os.path.exists(STORE) else {}
    done=set(json.load(open(STORE+'.files'))) if os.path.exists(STORE+'.files') else set()
    n=0
    for f in glob.glob(TD+'mcp-TinyFish-fetch_content-*.txt'):
        if f in done: continue
        done.add(f)
        try: raw=json.load(open(f))
        except Exception: continue
        for r in raw.get('results',[]):
            if 'whats-on-netflix.com/most-popular' not in r.get('url',''): continue
            p=parse(r.get('text') or '')
            if p and p['date'] not in store: store[p['date']]=p; n+=1
    json.dump(store,open(STORE,'w')); json.dump(sorted(done),open(STORE+'.files','w'))
    return n,len(store)
if __name__=='__main__': print(ingest())
