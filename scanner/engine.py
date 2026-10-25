"""Locked-payout cost at executable depth.

A structure is a list of buckets that together cover every outcome (MECE). Each bucket lists one
or more instruments that pay $1 in that bucket's outcomes (and >= $0 elsewhere). An instrument is
one or more legs bought together (e.g. a Senate x oil combo pair). Buying one unit of one
instrument per bucket pays >= $1 in every state, so cost < $1 is a locked edge, subject to the
structure's basis notes.

walk() takes sets greedily: at each step every bucket uses its cheapest instrument at the current
top of book (price + taker fee), and stops when the marginal set costs more than 1 - min_edge."""
import math
from fees import kalshi_unit, pm_unit, kalshi_fee, pm_fee

def _unit(book, price):
    return kalshi_unit(price) if book.venue == 'kalshi' else pm_unit(price, book.fee_rate)

def walk(struct, books, min_edge=0.0, max_capital=math.inf, max_sets=math.inf):
    lad = {}
    for b in struct['buckets']:
        for ins in b['instruments']:
            for leg in ins['legs']:
                if leg not in books: return dict(ok=False, reason=f'missing book {leg}')
                lad[leg] = [list(x) for x in books[leg].asks]
    fills = {}            # (leg, price) -> qty
    sets = 0.0; outlay = 0.0; first_px = None; last_px = None; used = {}
    while sets < max_sets:
        choice = []
        for b in struct['buckets']:
            best = None
            for ins in b['instruments']:
                if any(not lad[l] for l in ins['legs']): continue
                px = sum(lad[l][0][0] + _unit(books[l], lad[l][0][0]) for l in ins['legs'])
                q = min(lad[l][0][1] for l in ins['legs'])
                if best is None or px < best[0]: best = (px, q, ins)
            if best is None: choice = None; break
            choice.append(best)
        if not choice: break
        px = sum(c[0] for c in choice)
        if px > 1 - min_edge + 1e-12: break
        q = min(min(c[1] for c in choice), max_sets - sets)
        if outlay + q * px > max_capital: q = (max_capital - outlay) / px
        if q <= 1e-9: break
        for _, _, ins in choice:
            used[ins['name']] = used.get(ins['name'], 0) + q
            for l in ins['legs']:
                p = lad[l][0][0]
                fills[(l, p)] = fills.get((l, p), 0) + q
                lad[l][0][1] -= q
                if lad[l][0][1] <= 1e-9: lad[l].pop(0)
        if first_px is None: first_px = px
        last_px = px; sets += q; outlay += q * px
    gross = sum(p * q for (l, p), q in fills.items())
    fees = 0.0
    for (l, p), q in fills.items():
        bk = books[l]
        fees += kalshi_fee(p, q) if bk.venue == 'kalshi' else pm_fee(p, q, bk.fee_rate)
    cost = gross + fees
    profit = sets - cost
    return dict(ok=True, sets=sets, gross=gross, fees=fees, cost=cost, profit=profit,
                ret=(profit / cost if cost else 0.0), best_px=first_px, worst_px=last_px, used=used)

def top_edge(struct, books):
    """Edge of the very first set (1 - marginal cost), or None if the structure can't be priced."""
    r = walk(struct, books, min_edge=-1.0, max_sets=1e-6)
    return None if not r.get('ok') or r['best_px'] is None else 1 - r['best_px']
