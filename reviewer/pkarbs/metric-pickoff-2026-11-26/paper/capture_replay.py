"""Replay ONE recorded release capture (pm_event_books.js folder: markets.jsonl + books-*.jsonl.gz) through an unmodified Nautilus BacktestEngine
with PickoffStrategy (paper/pickoff_strategy.py). Read-only on the capture. Paper only, no network, no orders.

Nautilus does all matching, fees (PolymarketFeeModel) and P&L. This file only (a) turns each recorded own-token book row into an L2 snapshot
(clear + the recorded levels; the recorder keeps the top 3 levels, so depth beyond level 3 is NOT seen and fills are understated, never overstated),
(b) stamps the released number at R + L, and (c) prints Nautilus's own fills report and the depth table the coordinator asked for.
Latency: Nautilus LatencyModel, 250 ms base (SETTLED A3) on top of L. Each recorded book row enters the engine at its recv_ms (what we could have seen).

Usage: python3 capture_replay.py DIR RELEASE_ISO 'slug=value,slug=value' [--lat 0.5,2,5] [--usd 200] [--depth-out depth.json]
Output: one JSON line per latency: {"L_s", "fills": [Nautilus fills report rows], "commissions", "log": strategy audit rows}, then the depth table.
"""
import sys, os, json, gzip, glob, argparse, datetime as dt
from decimal import Decimal

NS = 1_000_000_000


def iso_ns(s):
    return int(dt.datetime.fromisoformat(s.replace('Z', '+00:00')).timestamp() * NS)


def load_capture(d):
    markets = [json.loads(l) for l in open(os.path.join(d, 'markets.jsonl')) if l.strip()]
    rows = []
    for p in sorted(glob.glob(os.path.join(d, 'books*.jsonl*'))):
        op = gzip.open if p.endswith('.gz') else open
        with op(p, 'rt') as f:
            for line in f:
                try:
                    rows.append(json.loads(line))
                except Exception:
                    continue
    rows.sort(key=lambda r: r['recv_ms'])
    return markets, rows


def depth_table(markets, rows, release_ns, values, offsets=(-5, -1, 0, 0.5, 1, 2, 5, 10, 30)):
    """Resting size per level on BOTH tokens at R+offset (last row at or before), and when the pre-release best ask of each token was last shown.
    Pure read of the capture; no P&L (P&L comes only from Nautilus)."""
    by = {}
    for r in rows:
        by.setdefault(r['asset'], []).append(r)
    R_ms = release_ns // 1_000_000
    out = []
    for m in markets:
        for tok, oc in zip(m['tokens'], m['outcomes']):
            rs = by.get(tok, [])
            snap = {}
            for off in offsets:
                t = R_ms + off * 1000
                last = None
                for r in rs:
                    if r['recv_ms'] <= t:
                        last = r
                    else:
                        break
                snap[str(off)] = None if last is None else [[a['price'], a['size']] for a in last.get('asks', [])]
            pre = snap.get('0')
            pulled_ms = None
            if pre:
                p0 = pre[0][0]
                for r in rs:
                    if r['recv_ms'] > R_ms and not any(abs(a['price'] - p0) < 1e-9 for a in r.get('asks', [])):
                        pulled_ms = r['recv_ms'] - R_ms
                        break
            out.append(dict(cond=m['cond'], slug=m.get('slug'), title=m.get('title') or m['q'], outcome=oc, asks_at=snap,
                            pre_best_ask=None if not pre else pre[0], pre_best_ask_gone_after_ms=pulled_ms))
    return out


def run_one(markets, rows, release_ns, values, L_s, usd, base_latency_ms=250):
    import pandas as pd  # noqa
    from nautilus_trader.config import LoggingConfig
    from nautilus_trader.backtest.engine import BacktestEngine, BacktestEngineConfig
    from nautilus_trader.backtest.models import LatencyModel
    from nautilus_trader.model.currencies import USDC
    from nautilus_trader.model.data import BookOrder, OrderBookDelta, OrderBookDeltas, DataType, CustomData
    from nautilus_trader.model.enums import AccountType, AssetClass, BookAction, BookType, OmsType, OrderSide
    from nautilus_trader.model.identifiers import ClientId, InstrumentId, Symbol, Venue, TraderId
    from nautilus_trader.model.instruments import BinaryOption
    from nautilus_trader.model.objects import Money, Price, Quantity
    from nautilus_trader.adapters.polymarket.fee_model import PolymarketFeeModel
    from pickoff_strategy import PickoffStrategy, PickoffConfig, ReleaseNumber

    V = Venue("POLYMARKET")
    eng = BacktestEngine(BacktestEngineConfig(trader_id=TraderId("REPLAY-001"), logging=LoggingConfig(log_level=os.environ.get("NT_LOG","ERROR"))))
    eng.add_venue(venue=V, oms_type=OmsType.NETTING, account_type=AccountType.CASH, base_currency=USDC, starting_balances=[Money(100000, USDC)],
                  book_type=BookType.L2_MBP, fee_model=PolymarketFeeModel(maker_rebates_enabled=False), bar_execution=False, trade_execution=False,
                  latency_model=LatencyModel(base_latency_nanos=base_latency_ms * 1_000_000))
    sym = {}
    by_slug = {}
    for i, m in enumerate(markets):
        rate = (m.get('fee') or {}).get('rate', 0.01) if isinstance(m.get('fee'), dict) else 0.01
        ids = []
        for tok, oc in zip(m['tokens'], m['outcomes']):
            s = "m%d-%s" % (i, oc.upper())
            inst = BinaryOption(instrument_id=InstrumentId(Symbol(s), V), raw_symbol=Symbol(s), outcome=oc, description=m['q'][:60], asset_class=AssetClass.ALTERNATIVE,
                                currency=USDC, price_increment=Price.from_str("0.001"), price_precision=3, size_increment=Quantity.from_str("0.01"), size_precision=2,
                                activation_ns=0, expiration_ns=release_ns + 30 * 86400 * NS, max_quantity=None, min_quantity=Quantity.from_str("%.2f" % float(m.get('min_size') or 5)),
                                maker_fee=Decimal(0), taker_fee=Decimal(str(rate)), ts_event=0, ts_init=0)
            eng.add_instrument(inst)
            sym[tok] = inst.id
            ids.append(str(inst.id))
        by_slug.setdefault(m.get('slug'), []).append(dict(cond=m['cond'], q=m['q'], yes_id=ids[m['outcomes'].index('Yes')], no_id=ids[m['outcomes'].index('No')], min_size=float(m.get('min_size') or 5)))
    data = []
    for r in rows:
        iid = sym.get(r['asset'])
        if iid is None:
            continue
        ts = int(r['recv_ms']) * 1_000_000
        ds = [OrderBookDelta.clear(iid, 0, ts, ts)]
        k = 0
        for side, lv in ((OrderSide.SELL, r.get('asks') or []), (OrderSide.BUY, r.get('bids') or [])):
            for a in lv:
                k += 1
                ds.append(OrderBookDelta(iid, BookAction.ADD, BookOrder(side, Price.from_str("%.3f" % a['price']), Quantity.from_str("%.2f" % a['size']), k), 0, 0, ts, ts))
        ds[-1] = OrderBookDelta(ds[-1].instrument_id, ds[-1].action, ds[-1].order, 128, 0, ts, ts)
        data.append(OrderBookDeltas(iid, ds))
    eng.add_data(data)
    t_num = release_ns + int(L_s * NS)
    for slug, mk in by_slug.items():
        if slug not in values:
            continue
        eng.add_strategy(PickoffStrategy(PickoffConfig(strategy_id="PICKOFF-%s" % slug[:20], markets_json=json.dumps(mk), event_slug=slug, release_ns=release_ns)))
        eng.add_data([CustomData(DataType(ReleaseNumber), ReleaseNumber(event_slug=slug, value=float(values[slug]), source="print", ts_event=t_num, ts_init=t_num))], client_id=ClientId('SRC'))
    eng.run()
    fills = eng.trader.generate_order_fills_report()
    logs = [row for s in eng.trader.strategies() for row in s.log_rows]
    names = {str(v): k for k, v in sym.items()}
    out = []
    if fills is not None and len(fills):
        for _, f in fills.iterrows():
            out.append(dict(instrument=str(f['instrument_id']), qty=str(f.get('filled_qty')), avg_px=str(f.get('avg_px')), commissions=str(f.get('commissions'))))
    return dict(L_s=L_s, base_latency_ms=base_latency_ms, fills=out, n_fills=len(out), log=logs, label="Nautilus BacktestEngine on recorded own-token books (top 3 levels); P&L at settlement = sum(qty x (1 if token won else 0)) - qty x avg_px - commissions")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('dir'); ap.add_argument('release'); ap.add_argument('values')
    ap.add_argument('--lat', default='0.5,2,5'); ap.add_argument('--usd', type=float, default=200.0); ap.add_argument('--depth-out')
    a = ap.parse_args()
    R = iso_ns(a.release)
    values = dict(kv.split('=') for kv in a.values.split(','))
    markets, rows = load_capture(a.dir)
    for L in [float(x) for x in a.lat.split(',')]:
        print(json.dumps(run_one(markets, rows, R, values, L, a.usd), default=str))
    dtab = depth_table(markets, rows, R, values)
    if a.depth_out:
        json.dump(dtab, open(a.depth_out, 'w'), indent=1)
    t = [r['recv_ms'] for r in rows if R // 1_000_000 <= r['recv_ms'] <= R // 1_000_000 + 10000]
    gap = max((b - a for a, b in zip(t, t[1:])), default=None)
    # Nautilus processes an in-flight order at the next data timestamp, so a long gap after R delays matching: report the largest gap in R..R+10 s
    print(json.dumps({"depth_rows": len(dtab), "rows_R_to_R10s": len(t), "max_gap_ms_R_to_R10s": gap}))


if __name__ == '__main__':
    main()
