#!/usr/bin/env python3
"""TheSports free-trial timing capture (5 Nov 2026). Read-only: no orders, no money.

Question: does a TheSports message reach our server BEFORE the Polymarket price moves? Every row carries our own
receive time `ms` (UTC epoch ms, one clock for all streams), so delays vs the price need no clock sync.

Streams (JSONL under OUT, one file each):
  ts_mqtt.jsonl   every TheSports MQTT message, raw (topic, payload), stamped on receipt
  ts_poll.jsonl   optional HTTP polling of the paths in THESPORTS_POLL_PATHS, written only when the body changes
  books.jsonl     1 s Polymarket order books (top 15 levels) for every moneyline / game-winner token of live
                  tennis, LoL, CS2, Dota 2, NBA, NFL and cricket events, written only when the book changes
  markets.jsonl   event slug -> sport, title, start, question, tokens, outcomes
  pmws.jsonl      Polymarket sports WS rows for the same sports (free benchmark)
  log.jsonl       connects, errors, subscription acks, counts
Credentials only from env (installed by Hermes in /etc/pkarbs/thesports.env, never logged; see KEY-INSTALL-THESPORTS.md):
  THESPORTS_USER, THESPORTS_SECRET            account user and secret (both used for MQTT login and HTTP ?user=&secret=)
  THESPORTS_MQTT_HOST (mq.thesports.com), THESPORTS_MQTT_PORT (443), THESPORTS_MQTT_PATH (/mqtt),
  THESPORTS_MQTT_TRANSPORT (websockets|tcp), THESPORTS_TOPICS (comma list, from TheSports support; default '#')
  THESPORTS_API (https://api.thesports.com), THESPORTS_POLL_PATHS (comma list of path[@seconds], optional), THESPORTS_POLL_EVERY (2)
Usage: capture.py OUT HOURS [--share DIR] [--sports tennis,lol,cs2,dota2,nba,nfl] [--no-books]
Without credentials it still records books + PM WS (useful as a dry run) and logs 'thesports_no_creds'.
"""
import argparse, base64, gzip, hashlib, json, os, shutil, ssl, threading, time, urllib.parse, urllib.request

ap = argparse.ArgumentParser()
ap.add_argument('out'); ap.add_argument('hours', type=float)
ap.add_argument('--share', default='')
ap.add_argument('--sports', default='tennis,lol,cs2,dota2,nba,nfl,cricket')
ap.add_argument('--book-every', type=float, default=1.0)
ap.add_argument('--no-books', action='store_true')
A = ap.parse_args()
OUT = A.out; os.makedirs(OUT, exist_ok=True); END = time.time() + A.hours * 3600
SPORTS = set(A.sports.split(','))
GAMMA = 'https://gamma-api.polymarket.com'; CLOB = 'https://clob.polymarket.com'
UA = 'pkarbs-thesports-trial/1.0'
CA = os.environ.get('SSL_CERT_FILE') or ('/root/.ccr/ca-bundle.crt' if os.path.exists('/root/.ccr/ca-bundle.crt') else None)
CTX = ssl.create_default_context(cafile=CA)
E = os.environ
USER, SECRET = E.get('THESPORTS_USER', ''), E.get('THESPORTS_SECRET', '')
SECRETS = [s for s in (USER, SECRET) if len(s) >= 4]
# gamma tag slug, PM sports-WS leagueAbbreviation values
TAGS = {'tennis': ('tennis', {'atp', 'wta', 'challenger', 'itf', 'tennis'}), 'lol': ('league-of-legends', {'lol'}),
        'cs2': ('counter-strike-2', {'cs2'}), 'dota2': ('dota-2', {'dota2'}), 'nba': ('nba', {'nba'}),
        'nfl': ('nfl', {'nfl'}), 'cricket': ('cricket', {'cricket', 'bbl', 'wbbl', 'ipl', 'npl', 'ct20', 'psl', 'sa20', 'cpl', 'ilt20', 't20'})}
MKT_TYPES = (None, 'moneyline', 'child_moneyline')
_lock = threading.Lock(); files = {}; counts = {}


def redact(s):
    for x in SECRETS: s = s.replace(x, '[R]')
    return s


def rec(name, obj):
    line = redact(json.dumps(obj, separators=(',', ':'))) + '\n'
    with _lock:
        f = files.get(name) or files.setdefault(name, open(os.path.join(OUT, name + '.jsonl'), 'a', buffering=1))
        f.write(line); counts[name] = counts.get(name, 0) + 1


def ms(): return int(time.time() * 1000)


def http(url, data=None, timeout=10):
    h = {'User-Agent': UA}
    if data is not None: h['Content-Type'] = 'application/json'; data = json.dumps(data).encode()
    with urllib.request.urlopen(urllib.request.Request(url, data=data, headers=h), timeout=timeout, context=CTX) as r:
        return r.read()


# ---------------- TheSports MQTT (push) ----------------
def mqtt_thread():
    if not (USER and SECRET):
        rec('log', dict(ms=ms(), what='thesports_no_creds')); return
    try:
        import paho.mqtt.client as mqtt
    except ImportError:
        rec('log', dict(ms=ms(), what='thesports_err', err='paho-mqtt not installed (pip install --user paho-mqtt)')); return
    host = E.get('THESPORTS_MQTT_HOST', 'mq.thesports.com'); port = int(E.get('THESPORTS_MQTT_PORT', '443'))
    transport = E.get('THESPORTS_MQTT_TRANSPORT', 'websockets')
    topics = [t.strip() for t in E.get('THESPORTS_TOPICS', '#').split(',') if t.strip()]
    kw = dict(client_id='pkarbs-%d' % (time.time() % 100000), transport=transport)
    try: c = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, **kw)      # paho >= 2
    except AttributeError: c = mqtt.Client(**kw)                       # paho 1.x
    if transport == 'websockets': c.ws_set_options(path=E.get('THESPORTS_MQTT_PATH', '/mqtt'))
    c.tls_set_context(CTX); c.username_pw_set(USER, SECRET)
    c.reconnect_delay_set(1, 30)

    def on_connect(cl, ud, flags, rc, *a):
        rec('log', dict(ms=ms(), what='mqtt_connect', rc=str(rc), host=host, topics=topics))
        for t in topics: cl.subscribe(t, qos=0)

    def on_subscribe(cl, ud, mid, rcs, *a):
        rec('log', dict(ms=ms(), what='mqtt_suback', mid=mid, rc=[str(x) for x in (rcs if isinstance(rcs, list) else [rcs])]))

    def on_disconnect(cl, ud, *a):
        rec('log', dict(ms=ms(), what='mqtt_disconnect', info=[str(x) for x in a]))

    def on_message(cl, ud, m):
        R = ms()
        try: p = m.payload.decode('utf-8'); enc = 'utf8'
        except UnicodeDecodeError: p = base64.b64encode(m.payload).decode(); enc = 'b64'
        rec('ts_mqtt', dict(ms=R, topic=m.topic, enc=enc, p=p))

    c.on_connect, c.on_subscribe, c.on_disconnect, c.on_message = on_connect, on_subscribe, on_disconnect, on_message
    while time.time() < END:
        try:
            c.connect(host, port, keepalive=30); c.loop_start()
            while time.time() < END: time.sleep(1)
            c.loop_stop(); c.disconnect(); return
        except Exception as e:
            rec('log', dict(ms=ms(), what='mqtt_err', err=repr(e)[:300])); time.sleep(10)


# ---------------- TheSports HTTP polling (optional comparison) ----------------
def poll_thread():
    """THESPORTS_POLL_PATHS: comma list of 'path' or 'path@seconds' (default THESPORTS_POLL_EVERY, 2 s). Use a slow cadence
    (e.g. @300) for the schedule/diary endpoints, which are big, and 2 s for the real-time endpoints (the docs' suggested rate)."""
    specs = []
    for p in (x.strip() for x in E.get('THESPORTS_POLL_PATHS', '').split(',')):
        if not p: continue
        path, _, sec = p.partition('@')
        specs.append((path, float(sec) if sec else float(E.get('THESPORTS_POLL_EVERY', '2'))))
    if not (specs and USER and SECRET): return
    base = E.get('THESPORTS_API', 'https://api.thesports.com'); last = {}; due = {p: 0.0 for p, _ in specs}
    while time.time() < END:
        for path, every in specs:
            if time.time() < due[path]: continue
            t0 = time.time(); due[path] = t0 + every
            sep = '&' if '?' in path else '?'
            try:
                b = http(base + path + sep + urllib.parse.urlencode(dict(user=USER, secret=SECRET)), timeout=10); R = ms()
                h = hashlib.md5(b).hexdigest()
                if last.get(path) == h: continue
                last[path] = h
                rec('ts_poll', dict(ms=R, sent=int(t0 * 1000), path=path, body=b.decode('utf-8', 'replace')))
            except Exception as e:
                rec('log', dict(ms=ms(), what='poll_err', path=path, err=repr(e)[:200]))
        time.sleep(0.2)


# ---------------- Polymarket discovery + 1 s books ----------------
tokens = {}   # token -> (sport, slug, outcome)


def discover_pm():
    emin = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(time.time() - 3600)); new = 0
    for sp in sorted(SPORTS):
        tag = TAGS[sp][0]; evs = []
        for off in range(0, 1000, 50):
            q = urllib.parse.urlencode(dict(tag_slug=tag, active='true', closed='false', limit=50, offset=off, end_date_min=emin))
            r = json.loads(http(f'{GAMMA}/events?{q}', timeout=20)); evs += r or []
            if not r or len(r) < 50: break
        for ev in evs:
            slug = ev.get('slug', '')
            if 'more-markets' in slug: continue
            for m in ev.get('markets') or []:
                if m.get('sportsMarketType') not in MKT_TYPES: continue
                gst = m.get('gameStartTime') or ''
                try: st = time.mktime(time.strptime(gst[:19].replace(' ', 'T'), '%Y-%m-%dT%H:%M:%S')) - time.timezone
                except Exception: continue
                if not (st - 1200 <= time.time() <= st + 6 * 3600): continue   # 20 min before start to 6 h after
                try: toks = json.loads(m['clobTokenIds']); outs = json.loads(m['outcomes'])
                except Exception: continue
                fresh = False
                for tk, o in zip(toks, outs):
                    if tk not in tokens: tokens[tk] = (sp, slug, o); new += 1; fresh = True
                if fresh:
                    rec('markets', dict(ms=ms(), sport=sp, slug=slug, gid=ev.get('gameId'), title=ev.get('title'),
                                        start=gst, q=m.get('question'), smt=m.get('sportsMarketType'),
                                        cond=m.get('conditionId'), tokens=toks, outcomes=outs))
    rec('log', dict(ms=ms(), what='discover_pm', tokens=len(tokens), new=new))


def books_thread():
    last = {}; nxt = 0
    while time.time() < END:
        if time.time() > nxt:
            try: discover_pm()
            except Exception as e: rec('log', dict(ms=ms(), what='discover_pm_err', err=repr(e)[:200]))
            nxt = time.time() + 300
        t0 = time.time(); toks = list(tokens)
        for i in range(0, len(toks), 50):
            try:
                r = json.loads(http(f'{CLOB}/books', data=[{'token_id': t} for t in toks[i:i + 50]], timeout=10)); t1 = ms()
                for b in r:
                    tk = b.get('asset_id')
                    bids = sorted(b.get('bids') or [], key=lambda x: -float(x['price']))[:15]
                    asks = sorted(b.get('asks') or [], key=lambda x: float(x['price']))[:15]
                    h = hashlib.md5(repr((bids, asks)).encode()).hexdigest()
                    if last.get(tk) == h: continue
                    last[tk] = h
                    rec('books', dict(ms=t1, sent=int(t0 * 1000), tk=tk, ts=b.get('timestamp'), bids=bids, asks=asks))
            except Exception as e:
                rec('log', dict(ms=ms(), what='books_err', err=repr(e)[:200]))
        time.sleep(max(0.0, A.book_every - (time.time() - t0)))


# ---------------- Polymarket sports WS (free benchmark) ----------------
def pmws_thread():
    import websocket
    leagues = set().union(*(TAGS[s][1] for s in SPORTS))
    sslopt = {'ca_certs': CA} if CA else {}
    while time.time() < END:
        try:
            ws = websocket.create_connection('wss://sports-api.polymarket.com/ws', header=['User-Agent: ' + UA],
                                             sslopt=sslopt, timeout=30)
            rec('log', dict(ms=ms(), what='pmws_open'))
            while time.time() < END:
                try: m = ws.recv()
                except websocket.WebSocketTimeoutException: continue
                R = ms()
                if m == 'ping': ws.send('pong'); continue
                try: d = json.loads(m)
                except Exception: continue
                if str(d.get('leagueAbbreviation', '')).lower() in leagues: d['ms'] = R; rec('pmws', d)
        except Exception as e:
            rec('log', dict(ms=ms(), what='pmws_err', err=repr(e)[:200])); time.sleep(5)


def copy_share():
    os.makedirs(A.share, exist_ok=True)
    with _lock:
        for f in files.values(): f.flush()
    for n in os.listdir(OUT):
        if n.endswith('.jsonl'):
            with open(os.path.join(OUT, n), 'rb') as a, gzip.open(os.path.join(A.share, n + '.gz.tmp'), 'wb') as b:
                shutil.copyfileobj(a, b)
            os.replace(os.path.join(A.share, n + '.gz.tmp'), os.path.join(A.share, n + '.gz'))


def share_thread():
    while time.time() < END:
        time.sleep(600)
        rec('log', dict(ms=ms(), what='counts', counts=dict(counts)))
        if A.share:
            try: copy_share()
            except Exception as e: rec('log', dict(ms=ms(), what='share_err', err=repr(e)[:200]))


if __name__ == '__main__':
    rec('log', dict(ms=ms(), what='start', hours=A.hours, sports=sorted(SPORTS), creds=bool(USER and SECRET)))
    fs = [mqtt_thread, poll_thread, pmws_thread, share_thread] + ([] if A.no_books else [books_thread])
    for f in fs: threading.Thread(target=f, daemon=True).start()
    while time.time() < END: time.sleep(5)
    time.sleep(2)
    rec('log', dict(ms=ms(), what='stop', counts=dict(counts)))
    if A.share: copy_share()
