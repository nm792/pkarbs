#!/usr/bin/env python3
"""Fallback team names for TheSports match ids that are missing from the diary (diary only covers days Hermes refreshed).
Matches a TheSports match to a Polymarket sports-ws game (pmws.jsonl.gz, which carries team names) by the sequence of score states
and their first-seen times (+-45 s), under both home/away orientations. Writes DIARY/fallback-names-<tag>.json in the diary format
that big_events.py / event_sweep.py already read ({'results': [{id, home_team_id, away_team_id}], 'results_extra': {'team': [{id, name}]}}),
so the locked harness picks it up with no code change.
Usage: fallback_names.py SLIM[:SLIM...] OUTDIR TAG   (OUTDIR = the diary dir). Env VALIDATE=1: also compare against diary names already known and print accuracy.
Tennis: state = (set, home games, away games). Dota 2: state = (home kills, away kills) with >=4 distinct non-zero states. CS2 not matched (pmws score format unclear)."""
import sys, os, json, gzip, glob, collections, re, unicodedata, difflib
DIRS = sys.argv[1].split(':'); OUT = sys.argv[2]; TAG = sys.argv[3]
def rd(p):
    for f in sorted(glob.glob(p, recursive=True)):
        for l in gzip.open(f, 'rt'):
            try: yield json.loads(l)
            except Exception: pass
def rdm(s):
    for d in DIRS: yield from rd(d + s)
# ---- PM sports-ws: first-seen time of each state per game
pm = collections.defaultdict(lambda: {'names': None, 'lg': None, 'st': {}})
for r in rdm('/pmws.jsonl.gz'):
    if 'gameId' not in r: continue
    lg = r.get('leagueAbbreviation'); g = pm[r['gameId']]
    g['names'] = (r.get('homeTeam'), r.get('awayTeam')); g['lg'] = lg
    sc = r.get('score') or ''; t = r['ms'] / 1000.0
    try:
        if lg in ('atp', 'wta', 'challenger'):
            a, b = [int(x) for x in sc.split(',')[-1].strip().split('-')]; s = int((r.get('period') or 'S0').replace('S', ''))
            g['st'].setdefault((s, a, b), t)
        elif lg == 'dota2':
            a, b = [int(x) for x in sc.split('|')[0].split('-')]
            if a + b > 0: g['st'].setdefault((a, b), t)
    except Exception: pass
# ---- TheSports: first-seen time of each state per match
ts = collections.defaultdict(lambda: {'sp': None, 'st': {}})
for r in sorted(rdm('/ts_mqtt/**/*.gz'), key=lambda r: r['ms']):
    sp = r['topic'].split('/')[1]
    if sp not in ('tennis', 'dota2'): continue
    try: ps = json.loads(r['p'])
    except Exception: continue
    t = r['ms'] / 1000.0
    for p in ps:
        if sp == 'tennis':
            m = ts[p['id']]; m['sp'] = 'tennis'
            for st_ in p.get('timeline') or []:
                for rd_ in st_.get('rounds', []):
                    sc = rd_.get('score')
                    if sc: m['st'].setdefault((st_['set'], sc.get('home', 0), sc.get('away', 0)), t)
        else:
            m = ts[p['match_id']]; m['sp'] = 'dota2'
            a, b = p['home']['stats'][0], p['away']['stats'][0]
            if a + b > 0: m['st'].setdefault((a, b, p['box_num']), t)
def score(tsm, g, swap, esports):
    n = 0
    for k, t in tsm['st'].items():
        k2 = k
        if esports:
            k2 = (k[1], k[0]) if swap else (k[0], k[1])              # drop box_num; kills (home, away)
        elif swap:
            k2 = (k[0], k[2], k[1])
        t2 = g['st'].get(k2)
        if t2 is not None and abs(t - t2) <= 45: n += 1
    return n
res = {}
for mid, m in ts.items():
    esp = m['sp'] == 'dota2'; need = 4
    best = []
    for gid, g in pm.items():
        if (g['lg'] == 'dota2') != esp or (not esp and g['lg'] not in ('atp', 'wta', 'challenger')): continue
        for swap in (False, True):
            n = score(m, g, swap, esp)
            if n >= need: best.append((n, gid, swap))
    best.sort(reverse=True)
    if best and (len(best) == 1 or best[0][0] >= best[1][0] + 2):
        n, gid, swap = best[0]; h, a = pm[gid]['names']
        res[mid] = (a, h) if swap else (h, a)         # TheSports home name, away name
        res[mid] = res[mid] + (n,)
print('TS matches %d | matched by score sequence %d' % (len(ts), len(res)))
# ---- validate against names already in the diary
DI = OUT
names = {}; known = {}
for f in glob.glob(DI + '/*.json'):
    if os.path.basename(f).startswith('fallback-names'): continue
    d = json.load(open(f))
    if 'results' in d:
        for t in d.get('results_extra', {}).get('team', []): names[t['id']] = t['name']
for f in glob.glob(DI + '/*.json'):
    if os.path.basename(f).startswith('fallback-names'): continue
    d = json.load(open(f))
    if 'results' in d:
        for m in d['results']: known[m['id']] = (names.get(m['home_team_id']), names.get(m['away_team_id']))
def norm(x): return re.sub(r'[^a-z0-9]', '', unicodedata.normalize('NFKD', x or '').encode('ascii', 'ignore').decode().lower())
def same(a, b):
    na, nb = norm(a), norm(b)
    return bool(na and nb) and (na in nb or nb in na or difflib.SequenceMatcher(None, na, nb).ratio() >= 0.8)
ok = bad = unk = 0
for mid, (h, a, n) in res.items():
    k = known.get(mid)
    if not k or None in k: unk += 1; continue
    if same(h, k[0]) and same(a, k[1]): ok += 1
    else: bad += 1; print('  MISMATCH', mid, (h, a), 'diary', k)
print('validation vs diary names: agree %d, disagree %d, no diary entry %d' % (ok, bad, unk))
missing = [m for m in ts if not known.get(m) or None in known[m]]
print('TS matches with no diary names: %d; of those matched by fallback: %d' % (len(missing), sum(1 for m in missing if m in res)))
out = {'results': [], 'results_extra': {'team': []}}
for mid, (h, a, n) in res.items():
    if known.get(mid) and None not in known[mid]: continue
    hid, aid = 'fb_%s_h' % mid, 'fb_%s_a' % mid
    out['results'].append({'id': mid, 'home_team_id': hid, 'away_team_id': aid})
    out['results_extra']['team'] += [{'id': hid, 'name': h}, {'id': aid, 'name': a}]
fn = os.path.join(OUT, 'fallback-names-%s.json' % TAG)
json.dump(out, open(fn, 'w'))
print('wrote', fn, len(out['results']), 'matches')
