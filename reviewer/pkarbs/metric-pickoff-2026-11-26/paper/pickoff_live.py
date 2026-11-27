"""Live PAPER node for the announcement pickoff (PickoffStrategy). PAPER ONLY: Polymarket public market data (level-0 client, no key) +
Nautilus SandboxExecutionClient whose SimulatedExchange is rebuilt with use_message_queue=True, insert latency 250 ms (SETTLED A3),
liquidity consumption on and PolymarketFeeModel (the bucket_live.py / MFW r156 pattern, gate PASS). No orders reach any venue.

One PickoffStrategy per Polymarket event. A source module (plug-in) is polled once a second on its own thread; when it reports a released
result for an event it is handed to that event's strategy ON THE EVENT LOOP (call_soon_threadsafe). Nautilus does matching, fees and P&L.

Usage:
  python3 pickoff_live.py --slugs slugs.txt --release 2026-11-28T08:00:00Z --source source_cec:Source --logdir DIR [--run-s 43200] [--preflight 60]
--preflight N: start, load instruments, check both tokens of every market have a book, stop after N s and print PASS/FAIL JSON (no source).
Outputs in DIR: fills.csv (Nautilus fills report, rewritten every 60 s and at stop), decisions.jsonl (strategy audit rows), source.jsonl, nautilus/ logs.
"""
import os, sys, json, time, threading, gzip, urllib.request, argparse, datetime as dt
from decimal import Decimal
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
INSERT_LATENCY_NS = 250_000_000
WALLET_PUSD = 100_000


def gamma_event(slug):
    req = urllib.request.Request('https://gamma-api.polymarket.com/events?slug=' + slug, headers={'Accept-Encoding': 'gzip', 'User-Agent': 'pickoff-paper'})
    raw = urllib.request.urlopen(req, timeout=30).read()
    try:
        raw = gzip.decompress(raw)
    except OSError:
        pass
    ev = json.loads(raw)
    return ev[0] if ev else None


def event_markets(ev):
    """Gamma event -> [{cond, q, title, yes_id, no_id, min_size}] for active, unclosed two-token markets. Instrument id = '<cond>-<token>.POLYMARKET' (Nautilus Polymarket adapter)."""
    out = []
    for m in ev.get('markets', []):
        if m.get('closed') or not m.get('active'):
            continue
        try:
            toks = json.loads(m['clobTokenIds']); oc = json.loads(m['outcomes'])
        except Exception:
            continue
        if len(toks) != 2 or [o.lower() for o in oc] != ['yes', 'no']:
            continue
        c = m['conditionId']
        out.append(dict(cond=c, q=m['question'], title=m.get('groupItemTitle'), yes_id=f'{c}-{toks[0]}.POLYMARKET', no_id=f'{c}-{toks[1]}.POLYMARKET',
                        min_size=float(m.get('orderMinSize') or 5)))
    return out


def slugs_for_provider():
    return json.load(open(os.environ['PICKOFF_SLUGS_FILE']))


def build_factories():
    from nautilus_trader.adapters.polymarket.data import PolymarketDataClient
    from nautilus_trader.adapters.polymarket.factories import get_polymarket_instrument_provider
    from nautilus_trader.adapters.polymarket.fee_model import PolymarketFeeModel
    from nautilus_trader.adapters.sandbox import execution as SX
    from nautilus_trader.live.factories import LiveDataClientFactory, LiveExecClientFactory

    class L0PolymarketDataFactory(LiveDataClientFactory):
        @staticmethod
        def create(loop, name, config, msgbus, cache, clock):
            from py_clob_client_v2.client import ClobClient
            http = ClobClient(config.base_url_http or 'https://clob.polymarket.com', chain_id=137)   # level 0: public endpoints only
            prov = get_polymarket_instrument_provider(client=http, clock=clock, config=config.instrument_config)
            return PolymarketDataClient(loop=loop, http_client=http, msgbus=msgbus, cache=cache, clock=clock, instrument_provider=prov, config=config, name=name)

    class PaperSandboxClient(SX.SandboxExecutionClient):
        def __init__(s, loop, portfolio, msgbus, cache, clock, config):
            super().__init__(loop=loop, portfolio=portfolio, msgbus=msgbus, cache=cache, clock=clock, config=config)
            from nautilus_trader.backtest.engine import SimulatedExchange
            from nautilus_trader.backtest.execution_client import BacktestExecClient
            from nautilus_trader.backtest.models import LatencyModel, FillModel
            from nautilus_trader.model.objects import Money
            from nautilus_trader.model.enums import book_type_from_str
            ex0 = s.exchange
            s.exchange = SimulatedExchange(
                venue=ex0.id, oms_type=ex0.oms_type, account_type=ex0.account_type, starting_balances=[Money.from_str(b) for b in config.starting_balances],
                base_currency=ex0.base_currency, default_leverage=config.default_leverage, leverages=config.leverages or {}, modules=[],
                portfolio=portfolio, msgbus=s._msgbus, cache=cache, clock=s.test_clock, fill_model=FillModel(),
                fee_model=PolymarketFeeModel(maker_rebates_enabled=False),
                latency_model=LatencyModel(base_latency_nanos=0, insert_latency_nanos=INSERT_LATENCY_NS, update_latency_nanos=0, cancel_latency_nanos=0),
                book_type=book_type_from_str(config.book_type), frozen_account=config.frozen_account, bar_execution=config.bar_execution,
                trade_execution=config.trade_execution, reject_stop_orders=config.reject_stop_orders, support_gtd_orders=config.support_gtd_orders,
                support_contingent_orders=config.support_contingent_orders, use_position_ids=config.use_position_ids, use_random_ids=config.use_random_ids,
                use_reduce_only=config.use_reduce_only, use_message_queue=True, liquidity_consumption=True)
            s._client = BacktestExecClient(exchange=s.exchange, msgbus=msgbus, cache=cache, clock=s.test_clock)
            s.exchange.register_client(s._client); s.exchange.initialize_account()

        # venue clock = wall clock (the stock sandbox only advances on data messages): Nautilus's own exchange.process(now) before each submit and every 20 ms
        def connect(s):
            super().connect()
            loop = s._loop
            s._clock.set_timer('paper-venue-clock', dt.timedelta(milliseconds=20), callback=lambda ev: loop.call_soon_threadsafe(s.pump))
        def pump(s):
            s.exchange.process(s._clock.timestamp_ns())
        def submit_order(s, command):
            s.exchange.process(s._clock.timestamp_ns())
            return super().submit_order(command)

    class PaperSandboxFactory(LiveExecClientFactory):
        @staticmethod
        def create(loop, name, config, portfolio, msgbus, cache, clock):
            return PaperSandboxClient(loop=loop, portfolio=portfolio, msgbus=msgbus, cache=cache, clock=clock, config=config)
    PaperSandboxFactory.__name__ = 'SandboxLiveExecClientFactory'   # node_builder passes the portfolio only to a factory of this name
    return L0PolymarketDataFactory, PaperSandboxFactory


class Jsonl:
    def __init__(s, path):
        s.f = open(path, 'a'); s.lock = threading.Lock()
    def write(s, row):
        with s.lock:
            s.f.write(json.dumps(row, default=str) + '\n'); s.f.flush()


def source_loop(src, strategies, loop, log, stop):
    """poll the source every src.POLL_S seconds (default 0.05 s: as fast as the source allows; HTTP sources set 1.0 for their rate limits); hand each NEW result to its event's strategy on the event loop. A result is (slug, name or None, value or None, info)."""
    from pickoff_strategy import ReleaseNumber
    done = set()
    while not stop.is_set():
        try:
            for slug, name, value, info in src.poll():
                if slug in done or slug not in strategies:
                    continue
                now = time.time_ns()
                rn = ReleaseNumber(event_slug=slug, value=float(value or 0.0), source=src.__class__.__name__, name=name or "", ts_event=now, ts_init=now)
                loop.call_soon_threadsafe(strategies[slug].on_data, rn)
                done.add(slug); log.write(dict(t=now, ev='release', slug=slug, name=name, value=value, info=info))
        except Exception as e:
            log.write(dict(t=time.time_ns(), ev='source error', err=repr(e)[:300]))
        stop.wait(float(getattr(src, 'POLL_S', 0.05)))


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument('--slugs'); ap.add_argument('--release'); ap.add_argument('--source')
    ap.add_argument('--spec', help='JSON {"events": [{"slug", "release" ISO, "source" "mod:Class"}]}: many events, each with its own release time and source')
    ap.add_argument('--logdir', required=True); ap.add_argument('--run-s', type=int, default=0); ap.add_argument('--preflight', type=int, default=0)
    a = ap.parse_args(argv)
    os.makedirs(a.logdir, exist_ok=True)
    iso_ns = lambda x: int(dt.datetime.fromisoformat(x.replace('Z', '+00:00')).timestamp() * 1e9)
    if a.spec:
        spec = json.load(open(a.spec))['events']
    else:
        spec = [dict(slug=x.strip(), release=a.release, source=a.source) for x in open(a.slugs).read().replace(',', '\n').split() if x.strip()]
    slugs = [e['slug'] for e in spec]
    REL = {e['slug']: iso_ns(e['release']) for e in spec}
    SRC = {e['slug']: e.get('source') for e in spec}
    GUARD = {e['slug']: float(e.get('guard', 0.002)) for e in spec}   # per-event edge guard (fraction of the number)
    evs = {}
    for s in slugs:
        ev = gamma_event(s)
        mk = event_markets(ev) if ev else []
        if mk:
            evs[s] = mk
    sf = os.path.join(a.logdir, 'slugs.json'); json.dump(list(evs), open(sf, 'w')); os.environ['PICKOFF_SLUGS_FILE'] = sf
    json.dump(evs, open(os.path.join(a.logdir, 'markets.json'), 'w'), indent=1)
    from nautilus_trader.config import TradingNodeConfig, LoggingConfig
    from nautilus_trader.live.node import TradingNode
    from nautilus_trader.adapters.polymarket.config import PolymarketDataClientConfig, PolymarketInstrumentProviderConfig
    from nautilus_trader.adapters.sandbox.config import SandboxExecutionClientConfig
    from pickoff_strategy import PickoffStrategy, PickoffConfig
    DF, XF = build_factories()
    strategies = {}
    for i, (s, mk) in enumerate(evs.items()):
        strategies[s] = PickoffStrategy(PickoffConfig(strategy_id=f'PICKOFF-{i:03d}', markets_json=json.dumps(mk), event_slug=s, release_ns=REL[s], subscribe_source=False,
                                                      edge_guard_frac=GUARD.get(s, 0.002)))
    data = dict(POLYMARKET=PolymarketDataClientConfig(instrument_config=PolymarketInstrumentProviderConfig(event_slug_builder='pickoff_live:slugs_for_provider'),
                                                      auto_load_missing_instruments=False))
    execc = dict(POLYMARKET=SandboxExecutionClientConfig(venue='POLYMARKET', starting_balances=[f'{WALLET_PUSD} pUSD'], base_currency='pUSD', oms_type='NETTING',
                                                         account_type='CASH', book_type='L2_MBP', trade_execution=False))
    node = TradingNode(config=TradingNodeConfig(trader_id='PAPER-PICKOFF-001', data_clients=data, exec_clients=execc,
                       logging=LoggingConfig(log_level='WARNING', log_level_file='INFO', log_directory=os.path.join(a.logdir, 'nautilus'), log_colors=False)))
    node.add_data_client_factory('POLYMARKET', DF)
    node.add_exec_client_factory('POLYMARKET', XF)
    for st in strategies.values():
        node.trader.add_strategy(st)
    node.build()
    loop = node.get_event_loop()
    log = Jsonl(os.path.join(a.logdir, 'source.jsonl')); dec = os.path.join(a.logdir, 'decisions.jsonl')
    stop = threading.Event()

    def reports():
        while not stop.wait(60):
            write_reports()
    def write_reports():
        try:
            f = node.trader.generate_order_fills_report()
            if f is not None:
                f.to_csv(os.path.join(a.logdir, 'fills.csv'))
            with open(dec, 'w') as g:
                for s, st in strategies.items():
                    for r in st.log_rows:
                        g.write(json.dumps(dict(slug=s, **r), default=str) + '\n')
        except Exception as e:
            log.write(dict(t=time.time_ns(), ev='report error', err=repr(e)[:300]))

    if a.preflight:
        def pf():
            time.sleep(a.preflight)
            books = {}
            for s, mk in evs.items():
                for m in mk:
                    for k in ('yes_id', 'no_id'):
                        from nautilus_trader.model.identifiers import InstrumentId
                        b = node.kernel.cache.order_book(InstrumentId.from_str(m[k]))
                        books[m[k]] = b is not None and (b.best_ask_price() is not None or b.best_bid_price() is not None)
            ok = sum(books.values()); rep = dict(preflight='PASS' if ok >= 0.9 * len(books) and len(books) else 'FAIL', events=len(evs), tokens=len(books), tokens_with_book=ok,
                                                 sandbox=type(node.kernel.exec_engine._clients[list(node.kernel.exec_engine._clients)[0]]).__name__)
            print(json.dumps(rep), flush=True); open(os.path.join(a.logdir, 'preflight.json'), 'w').write(json.dumps(rep))
            loop.call_soon_threadsafe(node.stop)
        threading.Thread(target=pf, daemon=True).start()
    else:
        import inspect
        for spec_src in sorted({v for v in SRC.values() if v}):
            sub = {s: mk for s, mk in evs.items() if SRC.get(s) == spec_src}
            if not sub:
                continue
            mod, cls = spec_src.split(':'); C_ = getattr(__import__(mod), cls)
            kw = dict(release_s={s: REL[s] / 1e9 for s in sub}) if 'release_s' in inspect.signature(C_.__init__).parameters else {}
            try:
                src = C_(sub, a.logdir, **kw)
            except Exception as e:
                log.write(dict(t=time.time_ns(), ev='source not started', source=spec_src, err=repr(e)[:300])); print('SOURCE NOT STARTED', spec_src, e, flush=True); continue
            log.write(dict(t=time.time_ns(), ev='source started', source=spec_src, events=len(sub)))
            threading.Thread(target=source_loop, args=(src, strategies, loop, log, stop), daemon=True).start()
        threading.Thread(target=reports, daemon=True).start()
        if a.run_s:
            threading.Timer(a.run_s, lambda: loop.call_soon_threadsafe(node.stop)).start()
    try:
        node.run()
    finally:
        stop.set(); write_reports(); node.dispose()
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
