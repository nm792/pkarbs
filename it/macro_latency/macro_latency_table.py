"""Per-fill latency table for the macro stale-ask pickoff (answers: why can P&L RISE with latency?). Offline, read-only, paper only. Uses macro_pickoff_score.py UNCHANGED for fills.
For each market and each latency L it prints: token, ask price and size at decision, AGE of that book row (decision time minus the row's recv time), whether the SAME price level with at least
the same size was already in the book at the SMALLEST latency (AVAILABLE_EARLIER) or was POSTED LATER (first time it appeared, seconds after release), and the resolution (winner from winners.json).
A level that first appears after R + L_small is liquidity that a faster bot could not have bought: P&L rising with L is then an opportunity-set effect (b), not the same trade delayed; a decision row whose
recv time is AFTER the decision time would be lookahead (a) and is asserted impossible: the tool raises if it ever sees one.
Usage: python3 -I macro_latency_table.py DIR RELEASE_ISO WINNERS_JSON [L1,L2,...=0.5,2,5]"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import macro_pickoff_score as S

def first_seen(rows, price, size, after_ms):
    """first row received at or after after_ms whose ask ladder holds this price with >= size; None if never."""
    for r in rows:
        if r['recv_ms'] >= after_ms and any(abs(a['price'] - price) < 1e-9 and a['size'] >= size for a in r.get('asks', [])): return r['recv_ms']
    return None

def table(markets, books, release_s, winners, lats, usd=200.0, cap=2000.0, maxp=0.95):
    out = []; Lmin = min(lats)
    for L in lats:
        res = S.score(markets, books, release_s, winners, L, usd, cap, maxp)
        for m, r in zip(markets, res['rows']):
            row = {'L': L, 'market': r.get('title'), 'winner': r.get('winner'), 'result': r['result']}
            w = winners.get(m['cond'])
            if w in ('Yes', 'No') and m.get('seconds_delay') is not None:
                tok = m['tokens'][m['outcomes'].index(w)]; rows = books.get(tok, []); t_dec = (release_s + L) * 1000
                r0 = S.last_at(rows, t_dec)
                if r0:
                    if r0['recv_ms'] > t_dec: raise AssertionError('LOOKAHEAD: decision row after decision time')
                    row['row_age_s'] = round((t_dec - r0['recv_ms']) / 1000, 3)
                    if r0.get('asks'):
                        p, sz = r0['asks'][0]['price'], r0['asks'][0]['size']; row.update(token=tok[:10], ask=p, ask_size=sz)
                        fs = first_seen(rows, p, min(sz, 5), (release_s) * 1000)   # first appearance at or after the release
                        row['level_first_seen_after_R_s'] = None if fs is None else round(fs / 1000 - release_s, 3)
                        # was it already there at Lmin? (row at or before R+Lmin holds the same level with >= size)
                        e = S.last_at(rows, (release_s + Lmin) * 1000)
                        row['available_at_Lmin'] = bool(e and any(abs(a['price'] - p) < 1e-9 and a['size'] >= min(sz, 5) for a in e.get('asks', [])))
            for k in ('price', 'shares', 'stake', 'pnl'):
                if k in r: row[k] = r[k]
            out.append(row)
    return out

if __name__ == '__main__':
    a = sys.argv[1:]
    if len(a) < 3: print(__doc__); sys.exit(64)
    lats = [float(x) for x in (a[3] if len(a) > 3 else '0.5,2,5').split(',')]
    mk = [json.loads(l) for l in open(os.path.join(a[0], 'markets.jsonl'))]
    for r in table(mk, S.load_books(a[0]), S.ts(a[1]), json.load(open(a[2])), lats): print(json.dumps(r))
