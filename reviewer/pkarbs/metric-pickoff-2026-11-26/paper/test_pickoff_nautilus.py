"""Nautilus BacktestEngine integration test: planted stale asks, pre-release rejection, NO on losing brackets, ladder markets. Fills and fees come from Nautilus (matching engine + PolymarketFeeModel).
Run: python3 test_pickoff_nautilus.py (needs nautilus_trader 1.231 + py-clob-client-v2). PASS or FAIL list, exit code."""
import json, sys
from decimal import Decimal
import pandas as pd
from nautilus_trader.config import LoggingConfig
from nautilus_trader.backtest.engine import BacktestEngine, BacktestEngineConfig
from nautilus_trader.model.currencies import USDC
from nautilus_trader.model.data import BookOrder, OrderBookDelta, OrderBookDeltas, DataType
from nautilus_trader.model.enums import AccountType, AssetClass, BookAction, BookType, OmsType, OrderSide
from nautilus_trader.model.identifiers import ClientId, InstrumentId, Symbol, Venue, TraderId
from nautilus_trader.model.instruments import BinaryOption
from nautilus_trader.model.objects import Money, Price, Quantity
from nautilus_trader.model.data import capsule_to_list  # noqa (import check only)
from nautilus_trader.core.data import Data
from nautilus_trader.adapters.polymarket.fee_model import PolymarketFeeModel
from nautilus_trader.backtest.models import FillModel
from pickoff_strategy import PickoffStrategy, PickoffConfig, ReleaseNumber
from nautilus_trader.model.data import CustomData

VENUE = Venue("POLYMARKET")
R = pd.Timestamp("2026-12-10 13:30:00", tz="UTC").value
S = 1_000_000_000
QS = ["Will Core CPI MoM be 0.2% in Dec?", "Will Core CPI MoM be 0.3% in Dec?", "Will Core CPI MoM be 0.3% or more in Dec?", "Will Core CPI MoM be 0.2% or less in Dec?"]
bad = []
def ck(c, m):
    if not c: bad.append(m)

def mkinst(sym, outcome, fee):
    return BinaryOption(instrument_id=InstrumentId(Symbol(sym), VENUE), raw_symbol=Symbol(sym), outcome=outcome, description=sym, asset_class=AssetClass.ALTERNATIVE, currency=USDC,
        price_increment=Price.from_str("0.001"), price_precision=3, size_increment=Quantity.from_str("0.01"), size_precision=2, activation_ns=0,
        expiration_ns=R + 86400 * S, max_quantity=None, min_quantity=Quantity.from_int(5), maker_fee=Decimal(0), taker_fee=Decimal(fee), ts_event=0, ts_init=0)

def book(iid, ts, asks, bids=()):
    ds = [OrderBookDelta.clear(iid, 0, ts, ts)]
    for i, (p, s) in enumerate(asks):
        ds.append(OrderBookDelta(iid, BookAction.ADD, BookOrder(OrderSide.SELL, Price.from_str("%.3f" % p), Quantity.from_str("%.2f" % s), 100 + i), 0, 0, ts, ts))
    for i, (p, s) in enumerate(bids):
        ds.append(OrderBookDelta(iid, BookAction.ADD, BookOrder(OrderSide.BUY, Price.from_str("%.3f" % p), Quantity.from_str("%.2f" % s), 200 + i), 0, 0, ts, ts))
    ds[-1] = OrderBookDelta(ds[-1].instrument_id, ds[-1].action, ds[-1].order, 128, 0, ts, ts)   # F_LAST
    return OrderBookDeltas(iid, ds)

def run(number_ts_offset_s, value=0.3, quotes=None):
    eng = BacktestEngine(BacktestEngineConfig(trader_id=TraderId("T-001"), logging=LoggingConfig(log_level="ERROR")))
    eng.add_venue(venue=VENUE, oms_type=OmsType.NETTING, account_type=AccountType.CASH, base_currency=USDC, starting_balances=[Money(100000, USDC)], book_type=BookType.L2_MBP,
                  fee_model=PolymarketFeeModel(maker_rebates_enabled=False), bar_execution=False, trade_execution=False)
    mk, insts = [], {}
    for i, q in enumerate(QS):
        y, n = mkinst("c%d-YES" % i, "Yes", "0.01"), mkinst("c%d-NO" % i, "No", "0.01")
        eng.add_instrument(y); eng.add_instrument(n); insts[i] = (y, n)
        mk.append(dict(cond="c%d" % i, q=q, yes_id=str(y.id), no_id=str(n.id), min_size=5))
    # quotes[(i, 'Y'|'N')] = (pre_ask, post_ask) ; default: everything stale-looking 0.50 before and repriced to 0.99 after for LOSERS, planted stale on winners
    data = []
    for i in range(4):
        for k, inst in zip("YN", insts[i]):
            pre, post = quotes[(i, k)]
            data.append(book(inst.id, R - 600 * S, [(pre, 1000.0)], [(0.01, 1000.0)]))
            data.append(book(inst.id, R + 3 * S, [(post, 1000.0)], [(0.01, 1000.0)]))
    eng.add_data(data)
    eng.add_strategy(PickoffStrategy(PickoffConfig(markets_json=json.dumps(mk), event_slug="core-cpi-dec", release_ns=R)))
    nd = CustomData(DataType(ReleaseNumber), ReleaseNumber(event_slug="core-cpi-dec", value=value, source="planted", ts_event=R + number_ts_offset_s * S, ts_init=R + number_ts_offset_s * S))
    eng.add_data([nd], client_id=ClientId('SRC'))
    eng.run()
    fills = eng.trader.generate_order_fills_report()
    strat = eng.trader.strategies()[0]
    return eng, fills, strat

# value 0.3 -> c0(0.2) F, c1(0.3) T, c2(>=0.3) T, c3(<=0.2) F.  winners: n0, y1, y2, n3. Losers y0,n1,n2,y3.
Q = {(0, "Y"): (0.60, 0.99), (0, "N"): (0.55, 0.60),   # n0 NO wins: stale 0.55 -> after release still stale 0.60 (<0.95) must be bought
     (1, "Y"): (0.40, 0.35), (1, "N"): (0.60, 0.995),   # y1 YES wins stale 0.35
     (2, "Y"): (0.45, 0.50), (2, "N"): (0.55, 0.99),   # y2 YES wins (threshold >=0.3) stale 0.50
     (3, "Y"): (0.40, 0.99), (3, "N"): (0.995, 0.995)}   # n3 NO wins: ask already 0.995 -> must NOT be bought
# Book snapshots at R+3 s: the number arrives at R+5 s (offset 5) so the post-release books are in place; before R the books show pre quotes.
eng, fills, strat = run(5, 0.3, Q)
sent = strat.log_rows[-1]
tokens = {r[0] + "-" + r[1] for r in sent["sent"]}
ck(tokens == {"c0-NO", "c1-YES", "c2-YES"}, "must fire NO on losing bracket c0, YES on c1 and ladder c2, skip repriced n3: got %s" % tokens)
ck(fills is not None and len(fills) == 3, "Nautilus must report 3 fills, got %s" % (0 if fills is None else len(fills)))
if fills is not None and len(fills):
    px = {str(r["instrument_id"]).split(".")[0]: float(r["avg_px"]) for _, r in fills.iterrows()}
    ck(abs(px.get("c1-YES", 0) - 0.35) < 1e-9 and abs(px.get("c0-NO", 0) - 0.60) < 1e-9 and abs(px.get("c2-YES", 0) - 0.50) < 1e-9, "fills must be at the stale own asks: %s" % px)
    ck(all(float(r["avg_px"]) < 0.99 for _, r in fills.iterrows()), "no fill at or above 0.99")
    comm = fills["commissions"].astype(str).tolist()
    ck(all("USDC" in c and not c.startswith("0.00 ") for c in comm), "Nautilus PolymarketFeeModel must charge a taker fee: %s" % comm)
# pre-release rejection: the same number stamped BEFORE R must send nothing
eng2, fills2, strat2 = run(-5, 0.3, Q)
ck(strat2.log_rows and "REFUSED" in strat2.log_rows[-1]["action"], "pre-release number must be refused")
ck(fills2 is None or len(fills2) == 0, "no fills before release")
# mutation proof for the test itself: if we pretend the winner is the other way round the fired set must differ (check can fail)
eng3, fills3, strat3 = run(5, 0.2, Q)
t3 = {r[0] + "-" + r[1] for r in strat3.log_rows[-1]["sent"]}
ck(t3 != tokens, "different number must give a different fired set (value 0.2 flips c0/c1)")
print("FAIL: " + "; ".join(bad) if bad else "PASS (Nautilus %s; fills 3 incl. NO on losing bracket, ladder both sides, pre-release refused)" % __import__("nautilus_trader").__version__)
sys.exit(1 if bad else 0)
