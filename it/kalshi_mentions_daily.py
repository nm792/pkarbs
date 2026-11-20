#!/usr/bin/env python3
"""Daily scorer for the Kalshi mentions FORWARD arms. Reuses the frozen helpers of mentions/forward-arm2/mm_forward2.py (same rule, 3c).
  arm 2: every Kalshi Mentions series except the 10 arm-1 series, FREEZE 2026-11-11T10:00Z, >=10 earlier resolved events (PREREG-forward-arm2-2026-11-11.md)
  arm 1: the 10 frozen series, FREEZE 2026-11-10T15:00Z, history = ALL earlier resolved events of the series (PREREG-forward-test-2026-11-10.md; min history 0)
Differences from the PREREG scorers, stated: (a) arm 1 uses the causal history of mm_forward2 (event enters history after all its markets settled before the new event opened) instead of mm_forward.py's start-order history;
(b) unresolved events with a decided bet are listed as PENDING and marked to the market's last price (information only, never in realised P&L).
Writes OUT/kalshi_arm<N>_daily.csv (one row per UTC date, replaced on rerun), kalshi_arm<N>_events_<date>.json, LATEST-kalshi-arm<N>.txt.
Usage: python3 -I kalshi_mentions_daily.py --mm2 PATH_TO_mm_forward2.py --out DIR --arm 1|2 [--asof ISO]"""
import argparse, collections, csv, datetime as dt, importlib.util, json, math, os, statistics as S, sys, time, concurrent.futures as cf
ap = argparse.ArgumentParser(); ap.add_argument('--mm2', required=True); ap.add_argument('--out', required=True); ap.add_argument('--arm', type=int, required=True); ap.add_argument('--asof', default=None)
FR = {1: '2026-11-10T15:00:00+00:00', 2: '2026-11-11T10:00:00+00:00'}


def load(p):
    sp = importlib.util.spec_from_file_location('mm2', p); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


def score(K, data, arm, asof, trades_fn=None):
    trades_fn = trades_fn or K.trades
    fz = K.ts(FR[arm]); minhist = 0 if arm == 1 else K.MIN_HIST
    rows = []
    for s, ms in data.items():
        ev = collections.defaultdict(list)
        for m in ms: ev[m['event_ticker']].append(m)
        E = []
        for et, L in ev.items():
            res = all(m['result'] in ('yes', 'no') for m in L) and len(L) >= K.MIN_MARKETS
            E.append(dict(et=et, L=L, t0=min(K.ts(m['open_time']) for m in L), res=res,
                          Kt=max(min(K.ts(m['close_time']), K.ts(m['settlement_ts']) if m.get('settlement_ts') else 9e18) for m in L)))
        for e in E:
            if e['t0'] < fz or len(e['L']) < K.MIN_MARKETS: continue
            hist = [h for h in E if h['res'] and h['Kt'] < e['t0']]
            r = dict(event=e['et'], series=s, start=dt.datetime.fromtimestamp(e['t0'], dt.timezone.utc).isoformat(), resolved=e['res'], hist=len(hist), eligible=len(hist) >= minhist, bet=None, LS=[], fills=[])
            window_done = asof >= e['t0'] + K.WINDOW
            if not r['eligible'] or not window_done: rows.append(r); continue
            wh = collections.defaultdict(lambda: [0, 0]); tot = [0, 0]
            for h in hist:
                for m in h['L']:
                    y = 1 if m['result'] == 'yes' else 0; k = wh[K.norm(m['yes_sub_title'])]; k[0] += 1; k[1] += y; tot[0] += 1; tot[1] += y
            gp = tot[1] / max(1, tot[0]); cand = []
            for m in e['L']:
                q = (wh[K.norm(m['yes_sub_title'])][1] + K.ALPHA * gp) / (wh[K.norm(m['yes_sub_title'])][0] + K.ALPHA)
                w = (1 if m['result'] == 'yes' else 0) if e['res'] else None
                pr = [x for x in trades_fn(m) if e['t0'] <= x[0] <= e['t0'] + K.WINDOW and x[4] > 0]
                if pr and w is not None:
                    mk = min(max(pr[0][2], .01), .99); qq = min(max(q, .01), .99)
                    r['LS'].append((w * math.log(qq) + (1 - w) * math.log(1 - qq)) - (w * math.log(mk) + (1 - w) * math.log(1 - mk)))
                for (t, side, yp, np_, sz) in pr:
                    oi, p = (0, yp) if side == 'yes' else (1, np_)
                    if not (K.PMIN <= p <= K.PMAX): continue
                    if w is not None: r['fills'].append((oi, p, sz, w))
                    if ((q - p) if oi == 0 else ((1 - q) - p)) >= K.THR: cand.append((t, oi, p, sz, m, q, w if w is not None else 0))
            if cand:
                t, oi, p, sz, m, q, _ = min(cand, key=lambda c: (c[0], c[1], c[2], c[3], c[6]))  # same tie-break as mm_forward2 (tuple min)
                b = dict(word=m['yes_sub_title'], side='YES' if oi == 0 else 'NO', price=p, size=sz, q=round(q, 4), fee=K.fee(p, sz), cost=round(p * sz, 4), oi=oi)
                if e['res']:
                    w = 1 if m['result'] == 'yes' else 0; b['w'] = w; b['pnl_gross'] = ((w if oi == 0 else 1 - w) - p) * sz; b['pnl_net'] = b['pnl_gross'] - b['fee']
                else:
                    lp = m.get('last_price_dollars'); lp = float(lp) if lp not in (None, '') else None
                    if lp is not None: b['mark'] = ((lp if oi == 0 else 1 - lp) - p) * sz - b['fee']
                r['bet'] = b
            rows.append(r)
    return rows


def summarize(rows, arm, asof):
    sc = [r for r in rows if r['resolved'] and r['eligible']]; br = [r for r in sc if r['bet']]
    bp = [r for r in rows if r['bet'] and not r['resolved']]
    net = [r['bet']['pnl_net'] for r in br]; gross = sum(r['bet']['pnl_gross'] for r in br)
    d = []
    for r in br:
        b = r['bet']; f = [x for x in r['fills'] if x[0] == b['oi']]
        if f: d.append(b['pnl_gross'] - S.mean(((x[3] if x[0] == 0 else 1 - x[3]) - x[1]) * b['size'] for x in f))
    wk = collections.defaultdict(float)
    for r in br: wk[dt.datetime.fromisoformat(r['start']).strftime('%G-W%V')] += r['bet']['pnl_net']
    ls = [x for r in sc for x in r['LS']]; srt = sorted(net, reverse=True); days = max(1.0, (asof - FRz[arm]) / 86400)
    ts_ = lambda v: None if len(v) < 3 or S.stdev(v) == 0 else round(S.mean(v) / S.stdev(v) * math.sqrt(len(v)), 2)
    return dict(asof=dt.datetime.fromtimestamp(asof, dt.timezone.utc).strftime('%Y-%m-%d'), arm=arm, forward_events=len(rows), eligible=sum(r['eligible'] for r in rows), scored_events=len(sc),
                bets_resolved=len(br), wins=sum(1 for r in br if r['bet']['pnl_gross'] > 0), pending_bets=len(bp), cost=round(sum(r['bet']['cost'] for r in br), 2),
                gross=round(gross, 2), fees=round(sum(r['bet']['fee'] for r in br), 2), net=round(sum(net), 2), net_per_day=round(sum(net) / days, 3),
                pending_mark=round(sum(r['bet'].get('mark', 0) for r in bp), 2), paired_t=ts_(d), logscore=None if len(ls) < 3 else round(S.mean(ls), 4),
                top3_share=None if not net or sum(net) <= 0 else round(sum(srt[:3]) / sum(net), 2), week_cluster_t=ts_(list(wk.values())), days=round(days, 2),
                verdict=('not yet defined: needs 100 events with a bet (have %d)' % len(br)) if len(br) < 100 else 'DECISION DUE: apply PREREG rule (net>0, paired t>=2, log score>0, top3<50%, cluster t>1.5)')


def write(out, rows, s):
    os.makedirs(out, exist_ok=True); a = s['arm']
    json.dump(dict(summary=s, events=[{k: v for k, v in r.items() if k not in ('fills', 'LS')} for r in rows]), open(os.path.join(out, 'kalshi_arm%d_events_%s.json' % (a, s['asof'])), 'w'), indent=1)
    fn = os.path.join(out, 'kalshi_arm%d_daily.csv' % a); old = []
    if os.path.exists(fn): old = [r for r in csv.DictReader(open(fn)) if r['asof'] != s['asof']]
    cols = [k for k in s if k != 'verdict']
    with open(fn, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction='ignore'); w.writeheader(); w.writerows(old + [s])
    txt = ('Mentions forward test, KALSHI arm %d, %s (freeze %s, 3c, paper only)\n' % (a, s['asof'], FR[a]) +
           'forward events %d (eligible %d, scored/resolved %d); bets resolved %d (wins %d, cost $%.2f), pending bets %d\n' % (s['forward_events'], s['eligible'], s['scored_events'], s['bets_resolved'], s['wins'], s['cost'], s['pending_bets']) +
           'NET P&L after Kalshi taker fees (resolved only): $%.2f (gross %.2f, fees %.2f) = $%.3f/day over %.1f days\n' % (s['net'], s['gross'], s['fees'], s['net_per_day'], s['days']) +
           'pending entries marked to last price (UNRESOLVED, information only): $%.2f\n' % s['pending_mark'] +
           'paired t %s | log score %s | top3 share %s | week-cluster t %s\n%s\n' % (s['paired_t'], s['logscore'], s['top3_share'], s['week_cluster_t'], s['verdict']))
    open(os.path.join(out, 'LATEST-kalshi-arm%d.txt' % a), 'w').write(txt); return txt


FRz = {}
if __name__ == '__main__':
    a = ap.parse_args(); K = load(a.mm2); FRz.update({k: K.ts(v) for k, v in FR.items()})
    asof = K.ts(a.asof) if a.asof else time.time()
    ser = sorted(K.ARM1) if a.arm == 1 else sorted(set(x['ticker'] for x in K.g(K.B + 'series?category=Mentions')['series']) - K.ARM1)
    with cf.ThreadPoolExecutor(6) as ex: data = dict(ex.map(K.pull_series, ser))
    rows = score(K, data, a.arm, asof); print(write(a.out, rows, summarize(rows, a.arm, asof)))
