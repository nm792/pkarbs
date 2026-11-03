"""Shared pieces for the per-sport win models and Nick's bidding-rule backtest (3 Nov 2026).

Rule (Nick, 3 Nov): bid = market x (1 - 0.025), never any other price, never at/above the best ask.
Place the bid on a token only when model_fair - bid >= E.  Same fill and P&L rules as the LoL
backtest (rn1/scores/lol/bidsim/bt_gate.py on branch claude/project-thread-3odnzj):
  * market price = trade-derived mid (avg of last sell-side and buy-side print), seen QDELAY s before.
  * fill: a print that sells into the bid side at a price strictly below our bid fills us at OUR bid,
    min(print size, Q) shares.  Queue position ignored (optimistic).
  * no bids from event+LAG to event+30 s after each score change (pull); model reads state LAG s late.
  * hold to result.  Rebate (ESTIMATE) = rebateRate x feeRate x p(1-p) per share (market feeSchedule).
"""
import os, json, gzip, time, bisect, math
import urllib.request, urllib.parse
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, 'raw')
Q = 100.0; QDELAY = 1; D = 0.025

def jget(url, params=None, tries=4):
    if params: url = url + ('&' if '?' in url else '?') + urllib.parse.urlencode(params)
    for k in range(tries):
        try:
            r = urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'pkarbs-research/1.0'}), timeout=40)
            return 200, json.load(r)
        except urllib.error.HTTPError as e:
            if e.code in (400, 404): return e.code, None
            time.sleep(2 ** k)
        except Exception:
            time.sleep(2 ** k)
    return -1, None

def pull_trades(cond, start, end, sub='trades'):
    """All data-api v2 trades for a condition between start and end (unix s). Cached."""
    od = os.path.join(RAW, sub); os.makedirs(od, exist_ok=True)
    fn = os.path.join(od, f'{cond}.json.gz')
    if os.path.exists(fn): return json.load(gzip.open(fn))
    p = {'condition': cond, 'limit': 500, 'start': int(start), 'end': int(end)}
    allt = []; cur = None
    for _ in range(600):
        if cur: p['cursor'] = cur
        c, d = jget('https://data-api.polymarket.com/v2/trades', p)
        if c != 200 or not d: break
        allt += [{k: z[k] for k in ('timestamp', 'outcome_index', 'side', 'price', 'size')} for z in d['data']]
        cur = d['pagination'].get('next_cursor')
        if not d['pagination'].get('has_more') or not cur: break
    json.dump(allt, gzip.open(fn, 'wt'))
    return allt

def prints(tr):
    """-> sorted [(ts, -k, price_token0, sell0, size)]; sell0 = print sells into token0's bid side."""
    pr = []
    for k, t in enumerate(tr):
        is0 = t['outcome_index'] == 0
        ph = t['price'] if is0 else 1 - t['price']
        sell0 = (is0 and t['side'] == 'SELL') or ((not is0) and t['side'] == 'BUY')
        pr.append((t['timestamp'], -k, ph, sell0, t['size']))
    pr.sort()
    return pr

class Mid:
    def __init__(s, pr):
        s.t = [p[0] for p in pr]; lb = la = None; s.m = []
        for p in pr:
            if p[3]: lb = p
            else: la = p
            if lb and la and abs(lb[0] - la[0]) <= 120 and lb[2] <= la[2] + 0.005 and la[2] - lb[2] < 0.10:
                s.m.append((lb[2] + la[2]) / 2)
            else:
                s.m.append(p[2])
    def at(s, T):
        i = bisect.bisect_left(s.t, T) - 1
        return s.m[i] if i >= 0 else None

def sim(pr, M, t0, t1, fair, win0, E, evs=(), lag=10, reb=0.0, d=D, gate=True, sevs=(), pull_s=30):
    """fair(T) -> model prob of token0 (None = no model -> no bid when gating). evs = event times.
    Returns per-fill rows. gate=False: bid on every print (market-only baseline)."""
    ev = sorted(evs); fills = []; sevs = sorted(sevs); st_ = [x[0] for x in sevs]
    for (T, _, ph, sell0, sz) in pr:
        if not (t0 <= T <= t1): continue
        mk = M.at(T - QDELAY)
        if mk is None or not (0.05 <= mk <= 0.95): continue
        i = bisect.bisect_right(ev, T - lag) - 1
        if i >= 0 and T < ev[i] + 30: continue           # pulled after a score change
        hurt = set()
        if sevs:                                          # speed guard: pull only the hurt token for pull_s after detection
            j = bisect.bisect_right(st_, T - lag) - 1
            while j >= 0 and T < st_[j] + lag + pull_s:
                hurt.add(sevs[j][1]); j -= 1
        b0, b1 = mk * (1 - d), (1 - mk) * (1 - d)
        f0 = fair(T) if gate else None
        if gate and f0 is None: continue
        if sell0 and 0 not in hurt and ph < b0 - 1e-9 and (not gate or f0 - b0 >= E): fills.append((T, 0, b0, min(sz, Q)))
        if (not sell0) and 1 not in hurt and (1 - ph) < b1 - 1e-9 and (not gate or (1 - f0) - b1 >= E): fills.append((T, 1, b1, min(sz, Q)))
    rows = []
    for (T, tok, b, q) in fills:
        m60 = M.at(T + 60)
        if tok == 1: m60 = 1 - m60
        out = 1.0 if (win0 == (tok == 0)) else 0.0
        rows.append(dict(usd=q * b, em1=q * (m60 - b), pnl=q * (out - b), reb=q * reb * b * (1 - b)))
    return rows

def summarize(per_event, rng=None, nb=2000):
    """per_event: list of [usd, em1, pnl, reb] sums per event (games are the resampling unit)."""
    P = np.array(per_event, float)
    if len(P) == 0: return dict(events=0, usd=0)
    rng = rng or np.random.default_rng(0); u = P[:, 0].sum()
    em = 100 * (P[:, 1] + P[:, 3]).sum() / u; pn = 100 * (P[:, 2] + P[:, 3]).sum() / u
    bs = []
    for _ in range(nb):
        s = rng.integers(0, len(P), len(P)); Qm = P[s]; uu = Qm[:, 0].sum() or 1
        bs.append((100 * (Qm[:, 1] + Qm[:, 3]).sum() / uu, 100 * (Qm[:, 2] + Qm[:, 3]).sum() / uu, (Qm[:, 2] + Qm[:, 3]).sum()))
    bs = np.array(bs)
    net = P[:, 2] + P[:, 3]; keep = np.argsort(-net)[5:]; Pk = P[keep]; uk = Pk[:, 0].sum() or 1
    ex5 = dict(ex_top5_usd=round(uk), ex_top5_1min_pct=round(100 * (Pk[:, 1] + Pk[:, 3]).sum() / uk, 2),
               ex_top5_result_pct=round(100 * (Pk[:, 2] + Pk[:, 3]).sum() / uk, 2), ex_top5_result_usd=round((Pk[:, 2] + Pk[:, 3]).sum()))
    return dict(**ex5, events=int((P[:, 0] > 0).sum()), usd=round(u), reb_usd=round(P[:, 3].sum()),
                net_1min_pct=round(em, 2), ci_1min=list(np.percentile(bs[:, 0], [5, 95]).round(2)),
                net_result_pct=round(pn, 2), ci_result=list(np.percentile(bs[:, 1], [5, 95]).round(2)),
                net_result_usd=round((P[:, 2] + P[:, 3]).sum()), ci_result_usd=list(np.percentile(bs[:, 2], [5, 95]).round(0)))

def reb_rate(meta):
    fs = meta.get('feeSchedule') or {}
    return float(fs.get('rebateRate') or 0) * float(fs.get('rate') or 0)

def brier(p, y):
    p, y = np.asarray(p), np.asarray(y); return float(np.mean((p - y) ** 2))

def calib_table(p, y, bins=10):
    p, y = np.asarray(p), np.asarray(y); out = []
    for k in range(bins):
        m = (p >= k / bins) & (p < (k + 1) / bins + (1e-9 if k == bins - 1 else 0))
        if m.sum(): out.append([round(k / bins, 1), int(m.sum()), round(float(p[m].mean()), 3), round(float(y[m].mean()), 3)])
    return out
