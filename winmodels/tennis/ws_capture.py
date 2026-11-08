"""Capture the Polymarket sports live-score stream (all leagues) with our receive time, for tennis feed-delay tests.
Usage: python3 ws_capture.py <seconds> <out.jsonl>   (4 Nov 2026)"""
import websocket, json, time, sys
dur, fn = float(sys.argv[1]), sys.argv[2]
t0 = time.time(); f = open(fn, 'a')
while time.time() - t0 < dur:
    try:
        ws = websocket.create_connection('wss://sports-api.polymarket.com/ws', header=['User-Agent: pkarbs-research/1.0'], sslopt={'ca_certs': '/root/.ccr/ca-bundle.crt'})
        ws.settimeout(10)
        while time.time() - t0 < dur:
            try: m = ws.recv()
            except websocket.WebSocketTimeoutException: continue
            f.write(json.dumps(dict(rt=time.time(), m=m)) + '\n'); f.flush()
    except Exception as e:
        f.write(json.dumps(dict(rt=time.time(), err=str(e))) + '\n'); time.sleep(2)
