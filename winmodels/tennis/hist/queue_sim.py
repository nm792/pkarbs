"""Tennis Pinnacle/bet365-trigger backtest WITH QUEUE POSITION from recorded PM books (5 Nov 2026).
Usage: python3 queue_sim.py OP_DIR(with hist/) BOOKS.jsonl.gz MARKETS.jsonl.gz   -> out_queue_sim.json
Triggers: book no-vig step >= 1.5pp (OddsPapi createdAt). Bid placed at trigger + ack (drawn from the 30 measured acks)
at tick-floor(mid*0.975) of the side the book moved to; skipped if PM mid already moved >= 50% of the step.
Queue ahead = full displayed size at our price level in the last 1 s snapshot at placement (no cancels assumed = conservative).
Fills from PM prints (data-api) on our token during [place, place+W]: trade below bid fills us; at bid fills after queue
ahead is eaten. Cap 500 sh, hold to resolution. Guard A: ack > 0.3 s -> cancel (no fill)."""
import sys, os, json, gzip, glob, re, bisect, datetime as dt, math
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(os.path.dirname(HERE))); sys.path.insert(0, HERE)
import common as C
OP, BF, MF = sys.argv[1:4]      # BF, MF: comma-separated lists of books / markets files
if os.environ.get('PK_RAW'): C.RAW = os.environ['PK_RAW']      # keep the trades cache off the repo/root disk
OUT = os.environ.get('OUT', f'{HERE}/out_queue_sim.json')
STEP = 0.015; W = 5; CAP = 500; D = 0.025
ACKS = [3.795, .157, .124, .086, 3.576, .222, 1.281, 1.585, .106, .084, .087, .089, .106, .145, .279, .555, .206, .414, .153, .206, .119, .314, .206, .088, .243, .312, .089, .291, .867, .084]
ts = lambda s: dt.datetime.fromisoformat(s.replace('Z', '+00:00')).timestamp()
toks = lambda s: [w for w in re.sub(r'[^a-z ]', ' ', s.lower().replace(',', ' ')).split() if len(w) > 2]
def same(a, b):
    A, B = set(toks(a)), set(toks(b)); return bool(A & B)
mk = {}
def lines(fn):
    return gzip.open(fn, 'rt') if fn.endswith('.gz') else open(fn)
for fn in MF.split(','):
    for l in lines(fn):
        try: r = json.loads(l)
        except Exception: continue
        mk[r['cond']] = r
span = {}       # token -> [first_ts, last_ts]  (pass 1: tiny memory; the full books are streamed twice, never held)
def stream():
    for l in (l for fn in BF.split(',') for l in lines(fn)):
        try: yield json.loads(l)
        except Exception: continue
for r in stream():
    t = r['ms'] / 1000; sp = span.setdefault(r['tk'], [t, t])
    sp[0] = min(sp[0], t); sp[1] = max(sp[1], t)
snaps = {}      # filled in pass 2 for MATCHED tokens only, top 12 levels per side
def book_series(b, flip):
    if '121' not in b['markets']: return []
    ev = sorted((ts(x['createdAt']), oid, x['price'], x['active']) for oid, ov in b['markets']['121']['outcomes'].items() for x in ov['players'].get('0', []))
    cur = {}; out = []
    for t, oid, pr, act in ev:
        if not act: continue
        cur[oid] = pr
        if cur.get('121') and cur.get('122'):
            q = (1 / cur['121']) / (1 / cur['121'] + 1 / cur['122']); out.append((t, 1 - q if flip else q))
    return out
def gamma_win(slug):
    import urllib.request
    try:
        d = json.load(urllib.request.urlopen(f'https://gamma-api.polymarket.com/events?slug={slug}', timeout=20))
        for m in d[0]['markets']:
            if m.get('sportsMarketType') == 'moneyline':
                op = json.loads(m['outcomePrices']); return op[0] == '1' if sorted(op) == ['0', '1'] else None
    except Exception: return None
games = []
for f in glob.glob(f'{OP}/hist/*'):
    d = json.load(gzip.open(f)); fx = d['fixture']
    if fx['sportId'] != 12 or '/' in fx['participant1Name']: continue
    hit = None
    for c, m in mk.items():
        o = m['outcomes']
        if same(fx['participant1Name'], o[0]) and same(fx['participant2Name'], o[1]): hit = (m, False); break
        if same(fx['participant1Name'], o[1]) and same(fx['participant2Name'], o[0]): hit = (m, True); break
    if not hit: continue
    m, flip = hit
    if m['tokens'][0] not in span: continue
    t_lo, t_hi = span[m['tokens'][0]]
    tr = C.pull_trades(m['cond'], t_lo - 600, t_hi + 6 * 3600, 'tennis/queue/trades')
    pr = C.prints(tr)
    win0 = gamma_win(m['slug'])
    if win0 is None and pr: win0 = pr[-1][2] > 0.9 if pr[-1][2] > 0.9 or pr[-1][2] < 0.1 else None
    g = dict(slug=m['slug'], m=m, flip=flip, pr=pr, win0=win0, t_lo=t_lo, t_hi=t_hi,
             books={bk: book_series(d['hist']['bookmakers'][bk], flip) for bk in ('pinnacle', 'bet365') if bk in d['hist']['bookmakers']})
    games.append(g)
print('matches paired with recorded books', len(games), [g['slug'] for g in games])
want = {tk for g in games for tk in g['m']['tokens']}
for r in stream():
    if r['tk'] not in want: continue
    sn = snaps.setdefault(r['tk'], ([], []))
    bids = sorted(((float(x['price']), float(x['size'])) for x in r['bids']), reverse=True)[:12]
    asks = sorted((float(x['price']), float(x['size'])) for x in r['asks'])[:12]
    sn[0].append(r['ms'] / 1000); sn[1].append((bids, asks))
for sn in snaps.values():                 # books of one token arrive in time order per file, but runs are merged: sort
    o = sorted(range(len(sn[0])), key=sn[0].__getitem__); sn[0][:] = [sn[0][i] for i in o]; sn[1][:] = [sn[1][i] for i in o]
del span
def snap_at(tok, T):
    s = snaps[tok]; i = bisect.bisect_right(s[0], T) - 1
    return (s[0][i], s[1][i]) if i >= 0 and T - s[0][i] < 5 else None
def sim(g, bk, ack, rng, guard):
    tot = np.zeros(4); n_orders = 0; filled = 0
    reb = 0
    for (t1, q1), (t2, q2) in zip(g['books'][bk], g['books'][bk][1:]):
        if abs(q2 - q1) < STEP or not (0.03 < q1 < 0.97) or t2 < g['t_lo'] + 10 or t2 > g['t_hi'] - 60: continue
        up = q2 > q1; k = 0 if up else 1; tok = g['m']['tokens'][k]
        a = ack if ack is not None else rng.choice(ACKS)
        if guard and a > 0.3: n_orders += 1; continue
        T = t2 + a; s = snap_at(tok, T); s0 = snap_at(g['m']['tokens'][0], t2 - 2)
        if not s or not s0 or not s[1][0] or not s[1][1]: continue
        bids, asks = s[1]; bb = max(p for p, _ in bids); ba = min(p for p, _ in asks); mid = (bb + ba) / 2
        m0 = snap_at(g['m']['tokens'][0], t2 - 2)[1]; m0 = (max(p for p, _ in m0[0]) + min(p for p, _ in m0[1])) / 2 if m0[0] and m0[1] else None
        if m0 is None or not (0.05 <= mid <= 0.95): continue
        mt0 = (max(p for p, _ in snap_at(g['m']['tokens'][0], T)[1][0]) + min(p for p, _ in snap_at(g['m']['tokens'][0], T)[1][1])) / 2 if snap_at(g['m']['tokens'][0], T) and snap_at(g['m']['tokens'][0], T)[1][0] and snap_at(g['m']['tokens'][0], T)[1][1] else m0
        moved = (mt0 - m0) if up else (m0 - mt0)
        if moved >= 0.5 * abs(q2 - q1): continue
        b = math.floor(mid * (1 - D) * 100 + 1e-9) / 100          # tick 0.01
        if b <= 0.01 or b >= ba: continue
        ahead = sum(sz for p, sz in bids if abs(p - b) < 1e-9)
        n_orders += 1; got = 0; eaten = 0
        for (Tp, _, ph, sell0, sz) in g['pr']:
            if Tp < T: continue
            if Tp > T + W: break
            hits = sell0 if k == 0 else (not sell0); pt = ph if k == 0 else 1 - ph
            if not hits or pt > b + 1e-9: continue
            if pt < b - 1e-9: got += sz                      # traded through: we are filled first
            else:
                eaten += sz
                if eaten > ahead: got += min(sz, eaten - ahead)
            if got >= CAP: break
        q = min(got, CAP)
        if q <= 0 or g['win0'] is None: continue
        won = (g['win0'] == (k == 0)); fs = g['m'].get('fee') or 0
        tot += [q * b, 0, q * ((1.0 if won else 0.0) - b), 0]; filled += 1
    return tot, n_orders, filled
out = {}
for bk in ('pinnacle', 'bet365'):
    gs = [g for g in games if len(g['books'].get(bk, [])) > 20]
    for name, ack, guard in (('ack 0.2s', 0.2, False), ('ack 1.3s', 1.3, False), ('drawn acks, no guard', None, False), ('drawn acks, 0.3 s guard', None, True)):
        rng = np.random.default_rng(1); reps = 1 if ack is not None else 40; res = []
        for _ in range(reps):
            P = []; no = 0; nf = 0
            for g in gs:
                t, o, f = sim(g, bk, ack, rng, guard); P.append(t); no += o; nf += f
            res.append((P, no, nf))
        per = [float(np.sum([p[2] for p in P])) / max(1, len(gs)) for P, _, _ in res]
        P0 = res[0][0]; s = C.summarize(P0) if len(gs) else {}
        k = dict(matches=len(gs), per_match=round(float(np.mean(per)), 2), per_match_range=[round(float(np.percentile(per, 5)), 2), round(float(np.percentile(per, 95)), 2)] if reps > 1 else None,
                 orders=res[0][1], filled_orders=int(np.mean([r[2] for r in res])), usd_filled=round(float(np.sum([p[0] for p in P0]))),
                 ex_top5_per_match=round(s.get('ex_top5_result_usd', 0) / max(1, len(gs) - 5), 2) if len(gs) > 5 else None)
        if len(gs) and reps == 1:
            net = np.array([p[2] for p in P0]); rr = np.random.default_rng(0); bs = [rr.choice(net, len(net)).sum() / len(net) for _ in range(2000)]
            k['ci90_boot'] = [round(float(np.percentile(bs, 5)), 2), round(float(np.percentile(bs, 95)), 2)]
        out[f'{bk} | {name}'] = k; print(bk, name, k, flush=True)
json.dump(out, open(OUT, 'w'), indent=1)
