"""Cito tennis WebSocket logger (room "all": every POINT_UPDATE / MATCH_FINISHED) + Polymarket sports WS tennis rows,
each line stamped with our receive time. Writes hourly UTC files <outdir>/cito_tennis_YYYYMMDDTHH.jsonl and every
COPY_EVERY s gzips finished+current files into <copydir> (if given). Key from env CITO_API_KEY (never logged).
Usage: CITO_API_KEY=... python3 tennis_logger.py <seconds> <outdir> [copydir]   (4 Nov 2026)"""
import websocket, json, time, sys, os, threading, gzip, shutil, datetime as dt
DUR, OUT = float(sys.argv[1]), sys.argv[2]; COPY = sys.argv[3] if len(sys.argv) > 3 else None
COPY_EVERY = float(os.environ.get('COPY_EVERY', 1800))
K = os.environ['CITO_API_KEY']; CA = os.environ.get('CA_BUNDLE', '/root/.ccr/ca-bundle.crt')
SSL = {'ca_certs': CA} if os.path.exists(CA) else None
END = time.time() + DUR; lock = threading.Lock(); os.makedirs(OUT, exist_ok=True)
TENNIS = {'atp', 'wta', 'challenger', 'itf', 'tennis'}
def path(t): return os.path.join(OUT, 'cito_tennis_' + dt.datetime.fromtimestamp(t, dt.UTC).strftime('%Y%m%dT%H') + '.jsonl')
def w(o):
    s = json.dumps(o).replace(K, '[R]') + '\n'
    with lock:
        with open(path(o['rt']), 'a') as f: f.write(s)
def cito():
    while time.time() < END:
        try:
            ws = websocket.create_connection('wss://api.citoapi.com/api/v1/tennis/live/ws',
                                             header=['x-api-key: ' + K, 'User-Agent: pkarbs-research/1.0'], sslopt=SSL, timeout=30)
            ws.send(json.dumps({'action': 'subscribe', 'rooms': ['all']}))
            w({'src': 'cito_open', 'rt': time.time()}); last_ping = time.time()
            while time.time() < END:
                if time.time() - last_ping > 25: ws.send(json.dumps({'action': 'ping'})); last_ping = time.time()
                try: m = ws.recv()
                except websocket.WebSocketTimeoutException: continue
                w({'src': 'cito_tennis_ws', 'rt': time.time(), 'm': m})
        except Exception as e: w({'src': 'cito_err', 'rt': time.time(), 'e': str(e)[:200]}); time.sleep(10)
def pm():
    while time.time() < END:
        try:
            ws = websocket.create_connection('wss://sports-api.polymarket.com/ws', header=['User-Agent: pkarbs-research/1.0'], sslopt=SSL, timeout=30)
            w({'src': 'pm_open', 'rt': time.time()})
            while time.time() < END:
                try: m = ws.recv()
                except websocket.WebSocketTimeoutException: continue
                if m == 'ping': ws.send('pong'); continue
                if any(f'"leagueAbbreviation":"{lg}"' in m for lg in TENNIS): w({'src': 'pm', 'rt': time.time(), 'm': m})
        except Exception as e: w({'src': 'pm_err', 'rt': time.time(), 'e': str(e)[:200]}); time.sleep(5)
def copier():
    while COPY:
        stop = time.time() >= END
        os.makedirs(COPY, exist_ok=True)
        for fn in sorted(os.listdir(OUT)):
            if not fn.endswith('.jsonl'): continue
            src, dst = os.path.join(OUT, fn), os.path.join(COPY, fn + '.gz')
            with lock, open(src, 'rb') as a, gzip.open(dst + '.tmp', 'wb') as b: shutil.copyfileobj(a, b)
            os.replace(dst + '.tmp', dst)
        if stop: break
        time.sleep(min(COPY_EVERY, max(1, END - time.time())))
ts = [threading.Thread(target=f) for f in (cito, pm)]; [t.start() for t in ts]
c = threading.Thread(target=copier); c.start(); [t.join() for t in ts]; c.join()
