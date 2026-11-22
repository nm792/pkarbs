#!/usr/bin/env python3
"""Mentions Polymarket 10c rule: volume per contract/event and P&L with fills capped at $200 per trade and $2,000 per UTC day, by family segment (R-031 / R-033).
Same rule/history as mentions_pm_daily_scorer.py (imported). DEPTH HERE IS A PRINT-BASED PROXY, NOT ASKS: historical order books were never recorded, so the
fill at an event is the first-hour BUY prints on the bet's own token (same market, same outcome) that clear the 10c edge, taken in time order up to $200 notional
(fee 0.04*p*(1-p) taker). A resting ask that never printed is invisible, so this is a FLOOR on depth and on P&L. Asks measured from logged books come from mentions_pm_firelog.py.
Usage: python3 -I mentions_pm_depth_backtest.py --scorer PATH --state DIR --out FILE --freeze ISO [--cap 200] [--daycap 2000]"""
import argparse, collections, datetime as dt, importlib.util, json, statistics as S, time, concurrent.futures as cf
ap = argparse.ArgumentParser(); ap.add_argument('--scorer', required=True); ap.add_argument('--state', required=True); ap.add_argument('--out', required=True)
ap.add_argument('--freeze', required=True); ap.add_argument('--cap', type=float, default=200.); ap.add_argument('--daycap', type=float, default=2000.)


def load(p):
    sp = importlib.util.spec_from_file_location('sc', p); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


def day(t): return dt.datetime.fromtimestamp(t, dt.timezone.utc).strftime('%Y-%m-%d')


def segment(fam): return {'trump-event': 'trump', 'trump-weekly': 'trump'}.get(fam, fam)


def sweep(sc, ev, hist, trades, t0, cap):
    """Fill the rule's chosen entry token with all first-hour qualifying BUY prints on that token, time order, up to cap notional. Returns (fills, first-print entry) or None."""
    ent = sc.pick_entry(ev, hist, trades, t0)
    if ent is None: return None
    t, cond, oi, p, sz, q, word, label, rate, toks = ent
    lim = (q - sc.THR) if oi == 0 else ((1 - q) - sc.THR)
    m = next(m for m in ev['markets'] if m['cond'] == cond); w = sc.win(m)
    left = cap; fills = []
    for (tt, side, pp, ss, o) in sorted(trades.get(cond, [])):
        if left <= 1e-9: break
        if not (t0 <= tt <= t0 + sc.WIN) or side != 'BUY' or o != oi or ss <= 0 or not (.05 <= pp <= lim): continue
        take = min(ss, left / pp); fills.append((pp, take)); left -= take * pp
    pnl = sum(sc.pnl(oi, pp, tk, w, rate) for pp, tk in fills); cost = sum(pp * tk for pp, tk in fills)
    return dict(cost=cost, pnl=pnl, n_fills=len(fills), single_pnl=sc.pnl(oi, p, sz, w, rate), single_cost=p * sz, won=(w if oi == 0 else 1 - w) == 1)


def volume(ev, trades):
    """$ notional (price*size, all sides) per market and per UTC day."""
    per = collections.defaultdict(float)   # (day) -> event total
    mk = {}
    for m in ev['markets']:
        tot = 0.0
        for (t, side, p, s, o) in trades.get(m['cond'], []):
            per[day(t)] += p * s; tot += p * s
        mk[m['cond']] = tot
    return per, mk


def apply_daycap(bets, daycap):
    """bets: list of dict(day, start, cost, pnl) in start order; scale a bet down if the UTC day's $ cap would be exceeded."""
    used = collections.defaultdict(float); out = []
    for b in sorted(bets, key=lambda b: b['start']):
        room = max(0.0, daycap - used[b['day']]); f = 0.0 if b['cost'] <= 0 else min(1.0, room / b['cost'])
        used[b['day']] += b['cost'] * f; out.append(dict(b, cost=b['cost'] * f, pnl=b['pnl'] * f))
    return out


def summarize(bets, vol_rows, span_days, cap):
    nb = len(bets); net = sum(b['pnl'] for b in bets); days_with = len({b['day'] for b in bets})
    return dict(events=len(vol_rows), bets=nb, bets_per_day=round(nb / span_days, 3), bets_per_active_day=round(nb / days_with, 2) if days_with else 0,
                net=round(net, 2), per_day=round(net / span_days, 3), pct_of_200=round(100 * net / span_days / 200, 2), cost=round(sum(b['cost'] for b in bets), 2),
                wins=sum(1 for b in bets if b['pnl'] > 0), avg_cost=round(S.mean([b['cost'] for b in bets]), 2) if bets else 0,
                event_usd_median=round(S.median([v['event_total'] for v in vol_rows]), 0) if vol_rows else 0,
                event_usd_first24h_median=round(S.median([v['first24h'] for v in vol_rows]), 0) if vol_rows else 0,
                contract_usd_median=round(S.median([x for v in vol_rows for x in v['contracts']]), 0) if vol_rows else 0,
                contract_usd_mean=round(S.mean([x for v in vol_rows for x in v['contracts']]), 0) if vol_rows else 0)


if __name__ == '__main__':
    a = ap.parse_args(); sc = load(a.scorer); fz = sc.ts(a.freeze); asof = time.time()
    closed = list(json.load(open(a.state + '/events.json')).values())
    op = [sc.slim(e) for e in (sc.fetch(f'{sc.GAMMA}/events?tag_slug=mention-markets&closed=false&limit=100&order=startDate&ascending=false') or [])]
    allev = {e['id']: e for e in closed}; allev.update({e['id']: e for e in op})
    pool = [e for e in allev.values() if sc.resolved(e)]
    fwd = sorted([e for e in allev.values() if e['markets'] and sc.start(e) >= fz], key=sc.start)
    conds = [m['cond'] for e in fwd for m in e['markets']]
    with cf.ThreadPoolExecutor(8) as ex: tr = dict(ex.map(sc.pull_trades, conds))
    miss = [c for c, v in tr.items() if v is None]
    if miss: raise SystemExit('trade pull failed for %d markets' % len(miss))
    seg_bets = collections.defaultdict(list); seg_vol = collections.defaultdict(list); seg_single = collections.defaultdict(list); daily_vol = collections.defaultdict(lambda: collections.defaultdict(float))
    for e in fwd:
        t0 = sc.start(e); sg = segment(e['fam']); per, mk = volume(e, tr)
        v = dict(id=e['id'], title=e['title'], start=t0, event_total=sum(per.values()), first24h=sum(p * s for m in e['markets'] for (t, sd, p, s, o) in tr.get(m['cond'], []) if t0 <= t < t0 + 86400), contracts=list(mk.values()))
        seg_vol[sg].append(v); seg_vol['ALL'].append(v)
        for d, x in per.items(): daily_vol[sg][d] += x; daily_vol['ALL'][d] += x
        if not sc.resolved(e) or sc.start(e) + sc.WIN > asof: continue
        hist = [h for h in pool if h['fam'] == e['fam'] and h['id'] != e['id'] and sc.settled_at(h) <= t0]
        r = sweep(sc, e, hist, tr, t0, a.cap)
        if r:
            b = dict(day=day(t0), start=t0, cost=r['cost'], pnl=r['pnl'], id=e['id']); seg_bets[sg].append(b); seg_bets['ALL'].append(b)
            seg_single[sg].append(dict(day=day(t0), start=t0, cost=r['single_cost'], pnl=r['single_pnl'])); seg_single['ALL'].append(dict(day=day(t0), start=t0, cost=r['single_cost'], pnl=r['single_pnl']))
    span = max(1.0, (asof - fz) / 86400); res = dict(freeze=a.freeze, span_days=round(span, 1), cap=a.cap, daycap=a.daycap, segments={})
    for sg in sorted(seg_vol):
        capped = apply_daycap(seg_bets[sg], a.daycap)
        s = summarize(capped, seg_vol[sg], span, a.cap)
        s['single_print_rule'] = summarize(seg_single[sg], seg_vol[sg], span, a.cap)   # frozen rule: first qualifying print only, print size
        dv = list(daily_vol[sg].values()); s['segment_usd_per_active_day_median'] = round(S.median(dv), 0) if dv else 0; s['segment_usd_per_calendar_day_mean'] = round(sum(dv) / span, 0)
        res['segments'][sg] = s
    json.dump(res, open(a.out, 'w'), indent=1)
    for sg, s in res['segments'].items():
        print(sg, {k: s[k] for k in ('events', 'bets', 'bets_per_day', 'net', 'per_day', 'pct_of_200', 'avg_cost', 'event_usd_median', 'event_usd_first24h_median', 'contract_usd_median', 'contract_usd_mean', 'segment_usd_per_calendar_day_mean')}, '| frozen single-print:', {k: s['single_print_rule'][k] for k in ('bets', 'net', 'per_day')})
