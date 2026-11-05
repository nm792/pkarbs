"""Cross-correlation lead test: at which lag do book price changes best line up with PM price changes?
Uses 1 s grids, 5 s increments, lags -60..+60 s. Peak at negative lag = book moves first.
Inputs: OUT_DIR from lead.py (pmtrades/), OP_DIR, plus CS2 PM books for a calibration match.
Usage: python3 xcorr.py OP_DIR LEAD_OUT_DIR GAMMA_TENNIS CS2_DIR
"""
import gzip, json, glob, sys, re, os, bisect, math, datetime as dt, collections
sys.argv += []
OP, LO, GT, CS = sys.argv[1:5]
sys.path.insert(0, os.path.dirname(__file__))
def ts(s): return dt.datetime.fromisoformat(s.replace('Z', '+00:00')).timestamp()
def toks(s): return [w for w in re.sub(r'[^a-z ]', ' ', s.lower().replace(',', ' ')).split() if len(w) > 2]
def same(a, b):
    A, B = set(toks(a)), set(toks(b))
    return bool(A & B) or any(x[:4] == y[:4] for x in A for y in B if len(x) > 4 and len(y) > 4)
MW = {12: '121', 17: '171', 18: '1821'}
K, H = 60, 5

def grid(ser, t0, t1):
    ser = sorted(ser); out = []; j = 0; v = None
    for t in range(int(t0), int(t1)):
        while j < len(ser) and ser[j][0] <= t: v = ser[j][1]; j += 1
        out.append(v)
    return out

def book_ser(b, mkt, flip):
    alt = str(int(mkt) + 1); cur = {}; out = []
    ev = sorted((ts(x['createdAt']), oid, x['price'], x['active']) for oid, ov in b['markets'][mkt]['outcomes'].items() for x in ov['players'].get('0', []))
    for t, oid, pr, act in ev:
        if not act: continue
        cur[oid] = pr
        if cur.get(mkt) and cur.get(alt):
            q = (1 / cur[mkt]) / (1 / cur[mkt] + 1 / cur[alt]); out.append((t, 1 - q if flip else q))
    return out

def xc(pmser, bser):
    t0 = max(pmser[0][0], bser[0][0]); t1 = min(pmser[-1][0], bser[-1][0])
    if t1 - t0 < 600: return None
    a = grid(pmser, t0, t1); b = grid(bser, t0, t1)
    da = [(a[i] - a[i - H]) if a[i] is not None and a[i - H] is not None else 0 for i in range(H, len(a))]
    db = [(b[i] - b[i - H]) if b[i] is not None and b[i - H] is not None else 0 for i in range(H, len(b))]
    n = len(da); acc = {}
    for k in range(-K, K + 1):   # corr(PM change at t, book change at t+k)
        s = 0.0
        for i in range(max(0, -k), min(n, n - k)): s += da[i] * db[i + k]
        acc[k] = s
    na = math.sqrt(sum(x * x for x in da)); nb = math.sqrt(sum(x * x for x in db))
    if na == 0 or nb == 0: return None
    return {k: v / (na * nb) for k, v in acc.items()}

pm = []
for e in json.load(gzip.open(GT)):
    if re.search(r'2026-11-0[45]$', e['slug']):
        for m in e['markets']:
            if m.get('sportsMarketType') == 'moneyline': pm.append((json.loads(m['outcomes']), m['conditionId'], 12))
for l in gzip.open(f'{CS}/markets.jsonl.gz', 'rt'):
    m = json.loads(l)
    if m['kind'] == 'Match Winner': pm.append((m['outcomes'], m['cond'], 17, m['tokens'][0]))
pm.append((['Gen.G', 'LYON'], '0xffb12fd0acd3b1015ea0cf57713715414b17ea694c9de7ac567643fb02a5ecdd', 18))

# CS2 PM books (1 s) for calibration
want = {p[3]: p for p in pm if len(p) > 3}
bk_mid = collections.defaultdict(list)
for l in gzip.open(f'{CS}/books.jsonl.gz', 'rt'):
    b = json.loads(l)
    if b['asset'] in want and b['bids'] and b['asks']:
        bb = max(float(x['price']) for x in b['bids']); ba = min(float(x['price']) for x in b['asks'])
        if ba - bb <= 0.1: bk_mid[b['asset']].append((b['recv_ms'] / 1000, (bb + ba) / 2))

agg = collections.defaultdict(lambda: collections.defaultdict(float)); cnt = collections.Counter(); per = []
for f in glob.glob(f'{OP}/hist/*'):
    d = json.load(gzip.open(f)); fx = d['fixture']; sp = fx['sportId']
    if sp not in MW or '/' in fx['participant1Name']: continue
    hit = None
    for p in pm:
        if p[2] != sp: continue
        o = p[0]
        if same(fx['participant1Name'], o[0]) and same(fx['participant2Name'], o[1]): hit = (p, False); break
        if same(fx['participant1Name'], o[1]) and same(fx['participant2Name'], o[0]): hit = (p, True); break
    if not hit: continue
    p, flip = hit; fn = f'{LO}/pmtrades/{p[1]}.json.gz'
    if not os.path.exists(fn): continue
    tr = sorted(json.load(gzip.open(fn)))
    pmser = [(t, pr if oi == 0 else 1 - pr) for t, pr, s, oi in tr if s >= 5]
    srcs = [('trades', pmser)]
    if len(p) > 3 and len(bk_mid.get(p[3], [])) > 500: srcs.append(('books', bk_mid[p[3]]))
    for bk in ['pinnacle', 'bet365', '1xbet']:
        b = d['hist'].get('bookmakers', {}).get(bk)
        if not b or MW[sp] not in b['markets']: continue
        bs = book_ser(b, MW[sp], flip)
        if len(bs) < 20: continue
        for sname, ps in srcs:
            if len(ps) < 50: continue
            r = xc(ps, bs)
            if not r: continue
            key = (sp, bk, sname)
            for k, v in r.items(): agg[key][k] += v
            cnt[key] += 1
            pk = max(r, key=r.get)
            per.append(dict(sport=sp, book=bk, pm=sname, match=f"{fx['participant1Name']} v {fx['participant2Name']}", book_lead_s=-pk, peak_corr=round(r[pk], 3), corr0=round(r[0], 3)))
res = {}
for key, v in agg.items():
    pk = max(v, key=v.get); sp, bk, sname = key
    res[f'{ {12:"tennis",17:"cs2",18:"lol"}[sp]}/{bk}/pm_{sname}'] = dict(matches=cnt[key], pooled_peak_lag_s=-pk, pooled_peak_corr=round(v[pk] / cnt[key], 3),
        corr_book_first_10s=round(v[-10] / cnt[key], 3), corr_book_first_5s=round(v[-5] / cnt[key], 3), corr_at_0=round(v[0] / cnt[key], 3), corr_book_later_5s=round(v[5] / cnt[key], 3), corr_book_later_10s=round(v[10] / cnt[key], 3))
# sign: k>0 means book change at t+k matches PM change at t -> book LATER by k. report as book lead = -k? keep explicit:
json.dump(dict(summary=res, per_match=per, note='pooled_peak_lag_s: positive = book moves FIRST by that many seconds'), open(f'{LO}/xcorr.json', 'w'), indent=1)
for k, v in sorted(res.items()): print(k, v)
