"""Upper bound on the stale-quote pool from LIVE books of upcoming US releases (as in the 26 Oct addendum, scripts/macro12m/book.py):
if every resting order (YES book, levels within 10c of the touch) stayed through the release and the release resolved per the book's own mid,
an INFORMED taker (knows the release) earns on each ask at p: if that bracket wins, (1 - p - fee) * size, probability mid;
on each bid at p: if that bracket loses, (p - fee) * size, probability 1 - mid. EV = sum of those. mid = book mid of the YES book.
usage: live_book_bound.py EVENT_ID..."""
import json, sys, urllib.request
H = {'User-Agent': 'curl/8.5.0', 'Accept': 'application/json', 'Content-Type': 'application/json'}
def get(u, data=None):
    with urllib.request.urlopen(urllib.request.Request(u, data=data, headers=H), timeout=30) as f: return json.load(f)
for eid in sys.argv[1:]:
    e = get('https://gamma-api.polymarket.com/events?id=' + eid)[0]
    mk = [m for m in e['markets'] if not m.get('closed') and m.get('clobTokenIds')]
    toks = [json.loads(m['clobTokenIds'])[0] for m in mk]
    books = get('https://clob.polymarket.com/books', json.dumps([{'token_id': t} for t in toks]).encode())
    bk = {b['asset_id']: b for b in books}
    out = {0.05: 0.0, 0.01: 0.0}; depth = 0.0
    for m, t in zip(mk, toks):
        b = bk[t]; bids = [(float(r['price']), float(r['size'])) for r in b['bids']]; asks = [(float(r['price']), float(r['size'])) for r in b['asks']]
        if not bids or not asks: continue
        bb = max(p for p, s in bids); aa = min(p for p, s in asks); mid = (bb + aa) / 2
        for p, s in asks:
            if p <= aa + 0.10:
                depth += p * s
                for r in out: out[r] += mid * max(1 - p - r * p * (1 - p), 0) * s
        for p, s in bids:
            if p >= bb - 0.10:
                depth += p * s
                for r in out: out[r] += (1 - mid) * max(p - r * p * (1 - p), 0) * s
    print('%s %-45s end %s markets %d resting notional within 10c $%.0f | EV bound net@5%% $%.0f net@1%% $%.0f' % (eid, e['slug'][:45], e['endDate'], len(mk), depth, out[0.05], out[0.01]))
