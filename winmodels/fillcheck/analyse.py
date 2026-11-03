"""Simulated vs real fills at rn1's own resting prices (22-29 Oct, soccer / NBA / LoL).
For each real rn1 maker fill (token k, price p, time T): find the taker transaction that filled it in the market's trade
list, express the taker's print price in token-k terms (ph), and ask whether our fill rule would have registered it.
Rule A (current, LoL/soccer/NBA backtests): fill iff a sell-into-k print has ph < bid (strict).
Rule B: fill iff ph <= bid (inclusive).
Also: 'sim-only' fills = other sell-into-k prints with ph < p in the 60 s before T (a bid resting at p would have been
filled by them under rule A, though rn1 got no fill then: either rn1 was not resting yet, or the rule invents them)."""
import sys, os, json, gzip, collections, bisect, datetime as dt
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import common as C
F = json.load(gzip.open(f'{C.RAW}/fillcheck/rn1_maker_fills_2026-10-22_29.json.gz'))
by = collections.defaultdict(list)
for f in F: by[f['cond']].append(f)
def gst(s):
    try: return dt.datetime.fromisoformat(s.replace(' ', 'T').replace('+00', '+00:00')).timestamp()
    except Exception: return None
A = collections.defaultdict(lambda: np.zeros(6)); miss = collections.Counter(); simonly = collections.defaultdict(lambda: np.zeros(4))
for cond, fs in by.items():
    fn = f'{C.RAW}/fillcheck/trades/{cond}.json.gz'
    if not os.path.exists(fn): miss['no trades file'] += len(fs); continue
    tr = json.load(gzip.open(fn))
    if not tr: miss['empty'] += len(fs); continue
    tx = {t['transaction_hash']: t for t in tr}
    pr = C.prints(tr); M = C.Mid(pr); pt = [p[0] for p in pr]
    for f in fs:
        k = f['oi']; p = f['price']; T = f['ts']; t = tx.get(f['tx'])
        if t is None: miss['taker row not found'] += 1; continue
        if t['outcome_index'] == k and t['side'] == 'SELL': ph = t['price']
        elif t['outcome_index'] != k and t['side'] == 'BUY': ph = 1 - t['price']
        else: miss['taker row same direction'] += 1; continue
        m0, m60 = M.at(T), M.at(T + 61)
        if m60 is None: miss['no mid'] += 1; continue
        if k == 1: m60 = 1 - m60; m0 = 1 - m0 if m0 is not None else None
        g = gst(f['gst']); phase = 'in-play' if g and T >= g else 'pre-game'
        if not (0.05 <= p <= 0.95): continue
        cls = 'taker print AT rn1 price' if abs(ph - p) < 6e-4 else ('taker avg ABOVE rn1 price (sweep)' if ph > p else 'taker print BELOW rn1 price')
        q = f['size']; row = [q * p, q * (m60 - p), 1, float(ph < p - 1e-9), float(ph <= p + 6e-4), q * (m0 - p) if m0 is not None else 0]
        for key in [(f['sport'], phase, 'ALL'), (f['sport'], phase, cls)]: A[key] += row
        # rule-A fills a bid resting at p would get from OTHER prints in the 60 s before T
        i0 = bisect.bisect_left(pt, T - 60); i1 = bisect.bisect_left(pt, T)
        for (Tq, _, ph0, sell0, sz) in pr[i0:i1]:
            phk = ph0 if k == 0 else 1 - ph0; into = sell0 if k == 0 else (not sell0)
            if into and phk < p - 1e-9:
                mm = M.at(Tq + 61)
                if mm is None: continue
                mm = mm if k == 0 else 1 - mm; qq = min(sz, 100)
                simonly[(f['sport'], phase)] += [qq * p, qq * (mm - p), 1, 0]
print('not scored:', dict(miss))
out = []
print(f"{'sport':7}{'phase':9}{'class':40}{'fills':>7}{'$':>11}{'entry vs mid':>13}{'1-min':>8}{'ruleA sees':>11}{'ruleB sees':>11}")
for key in sorted(A):
    v = A[key]; sp, ph_, cls = key
    out.append(dict(sport=sp, phase=ph_, cls=cls, fills=int(v[2]), usd=round(v[0]), entry_pct=round(100 * v[5] / v[0], 2), m1_pct=round(100 * v[1] / v[0], 2),
                    ruleA_share=round(v[3] / v[2], 3), ruleB_share=round(v[4] / v[2], 3)))
    print(f"{sp:7}{ph_:9}{cls:40}{int(v[2]):>7}{v[0]:>11.0f}{100*v[5]/v[0]:>12.2f}%{100*v[1]/v[0]:>7.2f}%{v[3]/v[2]:>10.1%}{v[4]/v[2]:>10.1%}")
print('\nRule-A fills from other prints in the 60 s before each real fill, bid at rn1 price:')
for key in sorted(simonly):
    v = simonly[key]; print(f"{key[0]:7}{key[1]:9} fills {int(v[2]):>7} $ {v[0]:>10.0f} 1-min {100*v[1]/v[0]:>6.2f}%")
    out.append(dict(sport=key[0], phase=key[1], cls='ruleA fills from other prints, 60 s before real fill', fills=int(v[2]), usd=round(v[0]), m1_pct=round(100 * v[1] / v[0], 2)))
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out_fillcheck.json'), 'w'), indent=1)
