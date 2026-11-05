"""Do Pinnacle / bet365 / 1xbet prices (OddsPapi history) move BEFORE the Polymarket price?
Tennis + CS2 + LoL, 4-5 Nov 2026. PM side = Polymarket v2 trades (1 s timestamps).

For each PM price jump (last-trade price on outcome 0 moves >= 5c within 10 s and still holds
>= half the move 20 s later; one jump per 60 s), find when each book's no-vig implied probability
first moved >= half the PM move from its own level 60 s before the jump, searching -60..+120 s.
lag = book time - PM time (negative = book first). Book times are OddsPapi ingest (createdAt),
which OddsPapi says is ~1 s after Pinnacle and 4-10 s after bet365.

Usage: python3 lead.py OP_DIR GAMMA_TENNIS_JSON CS2_MARKETS_JSONL OUT_DIR
"""
import gzip, json, glob, sys, os, re, bisect, statistics as stx, datetime as dt, urllib.request, urllib.parse, time
from concurrent.futures import ThreadPoolExecutor

OP, GT, CSM, OUT = sys.argv[1:5]
SHIFT = float(os.environ.get('PLACEBO_SHIFT', '0'))  # placebo: look for book moves around t0+SHIFT
os.makedirs(OUT + '/pmtrades', exist_ok=True)
BOOKS = ['pinnacle', 'bet365', '1xbet']
MW = {12: '121', 17: '171', 18: '181'}           # match-winner market per sport (2 outcomes: id, id+1)
LOL_MAP1 = '1821'                                 # PM LoL market is Game 1 Winner

def ts(s): return dt.datetime.fromisoformat(s.replace('Z', '+00:00')).timestamp()
def toks(s): return [w for w in re.sub(r'[^a-z ]', ' ', s.lower().replace(',', ' ')).split() if len(w) > 2]

def jget(url, p):
    u = url + '?' + urllib.parse.urlencode(p)
    for a in range(3):
        try:
            r = urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'pkarbs-research'}), timeout=60)
            return 200, json.loads(r.read())
        except Exception as e:
            time.sleep(2 * (a + 1)); err = e
    return -1, None

def pm_trades(cond):
    fn = f'{OUT}/pmtrades/{cond}.json.gz'
    if os.path.exists(fn): return json.load(gzip.open(fn))
    p = {'condition': cond, 'limit': 500}; out = []; cur = None
    for _ in range(400):
        if cur: p['cursor'] = cur
        c, d = jget('https://data-api.polymarket.com/v2/trades', p)
        if c != 200 or not d: break
        out += [(z['timestamp'], z['price'], z['size'], z['outcome_index']) for z in d['data']]
        cur = d['pagination'].get('next_cursor')
        if not d['pagination'].get('has_more') or not cur: break
    json.dump(out, gzip.open(fn, 'wt')); return out

# ---- PM markets: (outcome names, cond, sport)
pm = []
for e in json.load(gzip.open(GT)):
    if not re.search(r'2026-11-0[45]$', e['slug']): continue
    for m in e['markets']:
        if m.get('sportsMarketType') == 'moneyline':
            pm.append((json.loads(m['outcomes']), m['conditionId'], 12))
seen = set()
for l in gzip.open(CSM, 'rt'):
    m = json.loads(l)
    if m['kind'] == 'Match Winner' and m['cond'] not in seen:
        seen.add(m['cond']); pm.append((m['outcomes'], m['cond'], 17))
pm.append((['Gen.G', 'LYON'], '0xffb12fd0acd3b1015ea0cf57713715414b17ea694c9de7ac567643fb02a5ecdd', 18))  # Game 1

def same(a, b):
    A, B = set(toks(a)), set(toks(b))
    return bool(A & B) or any(x[:4] == y[:4] for x in A for y in B if len(x) > 4 and len(y) > 4)

# ---- match OddsPapi fixtures to PM markets
pairs = []
for f in glob.glob(f'{OP}/hist/*'):
    d = json.load(gzip.open(f)); fx = d['fixture']; sp = fx['sportId']
    if sp not in MW or '/' in fx['participant1Name']: continue      # skip doubles
    for outs, cond, s2 in pm:
        if s2 != sp: continue
        if same(fx['participant1Name'], outs[0]) and same(fx['participant2Name'], outs[1]): pairs.append((f, cond, False)); break
        if same(fx['participant1Name'], outs[1]) and same(fx['participant2Name'], outs[0]): pairs.append((f, cond, True)); break
print('matched fixtures', len(pairs), flush=True)
with ThreadPoolExecutor(8) as ex: list(ex.map(lambda p: pm_trades(p[1]), pairs))

def at(ser, times, t):
    i = bisect.bisect_right(times, t) - 1
    return ser[i][1] if i >= 0 else None

rows = []
for f, cond, flip in pairs:
    d = json.load(gzip.open(f)); fx = d['fixture']; sp = fx['sportId']
    tr = sorted(pm_trades(cond))
    if len(tr) < 50: continue
    ser = [(t, p if oi == 0 else 1 - p) for t, p, s, oi in tr if s >= 5]
    times = [x[0] for x in ser]
    jumps, last = [], -1e9
    for t, p in ser:
        if t - last < 60: continue
        p0 = at(ser, times, t - 10); p2 = at(ser, times, t + 20)
        if p0 is None or p2 is None or not (0.05 < p0 < 0.95): continue
        mv = p - p0
        if abs(mv) >= 0.05 and (p2 - p0) * (1 if mv > 0 else -1) >= abs(mv) / 2:
            jumps.append((t, mv)); last = t
    mkt = LOL_MAP1 if sp == 18 else MW[sp]
    alt = str(int(mkt) + 1)
    for bk in BOOKS:
        b = d['hist'].get('bookmakers', {}).get(bk)
        if not b or mkt not in b['markets']: continue
        ev = sorted((ts(x['createdAt']), oid, x['price'], x['active'])
                    for oid, ov in b['markets'][mkt]['outcomes'].items() for x in ov['players'].get('0', []))
        cur = {}; bser = []; susp = []
        for t, oid, pr, act in ev:
            if not act: susp.append(t); continue
            cur[oid] = pr
            if cur.get(mkt) and cur.get(alt):
                q = (1 / cur[mkt]) / (1 / cur[mkt] + 1 / cur[alt]); bser.append((t, 1 - q if flip else q))
        if len(bser) < 10: continue
        bt = [x[0] for x in bser]
        for t0r, mv in jumps:
            t0 = t0r + SHIFT
            if t0 < bt[0] or t0 > bt[-1] + 600: continue
            base = at(bser, bt, t0 - 60)
            if base is None: continue
            lag = None
            for tt, q in bser[bisect.bisect_left(bt, t0 - 60):]:
                if tt > t0 + 120: break
                if (q - base) * (1 if mv > 0 else -1) >= abs(mv) / 2: lag = round(tt - t0, 1); break
            sl = [s - t0 for s in susp if -60 <= s - t0 <= 60]
            rows.append(dict(sport=sp, book=bk, match=f"{fx['participant1Name']} v {fx['participant2Name']}",
                             t_pm=t0, move=round(mv, 3), lag=lag, susp_lag=round(sl[0], 1) if sl else None))
sfx = f'_placebo{int(SHIFT)}' if SHIFT else ''
json.dump(rows, open(f'{OUT}/lead_rows{sfx}.json', 'w'))

def summ(rs):
    l = [r['lag'] for r in rs if r['lag'] is not None]
    if not l: return dict(jumps=len(rs), found=0)
    q = stx.quantiles(l, n=4) if len(l) > 3 else [None] * 3
    return dict(jumps=len(rs), found=len(l), matches=len({r['match'] for r in rs}), median_lag=stx.median(l),
                q1=q[0], q3=q[2], book_first_5s=round(sum(x <= -5 for x in l) / len(l), 2),
                book_first_any=round(sum(x < 0 for x in l) / len(l), 2))
res = {}
for sp, name in [(12, 'tennis'), (17, 'cs2'), (18, 'lol')]:
    for bk in BOOKS:
        rs = [r for r in rows if r['sport'] == sp and r['book'] == bk]
        if rs: res[f'{name}/{bk}'] = summ(rs)
json.dump(res, open(f'{OUT}/lead_summary{sfx}.json', 'w'), indent=1)
for k, v in res.items(): print(k, v)
