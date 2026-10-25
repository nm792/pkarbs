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
import re, zlib
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
    def __init__(self, books, gap_s=5.0, create=False, dedup_window_s=60.0, repair=True):
        self.books = books            # asset -> Book-like (bids, asks, ts)
        self.create = create          # add books for unknown assets (sim) or ignore them (detector)
        self.gap_s = gap_s
        self.window = dedup_window_s
        self.seeded = set()
        self.last_r = None
        self.resets = 0
        self.skipped_s = 0.0
        self.dups = 0
        # exchange top of book: every price_change entry carries best_bid/best_ask after the change.
        # repair drops our levels that the exchange says no longer exist (e.g. asks a trade consumed
        # without a matching price_change), which otherwise linger and cross the book.
        self.repair = repair
        self.top_ex = {}          # asset -> (best_bid, best_ask) as last reported by the exchange
        self.top_checks = 0
        self.top_mismatch = 0     # entries where our top differed from the exchange's before repair
        self.levels_dropped = 0
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

    def _check_top(self, aid, b, c):
        try:
            xb, xa = float(c["best_bid"]), float(c["best_ask"])
        except (KeyError, TypeError, ValueError):
            self.top_ex.pop(aid, None)  # no exchange top for this change: the last one is out of date
            return
        self.top_ex[aid] = (xb, xa)
        if aid not in self.seeded:
            return
        self.top_checks += 1
        ob, oa = b.best_bid(), b.best_ask()
        if (xb > 0 and (ob is None or abs(ob - xb) > 1e-9)) or (0 < xa < 1 and (oa is None or abs(oa - xa) > 1e-9)):
            self.top_mismatch += 1
        if self.repair:
            if xb > 0:
                for p in [p for p in b.bids if p > xb + 1e-9]:
                    del b.bids[p]
                    self.levels_dropped += 1
            if 0 < xa < 1:
                for p in [p for p in b.asks if p < xa - 1e-9]:
                    del b.asks[p]
                    self.levels_dropped += 1

    def is_seeded(self, aid):
        return aid in self.seeded

    def feed(self, r, msgs):
        if self.last_r is not None and r - self.last_r > self.gap_s:
            for b in self.books.values():
                b.bids, b.asks, b.ts = {}, {}, 0
            self.seeded.clear()
            self.top_ex.clear()
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
                self.top_ex[aid] = (max(b.bids) if b.bids else 0.0, min(b.asks) if b.asks else 0.0)
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
                    self._check_top(aid, b, c)
                    touched.append(aid)
        return touched


# start of a gzip member written by shadow_logger (gzip.open on raw-*.jsonl.gz stores the name, FLG=FNAME)
HEADER = re.compile(rb"\x1f\x8b\x08\x08.{6}raw-", re.DOTALL)
CORRUPT = {"skips": 0}  # truncated or corrupt gzip members skipped, across all files read


def read_lines(path, chunk=1 << 16):
    """Stream text lines from a raw-*.jsonl.gz file, surviving a broken member.

    When the logger is killed mid-write and restarted, it appends a new gzip member after a
    truncated one. gzip.open then fails ("invalid block type") or silently decodes the new
    member as garbage, and the rest of the hour is lost. Here every member header (with the
    raw- file name) is located in the compressed stream; a member that has not ended cleanly
    when the next header starts is counted as truncated, its partial last line is dropped,
    and reading resumes at the new member. A truncated last member (file still being
    written) just ends the file."""
    with open(path, "rb") as f:
        data = f.read(chunk)
        if not data:
            return
        d = zlib.decompressobj(31)
        text = b""
        start = 1  # search for the NEXT header, not the one the current member began with
        eof_file = False
        while True:
            m = HEADER.search(data, start)
            if m is None and not eof_file:
                more = f.read(chunk)
                if more:
                    keep = max(0, len(data) - 16)  # a header may straddle the chunk edge
                    feed, data = data[:keep], data[keep:] + more
                    start = 0 if keep else start
                else:
                    eof_file = True
                    feed, data = data, b""
            elif m is None:
                feed, data = data, b""
            else:
                feed, data = data[:m.start()], data[m.start():]
            try:
                out = d.decompress(feed) if feed else b""
                bad = False
            except zlib.error:
                out, bad = b"", True
            text += out
            *lines, text = text.split(b"\n")
            for line in lines:
                yield line.decode("utf-8", "replace")
            if m is not None:  # a new member starts at data[0]
                if bad or not d.eof:
                    CORRUPT["skips"] += 1
                    text = b""
                d = zlib.decompressobj(31)
                start = 1
                continue
            if bad:
                CORRUPT["skips"] += 1
                text = b""
                d = zlib.decompressobj(31)  # wait for the next header; feed nothing until then
                while True:
                    m2 = HEADER.search(data, 0)
                    if m2 is not None:
                        data, start = data[m2.start():], 1
                        break
                    more = f.read(chunk)
                    if not more:
                        return
                    data = data[-16:] + more
                continue
            if eof_file and not data:
                return
