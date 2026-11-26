#!/usr/bin/env python3
"""Earnings-beat DAILY FORWARD LIST (own strategy, not will-say). Read-only public APIs (Gamma + CLOB /book), no orders, no keys.
Rule screened (reviewer/pkarbs/earnings-beat-2026-11-25): buy YES when the YES price is under 50c before the report. This script lists every OPEN 'beat quarterly earnings' market,
its YES token's OWN best ask, and for the ones under 50c the $ depth at asks under 50c capped at $cap (default 200), average fill price and the venue fee per share.
Usage: python3 -I mentions_beat_forward_list.py --scorer PATH/mentions_pm_daily_scorer.py --out DIR [--cap 200] [--thr 0.50]
Writes DIR/beat_forward_<UTC date>.csv (all open markets) and prints the under-threshold rows. NO NO-token pricing from YES: only the YES book is read for the rule."""
import argparse, csv, datetime as dt, importlib.util, json, os, re, sys


def load(n, p):
    sp = importlib.util.spec_from_file_location(n, p); m = importlib.util.module_from_spec(sp); sys.modules[n] = m; sp.loader.exec_module(m); return m


def depth_under(asks, thr, cap):
    """asks: [(price, size)] ascending. $ and shares available at prices strictly under thr, walking up to cap dollars."""
    left = cap; cost = size = 0.0
    for p, s in sorted(asks):
        if p >= thr or left <= 1e-9: break
        t = min(s, left / p); left -= t * p; cost += t * p; size += t
    return cost, size


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--scorer', required=True); ap.add_argument('--out', required=True); ap.add_argument('--cap', type=float, default=200.); ap.add_argument('--thr', type=float, default=.50)
    a = ap.parse_args(); sc = load('sc', a.scorer); now = dt.datetime.now(dt.timezone.utc); rows = []; evs = []
    for i in range(10):
        r = sc.fetch(f'{sc.GAMMA}/events?tag_slug=earnings&closed=false&limit=50&offset={i * 50}')
        if r is None: sys.exit('gamma read failed; nothing listed')
        evs += r
        if len(r) < 50: break
    for x in evs:
        if not re.search(r'beat', x.get('title', ''), re.I): continue
        try: end = sc.ts(x['endDate'])
        except Exception: end = None
        if end is not None and end < now.timestamp(): continue   # report time passed: not pre-report
        for m in x.get('markets', []):
            if not m.get('acceptingOrders'): continue
            try: toks = json.loads(m['clobTokenIds']); outs = json.loads(m['outcomes'])
            except Exception: continue
            if len(toks) < 2 or outs[0] != 'Yes': continue   # YES token must be index 0, else skip rather than guess
            b = sc.fetch(f'https://clob.polymarket.com/book?token_id={toks[0]}') or {}
            asks = sorted((float(q['price']), float(q['size'])) for q in b.get('asks', []))
            fs = m.get('feeSchedule') or {}; rate = fs.get('rate') or 0
            cost, size = depth_under(asks, a.thr, a.cap); avg = cost / size if size else None
            rows.append(dict(date=now.strftime('%Y-%m-%d'), time_utc=now.strftime('%H:%MZ'), event=x['id'], title=x['title'][:70], end=(x.get('endDate') or '')[:19], hours_to_end=None if end is None else round((end - now.timestamp()) / 3600, 1),
                             yes_best_ask=asks[0][0] if asks else None, yes_best_ask_size=asks[0][1] if asks else None, under_thr=bool(asks and asks[0][0] < a.thr), depth_usd_under_thr=round(cost, 2), shares_under_thr=round(size, 2),
                             avg_price=round(avg, 4) if avg else None, fee_rate=rate, fee_per_share=round(rate * avg * (1 - avg), 5) if avg else None, ask_levels=len(asks)))
    os.makedirs(a.out, exist_ok=True); fn = os.path.join(a.out, 'beat_forward_%s.csv' % now.strftime('%Y%m%d'))
    new = not os.path.exists(fn)
    with open(fn, 'a', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]) if rows else ['date']); 
        if new and rows: w.writeheader()
        for r in rows: w.writerow(r)
    u = [r for r in rows if r['under_thr']]
    print('BEAT FORWARD LIST %s UTC: %d open pre-report beat markets with a YES book, %d with YES best ask under %.2f' % (now.strftime('%Y-%m-%d %H:%M'), len(rows), len(u), a.thr))
    for r in sorted(rows, key=lambda r: (r['yes_best_ask'] is None, r['yes_best_ask'] or 9)): print('  %s | %s | end %s (%s h) | YES ask %s x %s | %s' % (r['event'], r['title'][:46], r['end'][:16], r['hours_to_end'], r['yes_best_ask'], r['yes_best_ask_size'], ('UNDER: $%.2f at asks under %.2f, avg %s, fee/share %s' % (r['depth_usd_under_thr'], a.thr, r['avg_price'], r['fee_per_share'])) if r['under_thr'] else 'not under'))
    return 0


if __name__ == '__main__': sys.exit(main() or 0)
