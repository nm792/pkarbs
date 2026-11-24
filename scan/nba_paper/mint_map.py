"""MINT mapping and de-duplication for the Nautilus paper node's trade feed (R-091 item 4b). TEST ORACLE + feed pre-processor spec; fills themselves are made by the Nautilus engine
(trade_execution=True), NOT by this file. Rules (Nick 03:33Z, as the MFW gate applied them):
 1. SAME-TOKEN prints pass through unchanged (a SELL-side print at or below our bid price can fill our bid; a BUY-side print cannot).
 2. OTHER-TOKEN BUYER prints are MAPPED to a FILL-ONLY tick on our token: a taker BUY of the other token at price q mints against our resting BUY at p >= 1 - q, so it is a SELL-aggressor tick on our token at price 1 - q.
    The mapped tick carries fill_only=True and must NEVER reach pricing, mid, markout or signals (consumers must drop fill_only ticks).
 3. DE-DUP: a mapped tick is dropped if an own-token print with the same (token, price, size, ts_event) exists (the same trade seen on both token feeds counts once).
 Price rounding: 1 - q is rounded to 3 decimals."""
from collections import namedtuple
Tick = namedtuple('Tick', 'token price size side ts_event fill_only')

def map_ticks(prints, own, other, mapping=True):
    """prints: iterable of dicts {token, price, size, side('BUY'|'SELL' = aggressor), ts_event}. Returns list of Tick for token `own`."""
    out, seen = [], set()
    ps = list(prints)
    for p in ps:
        if p['token'] == own:
            out.append(Tick(own, round(p['price'], 3), p['size'], p['side'], p['ts_event'], False)); seen.add((own, round(p['price'], 3), p['size'], p['ts_event']))
    if mapping:
        for p in ps:
            if p['token'] == other and p['side'] == 'BUY':
                px = round(1 - p['price'], 3)
                if (own, px, p['size'], p['ts_event']) in seen: continue          # rule 3
                out.append(Tick(own, px, p['size'], 'SELL', p['ts_event'], True))   # rule 2
                seen.add((own, px, p['size'], p['ts_event']))
    return sorted(out, key=lambda t: t.ts_event)

def pricing_view(ticks):
    """what pricing/mid/markout/signals may see: fill_only ticks are removed (rule 2)."""
    return [t for t in ticks if not t.fill_only]

def oracle_fills(bid_price, bid_size, ticks):
    """TEST ORACLE only: shares a resting BUY at bid_price fills from ticks (aggressor SELL at price <= bid_price), no queue ahead (new inside level)."""
    left, got = bid_size, 0
    for t in ticks:
        if t.side == 'SELL' and t.price <= bid_price and left > 0:
            q = min(left, t.size); got += q; left -= q
    return got

def post_only_ok(order_price, best_ask, tick=0.001):
    """pre-flight rule: a post-only BUY priced at or above the real own-token ask must be REJECTED, never accepted."""
    return order_price < best_ask - tick / 2
