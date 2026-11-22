#!/usr/bin/env python3
"""R-047/R-048: every OPEN Polymarket mentions event (gamma tag mention-markets): per token own-book ask $ (full ladder, and edge-priced = asks <= fair-10c), model side and fair,
Gamma 24h/total volume; plus a deep dive for chosen events (full ladder per strike, trade times vs market start, would the frozen rule have bet).
Usage: python3 -I mentions_pm_open_depth.py --scorer PATH --state DIR --out PREFIX [--deep SLUGPART ...]
Snapshot time is NOT decision time. Edge-priced depth is the capacity that the 10c rule could have lifted at these prices; full-ladder is shown beside it, never instead of it."""
import argparse, csv, datetime as dt, importlib.util, json, statistics as S, sys, time, collections
ap = argparse.ArgumentParser(); ap.add_argument('--scorer', required=True); ap.add_argument('--state', required=True); ap.add_argument('--out', required=True); ap.add_argument('--deep', nargs='*', default=[])


def load(p):
    sp = importlib.util.spec_from_file_location('sc', p); m = importlib.util.module_from_spec(sp); sys.modules['sc'] = m; sp.loader.exec_module(m); return m


def ladder_usd(asks, lo=0.0, hi=1.0): return sum(p * s for p, s in asks if lo <= p <= hi)


def token_row(asks, q, oi, thr=.10):
    fair = q if oi == 0 else 1 - q
    lim = fair - thr
    return dict(side='YES' if oi == 0 else 'NO', fair=round(fair, 3), limit=round(lim, 3), best_ask=min((p for p, _ in asks), default=None), full_usd=round(ladder_usd(asks), 2),
                edge_usd=round(ladder_usd(asks, .05, lim), 2), edge_levels=sum(1 for p, s in asks if .05 <= p <= lim))


def book(sc, tok):
    b = sc.fetch(f'https://clob.polymarket.com/book?token_id={tok}') or {}
    return sorted((float(a['price']), float(a['size'])) for a in b.get('asks', []))


if __name__ == '__main__':
    a = ap.parse_args(); sc = load(a.scorer); now = time.time()
    closed = list(json.load(open(a.state + '/events.json')).values()); pool = [e for e in closed if sc.resolved(e)]
    raw = sc.fetch(f'{sc.GAMMA}/events?tag_slug=mention-markets&closed=false&limit=100&order=startDate&ascending=false') or []
    rows = []; evs = []; deep = {}
    for r in raw:
        e = sc.slim(r); t0 = sc.start(e); hist = [h for h in pool if h['fam'] == e['fam'] and h['id'] != e['id'] and sc.settled_at(h) <= t0]
        tot = dict(full=0.0, edge=0.0, tokens=0, edge_tokens=0); bestedge = 0.0
        for m in e['markets']:
            q = sc.q_for(hist, e, m); toks = {}
            for oi, tok in enumerate(m['toks'][:2]):
                asks = book(sc, tok); tr = token_row(asks, q, oi); toks[oi] = (asks, tr)
                rows.append(dict(event=r['slug'], url='https://polymarket.com/event/' + r['slug'], fam=e['fam'], word=m['label'], q_yes=round(q, 3), vol24h_market=round(float((next((x for x in r['markets'] if x['conditionId'] == m['cond']), {}) or {}).get('volume24hr') or 0)),
                                 vol_total_market=round(float((next((x for x in r['markets'] if x['conditionId'] == m['cond']), {}) or {}).get('volumeNum') or 0)), **tr))
                tot['full'] += tr['full_usd']; tot['edge'] += tr['edge_usd']; tot['tokens'] += 1; tot['edge_tokens'] += tr['edge_usd'] > 0; bestedge = max(bestedge, tr['edge_usd'])
            if any(k in r['slug'] for k in a.deep): deep.setdefault(r['slug'], []).append((m, q, toks))
        evs.append(dict(event=r['slug'], url='https://polymarket.com/event/' + r['slug'], fam=e['fam'], start=r.get('startDate'), vol24h=round(float(r.get('volume24hr') or 0)), vol_total=round(float(r.get('volume') or 0)),
                        liquidity=round(float(r.get('liquidity') or 0)), full_ask_usd_event=round(tot['full']), edge_ask_usd_event=round(tot['edge']), edge_ask_usd_best_token=round(bestedge, 2), tokens=tot['tokens'], tokens_with_edge_depth=tot['edge_tokens']))
    with open(a.out + '_tokens.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    with open(a.out + '_events.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(evs[0].keys())); w.writeheader(); w.writerows(evs)
    for e in evs: print(e['event'][:60], e['fam'], 'vol24h', e['vol24h'], 'total', e['vol_total'], 'full ask $', e['full_ask_usd_event'], 'edge ask $ event', e['edge_ask_usd_event'], 'best token', e['edge_ask_usd_best_token'])
    # deep dive
    out = []
    for slug, items in deep.items():
        r = next(x for x in raw if x['slug'] == slug); e = sc.slim(r); t0 = sc.start(e); hist = [h for h in pool if h['fam'] == e['fam'] and h['id'] != e['id'] and sc.settled_at(h) <= t0]
        tr = {}
        for m in e['markets']:
            _, v = sc.pull_trades(m['cond']); tr[m['cond']] = v or []
        ent = sc.pick_entry(e, hist, tr, t0)
        out.append('## %s\nstart %s end %s; gamma 24h $%s total $%s liquidity $%s' % (slug, r.get('startDate'), r.get('endDate'), round(float(r.get('volume24hr') or 0)), round(float(r.get('volume') or 0)), round(float(r.get('liquidity') or 0))))
        allt = [(t, p * s) for m in e['markets'] for (t, sd, p, s, o) in tr[m['cond']]]
        if allt:
            hrs = collections.Counter(int((t - t0) // 3600) for t, _ in allt); d = collections.defaultdict(float)
            for t, usd in allt: d[int((t - t0) // 3600)] += usd
            tot = sum(u for _, u in allt)
            out.append('trades %d, $%.0f; first %s last %s; $ in first hour %.0f (%.1f%%), first 24h %.0f (%.1f%%), after day 3 %.0f (%.1f%%)' % (len(allt), tot, dt.datetime.fromtimestamp(min(t for t, _ in allt), dt.timezone.utc).strftime('%d %b %H:%MZ'), dt.datetime.fromtimestamp(max(t for t, _ in allt), dt.timezone.utc).strftime('%d %b %H:%MZ'),
                                                                                       d[0], 100 * d[0] / tot, sum(u for h, u in d.items() if h < 24), 100 * sum(u for h, u in d.items() if h < 24) / tot, sum(u for h, u in d.items() if h >= 72), 100 * sum(u for h, u in d.items() if h >= 72) / tot))
            top = sorted(d.items(), key=lambda x: -x[1])[:3]; out.append('busiest hours after start: ' + ', '.join('h+%d $%.0f' % (h, u) for h, u in top))
        if ent:
            t, cond, oi, p, sz, q, word, label, rate, toks = ent
            out.append('RULE WOULD HAVE BET: %s %s at %.3f x %.1f (print $%.2f) at +%.0f min after start, q=%.3f, fee %.3f; market outcome prices now %s' % ('YES' if oi == 0 else 'NO', label, p, sz, p * sz, (t - t0) / 60, q, sc.fee_of(rate, p, sz), next(m for m in e['markets'] if m['cond'] == cond)['prices']))
        else: out.append('RULE WOULD NOT HAVE BET (no first-hour BUY print with edge >= 10c)')
        out.append('| strike | q(YES) | YES asks (price x size, best 6 levels) | YES full $ | YES edge-priced $ | NO asks | NO full $ | NO edge $ | vol24h | vol total |\n|---|---|---|---|---|---|---|---|---|---|')
        for m, q, toks in items:
            gm = next((x for x in r['markets'] if x['conditionId'] == m['cond']), {})
            lv = lambda asks: ' '.join('%.3fx%.0f' % (p, s) for p, s in asks[:6]) or 'none'
            ty, tn = toks[0][1], toks[1][1]
            out.append('| %s | %.3f | %s | %.0f | %.0f | %s | %.0f | %.0f | %.0f | %.0f |' % (m['label'], q, lv(toks[0][0]), ty['full_usd'], ty['edge_usd'], lv(toks[1][0]), tn['full_usd'], tn['edge_usd'], float(gm.get('volume24hr') or 0), float(gm.get('volumeNum') or 0)))
    open(a.out + '_deep.md', 'w').write('\n\n'.join(out) + '\n'); print('\n'.join(out[:6]))
