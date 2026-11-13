# List completed pro LoL games (2025-01-01 onward) from esports-api.lolesports.com
import json, subprocess, sys, os
from concurrent.futures import ThreadPoolExecutor
K = os.environ.get("LOL_API_KEY", "0TvQnueqKa5mxJntVWt0w4LpLfEkrV1Ta8rQBb9Z")  # public site key
UA = "Mozilla/5.0"
def jget(url, params):
    cmd = ['curl','-sS','-m','30','-A',UA,'-H',f'x-api-key: {K}','-G',url]
    for k,v in params.items(): cmd += ['--data-urlencode', f'{k}={v}']
    o = subprocess.run(cmd+['-w','\n%{http_code}'],capture_output=True,text=True).stdout
    b, c = o.rsplit('\n',1)
    return json.loads(b) if c=='200' else None
LEAGUES = {'worlds':'98767975604431411','msi':'98767991325878492','first_stand':'113464388705111224',
 'lck':'98767991310872058','lpl':'98767991314006698','lec':'98767991302996019','lcs':'98767991299243165',
 'lcp':'113476371197627891','cblol':'98767991332355509','lta_n':'113470291645289904','lta_s':'113475181634818701',
 'ewc':'116838530616006090','lta_cross':'113475149040947852'}
SINCE = sys.argv[1] if len(sys.argv)>1 else '2025-01-01'
matches = []
for slug, lid in LEAGUES.items():
    tok = None; n=0
    while True:
        p = {'hl':'en-US','leagueId':lid}
        if tok: p['pageToken'] = tok
        d = jget("https://esports-api.lolesports.com/persisted/gw/getSchedule", p)
        if not d: break
        s = d['data']['schedule']
        for e in s['events']:
            if e.get('type')=='match' and e['state']=='completed' and e['startTime']>=SINCE:
                matches.append({'league':slug,'start':e['startTime'],'match_id':e['match']['id'],
                  'teams':[(t['code'],t['result']['gameWins'] if t.get('result') else None) for t in e['match']['teams']],'names':[t['name'] for t in e['match']['teams']]})
                n+=1
        if not s['events'] or min(e['startTime'] for e in s['events']) < SINCE or not s['pages'].get('older'): break
        tok = s['pages']['older']
    print(slug, n, file=sys.stderr)
def det(m):
    d = jget("https://esports-api.lolesports.com/persisted/gw/getEventDetails", {'hl':'en-US','id':m['match_id']})
    if not d: return m
    mt = d['data']['event']['match']
    m['team_ids'] = {t['id']:t['code'] for t in mt['teams']}
    m['games'] = [{'id':g['id'],'number':g['number'],'sides':{t['side']:t['id'] for t in g['teams']}} for g in mt['games'] if g['state']=='completed']
    return m
with ThreadPoolExecutor(8) as ex: matches = list(ex.map(det, matches))
json.dump(matches, open(sys.argv[2] if len(sys.argv)>2 else 'raw/matches.json','w'))
print('matches', len(matches), 'games', sum(len(m.get('games',[])) for m in matches), file=sys.stderr)
