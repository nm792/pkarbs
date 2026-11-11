#!/usr/bin/env python3
"""Step 12: team Elo from the WHOLE bo3.gg CS2 history (77k finished matches, K scaled by series length and score margin, 12 months decay toward 1500 not applied).
Evaluates Elo as a pre-match predictor on the whole history (time-ordered, held-out by construction: rating BEFORE each match), then maps TheSports/PM team names to bo3 teams
and writes elo_pre.json {pairkey: (elo_home, elo_away, n_prior_matches_home, n_prior_away)} for paired maps (rating before the map's match start)."""
import sys, json, re, math, datetime as dt, unicodedata, difflib, collections, numpy as np
M = json.load(open(sys.argv[1])); TM = {t['id']: t for t in json.load(open(sys.argv[2]))}
P = json.load(open(sys.argv[3]))['pairs']; R = json.load(open(sys.argv[4]))
def ts(s): return dt.datetime.fromisoformat(s).timestamp()
M = [m for m in M if m['t1'] and m['t2'] and m['w'] in (m['t1'], m['t2'])]; M.sort(key=lambda m: m['d'])
elo = collections.defaultdict(lambda: 1500.0); nm = collections.Counter(); hist = collections.defaultdict(list)
ll = []; y_all = []; p_all = []
K0 = 24.0
for m in M:
    a, b = m['t1'], m['t2']; d = elo[a] - elo[b]; p = 1 / (1 + 10 ** (-d / 400)); y = 1.0 if m['w'] == a else 0.0
    if nm[a] >= 10 and nm[b] >= 10: p_all.append(p); y_all.append(y)
    s = abs((m['s1'] or 0) - (m['s2'] or 0)); k = K0 * (1 + 0.25 * min(s, 2))
    elo[a] += k * (y - p); elo[b] -= k * (y - p); nm[a] += 1; nm[b] += 1
    hist[a].append((ts(m['d']), elo[a])); hist[b].append((ts(m['d']), elo[b]))
p = np.clip(np.array(p_all), 1e-4, 1 - 1e-4); y = np.array(y_all)
print('whole history: %d matches with both teams >=10 prior matches; Elo Brier %.4f logloss %.4f (coin 0.25 / 0.693); accuracy %.1f%%' % (len(y), np.mean((p - y) ** 2), -np.mean(y * np.log(p) + (1 - y) * np.log(1 - p)), 100 * np.mean((p > .5) == (y > .5))))
def norm(x):
    x = unicodedata.normalize('NFKD', x or '').encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[^a-z0-9]', '', x)
byname = collections.defaultdict(list)
for t in TM.values(): byname[norm(t['name'])].append(t)
def find(name):
    n = norm(name)
    c = byname.get(n)
    if c: return max(c, key=lambda t: nm[t['id']])
    best = difflib.get_close_matches(n, list(byname), n=1, cutoff=0.88)
    return max(byname[best[0]], key=lambda t: nm[t['id']]) if best else None
def elo_before(tid, t):
    h = hist.get(tid, []); i = 0
    import bisect
    ts_ = [x[0] for x in h]; i = bisect.bisect_left(ts_, t) - 1
    return (h[i][1] if i >= 0 else 1500.0), i + 1
out = {}; miss = 0
for key, p_ in P.items():
    th = find(p_['home']); ta = find(p_['away'])
    t0 = R[key]['meta'].get('t0') or p_.get('match_time')
    t0 = p_.get('match_time') or 0
    if not th or not ta: miss += 1; continue
    eh, nh = elo_before(th['id'], t0 - 3600 * 3); ea, na = elo_before(ta['id'], t0 - 3600 * 3)
    out[key] = dict(elo_h=eh, elo_a=ea, n_h=nh, n_a=na, name_h=th['name'], name_a=ta['name'])
json.dump(out, open(sys.argv[5], 'w'))
print('paired maps with both teams found in bo3:', len(out), 'missing', miss)
