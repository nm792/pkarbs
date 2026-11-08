#!/usr/bin/env python3
"""Tennis 1 s Polymarket order books + OddsPapi latency probe (5 Nov 2026).
Purpose: re-run the Pinnacle/bet365-triggered tennis backtest with real queue position, and measure how long it
takes us to receive an OddsPapi update and reach the CLOB. Pinnacle/bet365 price history is pulled afterwards from
OddsPapi's free /v4/historical-odds, so no live odds polling is needed for the backtest itself.
(Structure copied from live/cricket_feeds/capture.py.)

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
import argparse, hashlib, json, os, shutil, ssl, threading, time, urllib.parse, urllib.request
try:
    import requests
except ImportError:          # server may lack requests: minimal urllib shim with the same calls we use
    requests = None

ap = argparse.ArgumentParser()
ap.add_argument('out'); ap.add_argument('hours', type=float)
ap.add_argument('--probe-max', type=int, default=120, help='max billable OddsPapi calls for the latency probe')
ap.add_argument('--book-every', type=float, default=1.0)
ap.add_argument('--share', default='')
A = ap.parse_args()
OUT = A.out; os.makedirs(OUT, exist_ok=True); END = time.time() + A.hours * 3600
GAMMA = 'https://gamma-api.polymarket.com'; CLOB = 'https://clob.polymarket.com'
ESPN = 'https://site.api.espn.com/apis'
UA = 'Mozilla/5.0 pkarbs-tennis-books'
OPAPI = 'https://api.oddspapi.io/v4'
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
        r = s.get(f'{GAMMA}/events', params=dict(tag_slug='tennis', active='true', closed='false', limit=100,
                                                 offset=off, end_date_min=emin), timeout=20).json()
        evs += r or []
        if not r or len(r) < 100: break
    new = 0
    for ev in evs:
        slug = ev.get('slug', '')
        if 'more-markets' in slug: continue
        for m in ev.get('markets') or []:
            if m.get('sportsMarketType') not in (None, 'moneyline'): continue
            gst = m.get('gameStartTime') or ev.get('startTime') or ''
            try:
                st = time.mktime(time.strptime(gst[:19].replace(' ', 'T'), '%Y-%m-%dT%H:%M:%S')) - time.timezone
            except Exception:
                continue
            # from 20 min before start to 6 h after
            if not (st - 1200 <= time.time() <= st + 6 * 3600): continue
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
                    tk = b.get('asset_id'); key = (tuple(sorted((x['price'], x['size']) for x in b.get('bids', []))),
                                                   tuple(sorted((x['price'], x['size']) for x in b.get('asks', []))))
                    h = hashlib.md5(repr(key).encode()).hexdigest()
                    if last.get(tk) == h: continue
                    last[tk] = h
                    bids = sorted(b.get('bids') or [], key=lambda x: -float(x['price']))[:15]
                    asks = sorted(b.get('asks') or [], key=lambda x: float(x['price']))[:15]
                    rec('books', dict(ms=t1, sent=int(t0 * 1000), tk=tk, ts=b.get('timestamp'), bids=bids, asks=asks))
            except Exception as e:
                rec('log', dict(ms=ms(), what='books_err', err=repr(e)[:200]))
        time.sleep(max(0.0, A.book_every - (time.time() - t0)))



# ---------------- latency probe ----------------
def opkey():
    k = os.environ.get('ODDSPAPI_KEY')
    if not k:
        p = os.path.expanduser('~/.oddspapi_key')
        k = open(p).read().strip() if os.path.exists(p) else None
    return k


def probe_thread():
    """(a) CLOB round trip: GET /time every 60 s (proxy for order placement; no orders are sent).
    (b) OddsPapi: /v4/account (unmetered; key stripped before logging). If the plan has live odds and quota
    allows, poll /v4/odds for one live tennis fixture every 20 s, at most --probe-max billable calls, and log
    receive time vs the newest Pinnacle/bet365 changedAt / bookmakerChangedAt in the reply."""
    s = sess(); key = opkey(); used = 0; fx = []; nxt_fx = 0; last_clob = 0; allowed = False
    if key:
        try:
            a = s.get(f'{OPAPI}/account', params=dict(apiKey=key), timeout=15).json()
            sub = next((x for x in a.get('subscriptions', []) if x.get('is_active')), {})
            live = {b: v.get('has_live_odds') for b, v in (sub.get('bookmakers') or {}).items() if b in ('pinnacle', 'bet365')}
            left = (sub.get('request_limit') or 0) - (sub.get('request_count') or 0)
            budget = min(A.probe_max, int(left * 0.3))
            allowed = budget > 5
            rec('probe', dict(ms=ms(), what='account', live_odds=live, request_limit=sub.get('request_limit'),
                              request_count=sub.get('request_count'), websocket=sub.get('websocket_access'), budget=budget))
        except Exception as e:
            rec('log', dict(ms=ms(), what='account_err', err=repr(e)[:200])); budget = 0
    else:
        rec('log', dict(ms=ms(), what='no_oddspapi_key')); budget = 0
    while time.time() < END:
        if time.time() - last_clob >= 60:
            t0 = time.time()
            try:
                s.get(f'{CLOB}/time', timeout=10); rec('probe', dict(ms=ms(), what='clob_rtt', rtt_ms=round((time.time() - t0) * 1000, 1)))
            except Exception as e:
                rec('log', dict(ms=ms(), what='clob_rtt_err', err=repr(e)[:120]))
            last_clob = time.time()
        if allowed and used < budget:
            try:
                if time.time() > nxt_fx or not fx:
                    now = time.time()
                    r = s.get(f'{OPAPI}/fixtures', params=dict(apiKey=key, sportId=12, statusId=1,
                              **{'from': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(now - 6 * 3600)),
                                 'to': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(now + 600))}), timeout=20).json()
                    used += 1; nxt_fx = now + 1800
                    fx = [f['fixtureId'] for f in r if '(srl)' not in str(f.get('participant1Name', '')).lower()] if isinstance(r, list) else []
                    rec('probe', dict(ms=ms(), what='live_fixtures', n=len(fx)))
                if fx:
                    fid = fx[used % len(fx)]; t0 = time.time()
                    r = s.get(f'{OPAPI}/odds', params=dict(apiKey=key, fixtureId=fid, bookmakers='pinnacle,bet365'), timeout=15).json()
                    t1 = time.time(); used += 1
                    newest = {}
                    for bk, bo in (r.get('bookmakerOdds') or {}).items():
                        ch = []; bch = []
                        for mv in (bo.get('markets') or {}).values():
                            for ov in mv.get('outcomes', {}).values():
                                for pl in ov.get('players', {}).values():
                                    if pl.get('changedAt'): ch.append(pl['changedAt'])
                                    if pl.get('bookmakerChangedAt'): bch.append(pl['bookmakerChangedAt'])
                        newest[bk] = dict(changedAt=max(ch) if ch else None, bookmakerChangedAt=max(bch) if bch else None)
                    rec('probe', dict(ms=ms(), what='odds', fid=fid, sent=int(t0 * 1000), recv=int(t1 * 1000), newest=newest,
                                      status=r.get('statusName')))
            except Exception as e:
                rec('log', dict(ms=ms(), what='probe_err', err=repr(e)[:200])); used += 1
        time.sleep(20)


def share_thread():
    while A.share and time.time() < END + 60:
        time.sleep(600)
        try:
            os.makedirs(A.share, exist_ok=True)
            with _lock:
                for f in files.values(): f.flush()
            for n in os.listdir(OUT):
                if n.endswith('.jsonl'): shutil.copy2(os.path.join(OUT, n), os.path.join(A.share, n))
        except Exception as e:
            rec('log', dict(ms=ms(), what='share_err', err=repr(e)[:200]))


if __name__ == '__main__':
    rec('log', dict(ms=ms(), what='start', hours=A.hours))
    ths = [threading.Thread(target=f, daemon=True) for f in (books_thread, probe_thread, share_thread)]
    for t in ths: t.start()
    while time.time() < END: time.sleep(5)
    time.sleep(2)
    if A.share:
        os.makedirs(A.share, exist_ok=True)
        for n in os.listdir(OUT):
            if n.endswith('.jsonl'): shutil.copy2(os.path.join(OUT, n), os.path.join(A.share, n))
    rec('log', dict(ms=ms(), what='stop'))
