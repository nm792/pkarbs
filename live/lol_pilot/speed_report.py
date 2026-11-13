"""End-to-end speed + paper-fill report for a LoL pilot dry run (Nick 5 Nov 02:20Z: no real money until we know our speed).
Usage: python3 speed_report.py OUT/pilot.jsonl [frames.json]
Per kill event (times relative to the Polymarket price move, the market's own clock):
  price move  = first 1 s book mid at/past half the move (-60..+60 s around WS receipt), from feed_delay rows
  WS arrival  = when the PM sports WS showed the kill (ws_recv)
  decision    = first book poll after the WS update, when the bot decides (decision rows)
  order       = when the (paper) bid would be sent; accepted ~ order + one CLOB round trip (rtt_clob)
  true kill   = optional, Riot frame time of the kill (frames.json: [{"gid":..,"kills_home":..,"kills_away":..,"t":..}])
Paper fills: naive (first in line) and queue-adjusted (size resting ahead of us at our price must trade first)."""
import json, sys, statistics as S, collections

rows = [json.loads(l) for l in open(sys.argv[1]) if l.strip()]
by = collections.defaultdict(list)
for r in rows: by[r['type']].append(r)
ev = {r['eid']: r for r in by['event']}
fd = {r['eid']: r for r in by['feed_delay']}
dec = {r['eid']: r for r in by['decision']}
plc = collections.defaultdict(list)
for r in by['order_place']: plc[r['eid']].append(r)

def q(xs, p): xs = sorted(xs); return xs[min(len(xs) - 1, int(p * len(xs)))] if xs else None
def line(name, xs):
    xs = [x for x in xs if x is not None]
    if not xs: print(f"  {name:44} n 0"); return
    print(f"  {name:44} n {len(xs):3}  median {S.median(xs):+6.1f}  p10 {q(xs, .1):+6.1f}  p90 {q(xs, .9):+6.1f}  (s)")

ws_after_price = [fd[e]['delay_s'] for e in fd if fd[e].get('delay_s') is not None]
dec_after_ws = [dec[e]['first_book_after_ws'] for e in dec]
ord_after_ws = [p[0]['lag_since_event'] for p in plc.values()]
rtt = [r['rtt_clob'] for r in by['decision'] if r.get('rtt_clob') is not None]
accepted_after_price = []
for e, p in plc.items():
    if e in fd and fd[e].get('delay_s') is not None:
        accepted_after_price.append(fd[e]['delay_s'] + p[0]['lag_since_event'] + (S.median(rtt) if rtt else 0))
print(f"kill events {len(ev)}, windows {len(by['window'])}, events with a >=1c price move measured {len(ws_after_price)}")
print("delays (positive = after the price moved):")
line('WS arrival after price move', ws_after_price)
line('decision after WS arrival', dec_after_ws)
line('first paper bid after WS arrival', ord_after_ws)
line('CLOB round trip (order accept proxy)', rtt)
line('bid accepted after price move (sum)', accepted_after_price)
if len(sys.argv) > 2:
    fr = json.load(open(sys.argv[2])); tk = []
    for e, r in ev.items():
        n = r['new']; hit = [f['t'] for f in fr if f['gid'] == r['gid'] and f['kills_home'] >= n['ra'] and f['kills_away'] >= n['rb']]
        if hit: tk.append(r['t'] - min(hit))
    line('WS arrival after true kill (Riot frame)', tk)
pf = by['paper_fill']
print(f"paper bids {len(by['order_place'])}; queue ahead at placement (shares): "
      f"{'median %.0f, p90 %.0f' % (S.median([r['ahead'] for r in by['order_place']]), q([r['ahead'] for r in by['order_place']], .9)) if by['order_place'] else '-'}")
print(f"paper fills: naive {sum(r['naive'] for r in pf):.0f} shares, queue-adjusted {sum(r['queue'] for r in pf):.0f} shares "
      f"on {len({r['id'] for r in pf if r['queue'] > 0})} of {len(by['order_place'])} bids")
mo = [r for r in by['markout'] if r.get('pnl_60s') is not None]
if mo: print(f"1-min markout on naive paper fills: {len(mo)} fills, ${sum(r['pnl_60s'] for r in mo):+.2f}")
