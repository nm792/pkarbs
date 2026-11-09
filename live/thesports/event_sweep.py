#!/usr/bin/env python3
"""EVENT SWEEP (Nick via coordinator, 9 Nov 00:32Z): inventory every TheSports sport/event type in the capture and test
the ones with Polymarket markets against a placebo. DISCOVERY run on pre-cutoff data, not a pre-registered test.
Usage: event_sweep.py SLIMDIR[:SLIMDIR...]   (env: INV=1 inventory only; SPORTS=dota2,csgo,tennis,basketball,lol)
Entry: buy 1 share of the favourable token at best ask at t + 0.2 s (our latency) + 1.0 s (PM sports delay).
Quiet filter: |fav mid(t) - fav mid(t-30)| < 1c and fav mid(t-30) in BAND. Placebo: same event shifted +-60..600 s (30 shifts),
same filters re-checked at the shifted time. Statistic: per-event (real - mean placebo), averaged within match, 90% bootstrap CI over matches."""
import sys, os, json, gzip, glob, bisect, collections, random, statistics, math, re, unicodedata, difflib
DIRS = sys.argv[1].split(':')
DEL = 1.2
BAND = (0.10, 0.90)
rd = lambda p: (json.loads(l) for f in sorted(glob.glob(p, recursive=True)) for l in gzip.open(f, 'rt') if l.strip())
def rdm(s):
    for d in DIRS: yield from rd(d + s)
DI = os.path.join(os.path.dirname(DIRS[0].rstrip('/')), 'diary')
POP = lambda x: bin(int(x)).count('1')

# ---------- names bridge
def norm(x):
    x = unicodedata.normalize('NFKD', x or '').encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[^a-z0-9 ]', ' ', x).split()
def same(a, b):
    na, nb = norm(a), norm(b)
    if not na or not nb: return False
    ja, jb = ' '.join(na), ' '.join(nb)
    return ja == jb or ja in jb or jb in ja or difflib.SequenceMatcher(None, ja.replace(' ', ''), jb.replace(' ', '')).ratio() >= 0.85
names, matches = {}, {}
for f in glob.glob(DI + '/*.json'):
    d = json.load(open(f))
    if 'results' in d:
        for t in d.get('results_extra', {}).get('team', []): names[t['id']] = t['name']
for f in glob.glob(DI + '/*.json'):
    d = json.load(open(f))
    if 'results' in d:
        for m in d['results']: matches[m['id']] = (names.get(m['home_team_id']), names.get(m['away_team_id']))

# ---------- events
SP = {'dota2': 'dota2', 'csgo': 'cs2', 'tennis': 'tennis', 'basketball': 'nba', 'lol': 'lol'}
want = set((os.environ.get('SPORTS') or 'dota2,csgo,tennis,basketball,lol').split(','))
inv = collections.Counter(); invm = collections.defaultdict(set)
ev = collections.defaultdict(list)       # (sport, match, box) -> [(t, side, cls)]  side +1 = home favoured
msgs = sorted((r for r in rdm('/ts_mqtt/**/*.gz')), key=lambda r: r['ms'])
dprev = {}; dkills = collections.defaultdict(list); items_seen = {}; roshan = []; first = set()
for r in msgs:
    sp = r['topic'].split('/')[1]
    inv['msgs ' + sp] += 1
    if sp not in want: continue
    try: ps = json.loads(r['p'])
    except Exception: continue
    t = r['ms'] / 1000.0
    for p in ps:
        if sp == 'dota2':
            key = ('dota2', p['match_id'], p['box_num']); invm['dota2'].add(key)
            h, a = p['home']['stats'], p['away']['stats']
            cur = dict(k=(h[0], a[0]), tw=(POP(h[1]), POP(a[1])), br=(POP(h[2]), POP(a[2])), nw=(h[3], a[3]), ro=p.get('roushan_timer') or 0, st=p.get('status_id'))
            eq = {}
            for sd, tm in ((1, p['home']), (-1, p['away'])):
                for pl in tm.get('players', []):
                    for it in pl.get('equipments', []):
                        if it: eq[(sd, pl['id'], it)] = 1
            if key in dprev:
                pv = dprev[key]
                for i, sd in ((0, 1), (1, -1)):
                    if cur['k'][i] - pv['k'][i] == 1:
                        ev[key].append((t, sd, 'dota kill'))
                        if sum(len(dkills[key]) for _ in [0]) == 0 and sum(pv['k']) == 0: ev[key].append((t, sd, 'dota first blood'))
                        dkills[key].append((t, sd))
                        rec = [x for x in dkills[key] if t - x[0] <= 20 and x[1] == sd]
                        if len(rec) == 3 and cur['k'][i] - pv['k'][i] == 1: ev[key].append((t, sd, 'dota 3 kills in 20 s (teamfight)'))
                for i, sd in ((0, -1), (1, 1)):   # team i lost building -> other side favoured
                    if cur['tw'][i] < pv['tw'][i]: ev[key].append((t, sd, 'dota tower destroyed'))
                    if cur['br'][i] < pv['br'][i]: ev[key].append((t, sd, 'dota barracks destroyed'))
                    if cur['br'][i] == 0 and pv['br'][i] > 0: ev[key].append((t, sd, 'dota all barracks gone (megacreeps)'))
                    if cur['tw'][i] <= 3 and pv['tw'][i] > 3: ev[key].append((t, sd, 'dota team down to <=3 towers'))
                if pv['ro'] == 0 and cur['ro'] > 0: roshan.append((key, t, pv, eq, items_seen.get(key, {})))
                dn = (cur['nw'][0] - cur['nw'][1]); dp = (pv['nw'][0] - pv['nw'][1])
                for thr in (5000, 10000, 20000):
                    if dp < thr <= dn: ev[key].append((t, 1, 'dota NW lead crosses +%dk' % (thr // 1000)))
                    if dp > -thr >= dn: ev[key].append((t, -1, 'dota NW lead crosses +%dk (away)' % (thr // 1000)))
                if dp <= 0 < dn: ev[key].append((t, 1, 'dota NW lead flips'))
                if dp >= 0 > dn: ev[key].append((t, -1, 'dota NW lead flips'))
                if pv['st'] == 2 and cur['st'] != 2:
                    w = 1 if (cur['tw'][1] == 0 or cur['br'][1] == 0) else (-1 if (cur['tw'][0] == 0 or cur['br'][0] == 0) else 0)
                    if w: ev[key].append((t, w, 'dota game ends (feed status change)'))
            items_seen[key] = eq
            dprev[key] = cur
        elif sp == 'csgo':
            key = ('cs2', p['match_id'], p.get('box_num')); invm['cs2'].add(key)
            hs = p['home'].get('side')
            for e in (p.get('event') or []):
                k2 = (key, e['typeid'], e['index'])
                if k2 in first: continue
                first.add(k2); inv['cs2 event typeid %s' % e['typeid']] += 1
                if e['typeid'] == 2 and e.get('winner_side') in (1, 2) and hs in (1, 2): ev[key].append((t, 1 if e['winner_side'] == hs else -1, 'cs2 round end wintype %s' % e.get('wintype')))
                if e['typeid'] == 8 and e.get('killerside') in (1, 2) and hs in (1, 2):
                    ev[key].append((t, 1 if e['killerside'] == hs else -1, 'cs2 kill headshot' if e.get('headshot') else 'cs2 kill'))
        elif sp == 'basketball': invm['nba'].add(p.get('id'))
        elif sp == 'tennis':
            invm['tennis'].add(p.get('id')); key = ('tennis', p.get('id'), 0)
            fm = ('tn', p.get('id')) not in first; first.add(('tn', p.get('id')))
            RK = {'0': 0, '15': 1, '30': 2, '40': 3, 'AD': 4, 'A': 4}
            def rk(x):
                return RK[x] if x in RK else (int(x) if str(x).isdigit() else None)
            for st_ in (p.get('timeline') or []):
                prv = (0, 0); prvsrv = None
                for rd_ in st_.get('rounds', []):
                    pts = rd_.get('points') or []; sc = rd_.get('score')
                    tb = prv == (6, 6)
                    srv = (3 - prvsrv) if (prvsrv and not tb) else None      # 1 home serves, 2 away
                    trans = []
                    for i in range(1, len(pts)):
                        k2 = ('pt', p['id'], st_['set'], rd_['round'], i)
                        if k2 in first: continue
                        first.add(k2)
                        a_, b_, c_, d_ = rk(pts[i-1][0]), rk(pts[i-1][1]), rk(pts[i][0]), rk(pts[i][1])
                        if None in (a_, b_, c_, d_): continue
                        w = 1 if (c_ > a_ and d_ <= b_) or (d_ < b_) else (-1 if (d_ > b_ and c_ <= a_) or (c_ < a_) else 0)
                        if w: trans.append((w, a_, b_, 'listed'))
                    if sc:
                        k3 = ('gm', p['id'], st_['set'], rd_['round'])
                        if k3 not in first:
                            first.add(k3)
                            cur = (sc.get('home', 0), sc.get('away', 0)); dh, da = cur[0] - prv[0], cur[1] - prv[1]
                            if dh >= 0 and da >= 0 and dh + da == 1:
                                lp = pts[-1] if pts else ['0', '0']
                                a_, b_ = rk(lp[0]), rk(lp[1])
                                if None not in (a_, b_): trans.append((1 if dh else -1, a_, b_, 'decisive'))
                        srv = sc.get('serve') if sc.get('serve') in (1, 2) else srv
                    if not fm:
                        for w, a_, b_, kind in trans:
                            ev[key].append((t, w, 'tennis any point (%s)' % kind))
                            gp = lambda x, o: (x >= 6 and x - o >= 1) if tb else ((x == 3 and o < 3) or x == 4)
                            gh, ga = prv
                            spt = lambda x, o, gx, go: gp(x, o) and (tb or (gx == 5 and go <= 4) or (gx == 6 and go == 5))
                            hsp, asp = spt(a_, b_, gh, ga), spt(b_, a_, ga, gh)
                            if hsp or asp:
                                x = 1 if hsp else -1
                                ev[key].append((t, w, 'tennis set point converted (%s)' % kind if w == x else 'tennis set point saved (%s)' % kind))
                            if srv and not tb:
                                ret = 1 if srv == 2 else -1
                                rgp = gp(a_, b_) if ret == 1 else gp(b_, a_)
                                if rgp:
                                    ev[key].append((t, w, 'tennis break point converted (%s)' % kind if w == ret else 'tennis break point saved (%s)' % kind))
                            if tb: ev[key].append((t, w, 'tennis tiebreak point (%s)' % kind))
                    if sc: prv = (sc.get('home', 0), sc.get('away', 0)); prvsrv = sc.get('serve') if sc.get('serve') in (1, 2) else prvsrv
        elif sp == 'lol':
            key = ('lol', p['match_id'], p['box_num']); invm['lol'].add(key)
            for e in (p.get('event') or []):
                k2 = (key, e['type'], e['time'], e['killer'])
                if k2 in first: continue
                first.add(k2); inv['lol event type %s' % e['type']] += 1
                if key not in firstl if False else True:
                    ev[key].append((t, 1 if e['side'] == 1 else -1, 'lol event type %s' % e['type']))
# Roshan side = team whose player newly holds one item (the aegis) that appears in no other prior inventory; learn aegis id by vote
vote = collections.Counter(); cand = []
for key, t, pv, eq, before in roshan:
    cand.append((key, t))
print('INVENTORY (messages per sport, distinct games/matches, event-type counts)')
for k, v in sorted(inv.items()): print('  %-34s %d' % (k, v))
for k, v in sorted(invm.items()): print('  distinct %-12s %d' % (k, len(v)))
cnt = collections.Counter(c for evs in ev.values() for _, _, c in evs)
for k, v in sorted(cnt.items()): print('  events %-44s %d' % (k, v))
print('  dota roshan timer starts (side by aegis vote below): %d' % len(roshan))
if os.environ.get('INV'): sys.exit()
# aegis vote: item ids that appear in exactly one holder's inventory right after a roshan start but were absent before
after = {}
for r in msgs:
    pass
# (second pass: collect inventories 0-20 s after each roshan start)
rs_by = collections.defaultdict(list)
for key, t, pv, eq, before in roshan: rs_by[key].append((t, before))
post = {}
for r in msgs:
    if not r['topic'].endswith('dota2/match/v1'): continue
    t = r['ms'] / 1000.0
    try: ps = json.loads(r['p'])
    except Exception: continue
    for p in ps:
        key = ('dota2', p['match_id'], p['box_num'])
        for t0, before in rs_by.get(key, []):
            if 0 <= t - t0 <= 25 and (key, t0) not in post:
                eq = {}
                for sd, tm in ((1, p['home']), (-1, p['away'])):
                    for pl in tm.get('players', []):
                        for it in pl.get('equipments', []):
                            if it: eq[(sd, pl['id'], it)] = 1
                new = [k for k in eq if k not in before]
                post[(key, t0)] = new
                if len(new) >= 1:
                    for (sd, pid, it) in new: vote[it] += 1
aegis = [i for i, n in vote.most_common(1)]
print('  aegis item vote top:', vote.most_common(3))
for (key, t0), new in post.items():
    if aegis:
        s = [sd for sd, pid, it in new if it == aegis[0]]
        if len(s) == 1: ev[key].append((t0, s[0], 'dota roshan killed (aegis side)'))

# ---------- markets, books, pairing
mk = {m['cond']: m for m in rdm('/markets.jsonl.gz')}
tk_sport = {t: (m['sport'], m['q'], m['smt']) for m in mk.values() for t in m['tokens']}
book = collections.defaultdict(list)
for r in rdm('/books_mid/**/*.gz'):
    if r['tk'] in tk_sport and tk_sport[r['tk']][0] in ('dota2', 'cs2', 'lol', 'tennis'): book[r['tk']].append((r['ms'] / 1000.0, r['bb'], r['ba']))
T = {}
for k in book: book[k].sort(); T[k] = [x[0] for x in book[k]]
partner = {}
for m in mk.values():
    if len(m['tokens']) == 2: partner[m['tokens'][0]] = m['tokens'][1]; partner[m['tokens'][1]] = m['tokens'][0]
def row(tk, t, maxage=15):
    ts = T.get(tk)
    if not ts: return None
    i = bisect.bisect_right(ts, t) - 1
    return book[tk][i] if i >= 0 and t - ts[i] < maxage else None
def mid(tk, t):
    r = row(tk, t); return None if not r else (r[1] + r[2]) / 2
def settle(tk):
    r = book[tk][-1]; m = (r[1] + r[2]) / 2
    return 1.0 if m >= 0.95 else (0.0 if m <= 0.05 else None)
pair = {}
for key in ev:
    hm = matches.get(key[1])
    if not hm or None in hm: continue
    for tk, (sp, q, smt) in tk_sport.items():
        if tk not in book or sp != key[0]: continue
        if key[0] == 'dota2' and ('Game %d Winner' % key[2]) not in q: continue
        if key[0] == 'lol' and ('Game %d ' % key[2]) not in q: continue
        if key[0] == 'cs2' and ('Map %s Winner' % key[2]) not in q: continue
        if key[0] == 'tennis' and smt != 'moneyline': continue
        m = [m_ for m_ in mk.values() if tk in m_['tokens']][0]
        i = m['tokens'].index(tk); o, po = m['outcomes'][i], m['outcomes'][1 - i]
        if same(hm[0], o) and same(hm[1], po): pair[key] = (tk, 1); break
        if same(hm[1], o) and same(hm[0], po): pair[key] = (tk, -1); break
print('paired games to PM game-winner token: %d of %d games with events' % (len(pair), len(ev)))
def fav(tk, sg, side):
    f = tk if side * sg > 0 else partner.get(tk)
    return f if f in book else None
def ent(f, t):
    """returns dict of payoffs or None if filters fail at time t"""
    a, b = mid(f, t), mid(f, t - 30)
    if a is None or b is None or abs(a - b) >= 0.01 or not (BAND[0] <= b < BAND[1]): return None
    e = row(f, t + DEL)
    if not e or e[2] - e[1] > 0.05 or e[2] >= 0.99: return None
    out = {}
    m60 = row(f, t + DEL + 60); b30 = row(f, t + DEL + 30)
    if m60: out['mtm60'] = (m60[1] + m60[2]) / 2 - e[2]
    if b30: out['exit30'] = b30[1] - e[2]
    s = settle(f)
    if s is not None: out['hold'] = s - e[2]
    out['ask'] = e[2]
    return out
def boot(vals, n=2000):
    ms = list(vals)
    if len(ms) < 3: return None
    d = sorted(sum(random.choice(ms) for _ in ms) / len(ms) for _ in range(n))
    return d[int(.05 * n)], d[int(.95 * n)]
random.seed(5)
classes = collections.defaultdict(list)
for key, evs in ev.items():
    if key not in pair: continue
    tk, sg = pair[key]
    for t, sd, c in evs:
        if sd == 0: continue
        c = re.sub(r' \(away\)', '', c); classes[c].append((key, t, sd, tk, sg))
rows = []
for c, L in sorted(classes.items()):
    res = {}
    for k in ('mtm60', 'exit30', 'hold'):
        per = collections.defaultdict(list); n = 0
        for key, t, sd, tk, sg in L:
            f = fav(tk, sg, sd)
            if not f: continue
            real = ent(f, t)
            if not real or k not in real: continue
            pl = []
            for _ in range(30):
                x = ent(f, t + random.choice([-1, 1]) * random.uniform(60, 600))
                if x and k in x: pl.append(x[k])
            if len(pl) < 3: continue
            per[key[1]].append(real[k] - sum(pl) / len(pl)); n += 1
        ms = [sum(v) / len(v) for v in per.values()]
        res[k] = (n, len(ms), (100 * sum(ms) / len(ms)) if ms else None, boot(ms))
    # lead: signed move before/after message, real vs placebo (all events, no quiet filter)
    mv = lambda f, t, a, b: (None if mid(f, t + a) is None or mid(f, t + b) is None else mid(f, t + b) - mid(f, t + a))
    lead = {}
    for lab, shift in (('real', False), ('placebo', True)):
        for a, b in ((-30, 0), (0, 10), (10, 60)):
            v = []
            for key, t, sd, tk, sg in L:
                f = fav(tk, sg, sd)
                if not f: continue
                for _ in range(1 if not shift else 5):
                    tt = t + (random.choice([-1, 1]) * random.uniform(60, 600) if shift else 0)
                    m0 = mid(f, tt - 30)
                    if m0 is None or not (BAND[0] <= m0 < BAND[1]): continue
                    x = mv(f, tt, a, b)
                    if x is not None: v.append(x)
            lead[(lab, a, b)] = (100 * sum(v) / len(v), len(v)) if v else None
    rows.append((c, len(L), res, lead))
print('\nRESULT per event class (cents per share; diff = real minus placebo; 90%% match-clustered CI; band %.2f-%.2f)' % BAND)
nt = 0
for c, n, res, lead in rows:
    print('\n== %s | events %d' % (c, n))
    for k in ('mtm60', 'exit30', 'hold'):
        nn, nm, d, ci = res[k]
        print('   %-7s n=%d matches=%d diff %s CI %s' % (k, nn, nm, ('%+.2fc' % d) if d is not None else 'n/a', ('[%+.2f, %+.2f]' % (100 * ci[0], 100 * ci[1])) if ci else 'n/a'))
    print('   signed move real [-30,0] %s | [0,10] %s | [10,60] %s' % tuple(('%+.2fc(n%d)' % lead[('real', a, b)]) if lead[('real', a, b)] else 'n/a' for a, b in ((-30, 0), (0, 10), (10, 60))))
    print('   signed move plac [-30,0] %s | [0,10] %s | [10,60] %s' % tuple(('%+.2fc(n%d)' % lead[('placebo', a, b)]) if lead[('placebo', a, b)] else 'n/a' for a, b in ((-30, 0), (0, 10), (10, 60))))

if os.environ.get('ATTR'):
    print('\nATTRITION (tower/barracks/roshan/kill): stage counts')
    for c in ('dota tower destroyed', 'dota barracks destroyed', 'dota roshan killed (aegis side)', 'dota kill'):
        st = collections.Counter()
        for key, t, sd, tk, sg in classes.get(c, []):
            f = fav(tk, sg, sd); st['paired events'] += 1
            if not f: st['no fav book'] += 1; continue
            a, b = mid(f, t), mid(f, t - 30)
            if a is None or b is None: st['no mid at t or t-30 (book stale >15s)'] += 1; continue
            if abs(a - b) >= 0.01: st['price moved >=1c before msg'] += 1; continue
            if not (BAND[0] <= b < BAND[1]): st['outside band'] += 1; continue
            e = row(f, t + DEL)
            if not e: st['no row at entry'] += 1; continue
            if e[2] - e[1] > 0.05: st['spread>5c'] += 1; continue
            if e[2] >= 0.99: st['ask>=.99'] += 1; continue
            st['QUALIFY'] += 1
        print(' ', c, dict(st))
    unp = [k for k in ev if k not in pair]
    why = collections.Counter()
    for k in unp:
        if not matches.get(k[1]) or None in matches[k[1]]: why['no team names in diary'] += 1
        else: why['names found but no PM %s market with these teams/game no.' % k[0]] += 1
    print('unpaired games:', dict(why))

if os.environ.get('ATTR'):
    print('\nPRICE-LEADS CHECK: share of events where fav mid already moved FAVOURABLY by >=2c over [t-30,t] (real vs placebo same band), and median signed move [t-30,t+60]')
    for c in ('dota tower destroyed', 'dota barracks destroyed', 'dota roshan killed (aegis side)', 'dota kill', 'dota first blood', 'dota NW lead flips'):
        res = {}
        for lab in ('real', 'plac'):
            n = k = 0; tot = []
            for key, t, sd, tk, sg in classes.get(c, []):
                f = fav(tk, sg, sd)
                if not f: continue
                for _ in range(1 if lab == 'real' else 10):
                    tt = t if lab == 'real' else t + random.choice([-1, 1]) * random.uniform(60, 600)
                    a, b, z = mid(f, tt - 30), mid(f, tt), mid(f, tt + 60)
                    if a is None or b is None or z is None or not (BAND[0] <= a < BAND[1]): continue
                    n += 1; k += (b - a >= 0.02); tot.append(z - a)
            res[lab] = (n, 100 * k / n if n else float('nan'), 100 * statistics.median(tot) if tot else float('nan'))
        print('  %-36s real n=%d moved-before %.0f%% median[-30,+60] %+.1fc | placebo n=%d %.0f%% %+.1fc' % ((c,) + res['real'] + res['plac']))

if os.environ.get('TIMING'):
    # fine timing: mean signed fav-mid move in short windows around the message, real vs placebo, by band of fav mid at t-30
    WIN = [(-30, -20), (-20, -10), (-10, -5), (-5, -2), (-2, 0), (0, 1.2), (1.2, 3), (3, 10), (10, 30), (30, 60)]
    BANDS = [('all 10-90', 0.10, 0.90), ('25-75', 0.25, 0.75), ('40-60', 0.40, 0.60)]
    random.seed(21)
    for c in [k for k in sorted(classes) if k.startswith('tennis') and ('decisive' in k or 'listed' in k)]:
        L = classes[c]
        print('\n== TIMING %s | events %d' % (c, len(L)))
        for bn, lo, hi in BANDS:
            for lab in ('real', 'placebo'):
                out = []
                for a, b in WIN:
                    v = []
                    for key, t, sd, tk, sg in L:
                        f = fav(tk, sg, sd)
                        if not f: continue
                        for _ in range(1 if lab == 'real' else 8):
                            tt = t if lab == 'real' else t + random.choice([-1, 1]) * random.uniform(60, 600)
                            m0 = mid(f, tt - 30); x, y = mid(f, tt + a), mid(f, tt + b)
                            if m0 is None or x is None or y is None or not (lo <= m0 < hi): continue
                            v.append(y - x)
                    out.append('%+.2f(n%d)' % (100 * sum(v) / len(v), len(v)) if v else 'n/a')
                print('  %-9s %-7s %s' % (bn, lab, ' '.join('[%g,%g]%s' % (a, b, o) for (a, b), o in zip(WIN, out))))

if os.environ.get('FAVTEST'):
    # Nick 9 Nov 00:54Z: the favourite rule (T1: quiet, point winner's token mid in 0.40-0.60, buy ask at t+1.2, hold to resolution)
    # split by point-message class and by whether the point winner is the favourite (mid at t-30 >= 0.50).
    BAND = (0.40, 0.60); random.seed(33)
    def ent_h(f, t):
        a, b = mid(f, t), mid(f, t - 30)
        if a is None or b is None or abs(a - b) >= 0.01 or not (0.40 <= b < 0.60): return None
        e = row(f, t + DEL)
        if not e or e[2] - e[1] > 0.05 or e[2] >= 0.99: return None
        S = settle(f)
        return None if S is None else (S - e[2], b)
    def run(L, pred=lambda b: True, NP=30):
        per = collections.defaultdict(list)
        for key, t, sd, tk, sg in L:
            if t < float(os.environ.get('PREREG_AFTER', '0')): continue
            f = fav(tk, sg, sd)
            if not f: continue
            r0 = ent_h(f, t)
            if not r0 or not pred(r0[1]): continue
            pl = []
            for _ in range(NP):
                x = ent_h(f, t + random.choice([-1, 1]) * random.uniform(60, 600))
                if x and pred(x[1]): pl.append(x[0])
            if len(pl) < 3: continue
            per[key[1]].append((r0[0], sum(pl) / len(pl)))
        return per
    def summ(per):
        ms = [(sum(a for a, _ in v) / len(v), sum(b for _, b in v) / len(v)) for v in per.values()]
        if len(ms) < 3: return 'n=%d events, %d matches (too few)' % (sum(len(v) for v in per.values()), len(ms))
        d = [a - b for a, b in ms]; n = len(d)
        bs = sorted(sum(random.choice(d) for _ in d) / n for _ in range(1500))
        return 'events %d matches %d | real %+.1fc placebo %+.1fc diff %+.1fc 90%% CI [%+.1f, %+.1f]' % (sum(len(v) for v in per.values()), n, 100 * sum(a for a, _ in ms) / n, 100 * sum(b for _, b in ms) / n, 100 * sum(d) / n, 100 * bs[75], 100 * bs[1424])
    tpk = lambda kinds: [x for c, L in classes.items() for x in L if c.startswith('tennis any point') and any(k in c for k in kinds)]
    print('\n=== FAVOURITE RULE (quiet, winner token 0.40-0.60, buy ask t+1.2, HOLD to resolution; real - placebo; cluster = match) ===')
    allpts = tpk(['listed', 'decisive'])
    fv = lambda b: b >= 0.50; dg = lambda b: b < 0.50
    for lab, L in (('ALL point messages', allpts), ('listed points only', tpk(['listed'])), ('decisive point (game-score message) only', tpk(['decisive']))):
        print('\n## %s' % lab)
        for sl, pr in (('winner token 0.40-0.60', lambda b: True), ('winner is FAVOURITE (0.50-0.60)', fv), ('winner is UNDERDOG (0.40-0.50)', dg)):
            print('   %-34s %s' % (sl, summ(run(L, pr))))
    print('\n## by point class (winner token 0.40-0.60; favourite/underdog split)')
    for c in sorted(classes):
        if not c.startswith('tennis') or c.startswith('tennis any'): continue
        L = classes[c]
        for sl, pr in (('any', lambda b: True), ('fav wins', fv), ('dog wins', dg)):
            print('   %-48s %-9s %s' % (c, sl, summ(run(L, pr))))
    # does a class add value beyond the rule? within the rule: class events vs all OTHER point events of the same matches
    print('\n## incremental: class minus rest-of-points (same rule), per-match difference')
    restkey = lambda L: set((x[0][1], round(x[1], 1)) for x in L)
    base = run(allpts)
    for c in sorted(classes):
        if not c.startswith('tennis') or c.startswith('tennis any'): continue
        cls = run(classes[c])
        ms = [m for m in cls if m in base]
        if len(ms) < 5: print('   %-48s too few shared matches (%d)' % (c, len(ms))); continue
        d = []
        for m in ms:
            ca = sum(a - b for a, b in cls[m]) / len(cls[m]); ba = sum(a - b for a, b in base[m]) / len(base[m]); d.append(ca - ba)
        bs = sorted(sum(random.choice(d) for _ in d) / len(d) for _ in range(1500))
        print('   %-48s matches %d | class minus all-points diff %+.1fc 90%% CI [%+.1f, %+.1f]' % (c, len(d), 100 * sum(d) / len(d), 100 * bs[75], 100 * bs[1424]))

if os.environ.get('UNDERDOG'):
    # U1/U2 (see reviews/PREREG-thesports-underdog-2026-11-09.md). Tennis in-play = between first and last TheSports message of the match.
    AFTER = float(os.environ.get('PREREG_AFTER', '0')); random.seed(44)
    span = {}
    for r in msgs:
        if not r['topic'].endswith('tennis/match/v1'): continue
        try: ps = json.loads(r['p'])
        except Exception: continue
        for p_ in ps:
            a_ = span.setdefault(p_['id'], [r['ms'] / 1000.0, r['ms'] / 1000.0]); a_[1] = r['ms'] / 1000.0
    u1 = collections.defaultdict(list); u2 = {}
    for key in sorted(k for k in pair if k[0] == 'tennis'):
        if key[1] not in span: continue
        tk, sg = pair[key]; t0, t1 = span[key[1]]
        for f in (tk, partner.get(tk)):
            if not f or f not in book: continue
            S = settle(f)
            if S is None: continue
            first_in = None; t = t0 + 60
            while t < t1 - 60:
                if t >= AFTER:
                    m = mid(f, t)
                    if m is not None and 0.40 <= m < 0.50:
                        e = row(f, t + 1.0)
                        if e and e[2] - e[1] <= 0.05 and e[2] < 0.99:
                            u1[key[1]].append(S - e[2])
                            if first_in is None: first_in = S - e[2]
                t += 60
            if first_in is not None: u2.setdefault(key[1], []).append(first_in)
    def ci(d):
        ms = [sum(v) / len(v) for v in d.values()]
        if len(ms) < 3: return 'matches %d (too few)' % len(ms)
        n = len(ms); bs = sorted(sum(random.choice(ms) for _ in ms) / n for _ in range(2000))
        p1 = sum(1 for b in bs if b <= 0) / len(bs)
        return 'matches %d | mean per match %+.1fc | 90%% CI [%+.1f, %+.1f] | one-sided boot p(<=0) %.3f | matches with +payoff %d' % (n, 100 * sum(ms) / n, 100 * bs[100], 100 * bs[1899], p1, sum(1 for m in ms if m > 0))
    print('\n=== UNDERDOG (token mid 0.40-0.50, in play, 60 s grid, buy ask at +1 s, hold to resolution; benchmark 0 = fair price); events at/after %s ===' % AFTER)
    print('U1 every grid time  :', ci(u1), '| entries', sum(len(v) for v in u1.values()))
    print('U2 first time in band (per token per match):', ci(u2))
    if os.environ.get('UDBG'):
        vals = sorted((round(100 * sum(v) / len(v), 1), len(v)) for v in u2.values())
        print('U2 per-match (mean c, n tokens):', vals)

if os.environ.get('SELECT'):
    # diagnostic (no rule): underdog (token mid 0.40-0.50) win rate vs implied price, T1-style entries vs any-time entries, by distinct match-token
    from math import comb
    def pbin(k, n, p): return sum(comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k, n + 1))
    A = {}   # T1-style: after a point the token's side won, quiet, mid(t-30) in .40-.50, listed+decisive
    for c, L in classes.items():
        if not c.startswith('tennis any point'): continue
        for key, t, sd, tk, sg in L:
            f = fav(tk, sg, sd)
            if not f: continue
            a, b = mid(f, t), mid(f, t - 30)
            if a is None or b is None or abs(a - b) >= 0.01 or not (0.40 <= b < 0.50): continue
            e = row(f, t + DEL); S = settle(f)
            if not e or S is None or e[2] - e[1] > 0.05 or e[2] >= 0.99: continue
            A.setdefault((key[1], f), []).append((S, e[2]))
    span = {}
    for r in msgs:
        if not r['topic'].endswith('tennis/match/v1'): continue
        try: ps = json.loads(r['p'])
        except Exception: continue
        for p_ in ps:
            a_ = span.setdefault(p_['id'], [r['ms'] / 1000.0, r['ms'] / 1000.0]); a_[1] = r['ms'] / 1000.0
    B = {}
    for key in sorted(k for k in pair if k[0] == 'tennis'):
        if key[1] not in span: continue
        tk, sg = pair[key]; t0, t1 = span[key[1]]
        for f in (tk, partner.get(tk)):
            if not f or f not in book: continue
            S = settle(f)
            if S is None: continue
            t = t0 + 60
            while t < t1 - 60:
                m = mid(f, t)
                if m is not None and 0.40 <= m < 0.50:
                    e = row(f, t + 1.0)
                    if e and e[2] - e[1] <= 0.05 and e[2] < 0.99: B.setdefault((key[1], f), []).append((S, e[2]))
                t += 60
            pass
    def rep(name, D):
        ent = [x for v in D.values() for x in v]
        units = [(sum(s for s, _ in v) / len(v), sum(a for _, a in v) / len(v)) for v in D.values()]
        mt = set(m for m, _ in D)
        W = sum(1 for s, _ in units if s >= 0.5); n = len(units); pa = sum(a for _, a in units) / n
        print('%-44s matches %d | match-tokens %d | entries %d | mean ask %.3f | entry win rate %.1f%% | match-token win rate %.1f%% (%d/%d) vs implied %.1f%% | binomial p(wins>=obs | price) %.3f' % (name, len(mt), n, len(ent), sum(a for _, a in ent) / len(ent), 100 * sum(s for s, _ in ent) / len(ent), 100 * W / n, W, n, 100 * pa, pbin(W, n, pa)))
        return mt
    print('\n=== SELECTION DIAGNOSTIC: underdog 0.40-0.50 win rate vs implied price ===')
    ma = rep('A: after a point it won (T1 underdog half)', A)
    mb = rep('B: any in-play time, 60 s grid (U1)', B)
    print('matches in A:%d, in B:%d, A inside B:%d' % (len(ma), len(mb), len(ma & mb)))
    Bo = {k: v for k, v in B.items() if k[0] not in ma}
    rep('B restricted to matches NOT in A', Bo)
    Bi = {k: v for k, v in B.items() if k[0] in ma}
    rep('B restricted to the A matches', Bi)

if os.environ.get('LEAD'):
    # Does the TheSports message LEAD the PM price? For each class: share of the favourite's total move over [t-60, t+60] that is already done at the message
    # (price-led share = (mid(t)-mid(t-60)) / (mid(t+60)-mid(t-60)), pooled as ratio of sums over events with |total|>=2c), real vs placebo (shifted 60-600 s, 5 per event),
    # 90% bootstrap CI over matches. Share > 0.5 => price moved first; ~0 => message first.
    random.seed(66); MINMOVE = 0.02
    def ratio(items):
        num = sum(a for _, a, _ in items); den = sum(b for _, _, b in items)
        return None if den <= 0 else num / den
    print('\n=== LEAD: share of the [-60,+60] favourable move already in the price at the message (1.00 = price fully led, 0.00 = message first) ===')
    for c, L in sorted(classes.items()):
        res = {}
        for lab in ('real', 'placebo'):
            byk = collections.defaultdict(list)
            for key, t, sd, tk, sg in L:
                f = fav(tk, sg, sd)
                if not f: continue
                for _ in range(1 if lab == 'real' else 5):
                    tt = t if lab == 'real' else t + random.choice([-1, 1]) * random.uniform(60, 600)
                    a, b, z = mid(f, tt - 60), mid(f, tt), mid(f, tt + 60)
                    if None in (a, b, z) or not (0.05 <= a <= 0.95) or z - a < MINMOVE: continue
                    byk[key[1]].append((key[1], b - a, z - a))
            items = [x for v in byk.values() for x in v]; ms = list(byk)
            if len(ms) < 3 or not items: res[lab] = None; continue
            r0 = ratio(items); bs = []
            for _ in range(1000):
                pick = [random.choice(ms) for _ in ms]; r = ratio([x for m in pick for x in byk[m]])
                if r is not None: bs.append(r)
            bs.sort()
            res[lab] = (r0, bs[50], bs[949], len(items), len(ms))
        f_ = lambda r: 'n/a (too few)' if not r else '%.2f [%.2f, %.2f] events %d matches %d' % r
        print('%-52s real %s | placebo %s' % (c, f_(res['real']), f_(res['placebo'])))
