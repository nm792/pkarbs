"""Nautilus strategy: metric-release stale-ask pickoff (paper or backtest; the same class). Decision logic is pickoff_core (no fill/queue/P&L code here).
Flow: on_start subscribes order-book deltas for BOTH tokens of every market of the event (YES and NO), keeps held orders re-sized from each token's live own-book ask
(read from the Nautilus cache order book); on a ReleaseNumber data event (from the source actor) it decides EVERY market with the lookup table and submits ONE order list
(marketable limit BUY at 0.95, IOC) for the winning token of every market: YES where true, NO where false. Nautilus matches, charges fees and books P&L.
Honest limit: the Polymarket live adapter SIGNS at submit time (adapters/polymarket/execution.py _sign_orders_for_batch); orders built here are pre-built Order objects, not pre-signed.
Pre-signing is a separate, unverified change; paper/sandbox has no signing."""
import json
from decimal import Decimal
from nautilus_trader.config import StrategyConfig
from nautilus_trader.core.data import Data
from nautilus_trader.model.custom import customdataclass
from nautilus_trader.model.data import DataType
from nautilus_trader.model.enums import OrderSide, TimeInForce
from nautilus_trader.model.identifiers import ClientId, InstrumentId
from nautilus_trader.model.objects import Price, Quantity
from nautilus_trader.trading.strategy import Strategy
import pickoff_core as C


@customdataclass
class ReleaseNumber(Data):
    event_slug: str = ""
    value: float = 0.0
    source: str = ""
    name: str = ""             # winner name for named events (elections); when set, markets are decided by title, not by value


class PickoffConfig(StrategyConfig, frozen=True):
    markets_json: str          # [{cond,q,yes_id,no_id,min_size}] for ONE event (instrument ids as strings)
    event_slug: str
    release_ns: int            # scheduled release R (UTC ns); numbers stamped before R are refused (pre-release rejection)
    max_quote_age_ms: int = 0  # 0 = off
    subscribe_source: bool = True  # backtest: ReleaseNumber arrives as data from client SRC; live paper: the source thread calls on_data on the loop
    edge_guard_frac: float = 0.0   # skip markets whose edge is within this fraction of the number (0 = off)


class PickoffStrategy(Strategy):
    def __init__(self, config: PickoffConfig):
        super().__init__(config)
        mk = json.loads(config.markets_json)
        self.markets = [{"cond": m["cond"], "q": m["q"], "title": m.get("title"), "tokens": [m["yes_id"], m["no_id"]], "outcomes": ["Yes", "No"], "min_size": m.get("min_size", 5)} for m in mk]
        self.held = C.HeldOrders(self.markets)
        self.ids = {t: InstrumentId.from_str(t) for m in self.markets for t in m["tokens"]}
        self.day_spent = {}
        self.log_rows = []          # audit rows: what the lookup decided and sent

    def on_start(self):
        for t, iid in self.ids.items():
            self.subscribe_order_book_deltas(iid)
        if self.config.subscribe_source:
            self.subscribe_data(DataType(ReleaseNumber), client_id=ClientId("SRC"))

    def _refresh(self, iid):
        book = self.cache.order_book(iid)
        if book is None:
            return
        ask = book.best_ask_price()
        size = book.best_ask_size()
        self.held.reprice(str(iid), None if ask is None else float(ask), None if size is None else float(size), self.clock.timestamp_ns() // 1_000_000)

    def on_order_book_deltas(self, deltas):
        self._refresh(deltas.instrument_id)

    def on_data(self, data):
        if not isinstance(data, ReleaseNumber) or data.event_slug != self.config.event_slug:
            return
        now = self.clock.timestamp_ns()
        if data.ts_event < self.config.release_ns or now < self.config.release_ns:
            self.log_rows.append(dict(t=now, action="REFUSED pre-release number", value=data.value)); return
        for iid in self.ids.values():
            self._refresh(iid)
        day = now // 86_400_000_000_000
        if data.name.startswith("MAP:"):
            tt = C.truth_by_map(self.markets, json.loads(data.name[4:]))
        elif data.name:
            tt = C.truth_by_name(self.markets, data.name)
        else:
            tt = C.truth_table(self.markets, data.value, self.config.edge_guard_frac)
        orders, skipped = C.fire(self.held, tt, self.day_spent.get(day, 0.0), stale_ms=self.config.max_quote_age_ms or None, now_ms=now // 1_000_000)
        self.log_rows.append(dict(t=now, value=data.value, source=data.source, truth=tt, sent=[(o["cond"], o["side"], o["shares"], o["ask"]) for o in orders], skipped=skipped))
        built = []
        for o in orders:
            iid = self.ids[o["token"]]
            inst = self.cache.instrument(iid)
            built.append(self.order_factory.limit(instrument_id=iid, order_side=OrderSide.BUY, quantity=inst.make_qty(Decimal(o["shares"])), price=inst.make_price(o["limit"]), time_in_force=TimeInForce.IOC))
            self.day_spent[day] = self.day_spent.get(day, 0.0) + o["stake"]
        for chunk in C.batches(built):
            self.submit_order_list(self.order_factory.create_list(chunk))
