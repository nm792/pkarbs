#!/usr/bin/env python3
"""CS2 live capture for the feed race and queue question (4 Nov 2026).

Writes JSONL (one file per stream) under OUT:
  sports.jsonl  every cs2 message from the Polymarket sports WS, with local receive ms
  books.jsonl   full-depth order book (POST /books, 1 s poll) for Match / Map 1-3 Winner tokens of live CS2 games,
                written only when the book hash changes (CLOB market WS host is not on our allowlist)
  markets.jsonl gameId -> condition, kind, tokens, outcomes (rewritten on each discover)
Extra feed probes are separate scripts writing <name>.jsonl in the same folder.
Usage: capture.py OUT HOURS
"""
import asyncio, json, os, ssl, sys, time, urllib.request, urllib.parse
import websockets

OUT = sys.argv[1]; HOURS = float(sys.argv[2]); os.makedirs(OUT, exist_ok=True)
END = time.time() + HOURS * 3600
GAMMA = 'https://gamma-api.polymarket.com'; CS2_SERIES = '10310'; UA = 'Mozilla/5.0 pkarbs-cs2-feeds'
CTX = ssl.create_default_context(cafile=os.environ.get('SSL_CERT_FILE') or None)
files = {}
def rec(name, obj):
    f = files.get(name) or files.setdefault(name, open(os.path.join(OUT, name + '.jsonl'), 'a', buffering=1))
    f.write(json.dumps(obj, separators=(',', ':')) + '\n')
def ms(): return int(time.time() * 1000)

def get(url):
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    with urllib.request.urlopen(req, timeout=20, context=CTX) as r: return json.loads(r.read())

tokens = {}  # token -> (gid, kind, outcome)
async def discover_loop(changed):
    while time.time() < END:
        try:
            smin = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(time.time() - 14 * 86400)); evs = []
            for off in range(0, 1000, 100):
                q = urllib.parse.urlencode(dict(series_id=CS2_SERIES, closed='false', start_date_min=smin, limit=100, offset=off))
                page = await asyncio.to_thread(get, f'{GAMMA}/events?{q}'); evs += page or []
                if not page or len(page) < 100: break
            new = 0
            for ev in evs:
                st = ev.get('startTime') or ''
                try: st_t = time.mktime(time.strptime(st[:19], '%Y-%m-%dT%H:%M:%S')) - time.timezone
                except Exception: continue
                if abs(st_t - time.time()) > 8 * 3600: continue
                for m in ev.get('markets') or []:
                    t = m.get('groupItemTitle') or ''
                    if t not in ('Match Winner', 'Map 1 Winner', 'Map 2 Winner', 'Map 3 Winner'): continue
                    try: toks = json.loads(m['clobTokenIds']); outs = json.loads(m['outcomes'])
                    except Exception: continue
                    for tk, o in zip(toks, outs):
                        if tk not in tokens:
                            tokens[tk] = (ev.get('gameId'), t, o); new += 1
                    rec('markets', dict(ms=ms(), gid=ev.get('gameId'), title=ev.get('title'), vol=ev.get('volume'),
                                        start=st, kind=t, cond=m.get('conditionId'), tokens=toks, outcomes=outs))
            rec('log', dict(ms=ms(), what='discover', tokens=len(tokens), new=new))
            if new: changed.set()
        except Exception as e:
            rec('log', dict(ms=ms(), what='discover_err', err=repr(e)))
        await asyncio.sleep(300)

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
                    if d.get('leagueAbbreviation') == 'cs2':
                        d['recv_ms'] = R; rec('sports', d)
                        if d.get('live') and not d.get('ended'): live_gids.add(d.get('gameId'))
                        elif d.get('gameId') in live_gids: live_gids.discard(d.get('gameId'))
        except Exception as e:
            rec('log', dict(ms=ms(), what='sports_err', err=repr(e))); await asyncio.sleep(2)

live_gids = set()
async def clob_loop(changed):
    """CLOB market WS is not on our network allowlist, so poll POST /books (full depth) every 1 s for the tokens of
    games the sports WS says are live; write a token's book only when it changed."""
    last = {}
    while time.time() < END:
        t0 = time.time()
        toks = [tk for tk, (gid, k, o) in tokens.items() if gid in live_gids]
        if toks:
            try:
                body = json.dumps([{'token_id': t} for t in toks]).encode()
                def post():
                    req = urllib.request.Request('https://clob.polymarket.com/books', data=body,
                                                 headers={'User-Agent': UA, 'Content-Type': 'application/json'})
                    with urllib.request.urlopen(req, timeout=10, context=CTX) as r: return json.loads(r.read())
                S = ms(); books = await asyncio.to_thread(post); R = ms()
                for b in books:
                    key = (b.get('hash'), )
                    if last.get(b['asset_id']) == key: continue
                    last[b['asset_id']] = key
                    rec('books', dict(sent_ms=S, recv_ms=R, asset=b['asset_id'], ts=b.get('timestamp'),
                                      bids=b.get('bids'), asks=b.get('asks')))
            except Exception as e:
                rec('log', dict(ms=ms(), what='books_err', err=repr(e))); await asyncio.sleep(5)
        await asyncio.sleep(max(0.0, 1.0 - (time.time() - t0)))

async def bo3_loop():
    """bo3.gg current matches every 3 s: map scores, game status and the Thunderpick live odds it mirrors
    (bet_updates). Written only when the record changes."""
    last = {}
    url = 'https://api.bo3.gg/api/v1/matches?filter[matches.status][in]=current&page[limit]=50'
    while time.time() < END:
        t0 = time.time()
        try:
            S = ms(); d = await asyncio.to_thread(get, url); R = ms()
            for m in d.get('results') or []:
                bu = m.get('bet_updates') or {}
                keep = dict(id=m['id'], slug=m.get('slug'), tier=m.get('tier'), s1=m.get('team1_score'), s2=m.get('team2_score'),
                            maps=m.get('maps_score'), lu=m.get('live_updates'),
                            c1=(bu.get('team_1') or {}).get('coeff'), c2=(bu.get('team_2') or {}).get('coeff'),
                            a1=(bu.get('team_1') or {}).get('active'), a2=(bu.get('team_2') or {}).get('active'),
                            prov=bu.get('provider'))
                if last.get(m['id']) == keep: continue
                last[m['id']] = keep; rec('bo3', dict(sent_ms=S, recv_ms=R, **keep))
        except Exception as e:
            rec('log', dict(ms=ms(), what='bo3_err', err=repr(e)))
        await asyncio.sleep(max(0.0, 3.0 - (time.time() - t0)))

async def main():
    changed = asyncio.Event()
    await asyncio.gather(discover_loop(changed), sports_loop(), clob_loop(changed), bo3_loop())

asyncio.run(main())
