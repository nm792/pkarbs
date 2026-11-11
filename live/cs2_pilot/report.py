"""Summarise a pilot log. Usage: python3 report.py OUT/pilot.jsonl [more.jsonl ...]  -> prints a table and the dry-run gates."""
import json, sys, statistics as S, collections

rows = [json.loads(l) for fn in sys.argv[1:] for l in open(fn) if l.strip()]
by = collections.defaultdict(list)
for r in rows: by[r['type']].append(r)

def pct(xs, q):
    xs = sorted(xs); return xs[min(len(xs) - 1, int(q * len(xs)))] if xs else None

starts = by['start']; geo = starts[-1].get('geoblock') if starts else None
places = by['order_place']; cancels = by['order_cancel']; fills = by['fill']; pf = by['paper_fill']; mo = by['markout']
fd = [r['delay_s'] for r in by['feed_delay'] if r.get('delay_s') is not None]
fd_agree = [r for r in by['feed_delay'] if r.get('agrees') is not None]
cross = [r for r in places if r.get('best_ask') is not None and r['price'] >= r['best_ask'] - 1e-9]
over = [r for r in places if r.get('mid0') is not None and r['price'] < (r['mid0'] if r['tok'] == 0 else 1 - r['mid0']) * 0.975 - 1e-9]   # below market - 2.5% breaks Nick's rule
real_usd = sum(r['usd'] for r in fills if r['real']); paper_usd = sum(r['usd'] for r in fills if not r['real'])
pn = sum(r['naive'] for r in pf); pq = sum(r['queue'] for r in pf)
placed_sh = sum(r['size'] for r in places)
games = {r['gid'] for r in by['event']}
errs = collections.Counter(r.get('where') for r in by['error'])

print(f"log rows {len(rows)}, from {rows[0]['iso'] if rows else '-'} to {rows[-1]['iso'] if rows else '-'}")
print(f"geoblock at start: {geo}")
print(f"games with round events {len(games)}; round events {len(by['event'])}; windows opened {len(by['window'])}; "
      f"window skips {len(by['window_skip'])}; map-end/reset skipped {len(by['event_skip'])}")
print(f"orders placed {len(places)} ({placed_sh:.0f} shares, ${sum(r['usd'] for r in places):.0f} quoted); cancels {len(cancels)}; "
      f"rejects {len(by['order_reject'])}")
if places:
    print(f"  queue ahead at placement (shares): median {S.median([r['ahead'] for r in places]):.0f}, "
          f"p90 {pct([r['ahead'] for r in places], 0.9):.0f}; placed {S.median([r['lag_since_event'] for r in places]):.1f} s after WS event (median)")
print(f"fills: real ${real_usd:.2f} ({sum(1 for r in fills if r['real'])}), paper ${paper_usd:.2f} ({sum(1 for r in fills if not r['real'])})")
print(f"paper fills from public prints: naive {pn:.0f} shares, queue-adjusted {pq:.0f} shares "
      f"({100 * pq / pn:.0f}% of naive)" if pn else "paper fills from public prints: none")
for real in (True, False):
    m = [r for r in mo if r.get('real') == real and r.get('pnl_60s') is not None]
    if m:
        usd = sum(r['shares'] * r['price'] for r in m); pnl = sum(r['pnl_60s'] for r in m)
        print(f"  1-min markout ({'real' if real else 'paper'}): {len(m)} fills, ${usd:.0f}, ${pnl:+.2f} = {100 * pnl / usd:+.2f}%")
if fd:
    print(f"feed delay (WS receipt minus market's half-move time): n {len(fd)}, median {S.median(fd):+.1f} s, "
          f"p10 {pct(fd, 0.1):+.1f}, p90 {pct(fd, 0.9):+.1f}; market moved the model's way on "
          f"{sum(r['agrees'] for r in fd_agree)}/{len(fd_agree)} events with a >=1c move")
res = by['resolve']
print(f"resolved markets {len(res)}, realized P&L ${sum(r['pnl'] for r in res):+.2f}; halts {[r['why'] for r in by['halt']]}")
print(f"errors by place: {dict(errs)}")
print("rule checks: bids at/above best ask:", len(cross), "| bids below mid x 0.975:", len(over))

# dry-run gates (fixed in agent/tasks/cs2-pilot.md before the run)
book_err = errs.get('books', 0); n_poll = max(1, len(by['queue']) + len(by['window']))
gates = [('geoblock check recorded and not blocked', bool(geo) and geo.get('blocked') is False),
         ('>= 20 within-map round events on tier-1 matches', len(by['event']) >= 20),
         ('>= 10 windows opened', len(by['window']) >= 10),
         ('no bid at/above best ask or below mid x 0.975', not cross and not over),
         ('feed delay measured on >= 10 events', len(fd) >= 10),
         ('no crash (no error in main)', errs.get('main', 0) == 0)]
for name, ok in gates: print(('PASS ' if ok else 'FAIL ') + name)
print(f"{sum(ok for _, ok in gates)} of {len(gates)} gates pass")
