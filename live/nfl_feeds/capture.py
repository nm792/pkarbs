#!/usr/bin/env python3
"""NFL live capture: feed delays vs the Polymarket PRICE, and queue at our bid (5 Nov 2026, thread "Measure NFL feed speed and value").

Writes JSONL under OUT (local receive ms on every row):
  sports.jsonl  every NFL message from the Polymarket sports WS
  espn.jsonl    ESPN summary (1 s poll per live game): each new play (id, text, type, wallclock, period, clock,
                scores, start/end down-distance-yardline), written once per new (id, score, text)
  sb.jsonl      ESPN scoreboard (1 s poll): situation.lastPlay id/text + scores, written on change
  books.jsonl   full-depth order book (POST /books, 1 s poll) for the NFL moneyline tokens, written on hash change
  markets.jsonl moneyline condition/tokens/outcomes;  log.jsonl
A game is live from kickoff-10 min to kickoff+4.5 h (the sports WS updated NFL only every 5 min on 2-3 Nov).
Usage: capture.py OUT HOURS
"""
import asyncio, json, os, ssl, sys, time, urllib.request, urllib.parse, datetime as dt
import websockets
OUT = sys.argv[1]; HOURS = float(sys.argv[2]); os.makedirs(OUT, exist_ok=True)
END = time.time() + HOURS * 3600
UA = 'Mozilla/5.0 pkarbs-nfl-feeds'; CTX = ssl.create_default_context(cafile=os.environ.get('SSL_CERT_FILE') or None)
ESPN = 'https://site.api.espn.com/apis/site/v2/sports/football/nfl'
files = {}
def rec(name, obj):
    f = files.get(name) or files.setdefault(name, open(os.path.join(OUT, name + '.jsonl'), 'a', buffering=1))
    f.write(json.dumps(obj, separators=(',', ':')) + '\n')
def ms(): return int(time.time() * 1000)
def ts(s): return dt.datetime.fromisoformat(s.replace('Z', '+00:00')).timestamp()
def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': UA}), timeout=10, context=CTX) as r: return json.loads(r.read())
tokens = {}; starts = {}   # token -> slug ; slug -> kickoff ts
def live(slug): return slug in starts and starts[slug] - 600 <= time.time() <= starts[slug] + 4.5 * 3600

async def discover_loop():
    while time.time() < END:
        try:
            evs = []; off = 0   # start_date_min filters on creation date, so page all open events of series 12185 (nfl-2026)
            while True:
                page = await asyncio.to_thread(get, 'https://gamma-api.polymarket.com/events?' + urllib.parse.urlencode(dict(series_id=12185, closed='false', limit=100, offset=off)))
                evs += page or []; off += 100
                if not page or len(page) < 100: break
            for e in evs or []:
                if not e.get('startTime') or abs(ts(e['startTime']) - time.time()) > 8 * 3600: continue
                for m in e.get('markets') or []:
                    if m.get('sportsMarketType') != 'moneyline': continue
                    toks = json.loads(m['clobTokenIds']); outs = json.loads(m['outcomes'])
                    if toks[0] not in tokens:
                        for t in toks: tokens[t] = e['slug']
                        starts[e['slug']] = ts(e['startTime'])
                        rec('markets', dict(ms=ms(), slug=e['slug'], start=e['startTime'], cond=m['conditionId'], tokens=toks, outcomes=outs, fee=m.get('feeSchedule')))
            rec('log', dict(ms=ms(), what='discover', tokens=len(tokens)))
        except Exception as e: rec('log', dict(ms=ms(), what='discover_err', err=repr(e)))
        await asyncio.sleep(600)

async def sports_loop():
    while time.time() < END:
        try:
            async with websockets.connect('wss://sports-api.polymarket.com/ws', ssl=CTX, user_agent_header=UA, open_timeout=20, ping_interval=None, max_size=2 ** 22) as ws:
                rec('log', dict(ms=ms(), what='sports_open'))
                while time.time() < END:
                    m = await asyncio.wait_for(ws.recv(), 60); R = ms()
                    if m == 'ping': await ws.send('pong'); continue
                    if '"nfl"' not in m: continue
                    try: d = json.loads(m)
                    except Exception: continue
                    d['recv_ms'] = R; rec('sports', d)
        except Exception as e: rec('log', dict(ms=ms(), what='sports_err', err=repr(e))); await asyncio.sleep(2)

async def books_loop():
    last = {}
    while time.time() < END:
        t0 = time.time(); toks = [t for t, s in tokens.items() if live(s)]
        if toks:
            try:
                body = json.dumps([{'token_id': t} for t in toks]).encode()
                def post():
                    req = urllib.request.Request('https://clob.polymarket.com/books', data=body, headers={'User-Agent': UA, 'Content-Type': 'application/json'})
                    with urllib.request.urlopen(req, timeout=10, context=CTX) as r: return json.loads(r.read())
                S = ms(); books = await asyncio.to_thread(post); R = ms()
                for b in books:
                    if last.get(b['asset_id']) == b.get('hash'): continue
                    last[b['asset_id']] = b.get('hash')
                    rec('books', dict(sent_ms=S, recv_ms=R, asset=b['asset_id'], ts=b.get('timestamp'), bids=b.get('bids'), asks=b.get('asks')))
            except Exception as e: rec('log', dict(ms=ms(), what='books_err', err=repr(e))); await asyncio.sleep(3)
        await asyncio.sleep(max(0.0, 1.0 - (time.time() - t0)))

def yl(s): return None if not s else [s.get('down'), s.get('distance'), s.get('yardLine'), (s.get('team') or {}).get('id')]
async def espn_game(eid):
    seen = set()
    while time.time() < END:
        t0 = time.time()
        try:
            S = ms(); d = await asyncio.to_thread(get, f'{ESPN}/summary?event={eid}'); R = ms()
            plays = [p for dr in ((d.get('drives') or {}).get('previous') or []) for p in dr.get('plays', [])]
            cur = (d.get('drives') or {}).get('current')
            if cur: plays += [p for p in cur.get('plays', []) if p.get('id') not in {q.get('id') for q in plays}]
            for p in plays:
                k = (p.get('id'), p.get('homeScore'), p.get('awayScore'), p.get('text'))
                if k in seen: continue
                seen.add(k)
                rec('espn', dict(sent_ms=S, recv_ms=R, eid=eid, id=p.get('id'), seq=p.get('sequenceNumber'), typ=(p.get('type') or {}).get('text'), text=(p.get('text') or '')[:160],
                                 wc=p.get('wallclock'), mod=p.get('modified'), per=(p.get('period') or {}).get('number'), clk=(p.get('clock') or {}).get('displayValue'),
                                 h=p.get('homeScore'), a=p.get('awayScore'), sc=p.get('scoringPlay'), st=yl(p.get('start')), en=yl(p.get('end')), yds=p.get('statYardage')))
            stt = (((d.get('header') or {}).get('competitions') or [{}])[0].get('status') or {}).get('type') or {}
            if stt.get('completed'): rec('log', dict(ms=ms(), what='espn_final', eid=eid)); return
        except Exception as e: rec('log', dict(ms=ms(), what='espn_err', eid=eid, err=repr(e)[:200])); await asyncio.sleep(2)
        await asyncio.sleep(max(0.0, 1.0 - (time.time() - t0)))

async def scoreboard_loop():
    started = set(); last = {}
    while time.time() < END:
        t0 = time.time()
        try:
            S = ms(); d = await asyncio.to_thread(get, f'{ESPN}/scoreboard'); R = ms()
            for e in d.get('events', []):
                state = e['status']['type'].get('state')
                if state == 'in' and e['id'] not in started:
                    started.add(e['id']); asyncio.create_task(espn_game(e['id'])); rec('log', dict(ms=ms(), what='espn_start', eid=e['id'], name=e['shortName']))
                c = e['competitions'][0]; si = c.get('situation') or {}; lp = si.get('lastPlay') or {}
                sc = {x['homeAway']: x.get('score') for x in c['competitors']}
                keep = dict(eid=e['id'], state=state, h=sc.get('home'), a=sc.get('away'), lp=lp.get('id'), lpt=(lp.get('text') or '')[:120], dd=si.get('downDistanceText'), clk=e['status'].get('displayClock'), per=e['status'].get('period'))
                if last.get(e['id']) != keep: last[e['id']] = keep; rec('sb', dict(sent_ms=S, recv_ms=R, **keep))
        except Exception as e: rec('log', dict(ms=ms(), what='sb_err', err=repr(e)[:200])); await asyncio.sleep(2)
        await asyncio.sleep(max(0.0, 1.0 - (time.time() - t0)))

async def main(): await asyncio.gather(discover_loop(), sports_loop(), books_loop(), scoreboard_loop())
asyncio.run(main())
