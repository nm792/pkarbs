"""1 s Polymarket CLOB book capture for NBA moneyline tokens (POST /books batch). Writes a row per token when
its top-15 levels change. Usage: python3 books.py MARKETS.json|auto OUT.jsonl SECONDS
'auto' = every 10 min take every not-yet-final game on the NBA liveData scoreboard, find its Polymarket moneyline by slug
(nba-<away>-<home>-<ET date>) and capture all of them. Also writes OUT.markets.json (token -> game) for the analysis."""
import sys, json, time, urllib.request, hashlib
MK, OUT, DUR = sys.argv[1], sys.argv[2], float(sys.argv[3]); T1 = time.time() + DUR
UA = {'User-Agent': 'Mozilla/5.0 pkarbs'}
def jget(u): return json.load(urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=20))
def discover():
    sb = jget('https://nba-prod-us-east-1-mediaops-stats.s3.amazonaws.com/NBA/liveData/scoreboard/todaysScoreboard_00.json')['scoreboard']
    out = []
    for g in sb['games']:
        if g['gameStatus'] == 3: continue
        a, h = g['awayTeam']['teamTricode'].lower(), g['homeTeam']['teamTricode'].lower()
        e = jget(f"https://gamma-api.polymarket.com/events?slug=nba-{a}-{h}-{g['gameEt'][:10]}")
        ml = [m for m in (e[0]['markets'] if e else []) if m.get('sportsMarketType') == 'moneyline']
        if ml: out.append(dict(gid=g['gameId'], slug=e[0]['slug'], cond=ml[0]['conditionId'], tokens=json.loads(ml[0]['clobTokenIds']), outcomes=json.loads(ml[0]['outcomes'])))
    return out
mk_list = [] if MK == 'auto' else json.load(open(MK)); next_disc = 0
toks = [t for m in mk_list for t in m['tokens']]
f = open(OUT, 'a'); last = {}
while time.time() < T1:
    t0 = time.time()
    if MK == 'auto' and t0 >= next_disc:
        try:
            new = discover(); seen = {m['cond'] for m in mk_list}
            mk_list += [m for m in new if m['cond'] not in seen]
            toks = [t for m in mk_list for t in m['tokens']]; json.dump(mk_list, open(OUT + '.markets.json', 'w'), indent=1)
        except Exception as e: f.write(json.dumps(dict(recv_ms=int(t0 * 1000), err='discover ' + str(e)[:150])) + '\n')
        next_disc = t0 + 600
    if not toks: time.sleep(5); continue
    try:
        req = urllib.request.Request('https://clob.polymarket.com/books', data=json.dumps([{'token_id': t} for t in toks]).encode(),
                                     headers={'User-Agent': 'Mozilla/5.0 pkarbs', 'Content-Type': 'application/json'})
        B = json.load(urllib.request.urlopen(req, timeout=10)); rm = int(time.time() * 1000)
        for b in B:
            bids = sorted(((float(x['price']), float(x['size'])) for x in b.get('bids', [])), reverse=True)[:15]
            asks = sorted((float(x['price']), float(x['size'])) for x in b.get('asks', []))[:15]
            h = hashlib.md5(json.dumps([bids, asks]).encode()).hexdigest()
            if last.get(b['asset_id']) == h: continue
            last[b['asset_id']] = h
            f.write(json.dumps(dict(recv_ms=rm, ts=b.get('timestamp'), tok=b['asset_id'], bids=bids, asks=asks)) + '\n')
        f.flush()
    except Exception as e:
        f.write(json.dumps(dict(recv_ms=int(time.time() * 1000), err=str(e)[:200])) + '\n'); f.flush()
    time.sleep(max(0, 1.0 - (time.time() - t0)))
