#!/usr/bin/env python3
"""Slim export of a capture chunk so it can be committed (books are ~1 GB raw).
Usage: export_slim.py CHUNKDIR OUTDIR
Writes OUTDIR/ts_mqtt, markets, pmws, ts_poll, log (.jsonl.gz copies), books_mid.jsonl.gz
(one row per token per second: ms, tk, bb, ba, q = bid size at mid*0.975 floored to 0.01),
counts.json (messages per topic|UTC-hour). Read-only on CHUNKDIR."""
import sys, os, json, gzip, shutil, collections
src, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
for n in ('ts_mqtt.jsonl', 'markets.jsonl', 'pmws.jsonl', 'ts_poll.jsonl', 'log.jsonl'):
    p = os.path.join(src, n)
    if os.path.exists(p):
        with open(p, 'rb') as f, gzip.open(os.path.join(out, n + '.gz'), 'wb') as g:
            shutil.copyfileobj(f, g)
cnt = collections.defaultdict(int)
p = os.path.join(src, 'ts_mqtt.jsonl')
if os.path.exists(p):
    for l in open(p, errors='replace'):
        try: d = json.loads(l)
        except Exception: continue
        cnt["%s|%d" % (d.get('topic'), int(d['ms'] // 3600000) * 3600)] += 1
json.dump(cnt, open(os.path.join(out, 'counts.json'), 'w'))
last = {}
with open(os.path.join(src, 'books.jsonl'), errors='replace') as f, \
     gzip.open(os.path.join(out, 'books_mid.jsonl.gz'), 'wt') as g:
    for l in f:
        try: d = json.loads(l)
        except Exception: continue
        b = [(float(x['price']), float(x['size'])) for x in d.get('bids', [])]
        a = [(float(x['price']), float(x['size'])) for x in d.get('asks', [])]
        if not b or not a: continue
        bb, ba = max(b)[0], min(a)[0]
        mid = (bb + ba) / 2
        tk = d['tk']; s = d['ms'] // 1000
        if last.get(tk) == s: continue
        last[tk] = s
        p2 = int(mid * 0.975 * 100) / 100
        q = sum(sz for pr, sz in b if abs(pr - p2) < 1e-9)
        g.write(json.dumps({'ms': d['ms'], 'tk': tk, 'bb': bb, 'ba': ba, 'q': q}) + '\n')
