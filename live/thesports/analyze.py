#!/usr/bin/env python3
"""Time TheSports events against the Polymarket PRICE, with queue position from our 1 s books (5 Nov 2026).

Input
  CAPDIR      a capture.py folder (books.jsonl[.gz], markets.jsonl[.gz])
  EVENTS      normalized TheSports events, JSONL, one per scoring event (point / kill / round / basket / play):
              {"ms": our receive ms, "ev_ms": TheSports event time ms or null, "sport": "tennis|lol|cs2|dota2|nba|nfl",
               "teams": ["A name", "B name"], "gains": 0 or 1 (index of the side the event helps), "kind": "point|kill|..."}
              The raw MQTT payload format is only known once the trial starts; normalize_<sport>.py turns ts_mqtt
              rows into this file. Any other feed (PM sports WS, Cito) can be normalized the same way for a fair race.
Method (per event, on the PM token of the side the event helps; markets matched by team/player names)
  R      = our receive time of the event.
  m0     = median book mid 45-90 s before R;  post = mid at R + 30 s.  Keep the event only if post - m0 >= 1c.
  Tm     = price onset: in the largest 3 s mid rise in [R - 75 s, R + 5 s] (must be >= max(1c, move/3)), the first
           time the mid has made half of that rise (250 ms grid; books are 1 s, so +-1 s resolution).
  lead_s = (Tm - R) / 1000.  POSITIVE = the feed arrived BEFORE the price moved (what we need). Negative = late.
  Queue at our bid P = floor_tick(mid at R x 0.975): size already resting at P at R, and whether best ask > P
  (bid is still placeable post-only).  Fills need PM v2 trades (pull afterwards); not estimated here.
Output: table to stdout + CAPDIR/thesports_timing.json (rows + per-sport medians, share of events with lead >= 0).
Usage: analyze.py CAPDIR EVENTS [--label name]
"""
import argparse, bisect, collections, gzip, json, math, os, re, statistics as st

ap = argparse.ArgumentParser(); ap.add_argument('cap'); ap.add_argument('events'); ap.add_argument('--label', default='thesports')
A = ap.parse_args()


def rd(path):
    for p in (path, path + '.gz'):
        if os.path.exists(p):
            op = gzip.open if p.endswith('.gz') else open
            with op(p, 'rt') as f:
                for l in f:
                    try: yield json.loads(l)
                    except Exception: pass
            return


def words(s): return set(w for w in re.sub(r'[^a-z0-9 ]', ' ', (s or '').lower()).split() if len(w) >= 3)


mk = []   # (sport, token, outcome words, other outcome words, question)
for m in rd(os.path.join(A.cap, 'markets.jsonl')):
    outs = m['outcomes']
    if len(outs) != 2: continue
    q = (m.get('q') or '').lower()
    gm = re.search(r'(game|map) (\d)', q)
    for i, t in enumerate(m['tokens']):
        mk.append(dict(sport=m['sport'], tk=t, me=words(outs[i]), other=words(outs[1 - i]), q=q, slug=m['slug'],
                       part=('match' if not gm else gm.group(1) + gm.group(2))))

books = collections.defaultdict(list)
for b in rd(os.path.join(A.cap, 'books.jsonl')):
    bids = {float(x['price']): float(x['size']) for x in b.get('bids') or []}
    asks = {float(x['price']): float(x['size']) for x in b.get('asks') or []}
    books[b['tk']].append((b['ms'], bids, max(bids) if bids else None, min(asks) if asks else None))
keys = {}
for t, v in books.items(): v.sort(key=lambda x: x[0]); keys[t] = [x[0] for x in v]


def at(t, T):
    i = bisect.bisect_right(keys.get(t, []), T) - 1
    return books[t][i] if i >= 0 else None


def mid(t, T):
    x = at(t, T)
    if not x or x[2] is None or x[3] is None or x[3] - x[2] > 0.10: return None
    if T - x[0] > 120000: return None
    return (x[2] + x[3]) / 2


def tick(p): return 0.001 if p < 0.04 or p > 0.96 else 0.01
def floor_t(p): k = tick(p); return round(math.floor(p / k + 1e-9) * k, 3)


def tokens_for(e):
    """PM tokens of the side the event helps: every market (match, and game/map winner) whose outcomes match the names."""
    a, b = (words(x) for x in e['teams']); g = a if e['gains'] == 0 else b; o = b if e['gains'] == 0 else a
    return [m for m in mk if m['sport'] == e['sport'] and m['me'] & g and m['other'] & o]


rows = []; n_ev = 0; n_nomatch = 0
for e in rd(A.events):
    n_ev += 1; R = e['ms']; ms_ = tokens_for(e)
    if not ms_: n_nomatch += 1; continue
    for m in ms_:
        t = m['tk']
        pre = [x for x in (mid(t, R - d) for d in range(90000, 44000, -1000)) if x is not None]
        post = mid(t, R + 30000)
        if len(pre) < 10 or post is None: continue
        m0 = st.median(pre); mv = post - m0
        if mv < 0.01: continue
        Tm = None; best = 0.0
        for d in range(-75000, 5001, 500):
            x0, x1 = mid(t, R + d - 3000), mid(t, R + d)
            if x0 is not None and x1 is not None and x1 - x0 > best: best, Tm = x1 - x0, R + d - 3000
        if Tm is None or best < max(0.01, mv / 3): continue
        x0 = mid(t, Tm)                                   # onset = first time inside the step window the mid
        for d in range(0, 3001, 250):                     # has made half of the step
            x1 = mid(t, Tm + d)
            if x1 is not None and x1 - x0 >= best / 2: Tm = Tm + d; break
        mR = mid(t, R) or m0; P = floor_t(mR * 0.975); bk = at(t, R)
        rows.append(dict(sport=e['sport'], kind=e.get('kind'), slug=m['slug'], part=m['part'], R=R, ev_ms=e.get('ev_ms'),
                         move=round(mv, 3), mid_pre=round(m0, 3), lead_s=round((Tm - R) / 1000, 1),
                         src_to_recv_s=None if not e.get('ev_ms') else round((R - e['ev_ms']) / 1000, 2),
                         P=P, q_at_P=None if not bk else round(bk[1].get(P, 0.0)),
                         placeable=None if not bk or bk[3] is None else bk[3] > P + 1e-9))

hdr = ['sport', 'kind', 'slug', 'part', 'move', 'mid_pre', 'lead_s', 'src_to_recv_s', 'P', 'q_at_P', 'placeable']
print('\t'.join(hdr))
for r in rows: print('\t'.join(str(r[h]) for h in hdr))
summ = dict(label=A.label, events=n_ev, events_no_market=n_nomatch, rows=len(rows), by_sport={})
for sp in sorted(set(r['sport'] for r in rows)):
    v = [r for r in rows if r['sport'] == sp]; L = sorted(r['lead_s'] for r in v)
    q = [r['q_at_P'] for r in v if r['q_at_P'] is not None]; s2 = [r['src_to_recv_s'] for r in v if r['src_to_recv_s'] is not None]
    summ['by_sport'][sp] = dict(n=len(v), lead_median_s=st.median(L), lead_p25_s=L[len(L) // 4], lead_p75_s=L[(3 * len(L)) // 4],
                                share_ahead_of_price=round(sum(x >= 0 for x in L) / len(L), 2),
                                queue_at_P_median=st.median(q) if q else None,
                                src_to_recv_median_s=st.median(s2) if s2 else None)
print(json.dumps(summ, indent=1))
json.dump(dict(rows=rows, summary=summ), open(os.path.join(A.cap, f'{A.label}_timing.json'), 'w'), indent=1)
