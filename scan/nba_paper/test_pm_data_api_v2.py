"""Planted wrong-param test (R-080): a fake v2 server that, like the real one, ignores unknown params.
Checks: right param passes; wrong param ('condition_ids','markets') MUST raise; a row with no condition field MUST raise."""
import json, threading, http.server, urllib.parse, sys
sys.path.insert(0, __file__.rsplit('/', 1)[0])
import pm_data_api_v2 as D

A, B = '0x' + 'a' * 64, '0x' + 'b' * 64
DB = {A: [{'condition_id': A, 'price': 0.5, 'timestamp': 100}, {'condition_id': A, 'price': 0.5, 'timestamp': 200}, {'condition_id': A, 'price': 0.5, 'timestamp': 999}], B: [{'condition_id': B, 'price': 0.6, 'timestamp': 150}] * 3}


class H(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def do_GET(self):
        q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        c = (q.get('condition_id') or q.get('condition') or q.get('conditionId') or [None])[0]
        rows = DB[c] if c in DB else DB[B] + DB[A]       # unknown params ignored: OTHER markets' rows
        if 'nofield' in q.get('x', []):
            rows = [{'price': 1}]
        self.send_response(200); self.end_headers()
        self.wfile.write(json.dumps({'data': rows, 'pagination': {'has_more': False}}).encode())


s = http.server.HTTPServer(('127.0.0.1', 0), H)
threading.Thread(target=s.serve_forever, daemon=True).start()
base = 'http://127.0.0.1:%d' % s.server_port
fails = 0


def ok(name, cond):
    global fails
    print(('PASS ' if cond else 'FAIL ') + name)
    fails += 0 if cond else 1


ok('right param returns only requested market', len(D.fetch_trades(A, base=base)) == 3)
for bad in ('condition_ids', 'markets', 'market'):
    try:
        D.fetch_trades(A, base=base, param=bad); ok('wrong param %s must raise' % bad, False)
    except D.WrongMarketRows:
        ok('wrong param %s raises' % bad, True)
try:
    D.check_rows([{'price': 1}], A); ok('row without condition field must raise', False)
except D.WrongMarketRows:
    ok('row without condition field raises', True)
# planted out-of-window trade (ts 999) must be excluded; server ignores any start/end like the real v2
w = D.fetch_trades(A, base=base, start=50, end=300)
ok('planted out-of-window trade excluded', [r['timestamp'] for r in w] == [100, 200])
ok('no window returns all 3', len(D.fetch_trades(A, base=base)) == 3)
sys.exit(1 if fails else 0)
