"""Rebuild market metadata for tokens that have books in an export but are missing from markets.jsonl.gz
(the slim export truncates markets.jsonl at ~02:16Z 8 Nov). Uses Polymarket gamma /markets?clob_token_ids=.
usage: recover_markets.py OUTDIR EXPORTDIR [EXPORTDIR...]"""
import sys, os, glob, gzip, json, requests, collections
out, dirs = sys.argv[1], sys.argv[2:]
known, seen = set(), set()
for d in dirs:
    f = d + '/markets.jsonl.gz'
    if os.path.exists(f):
        for l in gzip.open(f, 'rt'):
            try: known.update(json.loads(l)['tokens'])
            except Exception: pass
    for f in glob.glob(d + '/books_mid/**/*.gz', recursive=True):
        for l in gzip.open(f, 'rt'):
            try: seen.add(json.loads(l)['tk'])
            except Exception: pass
miss = sorted(seen - known)
print('tokens with books', len(seen), 'known', len(seen & known), 'missing', len(miss))
SP = {'tennis': 'tennis', 'counter-strike': 'cs2', 'dota-2': 'dota2', 'league-of-legends': 'lol', 'nba': 'nba'}
rows = {}
for i in range(0, len(miss), 20):
    try: r = requests.get('https://gamma-api.polymarket.com/markets', params=[('clob_token_ids', t) for t in miss[i:i+20]] + [('limit', 100)], timeout=60).json()
    except Exception as e: print('err', e); continue
    for m in r:
        ev = (m.get('events') or [{}])[0]
        tags = [t['slug'] for t in ev.get('tags', [])] if ev.get('tags') else []
        sport = next((SP[t] for t in tags if t in SP), None)
        if not sport:
            s = ev.get('slug', '')
            sport = 'tennis' if s.split('-')[0] in ('atp', 'wta', 'itf', 'challenger') else None
        if not sport: continue
        toks = json.loads(m['clobTokenIds']) if isinstance(m['clobTokenIds'], str) else m['clobTokenIds']
        outs = json.loads(m['outcomes']) if isinstance(m['outcomes'], str) else m['outcomes']
        rows[m['conditionId']] = {'ms': 0, 'sport': sport, 'slug': ev.get('slug', ''), 'gid': ev.get('id'), 'title': ev.get('title', ''),
            'start': m.get('gameStartTime') or '', 'q': m.get('question', ''), 'smt': m.get('sportsMarketType') or 'moneyline',
            'cond': m['conditionId'], 'tokens': toks, 'outcomes': outs}
os.makedirs(out, exist_ok=True)
with gzip.open(out + '/markets.jsonl.gz', 'wt') as f:
    for r in rows.values(): f.write(json.dumps(r) + '\n')
print('recovered', len(rows), collections.Counter((r['sport'], r['smt']) for r in rows.values()))
