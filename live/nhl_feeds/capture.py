#!/usr/bin/env python3
"""NHL live capture for the feed-vs-price timing question (5 Nov 2026).

Streams (JSONL, one file each, under OUT):
  sports.jsonl  every NHL message from the Polymarket sports WS, with local receive ms (recv_ms)
  books.jsonl   full-depth order book (POST clob /books, 1 s poll) for moneyline tokens of games in progress,
                written only when the book hash changes
  markets.jsonl PM event -> moneyline condition, tokens, outcomes (rewritten on each discover)
  nhl.jsonl     api-web.nhle.com play-by-play, polled 1 s per live game with a cache-busting query
                (the CDN otherwise serves copies up to 19 s old); new plays and score/clock changes
  espn.jsonl    ESPN NHL summary, polled 2 s per live game; new plays (carry ESPN wallclock)
  sched.jsonl   NHL schedule rows; log.jsonl  status/errors
Every 10 min the files are gzipped to COPY (shared folder) from scratch.
Usage: capture.py OUT HOURS [COPY]
"""
import asyncio, gzip, json, os, shutil, ssl, sys, time, urllib.request, urllib.parse
import websockets

OUT = sys.argv[1]; HOURS = float(sys.argv[2]); COPY = sys.argv[3] if len(sys.argv) > 3 else None
os.makedirs(OUT, exist_ok=True)
END = time.time() + HOURS * 3600
GAMMA = 'https://gamma-api.polymarket.com'; NHL_SERIES = '10346'; UA = 'Mozilla/5.0 pkarbs-nhl-feeds'
CTX = ssl.create_default_context(cafile=os.environ.get('SSL_CERT_FILE') or None)
files = {}
def rec(name, obj):
    f = files.get(name) or files.setdefault(name, open(os.path.join(OUT, name + '.jsonl'), 'a', buffering=1))
    f.write(json.dumps(obj, separators=(',', ':')) + '\n')
def ms(): return int(time.time() * 1000)
def get(url):
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    with urllib.request.urlopen(req, timeout=15, context=CTX) as r: return json.loads(r.read())
def iso2t(s):
    return time.mktime(time.strptime(s[:19], '%Y-%m-%dT%H:%M:%S')) - time.timezone

tokens = {}   # token -> (eventId, outcome, start_t)
async def discover_loop():
    while time.time() < END:
        try:
            q = urllib.parse.urlencode(dict(series_id=NHL_SERIES, closed='false', order='startTime', ascending='true', limit=100))
            evs = await asyncio.to_thread(get, f'{GAMMA}/events?{q}')
            new = 0
            for ev in evs or []:
                st = ev.get('startTime') or ''
                try: st_t = iso2t(st)
                except Exception: continue
                if not (-2 * 3600 < time.time() - st_t < 5 * 3600): continue
                for m in ev.get('markets') or []:
                    if m.get('sportsMarketType') != 'moneyline': continue
                    try: toks = json.loads(m['clobTokenIds']); outs = json.loads(m['outcomes'])
                    except Exception: continue
                    for tk, o in zip(toks, outs):
                        if tk not in tokens: tokens[tk] = (ev.get('id'), o, st_t); new += 1
                    rec('markets', dict(ms=ms(), event=ev.get('id'), gid=ev.get('gameId'), title=ev.get('title'),
                                        slug=ev.get('slug'), vol=ev.get('volume'), start=st, cond=m.get('conditionId'),
                                        tokens=toks, outcomes=outs))
            rec('log', dict(ms=ms(), what='discover', tokens=len(tokens), new=new))
        except Exception as e:
            rec('log', dict(ms=ms(), what='discover_err', err=repr(e)))
        await asyncio.sleep(300)

abbrevs = set()
async def sports_loop():
    while time.time() < END:
        try:
            async with websockets.connect('wss://sports-api.polymarket.com/ws', ssl=CTX, user_agent_header=UA,
                                          open_timeout=20, ping_interval=None, max_size=2 ** 22) as ws:
                rec('log', dict(ms=ms(), what='sports_open'))
                while time.time() < END:
                    m = await asyncio.wait_for(ws.recv(), 60); R = ms()
                    if m == 'ping': await ws.send('pong'); continue
                    try: d = json.loads(m)
                    except Exception: continue
                    ab = str(d.get('leagueAbbreviation', '')).lower()
                    if ab not in abbrevs: abbrevs.add(ab); rec('log', dict(ms=R, what='abbrev', ab=ab))
                    if ab == 'nhl': d['recv_ms'] = R; rec('sports', d)
        except Exception as e:
            rec('log', dict(ms=ms(), what='sports_err', err=repr(e))); await asyncio.sleep(2)

def live_tokens():
    now = time.time()
    return [tk for tk, (e, o, st) in tokens.items() if -900 < now - st < 4.5 * 3600]

async def clob_loop():
    last = {}
    while time.time() < END:
        t0 = time.time(); toks = live_tokens()
        if toks:
            try:
                body = json.dumps([{'token_id': t} for t in toks]).encode()
                def post():
                    req = urllib.request.Request('https://clob.polymarket.com/books', data=body,
                                                 headers={'User-Agent': UA, 'Content-Type': 'application/json'})
                    with urllib.request.urlopen(req, timeout=10, context=CTX) as r: return json.loads(r.read())
                S = ms(); books = await asyncio.to_thread(post); R = ms()
                for b in books:
                    if last.get(b['asset_id']) == b.get('hash'): continue
                    last[b['asset_id']] = b.get('hash')
                    rec('books', dict(sent_ms=S, recv_ms=R, asset=b['asset_id'], ts=b.get('timestamp'),
                                      bids=b.get('bids'), asks=b.get('asks')))
            except Exception as e:
                rec('log', dict(ms=ms(), what='books_err', err=repr(e))); await asyncio.sleep(3)
        await asyncio.sleep(max(0.0, 1.0 - (time.time() - t0)))

nhl_live = {}   # nhl game id -> espn id or None
async def sched_loop():
    while time.time() < END:
        try:
            day = time.strftime('%Y-%m-%d', time.gmtime(time.time() - 10 * 3600))
            d = await asyncio.to_thread(get, f'https://api-web.nhle.com/v1/schedule/{day}')
            espn = await asyncio.to_thread(get, 'https://site.api.espn.com/apis/site/v2/sports/hockey/nhl/scoreboard')
            emap = {}
            for e in espn.get('events') or []:
                comp = e['competitions'][0]; ab = {c['homeAway']: c['team']['abbreviation'] for c in comp['competitors']}
                emap[(ab.get('away'), ab.get('home'))] = (e['id'], e['status']['type']['state'])
            now = time.time()
            for wk in d.get('gameWeek', [])[:2]:
                for g in wk['games']:
                    a, h = g['awayTeam']['abbrev'], g['homeTeam']['abbrev']
                    eid = None
                    for (ea, eh), (i, s) in emap.items():
                        if (ea, eh) == (a, h) or (ea[:2], eh[:2]) == (a[:2], h[:2]): eid = i
                    st = iso2t(g['startTimeUTC'])
                    rec('sched', dict(ms=ms(), id=g['id'], start=g['startTimeUTC'], away=a, home=h,
                                      away_name=g['awayTeam'].get('commonName', {}).get('default'),
                                      home_name=g['homeTeam'].get('commonName', {}).get('default'),
                                      state=g.get('gameState'), espn=eid))
                    if g.get('gameState') in ('LIVE', 'CRIT') or (-600 < now - st < 4 * 3600 and g.get('gameState') not in ('OFF', 'FINAL')):
                        if g['id'] not in nhl_live:
                            nhl_live[g['id']] = eid
                            asyncio.create_task(nhl_game(g['id'])); asyncio.create_task(espn_game(g['id'], eid))
                            rec('log', dict(ms=ms(), what='game_start', id=g['id'], espn=eid, away=a, home=h))
        except Exception as e:
            rec('log', dict(ms=ms(), what='sched_err', err=repr(e)))
        await asyncio.sleep(60)

async def nhl_game(gid):
    seen = set(); last_state = None; n = 0
    while time.time() < END:
        t0 = time.time(); n += 1
        try:
            S = ms(); d = await asyncio.to_thread(get, f'https://api-web.nhle.com/v1/gamecenter/{gid}/play-by-play?cb={S}'); R = ms()
            st = (d['awayTeam'].get('score'), d['homeTeam'].get('score'), d.get('gameState'),
                  d.get('periodDescriptor', {}).get('number'), d.get('clock', {}).get('timeRemaining'),
                  d.get('clock', {}).get('running'), d.get('clock', {}).get('inIntermission'))
            if st != last_state:
                last_state = st
                rec('nhl', dict(kind='state', id=gid, sent_ms=S, recv_ms=R, away=st[0], home=st[1], gs=st[2], per=st[3],
                                clock=st[4], running=st[5], inter=st[6]))
            for p in d.get('plays') or []:
                if p['eventId'] in seen: continue
                seen.add(p['eventId'])
                rec('nhl', dict(kind='play', id=gid, sent_ms=S, recv_ms=R, play=p))
            if d.get('gameState') in ('OFF', 'FINAL') : 
                rec('log', dict(ms=ms(), what='game_end', id=gid)); return
        except Exception as e:
            rec('log', dict(ms=ms(), what='nhl_err', id=gid, err=repr(e))); await asyncio.sleep(2)
        await asyncio.sleep(max(0.0, 1.0 - (time.time() - t0)))

async def espn_game(gid, eid):
    if not eid: return
    seen = set(); last = None
    while time.time() < END:
        t0 = time.time()
        try:
            S = ms(); d = await asyncio.to_thread(get, f'https://site.api.espn.com/apis/site/v2/sports/hockey/nhl/summary?event={eid}&cb={S}'); R = ms()
            comp = (d.get('header') or {}).get('competitions', [{}])[0]
            sc = tuple((c.get('homeAway'), c.get('score')) for c in comp.get('competitors', []))
            state = comp.get('status', {}).get('type', {}).get('state')
            if (sc, state) != last:
                last = (sc, state); rec('espn', dict(kind='state', id=gid, espn=eid, sent_ms=S, recv_ms=R, score=sc, state=state))
            for p in d.get('plays') or []:
                k = p.get('id')
                if k in seen: continue
                seen.add(k); rec('espn', dict(kind='play', id=gid, espn=eid, sent_ms=S, recv_ms=R, play=p))
            if state == 'post':
                return
        except Exception as e:
            rec('log', dict(ms=ms(), what='espn_err', id=gid, err=repr(e))); await asyncio.sleep(3)
        await asyncio.sleep(max(0.0, 2.0 - (time.time() - t0)))

async def copy_loop():
    if not COPY: return
    os.makedirs(COPY, exist_ok=True)
    while True:
        await asyncio.sleep(600 if time.time() < END else 0)
        for fn in os.listdir(OUT):
            if not fn.endswith('.jsonl'): continue
            tmp = os.path.join(OUT, fn + '.gz.tmp')
            with open(os.path.join(OUT, fn), 'rb') as fi, gzip.open(tmp, 'wb') as fo: shutil.copyfileobj(fi, fo)
            shutil.copyfile(tmp, os.path.join(COPY, fn + '.gz')); os.remove(tmp)
        rec('log', dict(ms=ms(), what='copied'))
        if time.time() >= END: return

async def main():
    tasks = [discover_loop(), sports_loop(), clob_loop(), sched_loop()]
    await asyncio.gather(*tasks, return_exceptions=True)

async def runner():
    c = asyncio.create_task(copy_loop())
    try: await asyncio.wait_for(main(), HOURS * 3600 + 60)
    except asyncio.TimeoutError: pass
    global END; END = time.time(); await c

asyncio.run(runner())
