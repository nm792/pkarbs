"""Nautilus BacktestEngine test for MentionsStrategy and MeceStrategy (fills and fees from Nautilus; recorder called). PASS or FAIL list."""
import json, sys, os
from decimal import Decimal
import pandas as pd
from nautilus_trader.config import LoggingConfig
from nautilus_trader.backtest.engine import BacktestEngine, BacktestEngineConfig
from nautilus_trader.model.currencies import USDC
from nautilus_trader.model.data import BookOrder, OrderBookDelta, OrderBookDeltas
from nautilus_trader.model.enums import AccountType, AssetClass, BookAction, BookType, OmsType, OrderSide
from nautilus_trader.model.identifiers import InstrumentId, Symbol, Venue, TraderId
from nautilus_trader.model.instruments import BinaryOption
from nautilus_trader.model.objects import Money, Price, Quantity
from nautilus_trader.adapters.polymarket.fee_model import PolymarketFeeModel
from nautilus_trader.backtest.models import LatencyModel
import mm_strategy as S
V = Venue("POLYMARKET"); NS = 1_000_000_000
T0 = pd.Timestamp("2026-12-01 15:00:00", tz="UTC").value
bad = []
def ck(c, m):
    if not c: bad.append(m)
def inst(sym, oc):
    return BinaryOption(instrument_id=InstrumentId(Symbol(sym), V), raw_symbol=Symbol(sym), outcome=oc, description=sym, asset_class=AssetClass.ALTERNATIVE, currency=USDC,
        price_increment=Price.from_str("0.001"), price_precision=3, size_increment=Quantity.from_str("0.01"), size_precision=2, activation_ns=0,
        expiration_ns=T0 + 30 * 86400 * NS, max_quantity=None, min_quantity=Quantity.from_int(5), maker_fee=Decimal(0), taker_fee=Decimal("0.04"), ts_event=0, ts_init=0)
def book(i, ts, asks, bids=((0.01, 100),)):
    ds = [OrderBookDelta.clear(i, 0, ts, ts)]
    for k, (p, s) in enumerate(list(asks)):
        ds.append(OrderBookDelta(i, BookAction.ADD, BookOrder(OrderSide.SELL, Price.from_str("%.3f" % p), Quantity.from_str("%.2f" % s), 100 + k), 0, 0, ts, ts))
    for k, (p, s) in enumerate(list(bids)):
        ds.append(OrderBookDelta(i, BookAction.ADD, BookOrder(OrderSide.BUY, Price.from_str("%.3f" % p), Quantity.from_str("%.2f" % s), 200 + k), 0, 0, ts, ts))
    ds[-1] = OrderBookDelta(ds[-1].instrument_id, ds[-1].action, ds[-1].order, 128, 0, ts, ts)
    return OrderBookDeltas(i, ds)
eng = BacktestEngine(BacktestEngineConfig(trader_id=TraderId("T-001"), logging=LoggingConfig(log_level="ERROR")))
eng.add_venue(venue=V, oms_type=OmsType.NETTING, account_type=AccountType.CASH, base_currency=USDC, starting_balances=[Money(100000, USDC)], book_type=BookType.L2_MBP,
              fee_model=PolymarketFeeModel(maker_rebates_enabled=False), bar_execution=False, trade_execution=False, latency_model=LatencyModel(base_latency_nanos=250_000_000), liquidity_consumption=True)
I = {k: inst(k, "Yes" if k.endswith("Y") else "No") for k in ["wY", "wN", "aY", "aN", "bY", "bN", "cY", "cN"]}
for x in I.values(): eng.add_instrument(x)
data = []
# mentions word w: q = 0.70 -> YES fair .70, limit .60. YES ask 0.45 x 300 at t0-60 (below limit: buy), NO ask 0.50 (fair .30: no).
data += [book(I["wY"].id, T0 - 60 * NS, [(0.45, 300)]), book(I["wN"].id, T0 - 60 * NS, [(0.50, 300)])]
# MECE set a,b,c: NO asks 0.80/0.60/0.50 (sum 1.90 < 2 -> fire), each 40 sh. Arrives at t0+10s.
for k, p in (("aN", 0.80), ("bN", 0.60), ("cN", 0.50)):
    data.append(book(I[k].id, T0 + 10 * NS, [(p, 40)]))
for k in ("aY", "bY", "cY"):
    data.append(book(I[k].id, T0 + 10 * NS, [(0.5, 40)]))
# heartbeat data so the engine clock advances past t0+5 min
for s in range(0, 900, 5):
    data.append(book(I["wN"].id, T0 + s * NS, [(0.50, 300)]))
eng.add_data(data)
rec = []
S.RECORDER[0] = lambda tok, ts, b, a: rec.append(tok)
ev = dict(id="e1", slug="x", t0=T0 / 1e9, T=T0 / 1e9 + 10 * 86400, markets=[dict(cond="w", label="Word", q=0.70, yes_id=str(I["wY"].id), no_id=str(I["wN"].id))])
eng.add_strategy(S.MentionsStrategy(S.MentionsConfig(strategy_id="MENTIONS-000", event_json=json.dumps(ev))))
st = dict(slug="m", legs=[dict(cond=c, title=c, yes_id=str(I[c + "Y"].id), no_id=str(I[c + "N"].id), fee=0.0) for c in "abc"])
eng.add_strategy(S.MeceStrategy(S.MeceConfig(strategy_id="MECE-000", set_json=json.dumps(st))))
eng.run()
f = eng.trader.generate_order_fills_report()
got = {} if f is None else {str(r["instrument_id"]).split(".")[0]: (float(r["filled_qty"]), float(r["avg_px"])) for _, r in f.iterrows()}
ck(got.get("wY", (0,))[0] == 300 and abs(got["wY"][1] - 0.45) < 1e-9, "mentions: YES 300 sh at 0.45 (limit 0.60 walks the stale ask): %s" % got)
ck("wN" not in got, "mentions: NO side not underpriced -> no order")
ck(all(got.get(k, (0,))[0] == 40 for k in ("aN", "bN", "cN")), "MECE: all three NO legs 40 sh: %s" % got)
ck(not any(k in got for k in ("aY", "bY", "cY")), "MECE never buys YES")
ms = [s for s in eng.trader.strategies() if str(s.id).startswith("MENTIONS")][0]
ck(sum(1 for r in ms.log_rows if r.get("shares")) >= 2 and got["wY"][0] == 300, "mentions: an order at every slot ($200 per decision, frozen rule) but Nautilus fills the 300 displayed shares once (liquidity consumption): %d orders" % sum(1 for r in ms.log_rows if r.get("shares")))
ck(abs(S.DAY_SPENT.get(int(T0 // 86_400_000_000_000), 0) - 300 * 0.45 - sum(got[k][0] * got[k][1] for k in ("aN", "bN", "cN")) * 0) < 1e-6, "daily cap counts FILLED $ (135.00), not submissions: %s" % S.DAY_SPENT)
ck(rec, "recorder called on book changes")
print("FAIL: " + "; ".join(bad) if bad else "PASS (7 checks; Nautilus fills)"); sys.exit(1 if bad else 0)
