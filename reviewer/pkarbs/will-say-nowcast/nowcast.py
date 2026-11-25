#!/usr/bin/env python3
"""Will-say LIVE NOWCAST reprice-window scorer (SPEC-will-say-live-nowcast-2026-11-25, amendment v1.1).
Measurement only. No orders, no keys. Runs on Prime (R-039); this file only reads JSON inputs.

Data (v1.1): public own-token trade prints of each YES token (Data API /v2/trades; integer-second timestamps).
P121 does NOT keep a continuous book log for will-say tokens (decisions at slots only; earnings-beat books every 60 s),
so a book-based W is not measurable from recorded data (SETTLED B1).

Per YES word with utterance time t_w (s), thr = cheap threshold: a BUY print at price p is CHEAP when p + fee(p) <= 0.98.
  W_ub = first BUY print at p not cheap after t_w, minus t_w (a taker walks from the best ask, so no cheap ask remained then).
         Negative when it happened in [t_w-60, t_w) (leak / anticipation). None if no such print by t_w+300.
  W_lb = last CHEAP BUY print in (t_w, t_w+W_ub] (or (t_w, t_w+300] if W_ub is None), minus t_w; 0 if none. Cheap asks existed at least that long.
  usd(L) = sum price*size of CHEAP BUY prints with t_w+L+HOLD <= ts <= t_w+300: what others still lifted after our latency L plus the 250 ms
           hold (SETTLED A3). A FLOOR on $ available (unlifted asks are invisible; we would compete for these).
Placebo (MC type 1, random times, same data): K times per word drawn uniformly in [t_w-WIN_PRE, t_w-300]; usd(L) at each.
Plants (MC type 2, randomised data): plant_stale (100 sh at 0.50 lifted at t_w+3.0) and plant_hold (lifted at t_w+0.25).
Resolution: prints 1 s + transcript +-1 s, so L in {1,2} s are labelled BELOW/AT RESOLUTION and not used in the verdict."""
import json, random, statistics, sys

HOLD = 0.25
SPEC_HOLD = 0.25  # plant expectations use the spec value, so a scorer whose HOLD drifts fails the plant
LS = (1, 2, 5, 10, 30)
RES_LABEL = {1: 'BELOW RESOLUTION', 2: 'AT RESOLUTION', 5: 'ok', 10: 'ok', 30: 'ok'}
WIN_POST, WIN_PRE_LEAK = 300.0, 60.0


def fee(p, rate):
    return rate * p * (1 - p)


def cheap(p, rate):
    return p + fee(p, rate) <= 0.98 + 1e-12


def buys(trades, tok):
    return sorted((t for t in trades if t['asset'] == tok and t['side'] == 'BUY'), key=lambda t: t['ts'])


def measure(trades, w, rate):
    tw, b = w['t_w'], buys(trades, w['yes_token'])
    ub = next((t['ts'] - tw for t in b if tw - WIN_PRE_LEAK <= t['ts'] <= tw + WIN_POST and not cheap(t['price'], rate)), None)
    hi = tw + (ub if ub is not None and ub > 0 else WIN_POST)
    if ub is not None and ub <= 0:
        lb = 0.0
    else:
        c = [t['ts'] for t in b if tw < t['ts'] <= hi and cheap(t['price'], rate)]
        lb = (max(c) - tw) if c else 0.0
    usd = {L: round(sum(t['price'] * t['size'] for t in b if tw + L + HOLD <= t['ts'] <= tw + WIN_POST and cheap(t['price'], rate)), 2) for L in LS}
    return dict(W_lb=lb, W_ub=ub, leak=ub is not None and ub < 0, usd=usd)


def placebo(trades, w, rate, k=10, win_pre=6 * 3600, seed=0):
    rng = random.Random(seed)
    out = []
    for _ in range(k):
        t = rng.uniform(w['t_w'] - win_pre, w['t_w'] - WIN_POST)
        out.append(measure(trades, dict(w, t_w=t), rate)['usd'])
    return out


def plant(trades, words, frac=0.5, dt_lift=3.0, seed=1, px=0.50, sh=100.0):
    """MC type 2: copy of the prints with one stale ask (sh @ px) lifted by a BUY print at t_w+dt_lift on frac of the words."""
    rng = random.Random(seed)
    chosen = set(i for i in range(len(words)) if rng.random() < frac) or {0}
    extra = [dict(asset=words[i]['yes_token'], side='BUY', price=px, size=sh, ts=words[i]['t_w'] + dt_lift, planted=True) for i in sorted(chosen)]
    return trades + extra, chosen


def plant_check(trades, words, rate, dt_lift, seed=1):
    """Returns (ok, why). Planted words: usd(L) rises by exactly px*sh for every L with L+HOLD <= dt_lift and by 0 otherwise; W_lb >= dt_lift if
    no earlier non-cheap print; unplanted words unchanged."""
    pt, chosen = plant(trades, words, dt_lift=dt_lift, seed=seed)
    why = []
    for i, w in enumerate(words):
        a, b = measure(trades, w, rate), measure(pt, w, rate)
        for L in LS:
            exp = 50.0 if (i in chosen and L + SPEC_HOLD <= dt_lift) else 0.0
            if abs((b['usd'][L] - a['usd'][L]) - exp) > 0.01:
                why.append('word %d L=%d: delta %.2f expected %.2f' % (i, L, b['usd'][L] - a['usd'][L], exp))
        if i in chosen and (a['W_ub'] is None or a['W_ub'] > dt_lift) and not (dt_lift - 0.25 <= b['W_lb'] <= dt_lift + 0.25 or b['W_lb'] > dt_lift):
            why.append('word %d: W_lb %.2f not within %.2f+-0.25' % (i, b['W_lb'], dt_lift))
        if i not in chosen and a != b:
            why.append('word %d unplanted changed' % i)
    return (not why), why


def p95(xs):
    xs = sorted(xs)
    return xs[min(len(xs) - 1, int(0.95 * len(xs)))] if xs else 0.0


def verdict(rows, n_min=20):
    """rows: [{'W_lb','W_ub','usd':{L:..}, 'placebo':[{L:..}]}] of ONE sub-family (no pooling). v1.1 rule:
    ROOM: n>=n_min, median W_lb >= 5 s, median usd(5) >= $50 and above the placebo usd(5) 95th pct.
    NO ROOM: n>=n_min and median W_ub < 2 s (W_ub None counts as 300).  Else INCONCLUSIVE."""
    n = len(rows)
    if n == 0:
        return dict(verdict='INCONCLUSIVE', n=0)
    wlb = statistics.median(r['W_lb'] for r in rows)
    wub = statistics.median(300.0 if r['W_ub'] is None else r['W_ub'] for r in rows)
    u5 = statistics.median(r['usd'][5] for r in rows)
    pl = p95([p[5] for r in rows for p in r.get('placebo', [])])
    out = dict(n=n, median_W_lb=wlb, median_W_ub=wub, median_usd_L5=u5, placebo_usd_L5_p95=pl, leaks=sum(r.get('leak', False) for r in rows))
    if n < n_min:
        out['verdict'] = 'INCONCLUSIVE'
    elif wlb >= 5 and u5 >= 50 and u5 > pl:
        out['verdict'] = 'ROOM'
    elif wub < 2:
        out['verdict'] = 'NO ROOM'
    else:
        out['verdict'] = 'INCONCLUSIVE'
    return out


def run(trades, words, rate_of):
    """words carry 'subfam' and 'cond'; rate_of(cond) -> fee rate. Returns per-subfamily verdicts; void if either plant fails."""
    by = {}
    for w in words:
        by.setdefault(w['subfam'], []).append(w)
    res = {}
    for sf, ws in by.items():
        rate = rate_of(ws[0]['cond'])
        ok1, why1 = plant_check(trades, ws, rate, 3.0)
        ok2, why2 = plant_check(trades, ws, rate, 0.25)
        rows = []
        for w in ws:
            m = measure(trades, w, rate_of(w['cond']))
            m['placebo'] = placebo(trades, w, rate_of(w['cond']))
            rows.append(m)
        v = verdict(rows) if ok1 and ok2 else dict(verdict='VOID (plant failed)', why=(why1 + why2)[:5])
        v['resolution'] = RES_LABEL
        res[sf] = v
    return res


if __name__ == '__main__':
    a = json.load(open(sys.argv[1]))  # {"trades":[...], "words":[...], "fee_rate":{cond: rate}}
    rates = a.get('fee_rate', {})
    print(json.dumps(run(a['trades'], a['words'], lambda c: rates.get(c, 0.0)), indent=1, default=str))
