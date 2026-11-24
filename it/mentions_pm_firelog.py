#!/usr/bin/env python3
"""LIVE own-token ask logger + paper fills for the Polymarket mentions 10c rule (R-031 part 1). Paper only, read-only public endpoints, no orders, no keys.
Run every 2 minutes (cron). For every mention event whose first market started <= 3600 s ago (the rule's window), for every market, it reads BOTH tokens' books (YES and NO
are separate books, never one priced from the other) and, using the frozen q (mentions_pm_daily_scorer: per-word causal base rate), checks whether any token's best ask clears the 10c edge
(YES: ask <= q-0.10, NO: ask <= (1-q)-0.10, price 5c..95c). When it fires it logs the full ask ladders (all levels, both tokens of that market) and a paper fill:
  fill at CAP dollars (default $200) walking asks that keep edge >= 10c (never above the limit price); partial if depth is short (depth_usd reports what exists); fee 0.04*p*(1-p).
One paper bet per event (first firing, like the rule); a UTC-day cap of DAYCAP dollars (default $2,000) across paper bets, scaling the last bet down.
Files in OUT: firelog_<UTC date>.jsonl.gz (every firing snapshot), paper_bets.jsonl (one row per event), heartbeat.txt (last run time + counts; the live-read target).
--score: add P&L for paper bets whose event has resolved (writes paper_scored.csv + SCORE.txt).
Usage: python3 -I mentions_pm_firelog.py --scorer PATH --state DIR --out DIR [--cap 200] [--daycap 2000] [--score]"""
import argparse, csv, datetime as dt, gzip, importlib.util, json, os, time
ap = argparse.ArgumentParser(); ap.add_argument('--scorer', required=True); ap.add_argument('--state', required=True); ap.add_argument('--out', required=True)
ap.add_argument('--cap', type=float, default=200.); ap.add_argument('--daycap', type=float, default=2000.); ap.add_argument('--score', action='store_true'); ap.add_argument('--health', action='store_true')


def load(p):
    sp = importlib.util.spec_from_file_location('sc', p); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


def parse_asks(book): return sorted((float(a['price']), float(a['size'])) for a in (book or {}).get('asks', []))


def limit_price(q, oi, thr): return (q - thr) if oi == 0 else ((1 - q) - thr)


def fills_at(asks, limit, cap_usd):
    """Walk the asks from the best price up to limit (and >= 5c), up to cap_usd notional. Returns dict(size, cost, avg, partial, depth_usd)."""
    lv = [(p, s) for p, s in asks if .05 <= p <= limit + 1e-12]
    depth = sum(p * s for p, s in lv); left = cap_usd; size = cost = 0.0
    for p, s in lv:
        if left <= 1e-9: break
        take = min(s, left / p); size += take; cost += take * p; left -= take * p
    return dict(size=size, cost=cost, avg=cost / size if size else None, partial=cost < cap_usd - 1e-6, depth_usd=depth)


def paper_bet(asks, limit, cap, room, rate):
    """room = dollars left in the UTC-day cap. Returns the paper fill (or None if nothing qualifies / no room)."""
    f = fills_at(asks, limit, min(cap, room))
    if f['size'] <= 0: return None
    f['fee'] = rate * f['avg'] * (1 - f['avg']) * f['size']   # on the average price (per-level fees differ by cents at most)
    return f


def main():
    a = ap.parse_args(); sc = load(a.scorer); os.makedirs(a.out, exist_ok=True); now = time.time(); today = dt.datetime.fromtimestamp(now, dt.timezone.utc).strftime('%Y-%m-%d')
    bets_fn = os.path.join(a.out, 'paper_bets.jsonl'); bets = [json.loads(l) for l in open(bets_fn)] if os.path.exists(bets_fn) else []
    if a.health: return health(a, now)
    if a.score: return score(sc, a, bets)
    closed = list(json.load(open(os.path.join(a.state, 'events.json'))).values())
    raw_open = sc.open_events()
    if raw_open is None: raise SystemExit('gamma open-events read failed (R-076); nothing logged this run, cron retries')
    op = [sc.slim(e) for e in raw_open]
    pool = [e for e in closed if sc.resolved(e)]; have = {b['event'] for b in bets}; used = sum(b['cost'] for b in bets if b['day'] == today)
    n_ev = n_fire = n_books = n_exp = 0; fn = os.path.join(a.out, 'firelog_%s.jsonl.gz' % today)
    with gzip.open(fn, 'at') as lf:
        for e in op:
            if not e['markets']: continue
            t0 = sc.start(e)
            if not (0 <= now - t0 <= sc.WIN): continue
            n_ev += 1; hist = [h for h in pool if h['fam'] == e['fam'] and h['id'] != e['id'] and sc.settled_at(h) <= t0]
            for m in e['markets']:
                q = sc.q_for(hist, e, m); books = {}
                for oi, tok in enumerate(m['toks'][:2]):
                    n_exp += 1
                    b = sc.fetch(f'https://clob.polymarket.com/book?token_id={tok}')
                    if b is None: continue
                    books[oi] = parse_asks(b); n_books += 1
                fired = [oi for oi, asks in books.items() if any(.05 <= p <= limit_price(q, oi, sc.THR) for p, _ in asks)]
                if not fired: continue
                n_fire += 1
                rec = dict(t=int(now), age_s=int(now - t0), event=e['id'], title=e['title'], cond=m['cond'], word=m['label'], q=round(q, 4), fired=['YES' if o == 0 else 'NO' for o in fired],
                           ladders={('YES' if o == 0 else 'NO'): [[p, s] for p, s in asks] for o, asks in books.items()},
                           limit={('YES' if o == 0 else 'NO'): round(limit_price(q, o, sc.THR), 4) for o in books},
                           fill200={('YES' if o == 0 else 'NO'): fills_at(books[o], limit_price(q, o, sc.THR), a.cap) for o in fired})
                lf.write(json.dumps(rec) + '\n')
                if e['id'] not in have:
                    o = fired[0]; pb = paper_bet(books[o], limit_price(q, o, sc.THR), a.cap, max(0.0, a.daycap - used), m['fee'])
                    if pb:
                        row = dict(t=int(now), day=today, event=e['id'], title=e['title'], fam=e['fam'], cond=m['cond'], word=m['label'], side='YES' if o == 0 else 'NO', q=round(q, 4), age_s=int(now - t0),
                                   size=pb['size'], cost=pb['cost'], avg=pb['avg'], fee=pb['fee'], partial=pb['partial'], depth_usd=pb['depth_usd'], tok=m['toks'][o])
                        open(bets_fn, 'a').write(json.dumps(row) + '\n'); have.add(e['id']); used += pb['cost']
    open(os.path.join(a.out, 'runs.jsonl'), 'a').write(json.dumps(dict(t=int(now), pid=os.getpid(), events=n_ev, books_expected=n_exp, books_read=n_books, firings=n_fire)) + '\n')
    open(os.path.join(a.out, 'heartbeat.txt'), 'w').write('%s UTC events_in_window=%d books_read=%d firings=%d paper_bets_total=%d day_used=$%.2f\n' % (dt.datetime.fromtimestamp(now, dt.timezone.utc).isoformat(), n_ev, n_books, n_fire, len(have), used))


def health_eval(runs, now, errors_text, window=900, period=120):
    """HEALTH READ for the last 15 min (R-037). runs: list of dict(t, pid, books_expected, books_read). Returns (lines, ok)."""
    w = [r for r in runs if now - r['t'] <= window]
    exp_runs = window // period; ratio_runs = len(w) / exp_runs
    be = sum(r['books_expected'] for r in w); br = sum(r['books_read'] for r in w); ratio_books = (br / be) if be else None
    errs = [l for l in errors_text.splitlines() if 'Traceback' in l or 'Error' in l or 'SystemExit' in l]
    ok = len(w) >= exp_runs - 1 and (ratio_books is None or ratio_books >= .99) and not errs
    return w, ratio_runs, ratio_books, be, br, errs, ok


def health(a, now):
    fn = os.path.join(a.out, 'runs.jsonl'); runs = [json.loads(l) for l in open(fn)] if os.path.exists(fn) else []
    logs = sorted(f for f in os.listdir(a.out) if f.startswith('run-') and f.endswith('.log'))
    et = open(os.path.join(a.out, logs[-1])).read()[-20000:] if logs else ''
    et2 = open(os.path.join(a.out, 'cron-errors.log')).read()[-5000:] if os.path.exists(os.path.join(a.out, 'cron-errors.log')) else ''
    w, rr, rb, be, br, errs, ok = health_eval(runs, now, et + et2)
    st = os.statvfs(a.out); free = st.f_bavail * st.f_frsize / 1e9
    print('MENTIONS FIREWATCH HEALTH READ %s UTC' % dt.datetime.fromtimestamp(now, dt.timezone.utc).strftime('%Y-%m-%d %H:%M'))
    print('runs in last 15 min: %d of 7 expected (every 2 min); snapshots (token books) captured %s of expected %d (%s); errors in log tail: %d; disk free at %s: %.1f GB; last pids: %s' % (
        len(w), br, be, 'n/a: no mention event in its first hour in the window, so none were expected' if rb is None else '%.1f%%' % (100 * rb), len(errs), a.out, free, sorted({r['pid'] for r in w})[-2:]))
    print('price source: asks come from the traded token\'s OWN book, CLOB /book?token_id=<clobTokenIds[0] for YES, [1] for NO>, field asks[].price / asks[].size (parse_asks line in mentions_pm_firelog.py); NO is never derived from YES')
    print('RESULT: ' + ('PASS' if ok else 'FAIL: stop, keep files, fix, restart, post a new read within 15 min'))


def score(sc, a, bets):
    rows = []; allev = {}
    raw_open = sc.open_events()
    if raw_open is None: raise SystemExit('gamma open-events read failed (R-076)')
    for e in raw_open: allev[e['id']] = sc.slim(e)
    for e in json.load(open(os.path.join(a.state, 'events.json'))).values(): allev.setdefault(e['id'], e)
    for b in bets:
        e = allev.get(b['event'])
        if e is None:   # fetch the single event
            r = sc.fetch(f"{sc.GAMMA}/events?id={b['event']}"); e = sc.slim(r[0]) if r else None
        if e is None or not sc.resolved(e): rows.append(dict(b, status='open', pnl_net='')); continue
        m = next((m for m in e['markets'] if m['cond'] == b['cond']), None)
        if m is None: continue
        w = sc.win(m); oi = 0 if b['side'] == 'YES' else 1
        pnl = ((w if oi == 0 else 1 - w) * b['size']) - b['cost'] - b['fee']
        rows.append(dict(b, status='resolved', won=(w if oi == 0 else 1 - w) == 1, pnl_net=round(pnl, 4)))
    cols = ['day', 'event', 'title', 'fam', 'word', 'side', 'q', 'age_s', 'size', 'cost', 'avg', 'fee', 'partial', 'depth_usd', 'status', 'won', 'pnl_net']
    with open(os.path.join(a.out, 'paper_scored.csv'), 'w', newline='') as f:
        w_ = csv.DictWriter(f, fieldnames=cols, extrasaction='ignore'); w_.writeheader(); w_.writerows(rows)
    res = [r for r in rows if r['status'] == 'resolved']
    txt = 'paper bets %d (resolved %d, open %d); cost resolved $%.2f; net after fees $%.2f; wins %d\n' % (len(rows), len(res), len(rows) - len(res), sum(r['cost'] for r in res), sum(r['pnl_net'] for r in res), sum(1 for r in res if r['won']))
    open(os.path.join(a.out, 'SCORE.txt'), 'w').write(txt); print(txt)


if __name__ == '__main__': main()
