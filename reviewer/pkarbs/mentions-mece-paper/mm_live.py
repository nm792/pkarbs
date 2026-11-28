"""PAPER node: mentions (frozen 10c rule at the registered decision times) + MECE buy-all-NO, on Nautilus with the same paper sandbox as the
events pickoff node (pickoff_live.build_factories: level-0 Polymarket data, SimulatedExchange with 250 ms insert latency, PolymarketFeeModel,
liquidity consumption, wall-clock venue). PAPER ONLY: no keys, no orders reach any venue. Also a CONTINUOUS book recorder: every own-book change
(top 5 levels, both tokens) to books-YYYYMMDDHH.jsonl.gz, which is the data the will-say nowcast and the offline rescore need.

Universe at start (restart daily to refresh it):
  mentions: every open Polymarket mention-markets event, fair values from it/mentions_pm_ws_paper.universe (needs the P121 --state dir with events.json).
  MECE:     open neg-risk events with 3..MAXLEGS active legs ending within --mece-hours, top --mece-max by 24h volume.
Usage: python3 mm_live.py --state <P121 state dir> --logdir DIR [--run-s 86400] [--mece-hours 72] [--mece-max 80] [--no-mentions] [--no-mece] [--preflight 60]
Outputs: fills.csv (Nautilus, every 60 s), decisions.jsonl, universe.json, books-*.jsonl.gz, nautilus/ logs."""
import os, sys, json, time, gzip, threading, argparse, importlib.util, urllib.request, datetime as dt
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
PAPER = os.path.join(ROOT, 'reviewer', 'pkarbs', 'metric-pickoff-2026-11-26', 'paper')
for p in (HERE, PAPER, os.path.join(ROOT, 'it')):
    sys.path.insert(0, p)
MAXLEGS = 20


def load_mod(name, path):
    spec = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


def gamma(url):
    req = urllib.request.Request(url, headers={'Accept-Encoding': 'gzip', 'User-Agent': 'mm-paper'})
    raw = urllib.request.urlopen(req, timeout=30).read()
    try:
        raw = gzip.decompress(raw)
    except OSError:
        pass
    return json.loads(raw)


def iid(cond, tok):
    return f'{cond}-{tok}.POLYMARKET'


def mentions_universe(state, now):
    sc = load_mod('mentions_pm_daily_scorer', os.path.join(ROOT, 'it', 'mentions_pm_daily_scorer.py'))
    wp = load_mod('mentions_pm_ws_paper', os.path.join(ROOT, 'it', 'mentions_pm_ws_paper.py'))
    ev, _ = wp.universe(sc, state, now)
    out = []
    for e in ev.values():
        if e['T'] < now:
            continue
        mk = [dict(cond=m['cond'], label=m['label'], q=m['q'], yes_id=iid(m['cond'], m['toks'][0]), no_id=iid(m['cond'], m['toks'][1])) for m in e['markets']]
        out.append(dict(id=e['id'], slug=e['slug'], t0=e['t0'], T=e['T'], markets=mk))
    return out


def mece_sets(evs):
    """Gamma events -> MECE sets (neg-risk, 3..MAXLEGS active two-token legs)."""
    out = []
    for e in evs:
        if not (e.get('negRisk') or e.get('enableNegRisk')):
            continue
        legs = []
        for m in e.get('markets', []):
            if m.get('closed') or not m.get('active') or not m.get('acceptingOrders', True):
                continue
            try:
                toks = json.loads(m['clobTokenIds'])
            except Exception:
                continue
            if len(toks) != 2:
                continue
            fs = m.get('feeSchedule') or {}
            legs.append(dict(cond=m['conditionId'], title=m.get('groupItemTitle') or m.get('question'), yes_id=iid(m['conditionId'], toks[0]), no_id=iid(m['conditionId'], toks[1]),
                             fee=float(fs.get('rate') or 0)))
        if 3 <= len(legs) <= MAXLEGS and len(legs) == sum(1 for m in e.get('markets', []) if not m.get('closed')):
            out.append(dict(slug=e['slug'], vol=float(e.get('volume24hr') or 0), legs=legs))
    return out


def mece_universe(hours, cap):
    now = dt.datetime.now(dt.timezone.utc); hi = now + dt.timedelta(hours=hours)
    evs = []
    for off in range(0, 1000, 100):
        page = gamma('https://gamma-api.polymarket.com/events?closed=false&active=true&limit=100&offset=%d&end_date_min=%s&end_date_max=%s' %
                     (off, now.strftime('%Y-%m-%dT%H:%M:%SZ'), hi.strftime('%Y-%m-%dT%H:%M:%SZ')))
        evs += page
        if len(page) < 100:
            break
    return sorted(mece_sets(evs), key=lambda s: -s['vol'])[:cap]


class Recorder:
    """Every own-book change (top 5 levels) -> books-YYYYMMDDHH.jsonl.gz, written only when the levels changed."""
    def __init__(s, d):
        s.d, s.last, s.lock, s.f, s.hour = d, {}, threading.Lock(), None, None

    def __call__(s, tok, ts_ns, bids, asks):
        key = (tuple(bids), tuple(asks))
        if s.last.get(tok) == key:
            return
        s.last[tok] = key
        h = time.strftime('%Y%m%d%H', time.gmtime(ts_ns / 1e9))
        with s.lock:
            if h != s.hour:
                if s.f:
                    s.f.close()
                s.f, s.hour = gzip.open(os.path.join(s.d, 'books-%s.jsonl.gz' % h), 'at'), h
            s.f.write(json.dumps(dict(recv_ms=ts_ns // 1_000_000, asset=tok.split('-')[1].split('.')[0], cond=tok.split('-')[0],
                                      bids=[dict(price=p, size=z) for p, z in bids], asks=[dict(price=p, size=z) for p, z in asks])) + '\n')

    def close(s):
        with s.lock:
            if s.f:
                s.f.close()


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument('--state'); ap.add_argument('--logdir', required=True); ap.add_argument('--run-s', type=int, default=86400)
    ap.add_argument('--mece-hours', type=int, default=72); ap.add_argument('--mece-max', type=int, default=80)
    ap.add_argument('--no-mentions', action='store_true'); ap.add_argument('--no-mece', action='store_true'); ap.add_argument('--preflight', type=int, default=0)
    a = ap.parse_args(argv)
    os.makedirs(a.logdir, exist_ok=True)
    now = time.time()
    men = [] if a.no_mentions else mentions_universe(a.state, now)
    mec = [] if a.no_mece else mece_universe(a.mece_hours, a.mece_max)
    slugs = sorted({e['slug'] for e in men} | {s['slug'] for s in mec})
    json.dump(dict(mentions=men, mece=mec), open(os.path.join(a.logdir, 'universe.json'), 'w'), indent=1)
    sf = os.path.join(a.logdir, 'slugs.json'); json.dump(slugs, open(sf, 'w')); os.environ['PICKOFF_SLUGS_FILE'] = sf
    print(json.dumps(dict(mentions_events=len(men), mentions_markets=sum(len(e['markets']) for e in men), mece_sets=len(mec), mece_legs=sum(len(s['legs']) for s in mec))), flush=True)
    from nautilus_trader.config import TradingNodeConfig, LoggingConfig
    from nautilus_trader.live.node import TradingNode
    from nautilus_trader.adapters.polymarket.config import PolymarketDataClientConfig, PolymarketInstrumentProviderConfig
    from nautilus_trader.adapters.sandbox.config import SandboxExecutionClientConfig
    import pickoff_live as PL
    import mm_strategy as S
    rec = Recorder(a.logdir); S.RECORDER[0] = rec
    DF, XF = PL.build_factories()
    strats = [S.MentionsStrategy(S.MentionsConfig(strategy_id=f'MENTIONS-{i:03d}', event_json=json.dumps(e))) for i, e in enumerate(men)] + \
             [S.MeceStrategy(S.MeceConfig(strategy_id=f'MECE-{i:03d}', set_json=json.dumps(s))) for i, s in enumerate(mec)]
    data = dict(POLYMARKET=PolymarketDataClientConfig(instrument_config=PolymarketInstrumentProviderConfig(event_slug_builder='pickoff_live:slugs_for_provider'),
                                                      auto_load_missing_instruments=False))
    execc = dict(POLYMARKET=SandboxExecutionClientConfig(venue='POLYMARKET', starting_balances=[f'{PL.WALLET_PUSD} pUSD'], base_currency='pUSD', oms_type='NETTING',
                                                         account_type='CASH', book_type='L2_MBP', trade_execution=False))
    node = TradingNode(config=TradingNodeConfig(trader_id='PAPER-MM-001', data_clients=data, exec_clients=execc,
                       logging=LoggingConfig(log_level='WARNING', log_level_file='INFO', log_directory=os.path.join(a.logdir, 'nautilus'), log_colors=False)))
    node.add_data_client_factory('POLYMARKET', DF); node.add_exec_client_factory('POLYMARKET', XF)
    for st in strats:
        node.trader.add_strategy(st)
    node.build()
    loop = node.get_event_loop(); stop = threading.Event()

    def write_reports():
        try:
            f = node.trader.generate_order_fills_report()
            if f is not None:
                f.to_csv(os.path.join(a.logdir, 'fills.csv'))
            with open(os.path.join(a.logdir, 'decisions.jsonl'), 'w') as g:
                for st in strats:
                    for r in st.log_rows:
                        g.write(json.dumps(dict(strategy=str(st.id), **r), default=str) + '\n')
        except Exception as e:
            print('report error', repr(e)[:300], flush=True)

    if a.preflight:
        def pf():
            time.sleep(a.preflight)
            from nautilus_trader.model.identifiers import InstrumentId
            toks = [m[k] for e in men for m in e['markets'] for k in ('yes_id', 'no_id')] + [l[k] for s in mec for l in s['legs'] for k in ('yes_id', 'no_id')]
            ok = sum(1 for t in toks if (lambda b: b is not None and (b.best_ask_price() is not None or b.best_bid_price() is not None))(node.kernel.cache.order_book(InstrumentId.from_str(t))))
            rep = dict(preflight='PASS' if toks and ok >= 0.9 * len(toks) else 'FAIL', tokens=len(toks), tokens_with_book=ok, mentions_events=len(men), mece_sets=len(mec))
            print(json.dumps(rep), flush=True); open(os.path.join(a.logdir, 'preflight.json'), 'w').write(json.dumps(rep))
            loop.call_soon_threadsafe(node.stop)
        threading.Thread(target=pf, daemon=True).start()
    else:
        threading.Thread(target=lambda: [write_reports() for _ in iter(lambda: stop.wait(60), True)], daemon=True).start()
        if a.run_s:
            threading.Timer(a.run_s, lambda: loop.call_soon_threadsafe(node.stop)).start()
    try:
        node.run()
    finally:
        stop.set(); write_reports(); rec.close(); node.dispose()
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
