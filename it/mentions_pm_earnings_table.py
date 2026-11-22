#!/usr/bin/env python3
"""Per-call table for Polymarket earnings-call mentions (R-044): one row per call (event) and per contract. Uses the backtest helpers (print-based FLOOR) and, for OPEN calls, live own-token ask depth (CLOB /book of the token itself).
Usage: python3 -I mentions_pm_earnings_table.py --scorer PATH --backtest PATH_TO_mentions_pm_depth_backtest.py --state DIR --out CSV --freeze ISO [--fam earnings-call]
Columns: call, start, contracts, event_usd_total, event_usd_first24h, usd_per_active_day_median, contract_usd_median, qualifying_print_usd_first_hour (all tokens), bet_side/word/cost/pnl (FLOOR sweep $200), ask_depth_now_best (own token, open calls only; NOT decision time)."""
import argparse, collections, csv, importlib.util, json, statistics as S, sys, time, concurrent.futures as cf
ap = argparse.ArgumentParser()
for k in ('scorer', 'backtest', 'state', 'out', 'freeze'): ap.add_argument('--' + k, required=True)
ap.add_argument('--fam', default='earnings-call')


def load(n, p):
    sp = importlib.util.spec_from_file_location(n, p); m = importlib.util.module_from_spec(sp); sys.modules[n] = m; sp.loader.exec_module(m); return m


def call_row(sc, bt, ev, hist, tr, t0, live=None):
    per, mk = bt.volume(ev, tr)
    qual = 0.0
    for m in ev['markets']:
        q = sc.q_for(hist, ev, m)
        for (t, side, p, sz, oi) in tr.get(m['cond'], []):
            if t0 <= t <= t0 + sc.WIN and side == 'BUY' and sz > 0 and .05 <= p <= .95 and (((q - p) if oi == 0 else ((1 - q) - p)) >= sc.THR): qual += p * sz
    r = dict(call=ev['title'], id=ev['id'], start=bt.day(t0), resolved=sc.resolved(ev), contracts=len(ev['markets']), event_usd_total=round(sum(per.values())),
             event_usd_first24h=round(sum(p * s for m in ev['markets'] for (t, sd, p, s, o) in tr.get(m['cond'], []) if t0 <= t < t0 + 86400)),
             usd_per_active_day_median=round(S.median(per.values())) if per else 0, contract_usd_median=round(S.median(mk.values())) if mk else 0,
             qualifying_print_usd_first_hour=round(qual, 2), bet_side='', bet_word='', bet_cost_floor='', bet_pnl_floor='', ask_depth_now_best='')
    if sc.resolved(ev) and sc.start(ev) + sc.WIN <= time.time():
        ent = sc.pick_entry(ev, hist, tr, t0)
        if ent:
            x = bt.sweep(sc, ev, hist, tr, t0, 200.); r.update(bet_side='YES' if ent[2] == 0 else 'NO', bet_word=ent[7], bet_cost_floor=round(x['cost'], 2), bet_pnl_floor=round(x['pnl'], 2))
    if live: r['ask_depth_now_best'] = live
    return r


if __name__ == '__main__':
    a = ap.parse_args(); sc = load('sc', a.scorer); bt = load('bt', a.backtest); fz = sc.ts(a.freeze)
    closed = list(json.load(open(a.state + '/events.json')).values())
    op = [sc.slim(e) for e in (sc.fetch(f'{sc.GAMMA}/events?tag_slug=mention-markets&closed=false&limit=100&order=startDate&ascending=false') or [])]
    allev = {e['id']: e for e in closed}; allev.update({e['id']: e for e in op}); pool = [e for e in allev.values() if sc.resolved(e)]
    fwd = sorted([e for e in allev.values() if e['fam'] == a.fam and e['markets'] and sc.start(e) >= fz], key=sc.start)
    with cf.ThreadPoolExecutor(8) as ex: tr = dict(ex.map(sc.pull_trades, [m['cond'] for e in fwd for m in e['markets']]))
    if any(v is None for v in tr.values()): raise SystemExit('trade pull failed')
    live_ids = {e['id'] for e in op}; rows = []
    for e in fwd:
        t0 = sc.start(e); hist = [h for h in pool if h['fam'] == e['fam'] and h['id'] != e['id'] and sc.settled_at(h) <= t0]; live = None
        if e['id'] in live_ids and not sc.resolved(e):
            best = 0.0
            for m in e['markets']:
                q = sc.q_for(hist, e, m)
                for oi, tok in enumerate(m['toks'][:2]):
                    b = sc.fetch(f'https://clob.polymarket.com/book?token_id={tok}') or {}
                    asks = [(float(x['price']), float(x['size'])) for x in b.get('asks', [])]; lim = (q - sc.THR) if oi == 0 else ((1 - q) - sc.THR)
                    best = max(best, sum(p * s for p, s in asks if .05 <= p <= lim))
            live = round(best, 2)
        rows.append(call_row(sc, bt, e, hist, tr, t0, live))
    with open(a.out, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    print(len(rows), 'calls; resolved with bet:', sum(1 for r in rows if r['bet_side']), '; total net FLOOR $', round(sum(r['bet_pnl_floor'] or 0 for r in rows), 2))
