#!/usr/bin/env python3
"""Pull data-api v2 trades for every condition in CAPDIR/markets.jsonl whose game has sports-WS messages.
Usage: pull_trades.py CAPDIR  -> CAPDIR/trades/<cond>.json"""
import json, os, ssl, sys, urllib.request
d = sys.argv[1]; os.makedirs(os.path.join(d, 'trades'), exist_ok=True)
ctx = ssl.create_default_context(cafile=os.environ.get('SSL_CERT_FILE') or None)
gids = {json.loads(l).get('gameId') for l in open(os.path.join(d, 'sports.jsonl'))}
conds = {}
for l in open(os.path.join(d, 'markets.jsonl')):
    m = json.loads(l)
    if m['gid'] in gids: conds[m['cond']] = m['title'] + ' / ' + m['kind']
for c, title in conds.items():
    out, cur = [], None
    for _ in range(100):
        u = f'https://data-api.polymarket.com/v2/trades?condition={c}&limit=500' + (f'&cursor={cur}' if cur else '')
        r = json.loads(urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'pkarbs-research/1.0'}), context=ctx, timeout=30).read())
        out += r.get('data') or []; pg = r.get('pagination') or {}
        if not pg.get('has_more'): break
        cur = pg['next_cursor']
    json.dump(out, open(os.path.join(d, 'trades', c + '.json'), 'w')); print(len(out), title)
