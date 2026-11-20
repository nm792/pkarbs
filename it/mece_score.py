#!/usr/bin/env python3
"""Daily scorer for pm_mece_books.js output (sports MECE sets, 3+ legs, both tokens, OWN books only).
Usage: python3 -I mece_score.py <recorderDir> [YYYY-MM-DD (UTC, default yesterday)] [--tsv scores.tsv]
Per set (markets.jsonl 'set' = slug|sportsMarketType, 3 legs, each leg binary YES/NO tokens), variants:
  buyYES  : buy YES of every leg at own asks,  payoff 1
  buyNO   : buy NO  of every leg at own asks,  payoff n-1
  sellYES : mint a $1 set, sell every YES at own bids   (profit = sum bids - 1)
  sellNO  : hold (n-1)-pay NO set, sell every NO at own bids (profit = sum bids - (n-1))
Fee per share per leg 0.05*p*(1-p) (taker, sports, 20 Nov). Fill = walk each leg's levels to depth for equal shares while marginal > 0, at the book
1000 ms AFTER detection ('d1') and at detection time ('d0'). Runs = detections within 10 s in one set/variant merged. Not modelled: taker rebate (tier 0%),
neg-risk conversion cost (none assumed; conversion only re-expresses the same payoff), leg-risk (all-or-nothing at one time).
Output: one line per day: set count with every token seen, observations, min cost ratios, runs/net$ at d0 and d1, per variant. Appends to --tsv if given.
"""
import gzip, json, sys, os, glob, bisect, datetime, collections
FEE = 0.05
def fee(p): return FEE * p * (1 - p)
def read_gz(f):
    try:
        with gzip.open(f, 'rt') as h:
            for l in h:
                try: yield json.loads(l)
                except Exception: pass
    except EOFError: pass
def load(d, day):
    mk = {}
    for l in open(os.path.join(d, 'markets.jsonl')):
        try: r = json.loads(l)
        except Exception: continue
        mk[r['cond']] = r
    sets = collections.defaultdict(list)
    for c, m in mk.items(): sets[m['set']].append(c)
    sets = {s: cs for s, cs in sets.items() if len(cs) == 3}
    tok = {}
    for s, cs in sets.items():
        for li, c in enumerate(cs):
            for ti, t in enumerate(mk[c]['tokens']): tok[t] = (s, li, ti)
    t0 = int(datetime.datetime.strptime(day, '%Y-%m-%d').replace(tzinfo=datetime.timezone.utc).timestamp() * 1000); t1 = t0 + 86400000
    ser = collections.defaultdict(lambda: collections.defaultdict(list))   # set -> (leg,tok) -> [(ms, asks, bids)]
    for f in sorted(glob.glob(os.path.join(d, 'books-*.jsonl.gz'))):
        for r in read_gz(f):
            a = tok.get(r['asset'])
            if not a or not (t0 - 5000 <= r['recv_ms'] < t1 + 5000): continue
            asks = sorted((float(x['price']), float(x['size'])) for x in r['asks'] if float(x['size']) > 0)
            bids = sorted(((float(x['price']), float(x['size'])) for x in r['bids'] if float(x['size']) > 0), reverse=True)
            ser[a[0]][(a[1], a[2])].append((r['recv_ms'], asks, bids))
    return mk, sets, ser, t0, t1
def at(lst, ts, t):
    k = bisect.bisect_right(ts, t) - 1
    return lst[k] if k >= 0 else None
def walk(levels, price_fn, payoff, side):
    # levels: per-leg list of [price,size]; marginal = payoff-cost (buy) or proceeds-payoff (sell) per equal share across legs
    L = [[list(x) for x in lv] for lv in levels]; idx = [0] * len(L); sh = prof = 0.0
    while all(i < len(l) for i, l in zip(idx, L)):
        ps = [l[i][0] for i, l in zip(idx, L)]
        m = (payoff - sum(ps) - sum(fee(p) for p in ps)) if side == 'buy' else (sum(ps) - payoff - sum(fee(p) for p in ps))
        if m <= 0: break
        q = min(l[i][1] for i, l in zip(idx, L)); sh += q; prof += q * m
        for j, l in enumerate(L):
            l[idx[j]][1] -= q
            if l[idx[j]][1] <= 1e-9: idx[j] += 1
    return sh, prof
VARS = {'buyYES': (0, 'asks', 'buy', lambda n: 1), 'buyNO': (1, 'asks', 'buy', lambda n: n - 1), 'sellYES': (0, 'bids', 'sell', lambda n: 1), 'sellNO': (1, 'bids', 'sell', lambda n: n - 1)}
def top_ok(books, which):
    return all(b and b[which] for b in books)
def score(d, day):
    mk, sets, ser, t0, t1 = load(d, day)
    res = {v: {'d0': [], 'd1': [], 'min': 9.0, 'max': -9.0} for v in VARS}; nobs = 0; complete = 0
    for s, S in ser.items():
        n = 3
        if len(S) != 6: continue
        complete += 1
        tss = {k: [x[0] for x in S[k]] for k in S}
        times = sorted(x[0] for k in S for x in S[k] if t0 <= x[0] < t1)
        for v, (ti, which, side, pay) in VARS.items():
            last = [None] * 2
            for t in times:
                bk = [at(S[(li, ti)], tss[(li, ti)], t) for li in range(n)]
                if any(b is None for b in bk): continue
                col = 1 if which == 'asks' else 2
                if any(not b[col] for b in bk): continue
                top = [b[col][0][0] for b in bk]; nobs += 1
                cost = sum(top)
                if side == 'buy': res[v]['min'] = min(res[v]['min'], cost / pay(n))
                else: res[v]['max'] = max(res[v]['max'], cost / pay(n))
                edge = (pay(n) - cost - sum(fee(p) for p in top)) if side == 'buy' else (cost - pay(n) - sum(fee(p) for p in top))
                if edge <= 0: continue
                for tag, dly in (('d0', 0), ('d1', 1000)):
                    bk2 = [at(S[(li, ti)], tss[(li, ti)], t + dly) for li in range(n)]
                    if any(b is None or not b[col] for b in bk2): continue
                    sh, pr = walk([b[col] for b in bk2], None, pay(n), side)
                    if pr > 0:
                        L = res[v][tag]
                        if L and L[-1][0] == s and t - L[-1][1] < 10000: L[-1] = (s, t, max(L[-1][2], pr), max(L[-1][3], sh))
                        else: L.append((s, t, pr, sh))
    return complete, len(sets), nobs, res
def main():
    a = [x for x in sys.argv[1:] if not x.startswith('--')]; d = a[0]
    day = a[1] if len(a) > 1 else (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    complete, nsets, nobs, res = score(d, day)
    out = [day, 'sets_listed=%d' % nsets, 'sets_all6tokens=%d' % complete, 'obs=%d' % nobs]
    for v in VARS:
        r = res[v]
        ratio = ('min=%.4f' % r['min']) if VARS[v][2] == 'buy' else ('maxproceeds_ratio=%.4f' % r['max'])
        out.append('%s:%s d0runs=%d d0net=%.2f d1runs=%d d1net=%.2f' % (v, ratio, len(r['d0']), sum(x[2] for x in r['d0']), len(r['d1']), sum(x[2] for x in r['d1'])))
    line = '\t'.join(out); print(line)
    if '--tsv' in sys.argv:
        p = sys.argv[sys.argv.index('--tsv') + 1]
        with open(p, 'a') as h: h.write(line + '\n')
if __name__ == '__main__': main()
