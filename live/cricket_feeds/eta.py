#!/usr/bin/env python3
"""Event-triggered average of the batting team's mid price around ESPN-feed events (wicket / four / six).
For each event at R (our receive ms of the ball), s = -1 wicket, +1 boundary; curve(k) = mean over events of
s * (mid(R+k) - mid(R-60)). Placebo: random times and random signs (should be flat at 0).
Reads the capture folder (books.jsonl.gz, espn.jsonl) and the match map used by analyze.py.
Usage: eta.py CAPDIR MATCHMAP.json [OUT.json]
"""
import bisect, gzip, json, os, random, sys
import numpy as np

cap, mapf = sys.argv[1], sys.argv[2]
M = {m['slug']: m for m in json.load(open(mapf))}
books = {}
for l in gzip.open(os.path.join(cap, 'books.jsonl.gz'), 'rt'):
    r = json.loads(l)
    b = [float(x['price']) for x in r.get('bids') or []]; a = [float(x['price']) for x in r.get('asks') or []]
    if b and a:
        books.setdefault(r['tk'], ([], []))[0].append(r['ms'] / 1000); books[r['tk']][1].append((max(b) + min(a)) / 2)


def mid(tk, t):
    T, m = books[tk]; i = bisect.bisect_right(T, t) - 1
    return m[i] if i >= 0 else None


slug_ev = {m['espn']: s for s, m in M.items()}
ev = []
for l in (gzip.open(os.path.join(cap, 'espn.jsonl.gz'), 'rt') if os.path.exists(os.path.join(cap, 'espn.jsonl.gz')) else open(os.path.join(cap, 'espn.jsonl'))):
    r = json.loads(l)
    if r['first'] or r['play'] not in ('out', 'four', 'six') or r['ev'] not in slug_ev: continue
    tk = M[slug_ev[r['ev']]]['teams'].get(r['bat'])
    if tk in books: ev.append((tk, r['ms'] / 1000, -1 if r['play'] == 'out' else 1, r['play']))
ks = list(range(-60, 91, 5))


def curve(evs):
    C = []
    for tk, R, s, _ in evs:
        b = mid(tk, R - 60)
        if b is not None: C.append([s * (mid(tk, R + k) - b) for k in ks])
    return np.array(C)


C = curve(ev); mean = C.mean(0) * 100; se = C.std(0) / np.sqrt(len(C)) * 100
random.seed(2); P = []
for tk, R, s, _ in ev:
    for _ in range(5):
        R2 = R + random.uniform(-600, 600)
        if mid(tk, R2 - 60) is None or mid(tk, R2 + 90) is None: continue
        sg = random.choice([-1, 1]); b = mid(tk, R2 - 60); P.append([sg * (mid(tk, R2 + k) - b) for k in ks])
P = np.array(P) * 100
tot = mean[-1]; half = next(k for k, m in zip(ks, mean) if m >= tot / 2)
res = dict(n=len(C), ks=ks, mean_c=mean.round(2).tolist(), se_c=se.round(2).tolist(), placebo_mean_c=P.mean(0).round(2).tolist(),
           total_move_c_at_90s=round(float(tot), 2), share_done_at_R=round(float(mean[ks.index(0)] / tot), 2), half_move_at_k=half,
           by_play={pl: dict(n=len(curve([e for e in ev if e[3] == pl])), mean_c=(curve([e for e in ev if e[3] == pl]).mean(0) * 100).round(2).tolist()) for pl in ('four', 'six', 'out')})
print(json.dumps({k: v for k, v in res.items() if k not in ('by_play',)}))
if len(sys.argv) > 3: json.dump(res, open(sys.argv[3], 'w'))
