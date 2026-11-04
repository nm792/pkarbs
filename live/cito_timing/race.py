"""Race Cito live push (SSE now; WebSocket once the add-on is active) against the Polymarket sports live-score WS.
Logs every message with our receive time to one JSONL. Key comes from env CITO_API_KEY (never logged).
Usage: CITO_API_KEY=... python3 race.py <seconds> <out.jsonl> [cs2|lol|ufc ...]   (4 Nov 2026)"""
import websocket, json, time, sys, os, threading, requests
DUR, OUT = float(sys.argv[1]), sys.argv[2]; GAMES = sys.argv[3:] or ['cs2']
K = os.environ['CITO_API_KEY']; CA = os.environ.get('CA_BUNDLE', '/root/.ccr/ca-bundle.crt')
CA = CA if os.path.exists(CA) else True
END = time.time() + DUR; lock = threading.Lock(); f = open(OUT, 'a')
def w(o):
    s = json.dumps(o).replace(K, '[R]')
    with lock: f.write(s + '\n'); f.flush()
def pm():
    while time.time() < END:
        try:
            ws = websocket.create_connection('wss://sports-api.polymarket.com/ws', header=['User-Agent: pkarbs-research/1.0'],
                                             sslopt={'ca_certs': CA} if CA is not True else None, timeout=20)
            while time.time() < END:
                try: m = ws.recv()
                except websocket.WebSocketTimeoutException: continue
                if m == 'ping': ws.send('pong'); continue
                w({'src': 'pm', 'rt': time.time(), 'm': m})
        except Exception as e: w({'src': 'pm_err', 'rt': time.time(), 'e': str(e)[:200]}); time.sleep(2)
def cito_sse(game):
    url = f'https://api.citoapi.com/api/v1/{game}/live/stream'
    while time.time() < END:
        try:
            r = requests.get(url, headers={'x-api-key': K, 'Accept': 'text/event-stream', 'User-Agent': 'pkarbs-research/1.0'},
                             stream=True, timeout=(10, 40), verify=CA)
            w({'src': f'cito_{game}_sse_open', 'rt': time.time(), 'code': r.status_code,
               'delay_hdr': r.headers.get('X-Cito-Data-Delay-Seconds'), 'tier': r.headers.get('X-Cito-Tier')})
            if 'event-stream' not in r.headers.get('content-type', ''):
                w({'src': f'cito_{game}_sse_notlive', 'rt': time.time(), 'body': r.text[:200]}); time.sleep(60); continue
            ev = None
            for line in r.iter_lines(decode_unicode=True):
                if time.time() > END: break
                if line is None: continue
                if line.startswith('event:'): ev = line[6:].strip()
                elif line.startswith('data:'): w({'src': f'cito_{game}', 'rt': time.time(), 'ev': ev, 'd': line[5:].strip()})
        except Exception as e: w({'src': f'cito_{game}_err', 'rt': time.time(), 'e': str(e)[:200]}); time.sleep(3)
def cito_poll(game, every=5.0):
    # REST cross-check of the push feed: /<game>/live every `every` s (costs 1 request each).
    url = f'https://api.citoapi.com/api/v1/{game}/live'; s = requests.Session()
    while time.time() < END:
        t = time.time()
        try:
            r = s.get(url, headers={'x-api-key': K, 'User-Agent': 'pkarbs-research/1.0'}, timeout=10, verify=CA)
            w({'src': f'cito_{game}_rest', 'rt': time.time(), 'lat': time.time() - t, 'd': r.text})
        except Exception as e: w({'src': f'cito_{game}_rest_err', 'rt': time.time(), 'e': str(e)[:160]})
        time.sleep(max(0, every - (time.time() - t)))
def cito_ws(game):
    url = f'wss://api.citoapi.com/api/v1/{game}/live/ws'
    while time.time() < END:
        try:
            ws = websocket.create_connection(url, header=['x-api-key: ' + K, 'User-Agent: pkarbs-research/1.0'],
                                             sslopt={'ca_certs': CA} if CA is not True else None, timeout=20)
            w({'src': f'cito_{game}_ws_open', 'rt': time.time()})
            rooms = [r for r in os.environ.get(f'CITO_{game.upper()}_ROOMS', '').split(',') if r] or ['all']
            ws.send(json.dumps({'action': 'subscribe', 'rooms': rooms}))  # LoL needs match:<id> / game:<id>
            while time.time() < END:
                try: m = ws.recv()
                except websocket.WebSocketTimeoutException: continue
                w({'src': f'cito_{game}_ws', 'rt': time.time(), 'm': m})
        except Exception as e:
            w({'src': f'cito_{game}_ws_err', 'rt': time.time(), 'e': str(e)[:160]}); time.sleep(60)
ts = [threading.Thread(target=pm)] + [threading.Thread(target=cito_sse, args=(g,)) for g in GAMES] + \
     [threading.Thread(target=cito_ws, args=(g,)) for g in GAMES + os.environ.get('CITO_WS_ONLY', '').split(',') if g] + \
     [threading.Thread(target=cito_poll, args=(g,)) for g in GAMES if g in os.environ.get('CITO_POLL', '').split(',')]
[t.start() for t in ts]; [t.join() for t in ts]
