#!/usr/bin/env python3
"""Read-only inventory of Polymarket recorder dirs: per dir and sport, markets seen and first/last books ms (UTC).
Usage: pm_recorder_inventory.py ROOT [ROOT...]   Looks 3 levels deep for markets.jsonl(.gz). Writes nothing."""
import sys, os, json, gzip, collections, datetime
def op(p): return gzip.open(p, 'rt', errors='replace') if p.endswith('.gz') else open(p, errors='replace')
def utc(ms): return datetime.datetime.fromtimestamp(ms/1000, datetime.timezone.utc).strftime('%Y-%m-%d %H:%MZ')
def dirs(root):
    for dp, dn, fn in os.walk(root):
        if dp[len(root):].count(os.sep) >= 3: dn[:] = []
        if any(f.startswith('markets.jsonl') for f in fn): yield dp, fn
for root in sys.argv[1:]:
    for dp, fn in sorted(dirs(root)):
        mk = collections.defaultdict(set); lo = hi = None
        for f in fn:
            if f.startswith('markets.jsonl'):
                for line in op(os.path.join(dp, f)):
                    try: r = json.loads(line)
                    except Exception: continue
                    mk[r.get('sport', '?')].add(r.get('slug'))
        for f in fn:
            if f.startswith('books.jsonl'):
                first = last = None
                for line in op(os.path.join(dp, f)):
                    try: m = json.loads(line).get('ms')
                    except Exception: continue
                    if m: first = first or m; last = m
                if first: lo = min(lo or first, first); hi = max(hi or last, last)
        print(dp, 'books', utc(lo) if lo else 'none', utc(hi) if hi else 'none')
        for s, v in sorted(mk.items()): print('  sport', s, 'events', len(v))
