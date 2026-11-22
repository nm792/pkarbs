#!/usr/bin/env python3
"""R-049: every Polymarket mentions event that closed in the last N days, ALL families: Gamma volume vs data-api trade-dated volume (incl. the final hours before resolution),
frozen-rule bet at $200 per trade (print-based FLOOR) and P&L under the $2,000/day cap, and the weekly volume reconciliation.
Decision-time own-token ask depth: UNMEASURED (no recorder ran in the first hour); the column says so.
Usage: python3 -I mentions_pm_recent.py --scorer PATH --backtest PATH --state DIR --out PREFIX [--days 30]"""
import argparse, collections, csv, datetime as dt, importlib.util, json, statistics as S, sys, time, concurrent.futures as cf
ap = argparse.ArgumentParser()
for k in ('scorer', 'backtest', 'state', 'out'): ap.add_argument('--' + k, required=True)
ap.add_argument('--days', type=int, default=30)


def load(n, p):
    sp = importlib.util.spec_from_file_location(n, p); m = importlib.util.module_from_spec(sp); sys.modules[n] = m; sp.loader.exec_module(m); return m


def vol_between(trades_by_cond, lo, hi):
    """Notional (price*size, all sides) of trades with lo <= t < hi."""
    return sum(p * s for tr in trades_by_cond.values() for (t, sd, p, s, o) in tr if lo <= t < hi)


if __name__ == '__main__':
    a = ap.parse_args(); sc = load('sc', a.scorer); bt = load('bt', a.backtest); now = time.time(); lo = now - a.days * 86400
    raw = {}
    d0 = (dt.date.today() - dt.timedelta(days=a.days + 3))
    for tag_closed in ('true', 'false'):
        off = 0
        while True:
            r = sc.fetch(f'{sc.GAMMA}/events?tag_slug=mention-markets&closed={tag_closed}&limit=100&offset={off}' + (f'&end_date_min={d0}' if tag_closed == 'true' else '')) or []
            for x in r: raw[x['id']] = x
            if len(r) < 100: break
            off += 100
    closed = list(json.load(open(a.state + '/events.json')).values()); pool = [e for e in closed if sc.resolved(e)]
    ev = {}
    for i, x in raw.items():
        e = sc.slim(x); e['gvol'] = float(x.get('volume') or 0); e['gend'] = sc.ts(x['endDate']) if x.get('endDate') else None; e['slug'] = x['slug']; e['is_closed'] = bool(x.get('closed')); ev[i] = e
    allc = [e for e in ev.values() if e['markets'] and (e['gend'] or 0) >= lo or not e['is_closed']]
    with cf.ThreadPoolExecutor(8) as ex: tr = dict(ex.map(sc.pull_trades, [m['cond'] for e in allc for m in e['markets']]))
    if any(v is None for v in tr.values()): raise SystemExit('trade pull failed')
    rows = []; bets = []
    for e in sorted(allc, key=sc.start):
        t0 = sc.start(e); end = e['gend'] or now; trs = {m['cond']: tr[m['cond']] for m in e['markets']}
        hist = [h for h in pool if h['fam'] == e['fam'] and h['id'] != e['id'] and sc.settled_at(h) <= t0]
        r = dict(slug=e['slug'], fam=e['fam'], start=bt.day(t0), end=bt.day(end), status='closed' if e['is_closed'] else 'open', resolved=sc.resolved(e), gamma_volume=round(e['gvol']),
                 trade_volume_total=round(vol_between(trs, 0, 9e18)), trade_vol_last_6h_before_end=round(vol_between(trs, end - 6 * 3600, end)), trade_vol_last_24h_before_end=round(vol_between(trs, end - 86400, end)),
                 trade_vol_first_hour=round(vol_between(trs, t0, t0 + 3600)), trade_vol_last_7d=round(vol_between(trs, now - 7 * 86400, now)), ask_depth_at_decision='UNMEASURED (no recorder in first hour)',
                 bet_side='', bet_word='', bet_price='', bet_size_usd='', bet_pnl_floor='')
        if sc.resolved(e) and t0 + sc.WIN <= now:
            ent = sc.pick_entry(e, hist, tr, t0)
            if ent:
                x = bt.sweep(sc, e, hist, tr, t0, 200.)
                r.update(bet_side='YES' if ent[2] == 0 else 'NO', bet_word=ent[7], bet_price=round(ent[3], 3), bet_size_usd=round(x['cost'], 2), bet_pnl_floor=round(x['pnl'], 2))
                bets.append(dict(day=bt.day(t0), start=t0, cost=x['cost'], pnl=x['pnl'], slug=e['slug'], end=end))
        rows.append(r)
    capped = bt.apply_daycap(bets, 2000.)
    with open(a.out + '_events.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    res = {}
    for days in (7, 30):
        cut = now - days * 86400; sel = [r for r in rows if r['status'] == 'closed' and sc.ts(r['end'] + 'T00:00:00Z') >= cut - 86400]
        cb = [b for b in capped if b['end'] >= cut - 86400]
        res[days] = dict(events_closed=len(sel), gamma_volume=sum(r['gamma_volume'] for r in sel), trade_volume_total=sum(r['trade_volume_total'] for r in sel),
                         trade_vol_last_24h_before_end=sum(r['trade_vol_last_24h_before_end'] for r in sel), trade_vol_last_6h_before_end=sum(r['trade_vol_last_6h_before_end'] for r in sel),
                         bets=len(cb), net_floor=round(sum(b['pnl'] for b in cb), 2), per_day=round(sum(b['pnl'] for b in cb) / days, 2), pct_of_200=round(100 * sum(b['pnl'] for b in cb) / days / 200, 2))
    res['calendar_trade_volume_last_7d_all_events_incl_open'] = sum(r['trade_vol_last_7d'] for r in rows)
    res['calendar_trade_volume_last_7d_by_family'] = {f: sum(r['trade_vol_last_7d'] for r in rows if r['fam'] == f) for f in sorted({r['fam'] for r in rows})}
    ratios = [r['trade_volume_total'] / r['gamma_volume'] for r in rows if r['gamma_volume'] > 5000 and r['status'] == 'closed']
    res['trade_over_gamma_ratio_median'] = round(S.median(ratios), 3) if ratios else None
    json.dump(res, open(a.out + '_summary.json', 'w'), indent=1); print(json.dumps(res, indent=1))
