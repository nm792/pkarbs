"""Capped CS2 event-only live pilot (Polymarket). Nick approved building it 4 Nov 2026 06:34Z.

Rule (same as winmodels/esports/bo3/bo3bt.py event_only, NOTE-cs2-bo3-backtest-2026-11-04.md):
  After a round score change on the Polymarket sports WebSocket, for W=30 s, rest a post-only (maker) BUY at
  market mid x (1 - 0.025), rounded down to the tick, on the side whose model jump (beta x model move) is >= 1c and
  has not yet shown in the mid since 30 s before the event. Never at or above the best ask. Hold to result.
  Markets: Match Winner and the Map k Winner of the map in play, top-tier CS2 events only.
  Within-map round events only: map-end updates reach the WS minutes late, so they are not traded.

Caps (hard):
  - per match: filled cost + open order value <= MATCH_CAP_USD ($250)
  - whole pilot: open exposure (unresolved filled cost + open orders) <= LOSS_LIMIT_USD + min(realized P&L, 0),
    so the worst case total loss can never pass $500. Realized P&L <= -$500 halts the pilot (cancel all, stop).
  - state (positions, realized P&L) persists in OUT/state.json so a restart cannot reset the limit.

Modes:
  --mode dry  (default): everything runs against live markets; orders are paper only (nothing is sent).
  --mode live : real post-only orders. Needs PM_KEY_FILE (see KEY-INSTALL.md), a geoblock check that passes, the
                order heartbeat (auto-cancel if this process stops), and the file OUT/LIVE_OK (written by a person).

Logs (OUT/pilot.jsonl, one JSON object per line, 'type' field): ws_score, event, window, order_place,
  order_reject, order_cancel, queue (size ahead of our order at our price), fill (real), paper_fill (from public
  prints, naive and queue-adjusted), markout (token mid 60 s after each fill), feed_delay (WS receipt minus the
  market's own reaction time), resolve, risk, halt, error. OUT/summary.json is rewritten every minute.
Stop: touch OUT/STOP (cancels everything and exits), or SIGTERM.
"""
import argparse, asyncio, bisect, collections, json, math, os, signal, ssl, sys, time, traceback, urllib.request
import urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import model as MD

GAMMA = 'https://gamma-api.polymarket.com'; CLOB = 'https://clob.polymarket.com'
DATA = 'https://data-api.polymarket.com'; SPORTS_WS = 'wss://sports-api.polymarket.com/ws'
UA = 'Mozilla/5.0 pkarbs-cs2-pilot'
CS2_SERIES = '10310'
TIER1 = ['iem ', 'esl pro league', 'blast', 'pgl', 'major', 'starladder', 'thunderpick', 'fissure', 'esports world cup',
         'perfect world', 'cs asia', 'skyesports masters']

CFG = dict(W=30.0, PRE=30.0, D=0.025, MINJ=0.01, E=0.01, SHARE_CAP=1000, MATCH_CAP_USD=250.0, LOSS_LIMIT_USD=500.0,
           MIN_EVENT_VOL=20000.0, BOOK_POLL=1.0, TRADES_POLL=2.0, DISCOVER=300.0, RESOLVE_POLL=300.0,
           MAX_SPREAD=0.10, MID_LO=0.05, MID_HI=0.95, HOURS=12.0)


def now(): return time.time()
def iso(t=None): return time.strftime('%Y-%m-%dT%H:%M:%S', time.gmtime(t or now())) + 'Z'


# ---------------------------------------------------------------- HTTP (blocking, run in threads)
def _ctx():
    f = os.environ.get('SSL_CERT_FILE')
    return ssl.create_default_context(cafile=f) if f else ssl.create_default_context()


def http_json(url, body=None, timeout=10):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, headers={'User-Agent': UA, 'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=timeout, context=_ctx()) as r:
        return json.load(r)


async def aget(url, body=None):
    return await asyncio.to_thread(http_json, url, body)


def floor_tick(p, tick):
    return round(math.floor(p / tick + 1e-9) * tick, 6)


# ---------------------------------------------------------------- state
class Market:
    def __init__(s, gid, kind, m, home):
        s.gid, s.kind, s.cond = gid, kind, m['conditionId']
        s.tokens = json.loads(m['clobTokenIds']); s.outcomes = json.loads(m['outcomes'])
        s.o0_home = MD.same_team(s.outcomes[0], home)
        s.ok = s.o0_home != MD.same_team(s.outcomes[1], home)       # exactly one outcome matches the home team
        s.tick = float(m.get('orderPriceMinTickSize') or 0.01); s.min_size = float(m.get('orderMinSize') or 5)
        fs = m.get('feeSchedule') or {}; s.reb = float(fs.get('rebateRate') or 0) * float(fs.get('rate') or 0)
        s.mids = collections.deque(maxlen=900); s.book = {}          # tok index -> (best_bid, best_ask, {price: size})
        s.q = None; s.window = None; s.order = None; s.seen_trades = set(); s.last_trades_poll = 0

    def mid(s):
        return s.mids[-1][1] if s.mids else None

    def mid_at(s, t):
        if not s.mids: return None
        ts = [x[0] for x in s.mids]; i = bisect.bisect_right(ts, t) - 1
        return s.mids[i][1] if i >= 0 else None


class Game:
    def __init__(s, gid, ev):
        s.gid, s.title, s.slug = gid, ev['title'], ev['slug']
        s.home = s.away = None; s.state = None; s.markets = {}; s.ev = ev; s.last_ws = 0; s.live = False


class Pilot:
    def __init__(s, a):
        s.a = a; s.mode = a.mode; s.out = a.out; os.makedirs(s.out, exist_ok=True)
        s.logf = open(os.path.join(s.out, 'pilot.jsonl'), 'a', buffering=1)
        s.games = {}; s.client = None; s.halted = False; s.stop = False; s.nid = 0; s.hb_id = ''; s.hb_fail = 0
        s.pending = []   # (due_t, kind, payload) for markouts and feed-delay checks
        s.end_t = now() + CFG['HOURS'] * 3600
        s.state_fn = os.path.join(s.out, 'state.json')
        s.st = json.load(open(s.state_fn)) if os.path.exists(s.state_fn) else dict(
            realized=0.0, positions={}, resolved={}, fills=0, matches={}, started=iso())
        # positions: cond -> {tok: [shares, cost]}, plus gid; persisted

    # ---------------- logging / persistence
    def log(s, typ, **kw):
        kw = dict(t=round(now(), 3), iso=iso(), type=typ, mode=s.mode, **kw)
        s.logf.write(json.dumps(kw, default=str) + '\n')

    def save(s):
        tmp = s.state_fn + '.tmp'; json.dump(s.st, open(tmp, 'w'), indent=1); os.replace(tmp, s.state_fn)

    # ---------------- risk
    def open_value(s, gid=None):
        v = 0.0
        for g in s.games.values():
            for m in g.markets.values():
                o = m.order
                if o and (gid is None or m.gid == gid): v += (o['size'] - o['filled']) * o['price']
        return v

    def pos_cost(s, gid=None):
        v = 0.0
        for cond, p in s.st['positions'].items():
            if cond in s.st['resolved']: continue
            if gid is None or p['gid'] == gid: v += sum(x[1] for x in p['tok'].values())
        return v

    def room(s, gid):
        per_match = CFG['MATCH_CAP_USD'] - s.pos_cost(gid) - s.open_value(gid)
        total = CFG['LOSS_LIMIT_USD'] + min(s.st['realized'], 0.0) - s.pos_cost() - s.open_value()
        return min(per_match, total)

    # ---------------- discovery
    async def discover(s):
        # gamma's start_date_min filters on the event's creation date, not the match time: pull a wide window, page it,
        # and filter on startTime below
        smin = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(now() - 14 * 86400)); evs = []
        for off in range(0, 1000, 100):
            q = urllib.parse.urlencode(dict(series_id=CS2_SERIES, closed='false', start_date_min=smin, limit=100, offset=off))
            try: page = await aget(f'{GAMMA}/events?{q}')
            except Exception as e: s.log('error', where='discover', err=repr(e)); return
            evs += page or []
            if not page or len(page) < 100: break
        horizon = now() + 3600; n_new = 0
        for ev in evs:
            gid = ev.get('gameId')
            if not gid or gid in s.games: continue
            st = ev.get('startTime') or ''
            try: st_t = time.mktime(time.strptime(st[:19], '%Y-%m-%dT%H:%M:%S')) - time.timezone
            except Exception: continue
            if st_t > horizon or st_t < now() - 8 * 3600: continue
            title = ev['title'].lower(); vol = float(ev.get('volume') or 0)
            tier1 = any(k in title for k in TIER1)
            if not tier1 or vol < CFG['MIN_EVENT_VOL']:
                continue
            g = Game(int(gid), ev); s.games[int(gid)] = g; n_new += 1
            teams = [t.get('name') for t in ev.get('teams') or []]
            s.log('discover', gid=int(gid), title=ev['title'], vol=round(vol), start=st, teams=teams)
        if n_new: s.log('discover_done', tracked=len(s.games))

    def attach_markets(s, g):
        for m in g.ev.get('markets') or []:
            t = m.get('groupItemTitle') or ''
            kind = 'match' if t == 'Match Winner' else ('map' + t[4]) if t in ('Map 1 Winner', 'Map 2 Winner', 'Map 3 Winner') else None
            if not kind or kind in g.markets or not m.get('clobTokenIds'): continue
            mk = Market(g.gid, kind, m, g.home)
            g.markets[kind] = mk
            s.log('market', gid=g.gid, kind=kind, cond=mk.cond, outcomes=mk.outcomes, o0_home=mk.o0_home, ok=mk.ok,
                  home=g.home, away=g.away, tick=mk.tick, min_size=mk.min_size, reb=mk.reb)

    # ---------------- sports WS
    async def ws_loop(s):
        import websockets
        while not s.stop:
            try:
                async with websockets.connect(SPORTS_WS, ssl=_ctx(), user_agent_header=UA, open_timeout=20,
                                              ping_interval=None, max_size=2 ** 22) as ws:
                    s.log('ws_open')
                    while not s.stop:
                        msg = await asyncio.wait_for(ws.recv(), 60)
                        if msg == 'ping': await ws.send('pong'); continue
                        try: d = json.loads(msg)
                        except Exception: continue
                        if d.get('leagueAbbreviation') == 'cs2': s.on_score(d, now())
            except Exception as e:
                s.log('ws_error', err=repr(e)); await asyncio.sleep(1)

    def on_score(s, d, R):
        gid = d.get('gameId'); g = s.games.get(gid)
        if g is None: return
        g.last_ws = R; g.live = bool(d.get('live'))
        if g.home is None:
            g.home, g.away = d.get('homeTeam'), d.get('awayTeam'); s.attach_markets(g)
        new = MD.parse(d.get('score'))
        if new is None or (g.state and new == g.state['raw']): return
        s.log('ws_score', gid=gid, score=d.get('score'), period=d.get('period'), status=d.get('status'))
        prev = g.state['s'] if g.state else None
        kind, k = MD.round_event(prev, new)
        keep = dict(new)
        if kind == 'reset':        # keep the last round score of the map until the map count updates
            keep = dict(prev)
        g.state = dict(s=keep, raw=new)
        if kind != 'round':
            if kind: s.log('event_skip', gid=gid, kind=kind, map=k)
            return
        # map q for the map in play: fixed from the map market's home price 60 s before its first round event
        mk_map = g.markets.get(f'map{k}')
        if mk_map is not None and mk_map.q is None and prev['ra'] + prev['rb'] == 0:
            p0 = mk_map.mid_at(R - 60) or mk_map.mid()
            if p0 is not None:
                ph = p0 if mk_map.o0_home else 1 - p0
                mk_map.q = MD.q_from(min(max(ph, 0.05), 0.95)); s.log('map_q', gid=gid, map=k, p_home=ph, q=mk_map.q)
        moves = {}
        if mk_map is not None and mk_map.q is not None: moves[f'map{k}'] = (mk_map, MD.map_move(prev, new, mk_map.q), MD.BETA_MAP)
        mm = g.markets.get('match')
        if mm is not None:
            dmv = MD.match_move(prev, new)
            if dmv is not None: moves['match'] = (mm, dmv, MD.BETA_MATCH)
        s.nid += 1; eid = f'{gid}-{s.nid}'
        s.log('event', eid=eid, gid=gid, map=k, prev=prev, new=new, moves={kk: v[1] for kk, v in moves.items()})
        for kk, (mk, dh, beta) in moves.items():
            if not mk.ok: s.log('window_skip', eid=eid, kind=kk, why='team names do not match outcomes'); continue
            d0 = dh if mk.o0_home else -dh; j = beta * d0
            base = mk.mid_at(R - CFG['PRE'])
            s.pending.append((R + 60, 'feed_delay', dict(eid=eid, kind=kk, gid=gid, R=R, j=j)))
            if abs(j) < CFG['MINJ'] or base is None:
                s.log('window_skip', eid=eid, kind=kk, j=round(j, 4), base=base, why='small jump' if base is not None else 'no mid history')
                continue
            mk.window = dict(eid=eid, R=R, j=j, base=base, end=R + CFG['W'], tok=0 if j > 0 else 1)
            s.log('window', eid=eid, gid=gid, kind=kk, cond=mk.cond, j=round(j, 4), base=base, mid=mk.mid(), tok=mk.window['tok'])

    # ---------------- books
    async def book_loop(s):
        while not s.stop:
            t0 = now()
            mks = [m for g in s.games.values() if g.home and (g.live or now() - g.last_ws < 600) for m in g.markets.values()]
            if mks:
                body = [{'token_id': tk} for m in mks for tk in m.tokens]
                try:
                    books = await aget(f'{CLOB}/books', body)
                    by = {b['asset_id']: b for b in books}
                    T = now()
                    for m in mks:
                        for i, tk in enumerate(m.tokens):
                            b = by.get(tk)
                            if not b: continue
                            bids = {float(x['price']): float(x['size']) for x in b.get('bids') or []}
                            asks = {float(x['price']): float(x['size']) for x in b.get('asks') or []}
                            m.book[i] = (max(bids) if bids else None, min(asks) if asks else None, bids)
                            if b.get('tick_size'): m.tick = float(b['tick_size'])
                        bb, ba, _ = m.book.get(0, (None, None, None))
                        if bb is not None and ba is not None and ba > bb and ba - bb < CFG['MAX_SPREAD']:
                            m.mids.append((T, (bb + ba) / 2))
                    for m in mks: await s.manage(m, T)
                except Exception as e:
                    s.log('error', where='books', err=repr(e))
            await s.run_pending()
            await asyncio.sleep(max(0.05, CFG['BOOK_POLL'] - (now() - t0)))

    # ---------------- strategy / orders
    async def manage(s, m, T):
        w = m.window; o = m.order
        if o: await s.track_order(m, o, T)
        o = m.order
        if w is None:
            if o: await s.cancel(m, 'no window')
            return
        if T > w['end'] or s.halted or s.stop:
            if o: await s.cancel(m, 'window end' if T > w['end'] else 'halt')
            m.window = None; return
        mk = m.mid()
        why = None
        if mk is None or not (CFG['MID_LO'] <= mk <= CFG['MID_HI']): why = 'mid out of range'
        elif w['j'] > 0 and mk - w['base'] >= w['j']: why = 'already moved'
        elif w['j'] < 0 and w['base'] - mk >= -w['j']: why = 'already moved'
        tok = w['tok']; mt = mk if tok == 0 else (1 - mk if mk is not None else None)
        if why is None:
            price = floor_tick(mt * (1 - CFG['D']), m.tick)
            best_ask = m.book.get(tok, (None, None, None))[1]
            fair = (w['base'] + w['j']) if tok == 0 else 1 - (w['base'] + w['j'])
            if best_ask is not None and price >= best_ask - 1e-9: why = 'would cross'
            elif fair - price < CFG['E']: why = 'fair - bid < E'
            elif price < m.tick: why = 'price too low'
        if why:
            if o: await s.cancel(m, why)
            return
        if o and abs(o['price'] - price) < 1e-9: return
        if o:
            ok = await s.cancel(m, 'requote')
            if not ok: return
        room = s.room(m.gid)
        size = math.floor(min(CFG['SHARE_CAP'], room / price) if price > 0 else 0)
        if size < m.min_size or size * price < 1.0:
            s.log('order_skip', eid=w['eid'], kind=m.kind, why='cap', room=round(room, 2)); return
        await s.place(m, w, tok, price, size, T)

    def level(s, m, tok, price):
        b = m.book.get(tok)
        return b[2].get(round(price, 6), 0.0) if b else 0.0

    async def place(s, m, w, tok, price, size, T):
        ahead = s.level(m, tok, price)
        bb, ba, _ = m.book.get(tok, (None, None, None))
        o = dict(id=None, eid=w['eid'], tok=tok, token=m.tokens[tok], price=price, size=float(size), filled=0.0,
                 paper_naive=0.0, paper_queue=0.0, ahead0=ahead, ahead=ahead, placed=T)
        if s.mode == 'live':
            try:
                r = await s.client.place_limit_order(token_id=m.tokens[tok], price=str(price), size=str(size), side='BUY',
                                                     post_only=True)
            except Exception as e:
                s.log('order_reject', eid=w['eid'], kind=m.kind, err=repr(e)); return
            if not getattr(r, 'ok', False):
                s.log('order_reject', eid=w['eid'], kind=m.kind, code=getattr(r, 'code', None), msg=getattr(r, 'message', None)); return
            o['id'] = r.order_id
            if getattr(r, 'status', None) not in ('live', None):
                s.log('warn', what='order not resting', status=str(r.status), id=r.order_id)
        else:
            s.nid += 1; o['id'] = f'paper-{s.nid}'
        m.order = o
        s.st['matches'].setdefault(str(m.gid), m.gid)
        s.log('order_place', id=o['id'], eid=w['eid'], gid=m.gid, kind=m.kind, cond=m.cond, tok=tok, outcome=m.outcomes[tok],
              price=price, size=size, usd=round(price * size, 2), mid0=m.mid(), best_bid=bb, best_ask=ba, ahead=ahead,
              lag_since_event=round(T - w['R'], 2))

    async def cancel(s, m, why):
        o = m.order
        if not o: return True
        if s.mode == 'live':
            try:
                r = await s.client.cancel_order(order_id=o['id'])
                if o['id'] in (r.not_canceled or {}):
                    s.log('error', where='cancel', id=o['id'], resp=str(r.not_canceled))
            except Exception as e:
                s.log('error', where='cancel', id=o['id'], err=repr(e)); return False
            await s.track_order(m, o, now(), final=True)
        else:
            await s.paper_fills(m, o, now())
        s.log('order_cancel', id=o['id'], kind=m.kind, gid=m.gid, why=why, filled=o['filled'], paper_naive=o['paper_naive'],
              paper_queue=o['paper_queue'], ahead_end=o['ahead'], rested_s=round(now() - o['placed'], 1))
        m.order = None
        return True

    async def track_order(s, m, o, T, final=False):
        # queue: our place in line at our price = min(previous estimate, level size now minus our own remainder)
        lvl = s.level(m, o['tok'], o['price'])
        mine = (o['size'] - o['filled']) if s.mode == 'live' else 0.0
        o['ahead'] = max(0.0, min(o['ahead'], lvl - mine))
        s.log('queue', id=o['id'], kind=m.kind, level=lvl, ahead=round(o['ahead'], 2), filled=o['filled'])
        await s.paper_fills(m, o, T)
        if s.mode == 'live':
            try:
                r = await s.client.get_order(order_id=o['id'])
                got = float(r.size_matched or 0)
            except Exception as e:
                s.log('error', where='get_order', id=o['id'], err=repr(e)); return
            if got > o['filled'] + 1e-9:
                s.on_fill(m, o, got - o['filled'], T, real=True); o['filled'] = got
            if not final and o['filled'] >= o['size'] - 1e-9:
                s.log('order_done', id=o['id'], kind=m.kind, filled=o['filled']); m.order = None

    async def paper_fills(s, m, o, T):
        """Paper fills from public prints: a print that sells into our token's bids at <= our price, after we placed.
        naive = we are first in line; queue = the size ahead of us at placement must trade first."""
        if T - m.last_trades_poll < CFG['TRADES_POLL']: return
        m.last_trades_poll = T
        try: d = await aget(f"{DATA}/v2/trades?condition={m.cond}&limit=200")
        except Exception as e: s.log('error', where='trades', err=repr(e)); return
        rows = d.get('data') if isinstance(d, dict) else d
        for t in sorted(rows or [], key=lambda x: x['timestamp']):
            key = (t.get('transaction_hash'), t.get('proxy_wallet'), t.get('token_id'), t.get('price'), t.get('size'), t.get('side'))
            if key in m.seen_trades: continue
            m.seen_trades.add(key)
            if t['timestamp'] < o['placed'] - 0.5: continue
            is0 = t['token_id'] == m.tokens[0]; ph = t['price'] if is0 else 1 - t['price']
            sell0 = (is0 and t['side'] == 'SELL') or ((not is0) and t['side'] == 'BUY')
            hit = (o['tok'] == 0 and sell0 and ph <= o['price'] + 1e-9) or (o['tok'] == 1 and (not sell0) and (1 - ph) <= o['price'] + 1e-9)
            if not hit: continue
            sz = float(t['size']); rem_n = o['size'] - o['paper_naive']
            fn = min(sz, max(rem_n, 0)); o['paper_naive'] += fn
            # queue-adjusted: this print first eats the size still ahead of us
            o.setdefault('q_ahead', o['ahead0']); eat = min(sz, o['q_ahead']); o['q_ahead'] -= eat
            fq = min(sz - eat, max(o['size'] - o['paper_queue'], 0)); o['paper_queue'] += fq
            s.log('paper_fill', id=o['id'], kind=m.kind, gid=m.gid, print_px=round(ph if o['tok'] == 0 else 1 - ph, 4),
                  print_size=sz, naive=fn, queue=fq, ahead_left=round(o['q_ahead'], 2), print_ts=t['timestamp'])
            if s.mode == 'dry' and fn > 0:
                s.on_fill(m, o, fn, T, real=False); o['filled'] += fn

    def on_fill(s, m, o, q, T, real):
        p = s.st['positions'].setdefault(m.cond, dict(gid=m.gid, kind=m.kind, tokens=m.tokens, tok={}))
        x = p['tok'].setdefault(str(o['tok']), [0.0, 0.0]); x[0] += q; x[1] += q * o['price']
        s.st['fills'] += 1; s.save()
        mt = m.mid(); mt = mt if o['tok'] == 0 else (1 - mt if mt is not None else None)
        s.log('fill', id=o['id'], real=real, gid=m.gid, kind=m.kind, cond=m.cond, tok=o['tok'], price=o['price'], shares=q,
              usd=round(q * o['price'], 2), mid_at_fill=mt, est_rebate=round(q * m.reb * o['price'] * (1 - o['price']), 4),
              since_place=round(T - o['placed'], 1))
        s.pending.append((T + 60, 'markout', dict(id=o['id'], cond=m.cond, gid=m.gid, kind=m.kind, tok=o['tok'], price=o['price'], shares=q, real=real)))

    async def run_pending(s):
        T = now(); keep = []
        for due, kind, p in s.pending:
            if due > T: keep.append((due, kind, p)); continue
            g = s.games.get(p['gid']); m = g.markets.get(p['kind']) if g else None
            if m is None: continue
            if kind == 'markout':
                mt = m.mid(); mt = mt if (mt is None or p['tok'] == 0) else 1 - mt
                s.log('markout', **p, mid_60s=mt, pnl_60s=None if mt is None else round(p['shares'] * (mt - p['price']), 3),
                      pct_60s=None if mt is None else round(100 * (mt - p['price']) / p['price'], 2))
            elif kind == 'feed_delay':
                R = p['R']; pre = m.mid_at(R - 60); post = m.mid_at(R + 60)
                if pre is None or post is None or abs(post - pre) < 0.01:
                    s.log('feed_delay', **p, move=None if pre is None or post is None else round(post - pre, 4), delay_s=None); continue
                half = pre + (post - pre) / 2; sg = 1 if post > pre else -1; th = None
                for t_, v in m.mids:
                    if t_ >= R - 60 and (v - half) * sg >= 0: th = t_; break
                s.log('feed_delay', **p, move=round(post - pre, 4), agrees=(sg > 0) == (p['j'] > 0),
                      delay_s=None if th is None else round(R - th, 1))
        s.pending = keep

    # ---------------- resolution
    async def resolve_loop(s):
        while not s.stop:
            for cond, p in list(s.st['positions'].items()):
                if cond in s.st['resolved']: continue
                try: ms = await aget(f'{GAMMA}/markets?condition_ids={cond}')
                except Exception as e: s.log('error', where='resolve', err=repr(e)); continue
                if not ms or not ms[0].get('closed'): continue
                op = [float(x) for x in json.loads(ms[0]['outcomePrices'])]
                if max(op) < 0.99: continue
                pnl = sum(sh * op[int(k)] - cost for k, (sh, cost) in p['tok'].items())
                s.st['resolved'][cond] = round(pnl, 4); s.st['realized'] += pnl; s.save()
                s.log('resolve', cond=cond, gid=p['gid'], kind=p['kind'], payout=op, pnl=round(pnl, 2), realized=round(s.st['realized'], 2))
                if s.st['realized'] <= -CFG['LOSS_LIMIT_USD'] + 1e-6 and not s.halted:
                    await s.halt('loss limit reached')
            for _ in range(int(CFG['RESOLVE_POLL'] / 2)):
                if s.stop: return
                await asyncio.sleep(2)

    async def halt(s, why):
        s.halted = True; s.log('halt', why=why, realized=s.st['realized'])
        for g in s.games.values():
            for m in g.markets.values():
                if m.order: await s.cancel(m, 'halt')
                m.window = None
        if s.mode == 'live':
            try: await s.client.cancel_all()
            except Exception as e: s.log('error', where='cancel_all', err=repr(e))

    # ---------------- live client and heartbeat
    async def heartbeat_loop(s):
        while not s.stop and s.mode == 'live':
            try:
                hb = await s.client.send_order_heartbeat(heartbeat_id=s.hb_id); s.hb_id = hb.heartbeat_id; s.hb_fail = 0
            except Exception as e:
                hid = getattr(e, 'heartbeat_id', None)
                if hid: s.hb_id = hid
                s.hb_fail += 1; s.log('error', where='heartbeat', err=repr(e), n=s.hb_fail)
                if s.hb_fail >= 2 and not s.halted: await s.halt('heartbeat failing')
            await asyncio.sleep(5)

    async def misc_loop(s):
        last_disc = 0; last_sum = 0
        while not s.stop:
            T = now()
            if T - last_disc > CFG['DISCOVER']: await s.discover(); last_disc = T
            if T - last_sum > 60: s.summary(); last_sum = T
            if os.path.exists(os.path.join(s.out, 'STOP')) or T > s.end_t:
                s.log('stop', why='STOP file' if T <= s.end_t else 'time limit'); await s.shutdown(); return
            await asyncio.sleep(2)

    def summary(s):
        sm = dict(iso=iso(), mode=s.mode, halted=s.halted, games=len(s.games),
                  live_games=sum(1 for g in s.games.values() if g.live), realized=round(s.st['realized'], 2),
                  open_exposure=round(s.pos_cost() + s.open_value(), 2), fills=s.st['fills'],
                  positions=len(s.st['positions']), resolved=len(s.st['resolved']))
        json.dump(sm, open(os.path.join(s.out, 'summary.json'), 'w'), indent=1)

    async def shutdown(s):
        s.stop = True
        for g in s.games.values():
            for m in g.markets.values():
                if m.order: await s.cancel(m, 'shutdown')
        if s.mode == 'live' and s.client:
            try: await s.client.cancel_all()
            except Exception as e: s.log('error', where='cancel_all', err=repr(e))
        s.save(); s.summary()

    async def preflight(s):
        try: geo = await aget('https://polymarket.com/api/geoblock')
        except Exception as e: geo = dict(error=repr(e))
        s.log('start', cfg=CFG, geoblock=geo, state=dict(realized=s.st['realized'], positions=len(s.st['positions'])))
        if s.mode != 'live': return True
        if geo.get('blocked') is not False:
            s.log('halt', why='geoblock check did not pass', geo=geo); return False
        if not os.path.exists(os.path.join(s.out, 'LIVE_OK')):
            s.log('halt', why='OUT/LIVE_OK missing: a person must approve live trading by writing this file'); return False
        kf = os.environ.get('PM_KEY_FILE', '/etc/pkarbs/pm-pilot.env')
        st = os.stat(kf)
        if st.st_mode & 0o077:
            s.log('halt', why=f'{kf} is readable by group/others; chmod 600'); return False
        env = {}
        for line in open(kf):
            if '=' in line and not line.strip().startswith('#'):
                k, v = line.strip().split('=', 1); env[k.strip()] = v.strip().strip('"\'')
        from polymarket import AsyncSecureClient
        s.client = await AsyncSecureClient.create(private_key=env['POLYMARKET_PRIVATE_KEY'],
                                                  wallet=env.get('POLYMARKET_WALLET_ADDRESS') or None)
        del env
        bal = await s.client.get_balance_allowance(asset_type='COLLATERAL')
        s.log('live_ready', wallet=str(s.client.wallet), wallet_type=str(s.client.wallet_type), balance=str(bal.balance))
        await s.client.cancel_all()
        return True

    async def main(s):
        if not await s.preflight(): return
        loop = asyncio.get_running_loop()
        for sig in (signal.SIGTERM, signal.SIGINT):
            loop.add_signal_handler(sig, lambda: asyncio.ensure_future(s.shutdown()))
        tasks = [s.ws_loop(), s.book_loop(), s.resolve_loop(), s.misc_loop()]
        if s.mode == 'live': tasks.append(s.heartbeat_loop())
        try:
            await asyncio.gather(*[asyncio.create_task(t) for t in tasks])
        except Exception:
            s.log('error', where='main', err=traceback.format_exc())
        finally:
            if not s.stop: await s.shutdown()


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--mode', choices=['dry', 'live'], default='dry')
    ap.add_argument('--out', default=os.path.expanduser('~/cs2pilot/out'))
    ap.add_argument('--hours', type=float, default=CFG['HOURS'])
    a = ap.parse_args(); CFG['HOURS'] = a.hours
    asyncio.run(Pilot(a).main())
