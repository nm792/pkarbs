#!/usr/bin/env python3
"""Does $200 fill at the 10c-edge entry on new Polymarket mention markets? (R-026 item 4, Nick 22 Nov)
Imports the frozen scorer (mentions_pm_daily_scorer.py) so q, history and the 10c rule are identical.
A. PRINT DEPTH (historical, from /v2/trades): per forward event, the dollar notional of ALL first-hour BUY prints that clear the 10c edge
   (price 5c-95c, token's own price, q from causal history). This is what traded at qualifying prices, a floor for what resting asks could have filled. Not asks.
B. LIVE BOOK SNAPSHOT (own-token asks, CLOB /book per token, now): for each OPEN event whose first hour is over or running, per word and per token (YES and NO separately),
   ask depth in dollars at prices that clear the 10c edge now. Snapshot time is NOT decision time; only a recorder run in the first hour gives that.
Usage: python3 -I mentions_pm_depth.py --scorer PATH --state DIR --out FILE [--freeze ISO] [--asof ISO]"""
import argparse, importlib.util, json, statistics as S, sys, time, concurrent.futures as cf
ap = argparse.ArgumentParser(); ap.add_argument('--scorer', required=True); ap.add_argument('--state', required=True); ap.add_argument('--out', required=True)
ap.add_argument('--freeze', default='2026-11-10T15:00:00+00:00'); ap.add_argument('--asof', default=None)


def load(p):
    sp = importlib.util.spec_from_file_location('sc', p); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


def print_depth(sc, ev, hist, trades, t0):
    """Dollar notional of first-hour BUY prints clearing the 10c edge, by side, plus the first qualifying print's own notional."""
    tot = {0: 0.0, 1: 0.0}; n = 0; first = None
    for m in ev['markets']:
        q = sc.q_for(hist, ev, m)
        for (t, side, p, sz, oi) in sorted(trades.get(m['cond'], [])):
            if not (t0 <= t <= t0 + sc.WIN) or side != 'BUY' or sz <= 0 or not (.05 <= p <= .95): continue
            if ((q - p) if oi == 0 else ((1 - q) - p)) >= sc.THR:
                tot[oi] += p * sz; n += 1
                if first is None or t < first[0]: first = (t, p * sz)
    return dict(usd_yes=round(tot[0], 2), usd_no=round(tot[1], 2), usd_total=round(tot[0] + tot[1], 2), n_prints=n, first_print_usd=None if first is None else round(first[1], 2))


def ask_depth(asks, limit):
    """Dollars (price*size) of asks at price <= limit and >= 5c."""
    return sum(p * s for p, s in asks if .05 <= p <= limit)


def snapshot(sc, ev, hist):
    out = []
    for m in ev['markets']:
        q = sc.q_for(hist, ev, m)
        for oi, tok in enumerate(m['toks'][:2]):
            b = sc.fetch(f'https://clob.polymarket.com/book?token_id={tok}') or {}
            asks = [(float(a['price']), float(a['size'])) for a in b.get('asks', [])]
            lim = (q - sc.THR) if oi == 0 else ((1 - q) - sc.THR)
            out.append(dict(word=m['label'], side='YES' if oi == 0 else 'NO', q=round(q, 3), limit=round(lim, 3), best_ask=min((p for p, _ in asks), default=None), depth_usd=round(ask_depth(asks, lim), 2)))
    return out


def summarize(rows):
    v = [r['usd_total'] for r in rows]
    if not v: return {}
    return dict(events=len(v), with_qualifying_print=sum(1 for x in v if x > 0), median_usd=round(S.median(v), 2), mean_usd=round(S.mean(v), 2), max_usd=max(v),
                events_ge_200=sum(1 for x in v if x >= 200), events_ge_50=sum(1 for x in v if x >= 50), share_ge_200=round(sum(1 for x in v if x >= 200) / len(v), 3))


if __name__ == '__main__':
    a = ap.parse_args(); sc = load(a.scorer); asof = sc.ts(a.asof) if a.asof else time.time(); fz = sc.ts(a.freeze)
    closed = list(json.load(open(a.state + '/events.json')).values())
    op = [sc.slim(e) for e in (sc.fetch(f'{sc.GAMMA}/events?tag_slug=mention-markets&closed=false&limit=100&order=startDate&ascending=false') or [])]
    allev = {e['id']: e for e in closed}; allev.update({e['id']: e for e in op})
    pool = [e for e in allev.values() if sc.resolved(e)]
    fwd = sorted([e for e in allev.values() if e['markets'] and sc.start(e) >= fz and sc.start(e) + sc.WIN <= asof], key=sc.start)
    conds = [m['cond'] for e in fwd for m in e['markets']]
    with cf.ThreadPoolExecutor(8) as ex: tr = dict(ex.map(sc.pull_trades, conds))
    if any(v is None for v in tr.values()): raise SystemExit('trade pull failed')
    rows = []; snaps = []
    for e in fwd:
        t0 = sc.start(e); hist = [h for h in pool if h['fam'] == e['fam'] and h['id'] != e['id'] and sc.settled_at(h) <= t0]
        r = dict(id=e['id'], title=e['title'], start=t0, status='resolved' if sc.resolved(e) else 'open', **print_depth(sc, e, hist, tr, t0)); rows.append(r)
        if not sc.resolved(e) and not e['closed']: snaps.append(dict(id=e['id'], title=e['title'], books=snapshot(sc, e, hist)))
    res = dict(asof=asof, freeze=a.freeze, print_depth_summary=summarize(rows), events=rows, live_snapshot=snaps)
    json.dump(res, open(a.out, 'w'), indent=1); print(json.dumps(res['print_depth_summary']))
    for s in snaps:
        qual = [b for b in s['books'] if b['depth_usd'] > 0]; print(s['id'], s['title'][:50], 'own-token books with a qualifying ask now:', len(qual), 'max depth $', max([b['depth_usd'] for b in s['books']] or [0]))
