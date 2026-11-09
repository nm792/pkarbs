import os
import json, glob, re
K = os.environ["LOL_API_KEY"]
sched = []
for f in ['/tmp/sched_0.json'] + sorted(glob.glob('/tmp/sched_[0-9].json')):
    sched += json.load(open(f))['data']['schedule']['events']
done = [e for e in sched if e['state'] == 'completed' and e['startTime'] >= '2026-10-24' and e.get('match')]
closed = json.load(open('/tmp/lol_closed.json'))
pm = []
for e in closed:
    s = e.get('slug') or ''
    if s.startswith('lol-') and any('Game 1 Winner' in (m.get('question') or '') for m in e.get('markets', [])):
        pm.append(e)
def codes(s): return set(re.sub(r'\d', '', c) for c in s.split('-')[1:-3]) if False else None
out = []
for ev in done:
    m = ev['match']; teams = [t['code'].lower() for t in m['teams']]
    day = ev['startTime'][:10]
    cands = []
    for p in pm:
        slug = p['slug']
        d = (p.get('startDate') or '')[:10]
        parts = slug.split('-')
        if day not in [d, (p.get('endDate') or '')[:10]] and not slug.endswith(day): continue
        toks = [re.sub(r'\d', '', x) for x in parts]
        if all(any(t == tok for tok in toks) for t in teams):
            cands.append(p)
    if cands:
        out.append({'match_id': m['id'], 'start': ev['startTime'], 'teams': teams, 'pm_slug': cands[0]['slug'], 'pm_markets': [(x['id'], x['question'], x.get('conditionId')) for x in cands[0]['markets'] if 'Game 1 Winner' in x['question']]})
json.dump(out, open('matched.json', 'w'), indent=1)
print(len(done), len(pm), len(out))
for o in out: print(o['start'], o['teams'], o['pm_slug'], len(o['pm_markets']))
