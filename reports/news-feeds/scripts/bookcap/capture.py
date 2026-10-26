"""Read-only Polymarket order book capture around one scheduled release. Places no orders.

usage: capture.py OUTDIR R_EPOCH PRE_S POST_S EVENT_ID [EVENT_ID ...]
- REST: POST /books for every YES and NO token of the events, every 0.25 s (40 req/10 s, under the
  documented 50 req/10 s), from R-PRE_S to R+POST_S. One gzip JSONL line per poll.
- WebSocket market channel for the same tokens over the same window, every message logged with its
  local receive time.
Run under a hard time limit, e.g. `timeout 900 python3 capture.py ...`.
"""
import gzip, json, os, resource, sys, threading, time, urllib.request
resource.setrlimit(resource.RLIMIT_AS, (700 * 2 ** 20, 700 * 2 ** 20))
OUT, R, PRE, POST = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
EIDS = sys.argv[5:]
H = {'User-Agent': 'curl/8.5.0', 'Accept': 'application/json', 'Content-Type': 'application/json'}
os.makedirs(OUT, exist_ok=True)
def get(u, data=None):
    req = urllib.request.Request(u, data=data, headers=H)
    with urllib.request.urlopen(req, timeout=5) as f: return json.load(f)
tokens, meta = [], []
for eid in EIDS:
    e = get('https://gamma-api.polymarket.com/events?id=' + eid)[0]
    for m in e['markets']:
        if m.get('closed') or not m.get('clobTokenIds'): continue
        t = json.loads(m['clobTokenIds'])
        tokens += t
        meta.append({'event': eid, 'cid': m['conditionId'], 'item': m.get('groupItemTitle'), 'yes': t[0], 'no': t[1]})
def clock():  # /time returns whole server seconds; local minus server should sit in [0, 1) if the clock is right
    a = time.time(); s = get('https://clob.polymarket.com/time'); b = time.time()
    return {'local_mid': (a + b) / 2, 'rtt': b - a, 'server': s}
clk = [clock() for _ in range(5)]
json.dump({'R': R, 'events': EIDS, 'markets': meta, 'clock': clk}, open(OUT + '/meta.json', 'w'))
start, end = R - PRE, R + POST
print('tokens', len(tokens), 'start in %.0f s' % (start - time.time()), flush=True)
while time.time() < start - 5: time.sleep(1)
stop = threading.Event()
def ws_loop():
    import websocket
    f = gzip.open(OUT + '/ws.jsonl.gz', 'wt')
    while not stop.is_set():
        try:
            ws = websocket.create_connection('wss://ws-subscriptions-clob.polymarket.com/ws/market', timeout=5)
            ws.send(json.dumps({'assets_ids': tokens, 'type': 'market'}))
            last_ping = time.time()
            while not stop.is_set():
                if time.time() - last_ping > 9: ws.send('PING'); last_ping = time.time()
                try: msg = ws.recv()
                except websocket.WebSocketTimeoutException: continue
                f.write(json.dumps({'t': time.time(), 'm': msg}) + '\n')
            ws.close()
        except Exception as ex:
            f.write(json.dumps({'t': time.time(), 'err': str(ex)}) + '\n'); time.sleep(0.5)
    f.close()
th = threading.Thread(target=ws_loop, daemon=True); th.start()
body = json.dumps([{'token_id': t} for t in tokens]).encode()
f = gzip.open(OUT + '/books.jsonl.gz', 'wt'); n = errs = 0
nxt = time.time()
while time.time() < end:
    t0 = time.time()
    try:
        b = get('https://clob.polymarket.com/books', body)
        f.write(json.dumps({'t0': t0, 't1': time.time(), 'b': [{'a': x['asset_id'], 'ts': x.get('timestamp'), 'bids': x['bids'], 'asks': x['asks']} for x in b]}) + '\n')
        n += 1
    except Exception as ex:
        errs += 1; f.write(json.dumps({'t0': t0, 'err': str(ex)}) + '\n')
    nxt += 0.25
    time.sleep(max(0, nxt - time.time()))
f.close(); stop.set(); th.join(timeout=10)
print('polls', n, 'errors', errs, 'done', flush=True)
