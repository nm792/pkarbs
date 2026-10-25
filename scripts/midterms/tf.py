import json,re
def results(F):
    d=json.load(open(F))
    for r in d['results']:
        t=r['text'].strip().strip('`').strip()
        t2=re.sub(r'\\(?!["\\/bfnrtu])', '', t)
        try: yield r['url'], json.loads(t2)
        except Exception as e: yield r['url'], ('ERR', str(e), t[:300])
    for e in d.get('errors',[]): yield e.get('url'),('ERRFETCH',e)
