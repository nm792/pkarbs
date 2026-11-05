#!/usr/bin/env python3
"""Cricket live capture: free feeds vs the Polymarket price (5 Nov 2026, for BBL from 12 Dec).

Writes JSONL under OUT (one file per stream, every row has local receive ms):
  books.jsonl   full order book (POST clob /books, ~1 s poll) for every moneyline token of cricket
                events starting within the window; written only when the book changes
  markets.jsonl event slug -> condition, question, tokens, outcomes (each discover)
  espn.jsonl    ESPN site.api ball-by-ball (playbyplay), polled every --espn-every s for every ESPN
                cricket match in state 'in'; one row per new ball (first poll of a match flagged)
  espn_hdr.jsonl ESPN scoreboard header snapshot of live matches (score string), each discover
  sports.jsonl  every Polymarket sports-WS message that looks like cricket (league starts 'cri'
                or text mentions cricket), raw
  log.jsonl     discover counts and errors
Usage: capture.py OUT HOURS [--espn-every 1.0] [--share DIR]
ESPNcricinfo (hs-consumer-api / www) returns Akamai 403 to this IP, so it is not polled.
"""
import argparse, asyncio, hashlib, json, os, shutil, ssl, threading, time, urllib.parse, urllib.request
import websockets
try:
    import requests
except ImportError:          # server may lack requests: minimal urllib shim with the same calls we use
    requests = None

ap = argparse.ArgumentParser()
ap.add_argument('out'); ap.add_argument('hours', type=float)
ap.add_argument('--espn-every', type=float, default=1.0)
ap.add_argument('--book-every', type=float, default=1.0)
ap.add_argument('--share', default='')
A = ap.parse_args()
OUT = A.out; os.makedirs(OUT, exist_ok=True); END = time.time() + A.hours * 3600
GAMMA = 'https://gamma-api.polymarket.com'; CLOB = 'https://clob.polymarket.com'
ESPN = 'https://site.api.espn.com/apis'
UA = 'Mozilla/5.0 pkarbs-cricket-feeds'
CTX = ssl.create_default_context(cafile=os.environ.get('SSL_CERT_FILE') or None)
_lock = threading.Lock(); files = {}


def rec(name, obj):
    with _lock:
        f = files.get(name) or files.setdefault(name, open(os.path.join(OUT, name + '.jsonl'), 'a', buffering=1))
        f.write(json.dumps(obj, separators=(',', ':')) + '\n')


def ms(): return int(time.time() * 1000)


class _Resp:
    def __init__(self, b): self.b = b
    def json(self): return json.loads(self.b)


class _Sess:
    def _go(self, url, params=None, data=None, timeout=10):
        if params: url += '?' + urllib.parse.urlencode(params)
        h = {'User-Agent': UA}
        if data is not None: h['Content-Type'] = 'application/json'
        req = urllib.request.Request(url, data=data, headers=h)
        with urllib.request.urlopen(req, timeout=timeout, context=CTX) as r: return _Resp(r.read())
    def get(self, url, params=None, timeout=10): return self._go(url, params, None, timeout)
    def post(self, url, json=None, timeout=10): return self._go(url, None, __import__('json').dumps(json).encode(), timeout)


def sess():
    if requests is None: return _Sess()
    s = requests.Session(); s.headers['User-Agent'] = UA; return s


# ---------------- Polymarket discovery + books ----------------
tokens = {}   # token -> (slug, question, outcome)


def discover_pm(s):
    evs = []
    emin = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(time.time() - 3600))
    for off in range(0, 1000, 100):
        r = s.get(f'{GAMMA}/events', params=dict(tag_slug='cricket', active='true', closed='false', limit=100,
                                                 offset=off, end_date_min=emin), timeout=20).json()
        evs += r or []
        if not r or len(r) < 100: break
    new = 0
    for ev in evs:
        slug = ev.get('slug', '')
        if any(k in slug for k in ('more-markets', 'toss', 'sixes', 'top-batter')): continue
        for m in ev.get('markets') or []:
            if m.get('sportsMarketType') not in (None, 'moneyline'): continue
            gst = m.get('gameStartTime') or ev.get('startTime') or ''
            try:
                st = time.mktime(time.strptime(gst[:19].replace(' ', 'T'), '%Y-%m-%dT%H:%M:%S')) - time.timezone
            except Exception:
                continue
            # T20/T10/ODI: from 20 min before start to 10 h after; Tests run for days, keep 5 days
            if not (st - 1200 <= time.time() <= st + 5 * 86400): continue
            try: toks = json.loads(m['clobTokenIds']); outs = json.loads(m['outcomes'])
            except Exception: continue
            for tk, o in zip(toks, outs):
                if tk not in tokens: tokens[tk] = (slug, m.get('question'), o); new += 1
            rec('markets', dict(ms=ms(), slug=slug, gid=ev.get('gameId'), title=ev.get('title'), vol=ev.get('volume'),
                                start=gst, q=m.get('question'), cond=m.get('conditionId'), tokens=toks, outcomes=outs))
    rec('log', dict(ms=ms(), what='discover_pm', tokens=len(tokens), new=new))


def books_thread():
    s = sess(); last = {}; nxt = 0
    while time.time() < END:
        if time.time() > nxt:
            try: discover_pm(s)
            except Exception as e: rec('log', dict(ms=ms(), what='discover_pm_err', err=repr(e)))
            nxt = time.time() + 300
        t0 = time.time(); toks = list(tokens)
        for i in range(0, len(toks), 50):
            chunk = toks[i:i + 50]
            try:
                r = s.post(f'{CLOB}/books', json=[{'token_id': t} for t in chunk], timeout=10)
                t1 = ms()
                for b in r.json():
                    tk = b.get('asset_id'); key = (tuple((x['price'], x['size']) for x in b.get('bids', [])),
                                                   tuple((x['price'], x['size']) for x in b.get('asks', [])))
                    h = hashlib.md5(repr(key).encode()).hexdigest()
                    if last.get(tk) == h: continue
                    last[tk] = h
                    rec('books', dict(ms=t1, sent=int(t0 * 1000), tk=tk, ts=b.get('timestamp'), bids=b.get('bids'),
                                      asks=b.get('asks')))
            except Exception as e:
                rec('log', dict(ms=ms(), what='books_err', err=repr(e)[:200]))
        time.sleep(max(0.0, A.book_every - (time.time() - t0)))


# ---------------- ESPN ball by ball ----------------
live_espn = {}   # espn id -> name
# first-class domestic: no Polymarket in-play market worth timing, and polling ~25 of them at 1 Hz is abusive
SKIP_LEAGUES = ('Ranji', 'Quaid-e-Azam', 'Sheffield Shield', 'County Championship', 'Plunket Shield', 'Duleep', 'Irani')


def espn_discover(s):
    d = s.get(f'{ESPN}/personalized/v2/scoreboard/header', params=dict(sport='cricket'), timeout=15).json()
    cur = {}
    for sp in d.get('sports', []):
        for lg in sp.get('leagues', []):
            for e in lg.get('events', []):
                ln = lg.get('name') or ''
                if e.get('status') == 'in' and not any(k in ln for k in SKIP_LEAGUES):
                    cur[e['id']] = f"{lg.get('name')} | {e.get('name')}"
                    rec('espn_hdr', dict(ms=ms(), id=e['id'], league=lg.get('name'), name=e.get('name'),
                                         summary=e.get('summary'), comps=[(c.get('abbreviation'), c.get('score'))
                                                                          for c in e.get('competitors', [])]))
    return cur


def espn_items(s, ev, pc_hint):
    base = f'{ESPN}/site/v2/sports/cricket/8039/playbyplay'
    pc = pc_hint.get(ev)
    if pc:
        d = s.get(base, params=dict(event=ev, page=pc), timeout=10).json()
        c = d.get('commentary', {})
        if (c.get('pageCount') or pc) != pc:    # rolled over: re-read the new last page
            pc = c.get('pageCount'); d = s.get(base, params=dict(event=ev, page=pc), timeout=10).json()
    else:
        d = s.get(base, params=dict(event=ev), timeout=10).json()
        pc = d.get('commentary', {}).get('pageCount') or 1
        if pc > 1: d = s.get(base, params=dict(event=ev, page=pc), timeout=10).json()
    pc_hint[ev] = pc
    return d.get('commentary', {}).get('items', [])


def espn_match_thread(ev):
    s = sess(); seen = set(); first = True; pc_hint = {}; fails = 0
    while time.time() < END and ev in live_espn:
        t0 = time.time()
        try:
            items = espn_items(s, ev, pc_hint); t1 = time.time()
            for x in items:
                k = x.get('id')
                if k in seen: continue
                seen.add(k)
                rec('espn', dict(ms=int(t0 * 1000), done=int(t1 * 1000), ev=ev, id=k, seq=x.get('sequence'),
                                 over=(x.get('over') or {}).get('overs'), inn=x.get('period'),
                                 home=x.get('homeScore'), away=x.get('awayScore'),
                                 play=(x.get('playType') or {}).get('description'), sv=x.get('scoreValue'),
                                 bat=(x.get('team') or {}).get('abbreviation'), text=x.get('shortText'), first=first))
            first = False; fails = 0
        except Exception as e:
            fails += 1
            if fails in (1, 10, 100): rec('log', dict(ms=ms(), what='espn_err', ev=ev, err=repr(e)[:200]))
        time.sleep(max(0.0, A.espn_every - (time.time() - t0)))


def espn_thread():
    s = sess(); running = {}
    while time.time() < END:
        try:
            cur = espn_discover(s)
            for k in list(live_espn):
                if k not in cur: live_espn.pop(k, None)
            live_espn.update(cur)
            for ev in cur:
                if ev not in running or not running[ev].is_alive():
                    running[ev] = threading.Thread(target=espn_match_thread, args=(ev,), daemon=True); running[ev].start()
            rec('log', dict(ms=ms(), what='discover_espn', live=list(cur.values())))
        except Exception as e:
            rec('log', dict(ms=ms(), what='discover_espn_err', err=repr(e)[:200]))
        time.sleep(90)


# ---------------- Polymarket sports WS ----------------
async def sports_loop():
    while time.time() < END:
        try:
            async with websockets.connect('wss://sports-api.polymarket.com/ws', ssl=CTX, user_agent_header=UA,
                                          ping_interval=None, max_size=None) as ws:
                while time.time() < END:
                    msg = await asyncio.wait_for(ws.recv(), 60)
                    if msg == 'ping': await ws.send('pong'); continue
                    low = msg.lower()
                    try: lg = (json.loads(msg).get('leagueAbbreviation') or '').lower()
                    except Exception: lg = ''
                    if lg.startswith('cri') or 'cricket' in low or lg in ('ipl', 'bbl', 'wbbl', 'psl', 'npl', 'crint'):
                        rec('sports', dict(ms=ms(), raw=msg))
        except Exception as e:
            rec('log', dict(ms=ms(), what='sports_err', err=repr(e)[:200])); await asyncio.sleep(3)


def share_thread():
    while time.time() < END + 60 and A.share:
        time.sleep(600)
        try:
            os.makedirs(A.share, exist_ok=True)
            for fn in os.listdir(OUT):
                if fn.endswith('.jsonl'): shutil.copy(os.path.join(OUT, fn), A.share)
        except Exception as e:
            rec('log', dict(ms=ms(), what='share_err', err=repr(e)[:200]))


def main():
    for f in (books_thread, espn_thread, share_thread):
        threading.Thread(target=f, daemon=True).start()
    asyncio.run(sports_loop())
    time.sleep(5)
    if A.share:
        for fn in os.listdir(OUT):
            if fn.endswith('.jsonl'): shutil.copy(os.path.join(OUT, fn), A.share)


if __name__ == '__main__':
    main()
