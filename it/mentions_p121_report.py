#!/usr/bin/env python3
"""P147: READ-ONLY report on the P121 WS paper logger output (mentions will-say decisions + earnings-beat books). Paper only, public Gamma reads, no orders, no keys.

Usage: python3 -I mentions_p121_report.py --scorer PATH/mentions_pm_daily_scorer.py --state STATE_DIR --out P121_DIR [--beat-from-books] [--cap 200]
  --out is the P121 output folder (decisions.jsonl, fills.jsonl, runs.jsonl, earnings_beat/books.jsonl).
Prints, in this order (the FIRST NUMBER is line 'FIRST NUMBER'):
  A. will-say decisions: counts, resolved vs pending, TAKE results at resolution per variant, for the frozen setting (KEEP_THRESHOLD off, as logged)
     and for KEEP_THRESHOLD on (logged takes re-priced with the on-key base rate; a take that would be LARGER under on is not observable because P121 logs only tokens that
     cleared 10c under off: reported as 'on-only unobservable', never invented).
  B. earnings-beat daily forward list from the recorded YES books (family=earnings_beat): markets with a YES best ask under 50c before the report, depth at asks under 50c capped at $cap.
Writes REPORT-<utc date>.txt in --out/reports/."""
import argparse, collections, datetime as dt, importlib.util, json, os, sys


def load(n, p):
    sp = importlib.util.spec_from_file_location(n, p); m = importlib.util.module_from_spec(sp); sys.modules[n] = m; sp.loader.exec_module(m); return m


def pnl_take(r, w, levels=None):
    """P&L of the logged TAKE at resolution (same formula as the logger's --score): shares won pay 1, cost, taker fee 0.04-style rate from the market."""
    tk = r['take']; lv = tk['levels'] if levels is None else levels
    size = sum(s for p, s in lv); cost = sum(p * s for p, s in lv)
    if size <= 0: return 0.0, 0.0, 0.0
    avg = cost / size; oi = 0 if r['side'] == 'YES' else 1
    return cost, ((w if oi == 0 else 1 - w) * size) - cost - r['fee_rate'] * avg * (1 - avg) * size, size


def reprice_on(r, q_on):
    """Re-price a logged TAKE under the on-key base rate. Returns (status, levels). status: 'same' | 'shrunk' | 'dropped' | 'on_only_more' (limit would be higher, logged ladder is cut at the old limit)."""
    oi = 0 if r['side'] == 'YES' else 1; fair = q_on if oi == 0 else 1 - q_on; lim = fair - .10
    if lim > r['limit'] + 1e-9: return 'on_only_more', r['take']['levels']
    lv = [x for x in r['take']['levels'] if x[0] <= lim + 1e-12]
    if not lv: return 'dropped', []
    return ('same' if len(lv) == len(r['take']['levels']) else 'shrunk'), lv


def beat_list(rows, ends, cap=200.0, thr=.50, now=None):
    """rows: earnings_beat book rows (YES token = oi 0). ends: event id -> end epoch (None unknown). Per market: the recorded minute with the lowest YES best ask under thr, before the report."""
    best = {}
    for r in rows:
        if r.get('oi') != 0 or r.get('best_ask') is None: continue
        end = ends.get(r['event'])
        if end is not None and r['t'] > end: continue
        if r['best_ask'] < thr and (r['cond'] not in best or r['best_ask'] < best[r['cond']]['best_ask']): best[r['cond']] = r
    out = []
    for cond, r in best.items():
        left = cap; cost = size = 0.0
        for p, s in r['asks']:
            if p >= thr or left <= 1e-9: break
            take = min(s, left / p); left -= take * p; cost += take * p; size += take
        out.append(dict(event=r['event'], title=r['title'], t=r['t'], best_ask=r['best_ask'], depth_usd_under_thr=round(cost, 2), avg=round(cost / size, 4) if size else None, shares=round(size, 2), levels_logged=len(r['asks']), hours_to_end=None if ends.get(r['event']) is None else round((ends[r['event']] - r['t']) / 3600, 1)))
    return sorted(out, key=lambda x: x['t'])


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--scorer', required=True); ap.add_argument('--state', required=True); ap.add_argument('--out', required=True); ap.add_argument('--cap', type=float, default=200.)
    a = ap.parse_args(); sc = load('sc', a.scorer); L = []
    P = lambda s='': (L.append(s), print(s))
    dec = [json.loads(l) for l in open(os.path.join(a.out, 'decisions.jsonl'))] if os.path.exists(os.path.join(a.out, 'decisions.jsonl')) else []
    P('P121 REPORT %s UTC, folder %s' % (dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%d %H:%M'), a.out))
    P('A. will-say decisions logged: %d (decisions.jsonl); first %s, last %s' % (len(dec), dt.datetime.fromtimestamp(dec[0]['ts'], dt.timezone.utc).isoformat() if dec else '-', dt.datetime.fromtimestamp(dec[-1]['ts'], dt.timezone.utc).isoformat() if dec else '-'))
    pool_raw = list(json.load(open(os.path.join(a.state, 'events.json'))).values()); cache = {}
    sc.KEEP_THRESHOLD = False; res = collections.defaultdict(lambda: dict(n=0, cost=0.0, net=0.0)); pend = collections.Counter(); chk = [0, 0]; onst = collections.Counter(); ev_rows = collections.defaultdict(lambda: dict(n=0, cost=0.0, net=0.0, title=''))
    for r in dec:
        eid = r['event']
        if eid not in cache:
            x = sc.fetch(f"{sc.GAMMA}/events?id={eid}"); cache[eid] = (sc.slim(x[0]), x[0]) if x else None
        c = cache[eid]
        if c is None: pend['gamma-missing'] += 1; continue
        e, raw = c
        if not sc.resolved(e): pend[r['variant']] += 1; continue
        m = next((m for m in e['markets'] if m['cond'] == r['cond']), None)
        if m is None: continue
        w = sc.win(m); cost, net, size = pnl_take(r, w)
        if size <= 0: continue
        k = (r['variant'], 'off (frozen, as logged)'); g = res[k]; g['n'] += 1; g['cost'] += cost; g['net'] += net
        er = ev_rows[eid]; er['n'] += 1; er['cost'] += cost; er['net'] += net; er['title'] = e['title'][:60]
        # on-key recompute (history = settled before this event's start, same family, words re-keyed from labels)
        t0 = sc.start(e); sc.KEEP_THRESHOLD = True
        e_on = sc.slim(raw); m_on = next((mm for mm in e_on['markets'] if mm['cond'] == r['cond']), None)
        hist = []
        for h in pool_raw:
            if h['fam'] != e['fam'] or h['id'] == e['id'] or not sc.resolved(h) or sc.settled_at(h) > t0: continue
            hist.append(dict(h, markets=[dict(mm, word=sc.wkey(mm.get('label'))) for mm in h['markets']]))
        q_on = sc.q_for(hist, e_on, m_on); sc.KEEP_THRESHOLD = False
        hist_off = [h for h in pool_raw if h['fam'] == e['fam'] and h['id'] != e['id'] and sc.resolved(h) and sc.settled_at(h) <= t0]
        q_off = sc.q_for(hist_off, e, m); fair_off = q_off if r['side'] == 'YES' else 1 - q_off
        chk[1] += 1; chk[0] += abs(fair_off - r['fair']) < 2e-3
        st, lv = reprice_on(r, q_on); onst[st] += 1
        if st == 'dropped': continue
        cost2, net2, _ = pnl_take(r, w, lv); k2 = (r['variant'], 'on (KEEP_THRESHOLD, logged takes re-priced)'); g2 = res[k2]; g2['n'] += 1; g2['cost'] += cost2; g2['net'] += net2
    P('   resolved takes by variant and setting (net after taker fee, at resolution):')
    for k, g in sorted(res.items()): P('   %-10s %-46s n %3d  cost $%8.2f  net $%8.2f' % (k[0], k[1], g['n'], g['cost'], g['net']))
    P('   pending (event not resolved yet) by variant: %s' % (dict(pend) or 'none'))
    P('   KEEP_THRESHOLD on, status of the %d resolved takes: %s ("on_only_more" = the on key would take MORE than logged: not observable, P121 logs only tokens that cleared 10c under off; "dropped" = no longer 10c under the on key)' % (sum(onst.values()), dict(onst) or 'none'))
    P('   sanity: recomputed off-key fair equals the logged fair on %d of %d resolved takes (a mismatch means the state file or code differs from the logger)' % (chk[0], chk[1]))
    for eid, g in sorted(ev_rows.items(), key=lambda kv: kv[0]): P('   event %s %s: %d takes, cost $%.2f, net $%.2f' % (eid, g['title'], g['n'], g['cost'], g['net']))
    tot = res.get(('listing', 'off (frozen, as logged)'))
    allnet = sum(g['net'] for k, g in res.items() if k[1].startswith('off')); alln = sum(g['n'] for k, g in res.items() if k[1].startswith('off'))
    P('FIRST NUMBER: %d resolved paper takes from %d logged decisions, net $%.2f after fees at own-token asks (frozen setting). FLOOR/UNPROVEN until n >= 100 bets; one decision slot can repeat the same token, so n counts takes, not independent bets.' % (alln, len(dec), allnet))
    # B earnings-beat
    bf = os.path.join(a.out, 'earnings_beat', 'books.jsonl'); rows = [json.loads(l) for l in open(bf)] if os.path.exists(bf) else []
    P('B. earnings-beat YES-book forward list (family=earnings_beat): %d book rows' % len(rows))
    ends = {}
    for eid in {r['event'] for r in rows}:
        x = sc.fetch(f"{sc.GAMMA}/events?id={eid}")
        try: ends[eid] = sc.ts(x[0]['endDate']) if x else None
        except Exception: ends[eid] = None
    bl = beat_list(rows, ends, a.cap)
    P('   markets with a recorded YES best ask under 0.50 before the report: %d of %d markets recorded' % (len(bl), len({r['cond'] for r in rows})))
    for b in bl: P('   %s | %s | YES ask %.3f at %s | $%.2f at asks under 0.50 (cap $%d), avg %s, %s sh, %s ask levels logged | %s h before end' % (b['event'], b['title'][:44], b['best_ask'], dt.datetime.fromtimestamp(b['t'], dt.timezone.utc).strftime('%d %H:%MZ'), b['depth_usd_under_thr'], a.cap, b['avg'], b['shares'], b['levels_logged'], b['hours_to_end']))
    os.makedirs(os.path.join(a.out, 'reports'), exist_ok=True)
    open(os.path.join(a.out, 'reports', 'REPORT-%s.txt' % dt.datetime.now(dt.timezone.utc).strftime('%Y%m%d')), 'w').write('\n'.join(L) + '\n')


if __name__ == '__main__': sys.exit(main() or 0)
