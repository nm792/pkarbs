"""Macro stale-quote pickoff scorer (24 Nov 2026, re-audit thread; R-077/R-078 item 2). Offline, read-only, paper only.
Reads one release folder written by pm_event_books.js: markets.jsonl (with seconds_delay, fee, min_size) and books-*.jsonl.gz (both tokens' OWN books, recv_ms).
Rule (decided on information available at decision time, MODELLING-PRINCIPLES 8): at t_dec = R + L (L = our latency from the print, default 0.5 s) the released number is known,
so the winning token of each bucket is known (input file `winners.json`: {cond: "Yes"|"No"}, mapped from the PRINT, never from settlement). We buy that token at its own best ask
if that ask is below MAXP (0.95; above it there is no edge) with size SIZE_USD/price shares. The order lands at t_arr = t_dec + seconds_delay (the market's OWN hold, from CLOB /markets).
It fills only if the SAME price level is still shown, with at least min_size shares, in the last book row at or before t_arr; otherwise 'unfilled (hold)'. A market with seconds_delay null is REFUSED (never assumed).
Fee per share = rate * p * (1-p) from the market's feeSchedule (exponent 1, takerOnly; UNVERIFIED against the docs). P&L per share = 1 - p - fee (winner pays 1). Every $ is a SIM label.
Usage: python3 -I macro_pickoff_score.py DIR RELEASE_ISO WINNERS_JSON [--latency 0.5] [--usd 200] [--cap 2000] [--maxp 0.95]
"""
import sys, os, json, gzip, glob, datetime as dt


def ts(s):
    return dt.datetime.fromisoformat(s.replace('Z', '+00:00')).timestamp()


def load_books(d):
    by = {}
    for p in sorted(glob.glob(os.path.join(d, 'books*.jsonl*'))):
        op = gzip.open if p.endswith('.gz') else open
        with op(p, 'rt') as f:
            for line in f:
                try:
                    r = json.loads(line)
                except Exception:
                    continue
                by.setdefault(r['asset'], []).append(r)
    for v in by.values():
        v.sort(key=lambda r: r['recv_ms'])
    return by


def last_at(rows, t_ms):
    """last book row received at or before t_ms (None if none): the state we could have seen."""
    best = None
    for r in rows:
        if r['recv_ms'] <= t_ms:
            best = r
        else:
            break
    return best


def score(markets, books, release_s, winners, latency=0.5, usd=200.0, cap=2000.0, maxp=0.95):
    out, spent, tot = [], 0.0, 0.0
    t_dec = (release_s + latency) * 1000
    for m in markets:
        w = winners.get(m['cond'])
        row = {'cond': m['cond'], 'title': m.get('title') or m['q'], 'winner': w}
        if w not in ('Yes', 'No'):
            row['result'] = 'skip (no winner mapped)'; out.append(row); continue
        d = m.get('seconds_delay')
        if d is None:
            row['result'] = 'REFUSED (seconds_delay unknown)'; out.append(row); continue
        tok = m['tokens'][m['outcomes'].index(w)]
        rows = books.get(tok, [])
        r0 = last_at(rows, t_dec)
        if not r0 or not r0.get('asks'):
            row['result'] = 'no ask at decision'; out.append(row); continue
        a0 = r0['asks'][0]; p0 = a0['price']; row['ask_at_decision'] = p0
        if p0 >= maxp:
            row['result'] = 'not stale (ask %.3f >= %.2f)' % (p0, maxp); out.append(row); continue
        r1 = last_at(rows, t_dec + d * 1000)
        lvl = [x for x in (r1 or {}).get('asks', []) if abs(x['price'] - p0) < 1e-9]
        ms_ = m.get('min_size') or 5
        if not lvl or lvl[0]['size'] < ms_:
            row['result'] = 'unfilled (hold)'; out.append(row); continue
        sh = min(lvl[0]['size'], usd / p0)
        if spent + sh * p0 > cap:
            row['result'] = 'cap'; out.append(row); continue
        rate = (m.get('fee') or {}).get('rate', 0.0)
        fee = rate * p0 * (1 - p0)
        pnl = sh * (1 - p0 - fee)
        spent += sh * p0; tot += pnl
        row.update(result='FILLED', price=p0, shares=round(sh, 2), stake=round(sh * p0, 2), fee_per_share=round(fee, 5), pnl=round(pnl, 2))
        out.append(row)
    return {'rows': out, 'filled': sum(1 for r in out if r['result'] == 'FILLED'), 'stake': round(spent, 2), 'pnl': round(tot, 2),
            'label': 'SIM (own-token asks from recorded books; fee schedule UNVERIFIED; one release is not a $/day figure)'}


if __name__ == '__main__':
    a = sys.argv[1:]
    if len(a) < 3:
        print(__doc__); sys.exit(64)
    opt = {}
    i = 3
    while i < len(a):
        opt[a[i].lstrip('-')] = float(a[i + 1]); i += 2
    mk = [json.loads(l) for l in open(os.path.join(a[0], 'markets.jsonl'))]
    res = score(mk, load_books(a[0]), ts(a[1]), json.load(open(a[2])), opt.get('latency', 0.5), opt.get('usd', 200.0), opt.get('cap', 2000.0), opt.get('maxp', 0.95))
    print(json.dumps(res, indent=1))
