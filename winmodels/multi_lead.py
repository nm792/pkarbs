"""Bookmaker (Pinnacle / bet365) lead vs Polymarket price, and trigger backtest, for other sports.
Usage: python3 multi_lead.py OP_MULTI_DIR [--probe]
  OP_MULTI_DIR = untarred rn1/scores/oddspapi/multi-2026-11-05 (hist/<sport>_<fid>.json.gz)
Method 1 (lead): cross-correlation of 5 s price changes on a 1 s grid, lags -60..+60 s, pooled per sport;
  placebo = book series shifted by +900 s (should show no peak).
Method 2 (trigger backtest): book step >= 1.5pp -> bid PM at mid-2.5% on that side for W s, order latency
  drawn from the 30 measured Nautilus acks, cancel if no ack in 0.3 s (guard A), skip if moved (sim rule).
Fills are trade-based with queue ignored (optimistic); PM trades have 1 s timestamps."""
import os, sys, json, gzip, glob, re, math, bisect, collections, datetime as dt
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import common as C
OP = sys.argv[1]; PROBE = '--probe' in sys.argv
MW = json.loads(os.environ.get('MW', '{}'))     # sport -> winner market id (filled after --probe)
def ts(s): return dt.datetime.fromisoformat(str(s).replace('Z', '+00:00').replace(' ', 'T')).timestamp()
def toks(s): return [w for w in re.sub(r'[^a-z0-9 ]', ' ', str(s).lower().replace(',', ' ')).split() if len(w) > 2]
def same(a, b):
    A, B = set(toks(a)), set(toks(b))
    return bool(A & B) or any(x[:4] == y[:4] for x in A for y in B if len(x) > 4 and len(y) > 4)

files = sorted(glob.glob(f'{OP}/hist/*.json.gz'))
if PROBE:
    cnt = collections.defaultdict(collections.Counter)
    for f in files:
        d = json.load(gzip.open(f)); sp = d['sport']
        for bk, b in (d['hist'].get('bookmakers') or {}).items():
            for mid, m in (b.get('markets') or {}).items():
                n = sum(len(ov.get('players', {}).get('0', [])) for ov in m.get('outcomes', {}).values())
                cnt[sp][(mid, len(m.get('outcomes', {})))] += n
    for sp, c in cnt.items(): print(sp, len([f for f in files if os.path.basename(f).startswith(sp + '_')]), 'files', c.most_common(12))
    sys.exit()

LAT = np.array([float(r.split(',')[1]) for r in open(os.path.join(os.path.dirname(HERE), 'agent/outbox/nautilus-order-latency-2026-11-05.csv')).read().splitlines()[1:] if r.split(',')[1]])
PM = {sp: json.load(gzip.open(f'{HERE}/raw/multi/gamma_{sp}.json.gz')) for sp in MW}

def book_ser(b, mkt, flip):
    m = b['markets'].get(mkt)
    if not m: return []
    oids = sorted(m['outcomes'])
    if len(oids) != 2: return []
    ev = sorted((ts(x['createdAt']), oid, x['price'], x.get('active', True)) for oid, ov in m['outcomes'].items() for x in ov.get('players', {}).get('0', []))
    cur = {}; out = []
    for t, oid, pr, act in ev:
        if not act or not pr or pr <= 1: continue
        cur[oid] = pr
        if len(cur) == 2:
            q = (1 / cur[oids[0]]) / (1 / cur[oids[0]] + 1 / cur[oids[1]]); out.append((t, 1 - q if flip else q))
    return out

def grid(ser, t0, t1):
    out = []; j = 0; v = None
    for t in range(int(t0), int(t1)):
        while j < len(ser) and ser[j][0] <= t: v = ser[j][1]; j += 1
        out.append(v)
    return out
K, Hs = 60, 5
def xc(pmser, bser, shift=0):
    bser = [(t + shift, q) for t, q in bser]
    t0 = max(pmser[0][0], bser[0][0]); t1 = min(pmser[-1][0], bser[-1][0])
    if t1 - t0 < 600: return None
    a = grid(pmser, t0, t1); b = grid(bser, t0, t1)
    da = np.array([(a[i] - a[i - Hs]) if a[i] is not None and a[i - Hs] is not None else 0 for i in range(Hs, len(a))])
    db = np.array([(b[i] - b[i - Hs]) if b[i] is not None and b[i - Hs] is not None else 0 for i in range(Hs, len(b))])
    na, nb = np.linalg.norm(da), np.linalg.norm(db)
    if na == 0 or nb == 0: return None
    n = len(da); return {k: float(np.dot(da[max(0, -k):n - max(0, k)], db[max(0, k):n - max(0, -k)])) / (na * nb) for k in range(-K, K + 1)}

# --- match fixtures to PM moneylines and load PM trades
games = []
for f in files:
    d = json.load(gzip.open(f)); sp = d['sport']; fx = d['fixture']
    if sp not in MW: continue
    st = ts(fx['startTime']); hit = None
    for e in PM[sp]:
        try: es = ts(e['startTime'])
        except Exception: continue
        if abs(es - st) > 12 * 3600: continue
        for m in e['markets']:
            o = json.loads(m['outcomes'])
            if len(o) != 2: continue
            if same(fx['participant1Name'], o[0]) and same(fx['participant2Name'], o[1]): hit = (e, m, False); break
            if same(fx['participant1Name'], o[1]) and same(fx['participant2Name'], o[0]): hit = (e, m, True); break
        if hit: break
    if not hit: continue
    e, m, flip = hit; op = json.loads(m.get('outcomePrices') or '[]')
    if sorted(op) != ['0', '1']: continue
    tr = C.pull_trades(m['conditionId'], st - 3600, st + 6 * 3600, f'multi/trades_{sp}')
    pr = [p for p in C.prints(tr) if p[0] >= st - 600]
    if len(pr) < 30: continue
    fs = m.get('feeSchedule') or {}; reb = float(fs.get('rebateRate') or 0) * float(fs.get('rate') or 0)
    g = dict(sport=sp, slug=e['slug'], pr=pr, M=C.Mid(pr), win0=op[0] == '1', reb=reb, t0=st, flip=flip,
             books={bk: book_ser(b, MW[sp], flip) for bk, b in (d['hist'].get('bookmakers') or {}).items() if bk in ('pinnacle', 'bet365')})
    tt = sorted(tr, key=lambda z: z['timestamp'])
    g['pmser'] = [(z['timestamp'], z['price'] if z['outcome_index'] == 0 else 1 - z['price']) for z in tt if z['size'] >= 5]
    games.append(g)
print('matched games', collections.Counter(g['sport'] for g in games), flush=True)

# --- guard backtest (same rules as tennis guard_sim)
STEP = 0.015
def triggers(bs):
    return [dict(on=t2, pj=q2 - q1) for (t1, q1), (t2, q2) in zip(bs, bs[1:]) if abs(q2 - q1) >= STEP and 0.03 < q1 < 0.97]
def run_ev(g, E, W, caught=0.5, max_gap=0.01, d=0.025, Q=500):
    tot = np.zeros(4); pr, M = g['pr'], g['M']; E = [e for e in E if not e.get('skip')]; et = [e['on'] for e in E]
    for (T, _, ph, sell0, sz) in pr:
        i = bisect.bisect_right(et, T) - 1; e = None
        while i >= 0 and et[i] >= T - W - 5:
            c = E[i]
            if c['on'] + c['lag'] <= T <= c['on'] + c['lag'] + W: e = c; break
            i -= 1
        if e is None: continue
        tok = 0 if e['pj'] > 0 else 1; mk = M.at(T - C.QDELAY)
        if mk is None or not (0.05 <= mk <= 0.95): continue
        moved = (mk - e['m0']) if tok == 0 else (e['m0'] - mk)
        if moved >= caught * abs(e['pj']): continue
        if tok == 0:
            b = mk * (1 - d)
            if not sell0 or ph >= b - 1e-9 or (b - ph) / b > max_gap: continue
        else:
            b = (1 - mk) * (1 - d)
            if sell0 or (1 - ph) >= b - 1e-9 or (b - (1 - ph)) / b > max_gap: continue
        q = min(sz, Q); m60 = M.at(T + 60); m60 = m60 if tok == 0 else 1 - m60
        out = 1.0 if (g['win0'] == (tok == 0)) else 0.0
        tot += [q * b, q * (m60 - b), q * (out - b), q * g['reb'] * b * (1 - b)]
    return tot

res = {}
for sp in MW:
    gs = [g for g in games if g['sport'] == sp]
    if not gs: continue
    days = max(1.0, (max(g['t0'] for g in gs) - min(g['t0'] for g in gs)) / 86400 + 1)
    for bk in ('pinnacle', 'bet365'):
        G = [g for g in gs if len(g['books'].get(bk, [])) > 20]
        if not G: continue
        agg = collections.defaultdict(float); plc = collections.defaultdict(float); n = 0
        for g in G:
            r = xc(g['pmser'], g['books'][bk]); p = xc(g['pmser'], g['books'][bk], 900)
            if r: n += 1; [agg.__setitem__(k, agg[k] + v) for k, v in r.items()]
            if p: [plc.__setitem__(k, plc[k] + v) for k, v in p.items()]
        lead = None
        if n:
            pk = max(agg, key=agg.get); lead = dict(matches=n, book_lead_s=-pk, peak_corr=round(agg[pk] / n, 3), corr_at_0=round(agg[0] / n, 3),
                corr_book_first_5s=round(agg[-5] / n, 3), corr_book_later_5s=round(agg[5] / n, 3), placebo_peak_corr=round(max(plc.values()) / n, 3) if plc else None)
        bt = {}
        for gname, thr in (('no_guard', 1e9), ('guard_0.3s', 0.3)):
            rows = []
            for k in range(40):
                rng = np.random.default_rng(k); P = []
                for g in G:
                    E = []
                    for e in triggers(g['books'][bk]):
                        m0 = g['M'].at(e['on'] - 2)
                        if m0 is None or not (0.03 < m0 < 0.97): continue
                        l = float(rng.choice(LAT)); E.append(dict(e, m0=m0, lag=l, skip=l > thr))
                    P.append(run_ev(g, E, 5))
                s = C.summarize(P, rng=np.random.default_rng(k), nb=400); nG = len(G)
                rows.append((s['net_result_usd'] / nG, s['ci_result_usd'][0] / nG, s['ci_result_usd'][1] / nG, s.get('ex_top5_result_usd', 0) / nG, sum(1 for p in P if p[0] > 0)))
            a = np.median(np.array(rows, float), axis=0)
            bt[gname] = dict(matches=len(G), per_match=round(a[0], 2), ci90=[round(a[1], 2), round(a[2], 2)], ex_top5_per_match=round(a[3], 2),
                             matches_filled=int(a[4]), matches_per_day_in_sample=round(len(G) / days, 1), per_day_in_sample=round(a[0] * len(G) / days, 0))
        res[f'{sp}/{bk}'] = dict(lead=lead, backtest=bt)
        print(sp, bk, json.dumps(res[f'{sp}/{bk}']), flush=True)
json.dump(res, open(f'{HERE}/out_multi_lead.json', 'w'), indent=1)
