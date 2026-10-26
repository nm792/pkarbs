"""Full-book stale pool on live Polymarket release events: if every resting order stayed and was hit after
the release, what would takers earn? Expected value under the book's own mid as the probability."""
import json, time, urllib.request
H = {'User-Agent': 'curl/8.5.0', 'Accept': 'application/json'}
def get(u):
    for i in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(u, headers=H), timeout=40) as f: return json.load(f)
        except Exception as ex: err = ex; time.sleep(2 ** i)
    raise err
EV = {'606422': 'FOMC Oct 28', '1120074': 'Payrolls Oct', '1120075': 'Unemployment Oct', '1189083': 'CPI MoM Oct',
      '1189074': 'CPI YoY Oct', '1189688': 'Core CPI MoM Oct', '1189689': 'Core CPI YoY Oct', '1197595': 'PPI YoY Oct'}
out = {}
for eid, name in EV.items():
    e = get('https://gamma-api.polymarket.com/events?id=' + eid)[0]
    tot = {'all': 0.0, 'w10': 0.0, 'w5': 0.0}; depth = 0.0; nm = 0
    for m in e['markets']:
        if m.get('closed') or not m.get('clobTokenIds'): continue
        yes = json.loads(m['clobTokenIds'])[0]
        b = get('https://clob.polymarket.com/book?token_id=' + yes)
        bids = [(float(x['price']), float(x['size'])) for x in b.get('bids', [])]
        asks = [(float(x['price']), float(x['size'])) for x in b.get('asks', [])]
        if not bids or not asks: continue
        bb, ba = max(p for p, _ in bids), min(p for p, _ in asks)
        q = (bb + ba) / 2; nm += 1
        for lab, w in (('all', 1.0), ('w10', 0.10), ('w5', 0.05)):
            A = sum((1 - p) * s for p, s in asks if p <= ba + w)
            B = sum(p * s for p, s in bids if p >= bb - w)
            tot[lab] += q * A + (1 - q) * B
        depth += sum(p * s for p, s in asks if p <= ba + 0.05) + sum(p * s for p, s in bids if p >= bb - 0.05)
    out[name] = tot
    print('%-18s markets=%2d  depth$ within 5c of touch=%8.0f  expected full-book pool: all levels $%8.0f | within 10c $%7.0f | within 5c $%7.0f | end %s' % (
        name, nm, depth, tot['all'], tot['w10'], tot['w5'], e.get('endDate', '')[:10]), flush=True)
