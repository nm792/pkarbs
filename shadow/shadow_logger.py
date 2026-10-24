#!/usr/bin/env python3
"""Shadow logger for in-play Polymarket negRisk sports events (no orders).

Finds live, non-augmented negRisk sports events on gamma, streams every leg's
book from the public market WebSocket, and writes:
  OUT/raw-YYYYmmddHH.jsonl.gz  every WS message, prefixed with local receive time
  OUT/events.jsonl             leg lists, fee rates and secondsDelay snapshots
  OUT/runs.jsonl               each period where a full set is underpriced on either side:
                               yes: buy every YES at the ask, pays 1; edge = 1 - sum(ask + fee)
                               no:  buy every NO, pays n - 1; the NO book mirrors the YES book
                                    (NO ask = 1 - YES bid), so edge = sum(YES bid - fee) - 1
                               Only events whose leg list is complete (no closed or missing leg).

Usage: python3 shadow_logger.py --out data/ [--tags sports] [--minutes 0]
Needs: pip install websockets
"""
import argparse, asyncio, gzip, json, os, time, urllib.request
from datetime import datetime
import websockets

GAMMA = "https://gamma-api.polymarket.com/events"
WS = "wss://ws-subscriptions-clob.polymarket.com/ws/market"
BOOKS = "https://clob.polymarket.com/books"
MAX_ASSETS_PER_WS = 400


def now():
    return time.time()


def get_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": "shadow-logger"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)


def parse_ts(s):
    if not s:
        return None
    s = s.replace(" ", "T")
    if s.endswith("+00"):  # gamma gameStartTime looks like "2026-10-29 18:00:00+00"
        s += ":00"
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()
    except ValueError:
        return None


def discover(tags, window_h, lead_h=0.0):
    """Return {event_id: event_info} for in-play non-augmented negRisk events."""
    t = now()
    iso = lambda x: time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(x))
    out = {}
    for tag in tags:
        cursor = None
        while True:
            url = (f"{GAMMA}/keyset?tag_slug={tag}&active=true&closed=false&limit=100"
                   f"&end_date_min={iso(t - window_h * 3600)}&end_date_max={iso(t + lead_h * 3600)}")
            if cursor:
                url += f"&after_cursor={cursor}"
            try:
                page = get_json(url)
            except Exception as e:  # keep running on transient gamma errors
                print("gamma error", tag, e, flush=True)
                break
            for ev in page.get("events", []):
                if not ev.get("negRisk") or ev.get("negRiskAugmented"):
                    continue
                markets = ev.get("markets", [])
                legs = [m for m in markets
                        if m.get("active") and not m.get("closed") and m.get("acceptingOrders", True)]
                if len(legs) < 2:
                    continue
                start = parse_ts(legs[0].get("gameStartTime")) or parse_ts(ev.get("startTime"))
                if start is None or not (start - lead_h * 3600 <= t <= start + window_h * 3600):
                    continue
                out[str(ev["id"])] = {
                    "id": str(ev["id"]), "title": ev.get("title"), "sport": (ev.get("sport") or {}).get("sport") if isinstance(ev.get("sport"), dict) else (ev.get("sport") or tag), "start": start,
                    # a closed or missing leg breaks the "exactly one leg pays" property
                    "n_markets": len(markets), "complete": len(legs) == len(markets),
                    "closed_legs": [m.get("groupItemTitle") or m.get("question") for m in markets if m not in legs],
                    "legs": [{
                        "cid": m["conditionId"],
                        "yes": json.loads(m["clobTokenIds"])[0],
                        "no": json.loads(m["clobTokenIds"])[1],
                        "name": m.get("groupItemTitle") or m.get("question"),
                        "fee_rate": (m.get("feeSchedule") or {}).get("rate", 0.0) if m.get("feesEnabled") else 0.0,
                        "fee_exp": (m.get("feeSchedule") or {}).get("exponent", 1),
                        "seconds_delay": m.get("secondsDelay"),
                        "tick": m.get("orderPriceMinTickSize"),
                        "min_size": m.get("orderMinSize"),
                    } for m in legs],
                }
            cursor = page.get("next_cursor")
            if not cursor:
                break
    return out


def get_books(assets):
    """REST snapshot of many books, returned as WS-style "book" messages."""
    out = []
    for i in range(0, len(assets), 100):
        body = json.dumps([{"token_id": a} for a in assets[i:i + 100]]).encode()
        req = urllib.request.Request(BOOKS, data=body, headers={
            "Content-Type": "application/json", "User-Agent": "shadow-logger"})
        with urllib.request.urlopen(req, timeout=20) as r:
            out += [{**b, "event_type": "book", "src": "rest"} for b in json.load(r)]
    return out


class Book:
    __slots__ = ("bids", "asks", "ts")

    def __init__(self):
        self.bids, self.asks, self.ts = {}, {}, 0

    def best_ask(self):
        return min(self.asks) if self.asks else None

    def best_bid(self):
        return max(self.bids) if self.bids else None


class Logger:
    def __init__(self, out, tags, min_edge, window_h, lead_h):
        self.out, self.tags, self.min_edge, self.window_h, self.lead_h = out, tags, min_edge, window_h, lead_h
        os.makedirs(out, exist_ok=True)
        self.events = {}         # event_id -> info
        self.asset_event = {}    # yes token -> event_id
        self.books = {}          # yes token -> Book
        self.runs = {}           # (event_id, side) -> open run
        self.raw_hour, self.raw_f = None, None
        self.ws_tasks = []
        self.n_msgs = 0

    # ---- output ----
    def raw(self, recv, msg):
        hour = time.strftime("%Y%m%d%H", time.gmtime(recv))
        if hour != self.raw_hour:
            if self.raw_f:
                self.raw_f.close()
            self.raw_f = gzip.open(os.path.join(self.out, f"raw-{hour}.jsonl.gz"), "at")
            self.raw_hour = hour
        msg = msg.replace("\n", " ")  # WS frames can hold newlines; JSON strings cannot, so this is safe
        self.raw_f.write(f'{{"r":{recv:.3f},"m":{msg}}}\n')

    def append(self, name, obj):
        with open(os.path.join(self.out, name), "a") as f:
            f.write(json.dumps(obj) + "\n")

    # ---- books ----
    def apply(self, recv, m):
        et = m.get("event_type")
        if et == "book":
            b = self.books.get(m.get("asset_id"))
            if b is None or int(m.get("timestamp", 0)) < b.ts:  # older REST snapshot than our stream
                return None
            b.bids = {float(x["price"]): float(x["size"]) for x in m.get("bids", [])}
            b.asks = {float(x["price"]): float(x["size"]) for x in m.get("asks", [])}
            b.ts = int(m.get("timestamp", 0))
            return [m.get("asset_id")]
        if et == "price_change":
            changes = m.get("price_changes") or m.get("changes") or []
            touched = []
            for c in changes:
                aid = c.get("asset_id") or m.get("asset_id")
                b = self.books.get(aid)
                if b is None:
                    continue
                side = b.bids if c["side"].upper() == "BUY" else b.asks
                p, s = float(c["price"]), float(c["size"])
                if s == 0:
                    side.pop(p, None)
                else:
                    side[p] = s
                b.ts = int(m.get("timestamp", 0))
                touched.append(aid)
            return touched
        return None

    def check(self, recv, eid):
        ev = self.events.get(eid)
        if not ev:
            return
        if not ev.get("complete", True):
            self.close_run(recv, eid)
            return
        n = len(ev["legs"])
        for side in ("yes", "no"):
            cost, size, quotes = 0.0, float("inf"), []
            for leg in ev["legs"]:
                b = self.books.get(leg["yes"])
                p = (b.best_ask() if side == "yes" else b.best_bid()) if b else None
                if p is None:
                    break
                fee = leg["fee_rate"] * (p * (1 - p)) ** leg.get("fee_exp", 1)  # same for YES at p and NO at 1 - p
                cost += (p if side == "yes" else 1 - p) + fee
                lvl = b.asks if side == "yes" else b.bids
                size = min(size, lvl[p])
                quotes.append([p, lvl[p]])  # YES ask (yes side) or YES bid (no side)
            else:
                payout = 1 if side == "yes" else n - 1
                edge = payout - cost
                run = self.runs.get((eid, side))
                if edge > self.min_edge:
                    if run is None:
                        self.runs[(eid, side)] = {
                            "event": eid, "side": side, "title": ev["title"], "t0": recv, "cost0": cost,
                            "payout": payout, "size0": size, "quotes0": quotes,
                            "assets": [leg["yes"] for leg in ev["legs"]], "n_markets": ev.get("n_markets"),
                            "min_cost": cost, "max_edge_usd": edge * size, "updates": 1}
                    else:
                        run["updates"] += 1
                        run["min_cost"] = min(run["min_cost"], cost)
                        run["max_edge_usd"] = max(run["max_edge_usd"], edge * size)
                    continue
            self.close_run(recv, eid, side)

    def close_run(self, recv, eid, side=None):
        for sd in ("yes", "no") if side is None else (side,):
            run = self.runs.pop((eid, sd), None)
            if run:
                run["t1"] = recv
                run["dur"] = round(recv - run["t0"], 3)
                self.append("runs.jsonl", run)
                print(f"run {sd} {run['title'][:40]!r} dur={run['dur']}s "
                      f"edge0=${(run['payout'] - run['cost0']) * run['size0']:.2f}", flush=True)

    # ---- WS ----
    async def stream(self, assets):
        while True:
            try:
                async with websockets.connect(WS, ping_interval=None, max_size=2**24) as ws:
                    await ws.send(json.dumps({"assets_ids": assets, "type": "market"}))

                    async def pinger():
                        while True:
                            await asyncio.sleep(10)
                            await ws.send("PING")
                    pt = asyncio.create_task(pinger())
                    try:
                        async for text in ws:
                            recv = now()
                            if text == "PONG":
                                continue
                            self.raw(recv, text)
                            self.n_msgs += 1
                            data = json.loads(text)
                            for m in data if isinstance(data, list) else [data]:
                                touched = self.apply(recv, m)
                                for eid in {self.asset_event.get(a) for a in touched or []}:
                                    self.check(recv, eid)
                    finally:
                        pt.cancel()
            except asyncio.CancelledError:
                raise
            except Exception as e:
                print("ws error, reconnecting:", repr(e), flush=True)
                await asyncio.sleep(2)

    async def refresh(self):
        found = await asyncio.to_thread(discover, self.tags, self.window_h, self.lead_h)
        t = now()
        for eid, ev in found.items():
            self.append("events.jsonl", {"t": t, **ev})
        if set(found) == set(self.events):
            self.events = found
            return
        for eid in set(self.events) - set(found):
            self.close_run(t, eid)
        self.events = found
        self.asset_event = {leg["yes"]: eid for eid, ev in found.items() for leg in ev["legs"]}
        self.books = {a: self.books.get(a) or Book() for a in self.asset_event}
        for task in self.ws_tasks:
            task.cancel()
        assets = list(self.asset_event)
        chunks = []  # keep each event's legs on one connection
        cur = []
        for ev in found.values():
            ids = [leg["yes"] for leg in ev["legs"]]
            if cur and len(cur) + len(ids) > MAX_ASSETS_PER_WS:
                chunks.append(cur)
                cur = []
            cur += ids
        if cur:
            chunks.append(cur)
        self.ws_tasks = [asyncio.create_task(self.stream(c)) for c in chunks]
        print(f"{time.strftime('%H:%M:%S')} live events={len(found)} assets={len(assets)} ws={len(chunks)}", flush=True)

    async def resync(self, every):
        """Re-seed every book from REST in case the stream dropped an update."""
        while True:
            await asyncio.sleep(every)
            assets = list(self.asset_event)
            if not assets:
                continue
            try:
                msgs = await asyncio.to_thread(get_books, assets)
            except Exception as e:
                print("books error", repr(e), flush=True)
                continue
            recv = now()
            self.raw(recv, json.dumps(msgs))
            touched = set()
            for m in msgs:
                touched.update(self.apply(recv, m) or [])
            for eid in {self.asset_event.get(a) for a in touched}:
                self.check(recv, eid)

    async def run(self, minutes, refresh_s, resync_s):
        rs = asyncio.create_task(self.resync(resync_s))
        end = now() + minutes * 60 if minutes else None
        while end is None or now() < end:
            await self.refresh()
            await asyncio.sleep(refresh_s if end is None else min(refresh_s, max(0, end - now())))
        rs.cancel()
        for task in self.ws_tasks:
            task.cancel()
        for eid, _ in list(self.runs):
            self.close_run(now(), eid)
        if self.raw_f:
            self.raw_f.close()
        print("done, messages:", self.n_msgs, flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="data")
    ap.add_argument("--tags", default="sports")
    ap.add_argument("--window-h", type=float, default=4, help="hours after start an event counts as in play")
    ap.add_argument("--lead-h", type=float, default=0, help="also watch events starting within this many hours (testing)")
    ap.add_argument("--min-edge", type=float, default=0.0)
    ap.add_argument("--minutes", type=float, default=0, help="0 = run forever")
    ap.add_argument("--refresh", type=float, default=120, help="seconds between gamma rediscovery")
    ap.add_argument("--resync", type=float, default=60, help="seconds between REST book re-seeds")
    a = ap.parse_args()
    asyncio.run(Logger(a.out, a.tags.split(","), a.min_edge, a.window_h, a.lead_h).run(a.minutes, a.refresh, a.resync))


if __name__ == "__main__":
    main()
