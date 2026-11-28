"""Nautilus strategies for the mentions + MECE PAPER node (decision logic in mm_core). Both record each own book on change (top 5 levels) through `recorder`.
Orders: marketable limit BUY, IOC. Nautilus matches against the live own-token book (L2), applies 250 ms insert latency and PolymarketFeeModel."""
import json
from decimal import Decimal
from nautilus_trader.config import StrategyConfig
from nautilus_trader.model.enums import OrderSide, TimeInForce
from nautilus_trader.model.identifiers import InstrumentId
from nautilus_trader.trading.strategy import Strategy
import mm_core as M

RECORDER = [None]       # set by the runner: callable(token_id_str, ts_ns, bids, asks)
DAY_SPENT = {}          # shared $ FILLED per UTC day across all mentions strategies (one process); counted from Nautilus fills, not submissions


def _levels(book, side, n=5):
    lv = book.asks() if side == 'a' else book.bids()
    return [(float(x.price), float(x.size())) for x in lv[:n]]


class MentionsConfig(StrategyConfig, frozen=True):
    event_json: str        # {id, slug, t0, T, markets: [{cond, label, q, yes_id, no_id}]}
    timer_s: int = 5


class MentionsStrategy(Strategy):
    def __init__(self, config):
        super().__init__(config)
        self.ev = json.loads(config.event_json)
        self.slots = [tuple(s) for s in M.slots(self.ev['t0'], self.ev['T'])]
        self.done = set()
        self.ids = {}
        for m in self.ev['markets']:
            self.ids[m['yes_id']] = (m, 'YES', m['q']); self.ids[m['no_id']] = (m, 'NO', 1 - m['q'])
        self.iid = {t: InstrumentId.from_str(t) for t in self.ids}
        self.log_rows = []

    def on_start(self):
        for i in self.iid.values():
            self.subscribe_order_book_deltas(i)
        import datetime as dt
        self.clock.set_timer('mentions-slots-' + str(self.ev['id']), dt.timedelta(seconds=self.config.timer_s), callback=self.on_tick)

    def on_order_filled(self, event):
        day = int(event.ts_event // 86_400_000_000_000)
        DAY_SPENT[day] = DAY_SPENT.get(day, 0.0) + float(event.last_qty) * float(event.last_px)

    def on_order_book_deltas(self, deltas):
        if RECORDER[0]:
            b = self.cache.order_book(deltas.instrument_id)
            if b is not None:
                RECORDER[0](str(deltas.instrument_id), self.clock.timestamp_ns(), _levels(b, 'b'), _levels(b, 'a'))

    def on_tick(self, _ev=None):
        now = self.clock.timestamp_ns() / 1e9
        go, miss = M.due(self.slots, now, self.done)
        for s in miss:
            self.done.add(s); self.log_rows.append(dict(t=now, slot=s, action='MISSED'))
        for s in go:
            self.done.add(s); self.decide(s, now)

    def decide(self, slot, now):
        day = int(now // 86400)
        for tok, (m, side, fair) in self.ids.items():
            b = self.cache.order_book(self.iid[tok])
            ask = None if b is None or b.best_ask_price() is None else float(b.best_ask_price())
            o = M.mention_order(fair, ask)
            if o is None:
                continue
            limit, sh = o
            if DAY_SPENT.get(day, 0.0) + limit * sh > M.DAYCAP + 1e-9:
                self.log_rows.append(dict(t=now, slot=slot, cond=m['cond'], side=side, action='daily cap')); continue
            inst = self.cache.instrument(self.iid[tok])
            self.submit_order(self.order_factory.limit(instrument_id=self.iid[tok], order_side=OrderSide.BUY, quantity=inst.make_qty(Decimal(sh)),
                                                       price=inst.make_price(limit), time_in_force=TimeInForce.IOC))
            self.log_rows.append(dict(t=now, slot=slot, cond=m['cond'], label=m['label'], side=side, fair=round(fair, 4), ask=ask, limit=limit, shares=sh))


class MeceConfig(StrategyConfig, frozen=True):
    set_json: str          # {slug, legs: [{cond, title, no_id, yes_id, fee}]}


class MeceStrategy(Strategy):
    def __init__(self, config):
        super().__init__(config)
        self.st = json.loads(config.set_json)
        self.no = [InstrumentId.from_str(l['no_id']) for l in self.st['legs']]
        self.rec = [InstrumentId.from_str(l['yes_id']) for l in self.st['legs']]
        self.last_fire = -1e18
        self.log_rows = []

    def on_start(self):
        for i in self.no + self.rec:
            self.subscribe_order_book_deltas(i)

    def on_order_book_deltas(self, deltas):
        b = self.cache.order_book(deltas.instrument_id)
        if RECORDER[0] and b is not None:
            RECORDER[0](str(deltas.instrument_id), self.clock.timestamp_ns(), _levels(b, 'b'), _levels(b, 'a'))
        if deltas.instrument_id not in self.no:
            return
        now = self.clock.timestamp_ns() / 1e9
        if now - self.last_fire < M.MECE_COOLDOWN_S:
            return
        legs = []
        for l, i in zip(self.st['legs'], self.no):
            bk = self.cache.order_book(i)
            a = None if bk is None or bk.best_ask_price() is None else (float(bk.best_ask_price()), float(bk.best_ask_size()), float(l.get('fee') or 0))
            legs.append(a if a else (None, None, 0))
        f = M.mece_fire(legs)
        if f is None:
            return
        sh, cost, edge = f
        self.last_fire = now
        orders = []
        for (a, _, _), i in zip(legs, self.no):
            inst = self.cache.instrument(i)
            orders.append(self.order_factory.limit(instrument_id=i, order_side=OrderSide.BUY, quantity=inst.make_qty(Decimal(sh)), price=inst.make_price(a), time_in_force=TimeInForce.IOC))
        self.submit_order_list(self.order_factory.create_list(orders))
        self.log_rows.append(dict(t=now, slug=self.st['slug'], legs=len(legs), shares=sh, cost_per_set=round(cost, 4), edge_per_set=round(edge, 4), asks=[l[0] for l in legs]))
