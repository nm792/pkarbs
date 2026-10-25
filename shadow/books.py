"""One book replay shared by rescan.py (detector) and shadow_sim.py (fills), so they cannot drift apart.

Replay.feed(r, msgs) applies one raw record (receive time r, one or more WS/REST messages) to `books`:
- Gap reset: if r jumps by more than gap_s from the previous record, every book is cleared and every
  leg is unseeded. A leg is seeded again only by a full `book` message.
- Dedup per change: `book` on (asset_id, timestamp, hash); each `price_change` entry on (asset_id,
  timestamp, hash) taken from the entry itself (current WS format), falling back to the message's
  fields, and to (side, price, size) when there is no hash. Keys are kept only for dedup_window_s of
  receive time, so memory stays bounded on long files.
- A `book` older than the book's last exchange timestamp is ignored (a stale REST snapshot).
Returns the assets touched by the record.
"""
from collections import deque


class Book:
    __slots__ = ("bids", "asks", "ts")

    def __init__(self):
        self.bids, self.asks, self.ts = {}, {}, 0

    def best_ask(self):
        return min(self.asks) if self.asks else None

    def best_bid(self):
        return max(self.bids) if self.bids else None


class Replay:
    def __init__(self, books, gap_s=5.0, create=False, dedup_window_s=60.0):
        self.books = books            # asset -> Book-like (bids, asks, ts)
        self.create = create          # add books for unknown assets (sim) or ignore them (detector)
        self.gap_s = gap_s
        self.window = dedup_window_s
        self.seeded = set()
        self.last_r = None
        self.resets = 0
        self.skipped_s = 0.0
        self.dups = 0
        self._keys, self._order = set(), deque()

    def _book(self, aid):
        b = self.books.get(aid)
        if b is None and self.create and aid is not None:
            b = self.books[aid] = Book()
        return b

    def _dup(self, r, key):
        while self._order and r - self._order[0][0] > self.window:
            self._keys.discard(self._order.popleft()[1])
        if key in self._keys:
            self.dups += 1
            return True
        self._keys.add(key)
        self._order.append((r, key))
        return False

    def is_seeded(self, aid):
        return aid in self.seeded

    def feed(self, r, msgs):
        if self.last_r is not None and r - self.last_r > self.gap_s:
            for b in self.books.values():
                b.bids, b.asks, b.ts = {}, {}, 0
            self.seeded.clear()
            self.resets += 1
            self.skipped_s += r - self.last_r
        self.last_r = r
        touched = []
        for m in msgs if isinstance(msgs, list) else [msgs]:
            et = m.get("event_type")
            ts = int(m.get("timestamp") or 0)
            if et == "book":
                aid = m.get("asset_id")
                key = ("b", aid, ts, m.get("hash") or str(m.get("bids")) + str(m.get("asks")))
                if self._dup(r, key):
                    continue
                b = self._book(aid)
                if b is None or ts < b.ts:
                    continue
                b.bids = {float(x["price"]): float(x["size"]) for x in m.get("bids", [])}
                b.asks = {float(x["price"]): float(x["size"]) for x in m.get("asks", [])}
                b.ts = ts
                self.seeded.add(aid)
                touched.append(aid)
            elif et == "price_change":
                for c in m.get("price_changes") or m.get("changes") or []:
                    aid = c.get("asset_id") or m.get("asset_id")
                    h = c.get("hash") or m.get("hash") or (c.get("side"), c.get("price"), c.get("size"))
                    if self._dup(r, ("c", aid, ts, h)):
                        continue
                    b = self._book(aid)
                    if b is None:
                        continue
                    side = b.bids if c["side"].upper() == "BUY" else b.asks
                    p, s = float(c["price"]), float(c["size"])
                    if s == 0:
                        side.pop(p, None)
                    else:
                        side[p] = s
                    b.ts = max(b.ts, ts)
                    touched.append(aid)
        return touched
