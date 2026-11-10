#!/usr/bin/env python3
"""Step 3: pair TheSports CS2 maps with Polymarket 'Map N Winner' tokens by TEAM NAMES (diary names vs market outcome names, both orders),
then load PM top-of-book series (books_mid: ms, bb, ba) for those tokens. Output pairs.json + books.pkl.
No co-movement is used to pick sides. Unpaired maps are listed with the reason."""
import sys, json, gzip, glob, re, unicodedata, difflib, pickle, collections
ROOT = '/home/user/repo/rn1/scores/thesports/'
DIRS = ['final-topics-8917-slim', 'slim-1102-32295', 'slim-0517-32295', 'final-topics-32295-slim', 'final-topics-32295b-slim', 'final-topics-24925']
rounds = json.load(open(sys.argv[1]))
def rd(p):
    for f in sorted(glob.glob(p, recursive=True)):
        for l in gzip.open(f, 'rt'):
            try: yield json.loads(l)
            except Exception: pass
names = {}; matches = {}; tourn = {}
for f in glob.glob(ROOT + 'diary/*.json'):
    d = json.load(open(f))
    if 'results' not in d: continue
    for t in d.get('results_extra', {}).get('team', []): names[t['id']] = t['name']
    for t in d.get('results_extra', {}).get('tournament', []): tourn[t['id']] = t['name']
for f in glob.glob(ROOT + 'diary/*.json'):
    d = json.load(open(f))
    if 'results' not in d: continue
    for m in d['results']:
        if 'home_team_id' in m: matches[m['id']] = m
def norm(x):
    x = unicodedata.normalize('NFKD', x or '').encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[^a-z0-9 ]', ' ', x).split()
def same(a, b):
    na, nb = norm(a), norm(b)
    if not na or not nb: return False
    ja, jb = ''.join(na), ''.join(nb)
    return ja == jb or ja in jb or jb in ja or difflib.SequenceMatcher(None, ja, jb).ratio() >= 0.85
mk = {}
for d in DIRS:
    for m in rd(ROOT + d + '/markets.jsonl.gz'):
        if m['sport'] == 'cs2': mk[m['cond']] = m
print('cs2 markets', len(mk))
pairs = {}; unp = collections.Counter(); unp_list = []
for key, v in rounds.items():
    mt = v['meta']; dm = matches.get(mt['mid'])
    if not dm: unp['no diary'] += 1; unp_list.append((key, 'no diary')); continue
    hn, an = names.get(dm['home_team_id']), names.get(dm['away_team_id'])
    if not hn or not an: unp['no names'] += 1; unp_list.append((key, 'no names')); continue
    found = None
    for m in mk.values():
        if m['smt'] != 'child_moneyline' or ('Map %s Winner' % mt['box']) not in m['q']: continue
        o0, o1 = m['outcomes']
        if same(hn, o0) and same(an, o1): found = (m, 0, 1)
        elif same(hn, o1) and same(an, o0): found = (m, 1, 0)
        if found: break
    if not found: unp['no PM map market'] += 1; unp_list.append((key, 'no PM map market: %s v %s' % (hn, an))); continue
    m, ih, ia = found
    pairs[key] = dict(home=hn, away=an, tok_home=m['tokens'][ih], tok_away=m['tokens'][ia], cond=m['cond'], q=m['q'], slug=m['slug'], title=m['title'],
                      tournament=tourn.get(dm.get('tournament_id')), match_time=dm.get('match_time'), bo=dm.get('box'))
    # match winner (parent) market
    for m2 in mk.values():
        if m2['smt'] == 'moneyline' and m2['slug'] == m['slug'] and len(m2['outcomes']) == 2:
            o0, o1 = m2['outcomes']
            if same(hn, o0) and same(an, o1): pairs[key].update(mw_home=m2['tokens'][0], mw_away=m2['tokens'][1], mw_cond=m2['cond'])
            elif same(hn, o1) and same(an, o0): pairs[key].update(mw_home=m2['tokens'][1], mw_away=m2['tokens'][0], mw_cond=m2['cond'])
print('paired maps', len(pairs), 'unpaired', dict(unp))
need = set()
for p in pairs.values():
    for k in ('tok_home', 'tok_away', 'mw_home', 'mw_away'):
        if k in p: need.add(p[k])
book = collections.defaultdict(list)
for d in DIRS:
    files = sorted(glob.glob(ROOT + d + '/books_mid/**/*.gz', recursive=True)) + sorted(glob.glob(ROOT + d + '/books_mid*.gz'))
    for f in files:
        for l in gzip.open(f, 'rt'):
            try: r = json.loads(l)
            except Exception: continue
            if r['tk'] in need: book[r['tk']].append((r['ms'] / 1000.0, r['bb'], r['ba']))
for k in book: book[k] = sorted(set(book[k]))
pickle.dump(dict(book=dict(book)), open(sys.argv[3], 'wb'))
json.dump(dict(pairs=pairs, unpaired=unp_list), open(sys.argv[2], 'w'))
print('tokens with books', len(book), 'of', len(need), 'rows', sum(len(x) for x in book.values()))
