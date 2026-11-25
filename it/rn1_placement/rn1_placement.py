"""RN1 placement measurement (R-090 item 2): where is each RN1 MAKER fill priced relative to the token's OWN best bid/ask just before the fill?
Inputs: fills.jsonl (RN1 maker fills: ts, token_id, price, size; from v2 trades user= with taker_only set difference, wallet asserted) and the P106e books
(books.jsonl.gz rows: recv_ms, asset, bids[[p,s],..], asks[[p,s],..], best bid first). Own book of the SAME token only (SETTLED A1).
Uses only book rows with recv_ms <= fill_ts*1000 (no hindsight). Fill ts has 1 s resolution, so a book row up to 1 s after the second still precedes the fill: rule = last row with recv_ms < (ts+1)*1000 - 0, flagged 'ambiguous_1s' if a change occurred inside that second.
Classes: inside (bid < p < ask), at_bid, below_bid_within_2c, below_bid_deeper, at_or_above_ask (taker-like), no_book (no row within 60 s)."""
import json, gzip, bisect, collections, sys

def classify(p, bid, ask, tick=0.01):
    if bid is None or ask is None: return 'no_book'
    e = tick / 2
    if p >= ask - e: return 'at_or_above_ask'
    if p > bid + e: return 'inside'
    if abs(p - bid) <= e: return 'at_bid'
    return 'below_bid_within_2c' if bid - p <= 0.02 + e else 'below_bid_deeper'

def load_books(path):
    by = collections.defaultdict(list)
    for line in gzip.open(path, 'rt'):
        r = json.loads(line)
        if r.get('bids') is None or r.get('asks') is None: continue
        bb = r['bids'][0][0] if r['bids'] else None; ba = r['asks'][0][0] if r['asks'] else None
        by[r['asset']].append((r['recv_ms'], float(bb) if bb is not None else None, float(ba) if ba is not None else None))
    for v in by.values(): v.sort()
    return by

def run(fills, books, tick=0.01, max_age_s=60):
    out = collections.Counter(); notl = collections.Counter()
    for f in fills:
        rows = books.get(f['token_id'], []); t = f['ts'] * 1000
        i = bisect.bisect_right([x[0] for x in rows], t) - 1
        if i < 0 or t - rows[i][0] > max_age_s * 1000: c = 'no_book'
        else: c = classify(f['price'], rows[i][1], rows[i][2], tick)
        out[c] += 1; notl[c] += f['size'] * f['price']
    return out, notl

if __name__ == '__main__':
    fills = [json.loads(l) for l in open(sys.argv[1])]
    o, n = run(fills, load_books(sys.argv[2]), float(sys.argv[3]) if len(sys.argv) > 3 else 0.01)
    tot = sum(n.values()) or 1
    for c in ('inside', 'at_bid', 'below_bid_within_2c', 'below_bid_deeper', 'at_or_above_ask', 'no_book'):
        print(f'{c:22s} fills {o[c]:6d}  notional ${n[c]:10.0f}  {100*n[c]/tot:5.1f}%')
