#!/usr/bin/env python3
"""LIVE paper test on Prime (R-050/R-051): every open Polymarket mentions event, each token's OWN book over the market WebSocket, paper decisions at the variant windows. PAPER ONLY: no orders, no keys.
Stdlib only (ws_min.py beside it). One process; run under IT's caps (nice, memory cap, restart on exit). Output dir OUT:
  decisions.jsonl   one row per (event, variant, decision time, token) where the frozen fair value says the token is underpriced (edge-priced asks exist), with full-ladder $, edge-priced $, side, fair, limit,
                    paper TAKE fill (A: walks displayed asks at or below limit up to $200, instant, depth MEASURED, no latency) and paper RESTING BID (B: bid at the limit price for $200, queue = bids at that price at decision time).
  fills.jsonl       later own-token trade prints that fill B (print at or through the bid price after the queue ahead is consumed) and the 60 s print check for A (a BUY print at or below the take price within 60 s = 'confirmed')
  heartbeat.json    one write per 60 s (pid, connected, tokens subscribed, books received, messages, reconnects, errors, last message age)
  runs.jsonl        heartbeat history; --health reads it (R-037 15-minute read); --score adds P&L at resolution.
Rules (frozen model, no refit): fair YES = per-word causal base rate q at LISTING (mentions_pm_daily_scorer.q_for), NO fair = 1-q; underpriced = ask <= fair-10c and >= 5c; $200 per (decision, token), $2,000/day cap.
Decision times: listing+0..60 min every 5 min; T-24h; T-6h; T-1h; T-15m; during = every 5 min over [T-6h, T] (T = Gamma endDate). A decision later than 90 s after its time is logged as MISSED, never filled late.
Usage: python3 -I mentions_pm_ws_paper.py --scorer P --state DIR --out DIR [--cap 200] [--daycap 2000] | --health | --score"""
import argparse, collections, datetime as dt, fcntl, importlib.util, json, os, shutil, socket, sys, time

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
WSURL = 'wss://ws-subscriptions-clob.polymarket.com/ws/market'


def load(n, p):
    sp = importlib.util.spec_from_file_location(n, p); m = importlib.util.module_from_spec(sp); sys.modules[n] = m; sp.loader.exec_module(m); return m


class Book:
    """Local own-token book from 'book' snapshots and 'price_change' deltas."""
    def __init__(self): self.asks = {}; self.bids = {}; self.ts = 0.0

    def snapshot(self, msg, now):
        self.asks = {float(x['price']): float(x['size']) for x in msg.get('asks', [])}; self.bids = {float(x['price']): float(x['size']) for x in msg.get('bids', [])}; self.ts = now

    def change(self, side, price, size, now):
        d = self.asks if side == 'SELL' else self.bids
        if size <= 0: d.pop(price, None)
        else: d[price] = size
        self.ts = now

    def ask_ladder(self): return sorted(self.asks.items())


def take(asks, limit, cap):
    """Paper TAKE against displayed asks at or below limit (>= 5c) up to cap notional. Returns dict(levels, size, cost, avg, partial, edge_usd)."""
    lv = [(p, s) for p, s in asks if .05 <= p <= limit + 1e-12]; left = cap; size = cost = 0.0; used = []
    for p, s in lv:
        if left <= 1e-9: break
        t = min(s, left / p); size += t; cost += t * p; left -= t * p; used.append((p, t))
    return dict(levels=used, size=size, cost=cost, avg=(cost / size if size else None), partial=cost < cap - 1e-6, edge_usd=sum(p * s for p, s in lv))


def resting_fill(bid_price, size, queue_ahead, trades):
    """Paper RESTING BID: later SELL-aggressor prints at or below our price. A print AT our price first consumes the queue ahead; a print strictly below fills us without queue.
    trades: list of (price, qty) in time order (qty in shares). Returns filled shares."""
    q = queue_ahead; filled = 0.0
    for p, qty in trades:
        if p < bid_price - 1e-12: filled += min(qty, size - filled)
        elif abs(p - bid_price) <= 1e-12:
            if q >= qty: q -= qty
            else: filled += min(qty - q, size - filled); q = 0.0
        if filled >= size - 1e-9: break
    return filled


def slots(t0, T):
    out = [('listing', t0 + 300 * i) for i in range(13)] + [('T-24h', T - 86400), ('T-6h', T - 6 * 3600), ('T-1h', T - 3600), ('T-15m', T - 900)] + [('during', T - 6 * 3600 + 300 * i) for i in range(72)]
    return [(v, t) for v, t in out if t >= t0]


def due(slot_list, now, done, late=90, since=0.0):
    """Slots whose time has come (now >= t) and not done; those later than `late` seconds are returned as missed. Slots before `since` (process start minus late) predate this run and are ignored, not missed."""
    ok, missed = [], []
    for v, t in slot_list:
        if (v, t) in done or now < t or t < since: continue
        (ok if now - t <= late else missed).append((v, t))
    return ok, missed


def health_eval(runs, now, window=900):
    w = [r for r in runs if now - r['t'] <= window]
    if not w: return False, ['no heartbeat in the last 15 min']
    last = w[-1]; why = []
    exp = last.get('accepting_tokens', 0); got = last.get('books_received', 0)
    if len(w) < 13: why.append('only %d heartbeats in 15 min (expected 15, 60 s apart)' % len(w))
    if exp and got / exp < .99: why.append('books received %d of %d accepting tokens (%.1f%% < 99%%)' % (got, exp, 100 * got / exp))
    if not last.get('connected'): why.append('not connected')
    if last.get('last_msg_age_s', 1e9) > 60: why.append('no message for %ds' % last.get('last_msg_age_s', -1))
    if sum(r.get('errors_new', 0) for r in w): why.append('%d unhandled errors in window' % sum(r.get('errors_new', 0) for r in w))
    return (not why), why


def fetch_open(sc, page=50, maxpages=10):
    """R-076: page the open mention events at limit=50 with offset (Gamma has answered HTTP 406 to limit=100). Returns the list, or None if ANY page failed (sc.fetch returns None on failure), so the caller never mistakes a failed read for 'no events'."""
    out = []
    for i in range(maxpages):
        r = sc.fetch(f'{sc.GAMMA}/events?tag_slug=mention-markets&closed=false&limit={page}&offset={i * page}&order=startDate&ascending=false')
        if r is None: return None
        out += r
        if len(r) < page: return out
    return out


def keep_or_replace(old, new):
    """Never shrink to zero on a bad read: an empty new universe with a non-empty old one keeps the old one."""
    return old if (not new[1] and old[1]) else new


def universe(sc, state, now):
    closed = list(json.load(open(os.path.join(state, 'events.json'))).values()); pool = [e for e in closed if sc.resolved(e)]; ev = {}; toks = {}
    raw_open = fetch_open(sc)
    if raw_open is None: raise RuntimeError('gamma open-events read failed; keeping the last good universe')
    for x in raw_open:
        e = sc.slim(x)
        if not e['markets'] or not x.get('endDate'): continue
        t0 = sc.start(e); T = sc.ts(x['endDate']); hist = [h for h in pool if h['fam'] == e['fam'] and h['id'] != e['id'] and sc.settled_at(h) <= t0]
        raw_m = {m['conditionId']: m for m in x['markets']}
        mk = []
        for m in e['markets']:
            if not raw_m.get(m['cond'], {}).get('acceptingOrders') or len(m['toks']) < 2: continue
            q = sc.q_for(hist, e, m); mk.append(dict(cond=m['cond'], label=m['label'], q=q, toks=m['toks'][:2], fee=m['fee']))
            for oi, t in enumerate(m['toks'][:2]): toks[t] = (e['id'], m['cond'], oi)
        if mk: ev[e['id']] = dict(id=e['id'], slug=x['slug'], fam=e['fam'], t0=t0, T=T, markets=mk, slots=slots(t0, T))
    return ev, toks


def acquire_lock(out):
    """Single-instance lock (R-058): returns an open fd holding the lock, or None if another copy holds it."""
    fd = open(os.path.join(out, '.lock'), 'w')
    try: fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError: fd.close(); return None
    return fd


def preflight_eval(i):
    """R-058 gate. i: expected_tokens, tokens_subscribed, books_received, msgs, seconds, lines_written, second_copy_refused, health_ok. Any fail = nothing starts."""
    why = []
    if i['expected_tokens'] <= 0: why.append('expected tokens = 0')
    if i['tokens_subscribed'] <= 0: why.append('tokens subscribed = 0')
    if i['tokens_subscribed'] != i['expected_tokens']: why.append('tokens subscribed %d != expected %d' % (i['tokens_subscribed'], i['expected_tokens']))
    if i['tokens_subscribed'] and i['books_received'] / i['tokens_subscribed'] < .99: why.append('books received %d of %d (< 99%%)' % (i['books_received'], i['tokens_subscribed']))
    if i['msgs'] <= 0 or i['lines_written'] <= 0: why.append('no real live data written (msgs %d, lines %d)' % (i['msgs'], i['lines_written']))
    if i['seconds'] < 60: why.append('ran %ds, need 60 s of live data' % i['seconds'])
    if not i['second_copy_refused']: why.append('a second copy was NOT refused by the single-instance lock')
    if not i['health_ok']: why.append('health checker does not support this mode')
    return (not why), why


def preflight_cmd(sc, a):
    """Run by IT on Prime BEFORE any start; commit the printed block and PREFLIGHT.json. Writes 60 s of real data to <out>/preflight/."""
    import ws_min
    pd = os.path.join(a.out, 'preflight'); os.makedirs(pd, exist_ok=True); lock = acquire_lock(a.out)
    if lock is None: print('PREFLIGHT FAIL: another copy holds the lock (already running)'); return 1
    second = acquire_lock(a.out) is None
    now = time.time(); ev, toks = universe(sc, a.state, now); expected = sum(len(m['toks']) for e in ev.values() for m in e['markets'])
    w = ws_min.WS(WSURL, timeout=20); w.sock.settimeout(1.0); w.send(json.dumps({'assets_ids': list(toks), 'type': 'market'})); sub = len(toks); seen = set(); msgs = 0; lines = 0; t0 = time.time(); fn = os.path.join(pd, 'sample.jsonl')
    with open(fn, 'w') as f:
        while time.time() - t0 < 62:
            try: raw = w.recv()
            except socket.timeout: continue
            if raw in ('PONG', 'pong'): continue
            msgs += 1
            for x in (lambda j: j if isinstance(j, list) else [j])(json.loads(raw)):
                if x.get('event_type') == 'book': seen.add(x['asset_id'])
                f.write(json.dumps(x)[:2000] + '\n'); lines += 1
    w.close()
    syn = [dict(t=1000 - 60 * i, accepting_tokens=10, books_received=10, connected=True, last_msg_age_s=1, errors_new=0) for i in range(15)][::-1]
    info = dict(expected_tokens=expected, tokens_subscribed=sub, books_received=len(seen & set(toks)), msgs=msgs, seconds=int(time.time() - t0), lines_written=lines, second_copy_refused=second, health_ok=health_eval(syn, 1000)[0] and not health_eval([dict(r, books_received=1) for r in syn], 1000)[0])
    ok, why = preflight_eval(info); rec = dict(t=int(time.time()), ok=ok, why=why, **info); json.dump(rec, open(os.path.join(a.out, 'PREFLIGHT.json'), 'w'))
    print('PREFLIGHT %s UTC: expected tokens %d, subscribed %d, books received %d, messages %d in %d s, lines written %d, second copy refused %s, health checker ok %s' % (dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%d %H:%M'), expected, sub, info['books_received'], msgs, info['seconds'], lines, second, info['health_ok']))
    print('PREFLIGHT ' + ('PASS: supervisor may start' if ok else 'FAIL: ' + '; '.join(why) + ' -> NOTHING STARTS; commit this output and tell the Mentions thread'))
    return 0 if ok else 1


def merge_extra(ev, out):
    """R-071: extra decision slots from <out>/extra_slots.json {event_id: [[variant, epoch_seconds], ...]} (e.g. times anchored to the speech start, which Gamma does not give). Unknown events are ignored."""
    fn = os.path.join(out, 'extra_slots.json')
    if not os.path.exists(fn): return ev
    for k, lst in json.load(open(fn)).items():
        e = ev.get(str(k)) or ev.get(k)
        if e: e['slots'] = sorted(set(map(tuple, e['slots'])) | {(v, float(t)) for v, t in lst}, key=lambda x: x[1])
    return ev


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--scorer'); ap.add_argument('--state'); ap.add_argument('--out', required=True); ap.add_argument('--cap', type=float, default=200.); ap.add_argument('--daycap', type=float, default=2000.)
    ap.add_argument('--health', action='store_true'); ap.add_argument('--score', action='store_true'); ap.add_argument('--preflight', action='store_true'); a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
    if a.health: return health_cmd(a)
    sc = load('sc', a.scorer)
    if a.score: return score_cmd(sc, a)
    if a.preflight: return preflight_cmd(sc, a)
    lock = acquire_lock(a.out)
    if lock is None: sys.stderr.write('another copy holds the lock; refusing to start\n'); return 3
    import ws_min
    dec_fn = os.path.join(a.out, 'decisions.jsonl'); fill_fn = os.path.join(a.out, 'fills.jsonl'); run_fn = os.path.join(a.out, 'runs.jsonl')
    done = set(); used = collections.defaultdict(float)
    if os.path.exists(dec_fn):
        for l in open(dec_fn):
            r = json.loads(l); done.add((r['event'], r['variant'], r['t_decision']))
            if r.get('take'): used[r['day']] += r['take']['cost']
    books = collections.defaultdict(Book); pend = []; st = dict(msgs=0, reconnects=0, errors=0, errors_reported=0, missed=0, last_msg=time.time(), books_seen=set(), sub_time=0.0); ev = {}; toks = {}; w = None; last_hb = 0.0; last_uni = 0.0
    day = lambda t: dt.datetime.fromtimestamp(t, dt.timezone.utc).strftime('%Y-%m-%d')
    t_start = time.time()
    while True:
        now = time.time()
        try:
            if now - last_uni > 300 or w is None:
                try: ev2, toks2 = universe(sc, a.state, now); ev2 = merge_extra(ev2, a.out); last_uni = now
                except RuntimeError as ex:
                    st['uni_fail'] = st.get('uni_fail', 0) + 1; sys.stderr.write('%s universe kept: %s\n' % (dt.datetime.now(dt.timezone.utc).isoformat(), ex)); last_uni = now - 240
                    if toks: ev2, toks2 = ev, toks
                    else: time.sleep(10); continue
                ev2, toks2 = keep_or_replace((ev, toks), (ev2, toks2))
                if set(toks2) != set(toks) or w is None:
                    ev, toks = ev2, toks2
                    if w: w.close()
                    w = ws_min.WS(WSURL, timeout=20); w.sock.settimeout(1.0); w.send(json.dumps({'assets_ids': list(toks), 'type': 'market'})); st['sub_time'] = now; st['books_seen'] = set(); st['reconnects'] += 1
                else: ev = ev2
            try: raw = w.recv()
            except socket.timeout: raw = None
            if raw is not None and raw not in ('PONG', 'pong'):
                st['msgs'] += 1; st['last_msg'] = now
                for x in (lambda j: j if isinstance(j, list) else [j])(json.loads(raw)):
                    et = x.get('event_type')
                    if et == 'book': books[x['asset_id']].snapshot(x, now); st['books_seen'].add(x['asset_id'])
                    elif et == 'price_change':
                        for c in x.get('price_changes', []): books[c['asset_id']].change(c['side'], float(c['price']), float(c['size']), now)
                    elif et == 'last_trade_price':
                        for p in pend:
                            if p['asset'] == x['asset_id'] and now >= p['t']: p['trades'].append((float(x['price']), float(x['size']), x.get('side'), now))
            for e in ev.values():
                ok, missed = due(e['slots'], now, {(v, t) for (i, v, t) in done if i == e['id']}, since=t_start - 90)
                for v, t in missed: done.add((e['id'], v, t)); st['missed'] += 1
                for v, t in ok:
                    done.add((e['id'], v, t))
                    for m in e['markets']:
                        for oi, tok in enumerate(m['toks']):
                            b = books.get(tok)
                            if b is None or not b.asks: continue
                            fair = m['q'] if oi == 0 else 1 - m['q']; lim = fair - .10; asks = b.ask_ladder(); tk = take(asks, lim, a.cap)
                            if tk['edge_usd'] <= 0: continue
                            room = max(0.0, a.daycap - used[day(now)]); tk2 = take(asks, lim, min(a.cap, room)) if room < a.cap else tk
                            used[day(now)] += tk2['cost']
                            qa = b.bids.get(round(lim, 3), 0.0)
                            row = dict(ts=now, day=day(now), event=e['id'], slug=e['slug'], fam=e['fam'], variant=v, t_decision=t, delay_s=round(now - t, 1), cond=m['cond'], word=m['label'], side='YES' if oi == 0 else 'NO', fair=round(fair, 4), limit=round(lim, 4),
                                       best_ask=asks[0][0], full_usd=round(sum(p * s for p, s in asks), 2), edge_usd=round(tk['edge_usd'], 2), take=dict(tk2, levels=[list(x) for x in tk2['levels']]),
                                       bid=dict(price=round(lim, 3), shares=round(a.cap / lim, 2), queue_ahead=qa), fee_rate=m['fee'], age_since_book_s=round(now - b.ts, 1))
                            open(dec_fn, 'a').write(json.dumps(row) + '\n')
                            pend.append(dict(asset=tok, t=now, until=now + 3600, bid_price=lim, shares=a.cap / lim, queue=qa, trades=[], take_price=(tk2['levels'][-1][0] if tk2['levels'] else None), key=(e['id'], v, t, m['cond'], oi), logged=False))
            for p in list(pend):
                if now > p['t'] + 60 and not p['logged'] and p['take_price'] is not None:
                    conf = sum(q for pr, q, sd, tt in p['trades'] if tt <= p['t'] + 60 and pr <= p['take_price'] + 1e-12 and sd == 'BUY'); p['A_confirmed_shares'] = conf
                if now > p['until']:
                    fl = resting_fill(p['bid_price'], p['shares'], p['queue'], [(pr, q) for pr, q, sd, tt in p['trades'] if sd == 'SELL'])
                    open(fill_fn, 'a').write(json.dumps(dict(key=p['key'], bid_price=p['bid_price'], bid_filled_shares=fl, bid_shares=p['shares'], A_confirmed_shares_60s=p.get('A_confirmed_shares'), n_trades_seen=len(p['trades']))) + '\n'); pend.remove(p)
            if now - last_hb >= 60:
                last_hb = now; acc = len(toks); new = st['errors'] - st['errors_reported']; st['errors_reported'] = st['errors']
                hb = dict(t=int(now), pid=os.getpid(), connected=w is not None, tokens_subscribed=acc, accepting_tokens=acc, books_received=len(st['books_seen']), msgs=st['msgs'], reconnects=st['reconnects'], errors_new=new, missed_slots=st['missed'], last_msg_age_s=int(now - st['last_msg']), events=len(ev), universe_failures=st.get('uni_fail', 0))
                open(run_fn, 'a').write(json.dumps(hb) + '\n'); json.dump(hb, open(os.path.join(a.out, 'heartbeat.json'), 'w'))
        except (ConnectionError, OSError, ValueError) as ex:
            st['errors'] += 1; sys.stderr.write('%s %s %s\n' % (dt.datetime.now(dt.timezone.utc).isoformat(), type(ex).__name__, ex)); w = None; time.sleep(5)


def health_cmd(a):
    fn = os.path.join(a.out, 'runs.jsonl'); runs = [json.loads(l) for l in open(fn)] if os.path.exists(fn) else []; now = time.time(); ok, why = health_eval(runs, now)
    free = shutil.disk_usage(a.out).free / 1e9; last = runs[-1] if runs else {}
    print('MENTIONS WS PAPER HEALTH READ %s UTC' % dt.datetime.fromtimestamp(now, dt.timezone.utc).strftime('%Y-%m-%d %H:%M'))
    print('heartbeats in 15 min: %d (expected 15); books received %s of %s accepting tokens; messages %s; reconnects %s; errors in window %d; missed decision slots %s; last message age %ss; disk free %.1f GB; pid %s' % (
        len([r for r in runs if now - r['t'] <= 900]), last.get('books_received'), last.get('accepting_tokens'), last.get('msgs'), last.get('reconnects'), sum(r.get('errors_new', 0) for r in runs if now - r['t'] <= 900), last.get('missed_slots'), last.get('last_msg_age_s'), free, last.get('pid')))
    print("price source: each token's OWN book from the market WebSocket (event_type book = snapshot, price_change = delta, field asks[].price/size per asset_id = the token id of that outcome); NO is never derived from YES")
    print('RESULT: ' + ('PASS' if ok else 'FAIL: ' + '; '.join(why) + ' -> stop, keep files, fix, restart, new read within 15 min'))


def score_cmd(sc, a):
    dec = [json.loads(l) for l in open(os.path.join(a.out, 'decisions.jsonl'))] if os.path.exists(os.path.join(a.out, 'decisions.jsonl')) else []
    fills = {tuple(json.loads(l)['key']): json.loads(l) for l in open(os.path.join(a.out, 'fills.jsonl'))} if os.path.exists(os.path.join(a.out, 'fills.jsonl')) else {}
    res = collections.defaultdict(lambda: dict(n=0, cost=0.0, pnl=0.0)); cache = {}
    for r in dec:
        if r['event'] not in cache:
            x = sc.fetch(f"{sc.GAMMA}/events?id={r['event']}"); cache[r['event']] = sc.slim(x[0]) if x else None
        e = cache[r['event']]
        if e is None or not sc.resolved(e): continue
        m = next((m for m in e['markets'] if m['cond'] == r['cond']), None)
        if m is None: continue
        w = sc.win(m); oi = 0 if r['side'] == 'YES' else 1; tk = r['take']
        if tk['size'] > 0:
            k = (r['variant'], 'A take'); g = res[k]; g['n'] += 1; g['cost'] += tk['cost']; g['pnl'] += ((w if oi == 0 else 1 - w) * tk['size']) - tk['cost'] - r['fee_rate'] * tk['avg'] * (1 - tk['avg']) * tk['size']
        f = fills.get((r['event'], r['variant'], r['t_decision'], r['cond'], oi))
        if f and f['bid_filled_shares'] > 0:
            k = (r['variant'], 'B bid'); g = res[k]; p = f['bid_price']; sz = f['bid_filled_shares']; g['n'] += 1; g['cost'] += p * sz; g['pnl'] += ((w if oi == 0 else 1 - w) - p) * sz - r['fee_rate'] * p * (1 - p) * sz
    txt = 'WS paper scored decisions (resolved events only)\n' + '\n'.join('%s %s: n %d cost $%.2f net $%.2f' % (k[0], k[1], g['n'], g['cost'], g['pnl']) for k, g in sorted(res.items())) + '\n'
    open(os.path.join(a.out, 'SCORE.txt'), 'w').write(txt); print(txt)


if __name__ == '__main__': sys.exit(main() or 0)
