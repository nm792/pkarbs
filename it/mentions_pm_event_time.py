#!/usr/bin/env python3
"""R-051 screen (OFF-PRIME, public trade data): event-time entry variants for the Polymarket mentions rule, all families, events that CLOSED in the last N days.
Fair value = the frozen model (per-word causal base rate at LISTING, never refit). A token is 'underpriced' at price p when p <= fair-10c (YES fair = q, NO fair = 1-q), p >= 5c.
Fill model (FLOOR, print ladder rebuilt from trades): at each decision window [s, s+L] take own-token BUY prints with price <= limit, in time order, up to $200 notional per (decision, token);
$2,000 per UTC day cap per variant (scale later fills down). Fee 0.04*p*(1-p). Held to resolution. Depth otherwise UNMEASURED.
Event time is not in the data. Two anchors (named assumptions): A = Gamma endDate (tradable, but often 23:59Z of the event day); B = the hour of peak trade volume (HINDSIGHT proxy for the event, an upper-bound screen, not tradable as is).
Variants: listing+1h (frozen), T-24h, T-6h, T-1h, T-15m (decision windows of 1h/1h/1h/15m starting at those offsets before T), during (A: every 5 min over the last 6 h before T; B: every 5 min from T-1h to T+2h).
Placebo: same fill rule at random start times uniform in [T-24h, T] with the same window length, K draws; z = (real - placebo mean)/placebo std over draws.
Usage: python3 -I mentions_pm_event_time.py --scorer P --backtest P --state DIR --out PREFIX --days N [--k 30] [--seed 7]"""
import argparse, collections, csv, datetime as dt, importlib.util, json, random, statistics as S, sys, time, concurrent.futures as cf
ap = argparse.ArgumentParser()
for k in ('scorer', 'backtest', 'state', 'out'): ap.add_argument('--' + k, required=True)
ap.add_argument('--days', type=int, required=True); ap.add_argument('--k', type=int, default=30); ap.add_argument('--seed', type=int, default=7)
VARS = ['listing+1h', 'T-24h', 'T-6h', 'T-1h', 'T-15m', 'during']


def load(n, p):
    sp = importlib.util.spec_from_file_location(n, p); m = importlib.util.module_from_spec(sp); sys.modules[n] = m; sp.loader.exec_module(m); return m


def decisions(var, t0, T, anchor):
    if var == 'listing+1h': d = [(t0, 3600)]
    elif var == 'T-24h': d = [(T - 86400, 3600)]
    elif var == 'T-6h': d = [(T - 6 * 3600, 3600)]
    elif var == 'T-1h': d = [(T - 3600, 3600)]
    elif var == 'T-15m': d = [(T - 900, 900)]
    elif var == 'during': d = [(T - 6 * 3600 + 300 * i, 300) for i in range(72)] if anchor == 'A' else [(T - 3600 + 300 * i, 300) for i in range(36)]
    else: raise ValueError(var)
    return [(s, L) for s, L in d if s >= t0]


def fills(sc, ev, qs, trades, s, L, cap=200.):
    """Own-token BUY prints in [s, s+L] with price <= fair-10c, up to cap notional per token. qs: cond -> q. Returns list of dict(t, cost, pnl, side, word, cond)."""
    out = []
    for m in ev['markets']:
        q = qs[m['cond']]; w = sc.win(m)
        for oi in (0, 1):
            lim = (q - sc.THR) if oi == 0 else ((1 - q) - sc.THR); left = cap
            for (t, side, p, sz, o) in sorted(trades.get(m['cond'], [])):
                if left <= 1e-9: break
                if not (s <= t <= s + L) or side != 'BUY' or o != oi or sz <= 0 or not (.05 <= p <= lim): continue
                take = min(sz, left / p); left -= take * p
                out.append(dict(t=t, cost=take * p, pnl=sc.pnl(oi, p, take, w, m['fee']), side='YES' if oi == 0 else 'NO', word=m['label'], cond=m['cond'], price=p))
    return out


def daycap(fl, cap, day):
    used = collections.defaultdict(float); out = []
    for f in sorted(fl, key=lambda f: f['t']):
        d = day(f['t']); room = max(0.0, cap - used[d]); k = 0.0 if f['cost'] <= 0 else min(1.0, room / f['cost']); used[d] += f['cost'] * k; out.append(dict(f, cost=f['cost'] * k, pnl=f['pnl'] * k))
    return out


def peak_hour(trades, ev):
    h = collections.defaultdict(float)
    for m in ev['markets']:
        for (t, sd, p, s, o) in trades.get(m['cond'], []): h[int(t // 3600)] += p * s
    return (max(h, key=h.get) * 3600) if h else None


def run_variant(sc, bt, evs, var, anchor, span, rng, K):
    allf = []; per = {}
    for e in evs:
        T = e['T'][anchor]
        if T is None: continue
        fl = []
        for s, L in decisions(var, e['t0'], T, anchor): fl += fills(sc, e['ev'], e['qs'], e['tr'], s, L)
        per[e['ev']['slug']] = fl; allf += [dict(f, slug=e['ev']['slug']) for f in fl]
    capped = daycap(allf, 2000., bt.day)
    net = sum(f['pnl'] for f in capped); stake = sum(f['cost'] for f in capped)
    plac = []
    for _ in range(K):
        pf = []
        for e in evs:
            T = e['T'][anchor]
            if T is None: continue
            dec = decisions(var, e['t0'], T, anchor)
            if not dec: continue
            L = dec[0][1]; lo = max(e['t0'], T - 86400); hi = T - L
            if hi <= lo: continue
            for _i in range(len(dec)): pf += fills(sc, e['ev'], e['qs'], e['tr'], rng.uniform(lo, hi), L)
        plac.append(sum(f['pnl'] for f in daycap(pf, 2000., bt.day)))
    pm = S.mean(plac) if plac else 0.0; ps = S.stdev(plac) if len(plac) > 2 else 0.0
    return dict(variant=var, anchor=anchor, events_with_fill=sum(1 for v in per.values() if v), fills=len(capped), stake=round(stake, 2), net=round(net, 2), wins=sum(1 for f in capped if f['pnl'] > 0),
                per_day=round(net / span, 2), pct_of_200=round(100 * net / span / 200, 2), placebo_mean=round(pm, 2), placebo_sd=round(ps, 2), z=None if ps == 0 else round((net - pm) / ps, 2)), per


if __name__ == '__main__':
    a = ap.parse_args(); sc = load('sc', a.scorer); bt = load('bt', a.backtest); now = time.time(); lo = now - a.days * 86400; rng = random.Random(a.seed)
    raw = {}; d0 = dt.date.today() - dt.timedelta(days=a.days + 3); off = 0
    while True:
        r = sc.fetch(f'{sc.GAMMA}/events?tag_slug=mention-markets&closed=true&limit=100&offset={off}&end_date_min={d0}') or []
        for x in r: raw[x['id']] = x
        if len(r) < 100: break
        off += 100
    closed = list(json.load(open(a.state + '/events.json')).values()); pool = [e for e in closed if sc.resolved(e)]
    evs = []
    for x in raw.values():
        e = sc.slim(x)
        if not e['markets'] or not sc.resolved(e) or not x.get('endDate'): continue
        end = sc.ts(x['endDate'])
        if end < lo: continue
        e['slug'] = x['slug']; evs.append(dict(ev=e, end=end))
    with cf.ThreadPoolExecutor(8) as ex: tr = dict(ex.map(sc.pull_trades, [m['cond'] for e in evs for m in e['ev']['markets']]))
    if any(v is None for v in tr.values()): raise SystemExit('trade pull failed')
    for e in evs:
        ev = e['ev']; t0 = sc.start(ev); e['t0'] = t0; e['tr'] = {m['cond']: tr[m['cond']] for m in ev['markets']}
        hist = [h for h in pool if h['fam'] == ev['fam'] and h['id'] != ev['id'] and sc.settled_at(h) <= t0]; e['qs'] = {m['cond']: sc.q_for(hist, ev, m) for m in ev['markets']}
        e['T'] = {'A': e['end'], 'B': peak_hour(e['tr'], ev)}
    res = []; rowsev = []
    for anchor in ('A', 'B'):
        for var in VARS:
            r, per = run_variant(sc, bt, evs, var, anchor, a.days, rng, a.k); res.append(r)
            for slug, fl in per.items():
                if fl: rowsev.append(dict(anchor=anchor, variant=var, slug=slug, fam=next(e['ev']['fam'] for e in evs if e['ev']['slug'] == slug), fills=len(fl), stake=round(sum(f['cost'] for f in fl), 2), pnl=round(sum(f['pnl'] for f in fl), 2)))
    res.sort(key=lambda r: -r['per_day'])
    with open(a.out + '_variants.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(res[0].keys())); w.writeheader(); w.writerows(res)
    rowsev.sort(key=lambda r: -r['pnl'])
    with open(a.out + '_events_ranked.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['anchor', 'variant', 'slug', 'fam', 'fills', 'stake', 'pnl']); w.writeheader(); w.writerows(rowsev)
    print('events', len(evs), 'window days', a.days)
    for r in res: print(r)
