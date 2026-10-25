"""Stale-quote pickoff around a scheduled release, from Polymarket public trades.

Input: a TinyFish fetch_content dump of data-api /v2/trades?event_id=..&limit=500 responses.
For each event: release epoch R. Winner per market (title) is inferred from trades after
R+60 s at price >= 0.99 (the outcome holders pay ~1 for). Edge of a taker trade = (value - price)
* size for BUY, (price - value) * size for SELL; positive edges are summed by seconds after R.
Timestamps are on-chain settlement times, so they lag matching by a few seconds.
"""
import json, re, sys, collections

ROW = re.compile(r'"side":"(\w+)".{0,250}?"size":([\d.]+),"price":([\d.]+),"timestamp":(\d+),'
                 r'"title":"([^"]+)".{0,400}?"outcome":"(\w+)"')


def rows_of(result):
    t = result['text']
    t = t if isinstance(t, str) else json.dumps(t)
    t = t.replace('\\_', '_')
    return [(side, float(s), float(p), int(ts), ti, oc) for side, s, p, ts, ti, oc in ROW.findall(t)]


def winners(rows, R):
    w = {}
    for side, s, p, ts, ti, oc in rows:
        if ts > R + 60 and p >= 0.99:
            w.setdefault(ti, collections.Counter())[oc] += s
    return {ti: c.most_common(1)[0][0] for ti, c in w.items()}


def pool(rows, R, bins=(10, 30, 300)):
    win = winners(rows, R)
    out = collections.OrderedDict((b, [0, 0.0, 0.0]) for b in bins)
    unknown = 0
    for side, s, p, ts, ti, oc in rows:
        d = ts - R
        if d < 0 or d > bins[-1]:
            continue
        if ti not in win:
            unknown += 1
            continue
        val = 1.0 if oc == win[ti] else 0.0
        edge = (val - p) * s if side == 'BUY' else (p - val) * s
        b = next(b for b in bins if d <= b)
        x = out[b]
        x[0] += 1
        x[1] += s * p
        x[2] += max(edge, 0.0)
    return out, unknown, len(win)


def bursts(rows, top=5):
    c = collections.Counter(ts // 60 * 60 for *_, ts, _t, _o in [(r[0], r[1], r[2], r[3], r[4], r[5]) for r in rows])
    return c.most_common(top)


if __name__ == '__main__':
    dump = json.load(open(sys.argv[1]))
    for res in dump['results']:
        rows = rows_of(res)
        print(res['url'], len(rows), 'rows')
        if len(sys.argv) > 2:
            R = int(sys.argv[2 + dump['results'].index(res)]) if len(sys.argv) > 2 + dump['results'].index(res) else None
            if R:
                out, unk, nw = pool(rows, R)
                print('  R', R, 'winners', nw, 'unknown-market trades', unk)
                for b, (n, usd, e) in out.items():
                    print(f'  <= {b:4d}s  trades {n:3d}  notional ${usd:8.0f}  pickoff edge ${e:7.0f}')
        else:
            print('  busiest minutes', bursts(rows))
