"""Normalise venue order books into 'what it costs to BUY this token': ascending ask ladders."""
import json

class Book:
    def __init__(self, asks, bids, ts=None, fetched=None, venue='pm', fee_rate=0.0):
        self.asks = sorted((float(p), float(s)) for p, s in asks if float(s) > 0)
        self.bids = sorted(((float(p), float(s)) for p, s in bids if float(s) > 0), reverse=True)
        self.ts = ts            # venue timestamp (s), None if the venue gives none
        self.fetched = fetched  # our fetch time (s)
        self.venue = venue
        self.fee_rate = fee_rate
    def crossed(self):
        return bool(self.asks and self.bids and self.bids[0][0] >= self.asks[0][0])

def pm_book(raw, fetched=None, fee_rate=0.0):
    """raw = clob /book JSON. Asks/bids for the token itself."""
    return Book([(x['price'], x['size']) for x in raw['asks']],
                [(x['price'], x['size']) for x in raw['bids']],
                ts=int(raw['timestamp']) / 1000, fetched=fetched, venue='pm', fee_rate=fee_rate)

def pm_mirror_no(yes):
    """NO token ladder implied by the YES book (NO ask = 1 - YES bid). Use the real NO book in
    production; this mirror is only for fixtures that lack it."""
    return Book([(round(1 - p, 6), s) for p, s in yes.bids], [(round(1 - p, 6), s) for p, s in yes.asks],
                ts=yes.ts, fetched=yes.fetched, venue='pm', fee_rate=yes.fee_rate)

def kalshi_books(raw, fetched=None):
    """raw = /markets/{t}/orderbook JSON (orderbook_fp with yes_dollars/no_dollars bid ladders).
    Kalshi shows bids only: buying YES lifts NO bids at 1-p, buying NO lifts YES bids at 1-p.
    Returns (yes_book, no_book). Kalshi gives no book timestamp, so ts = fetch time."""
    ob = raw.get('orderbook_fp') or raw.get('orderbook') or {}
    yb = [(float(p), float(s)) for p, s in (ob.get('yes_dollars') or [])]
    nb = [(float(p), float(s)) for p, s in (ob.get('no_dollars') or [])]
    yes = Book([(round(1 - p, 6), s) for p, s in nb], yb, ts=fetched, fetched=fetched, venue='kalshi')
    no = Book([(round(1 - p, 6), s) for p, s in yb], nb, ts=fetched, fetched=fetched, venue='kalshi')
    return yes, no

def kalshi_crossed(yes):
    """YES bid + NO bid > 1 means the Kalshi book is crossed (should never happen on a live book)."""
    return yes.crossed()
