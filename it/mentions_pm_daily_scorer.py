#!/usr/bin/env python3
"""Daily scorer for the Polymarket mentions FORWARD test (arm: Polymarket 10c, PRIMARY).
Rule source (frozen, no tuning): mentions/PREREG-forward-test-2026-11-10.md + mentions/PREREG-addendum-polymarket-2026-11-10.md
  - tag mention-markets, events whose earliest market startDate >= FREEZE (2026-11-10T15:00Z)
  - per-word base rate q = (wins + 2*gp)/(n + 2), gp = family base rate; history = earlier events whose markets had ALL closed
    before this event's start (causal rule, audit 10 Nov, mentions/audit-polymarket-2026-11-10)
  - entry: first BUY print in the first hour after event start, price 5c..95c, edge >= 10c
    (YES token: q-p, NO token: (1-q)-p); one bet per event; size = the print size; hold to resolution
  - fee: taker, size*rate*p*(1-p) with the market's own feeSchedule rate (mentions_fees, 0.04); 0 if no fee schedule
Real asks: with --books DIR (recorder live/mentions/record_mention_books.py) each bet is re-priced at the first recorded book
  of the bet's OWN token that shows a qualifying ask (never NO from YES). No recorded book => reported as 'no book', never guessed.
Every run writes (OUT): mentions_pm_daily.csv (one row per UTC date, replaced if rerun), mentions_pm_events_<date>.json, LATEST.txt.
A number is produced on day 1 even with 0 resolved events: pending entries marked to the current market price (UNRESOLVED, label says so).
Usage: python3 -I mentions_pm_daily_scorer.py --state DIR --out DIR [--books DIR] [--freeze ISO] [--asof ISO]"""
import argparse, collections, csv, datetime as dt, glob, gzip, json, math, os, re, statistics as S, sys, time, urllib.request
import concurrent.futures as cf

FREEZE = '2026-11-10T15:00:00+00:00'
THR = 0.10            # primary and only decision variant
WIN = 3600            # first hour
ALPHA = 2
GAMMA = 'https://gamma-api.polymarket.com'
DATA = 'https://data-api.polymarket.com'


def fetch(u):
    for a in range(5):
        try:
            d = urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'x', 'Accept-Encoding': 'gzip'}), timeout=60)
            b = d.read()
            if d.headers.get('Content-Encoding') == 'gzip':
                b = gzip.decompress(b)
            return json.loads(b)
        except Exception as e:
            if getattr(e, 'code', 0) == 404:
                return None
            time.sleep(2 * (a + 1))
    return None


def ts(s):
    s = s.replace(' ', 'T').replace('Z', '+00:00')
    if re.search(r'[+-]\d\d$', s):
        s += ':00'
    return dt.datetime.fromisoformat(s).timestamp()


def norm(s):
    return re.sub(r'[^a-z]', '', (s or '').lower())


KEEP_THRESHOLD = False  # R-064 2a: True keeps digits so "AI 5+ times" and "AI 50+ times" are different words. Default False = the FROZEN rule (norm strips digits).


def wkey(s):
    return re.sub(r'[^a-z0-9]', '', (s or '').lower()) if KEEP_THRESHOLD else norm(s)


def fam(title):  # identical to mentions/pm_forward.py
    t = (title or '').lower()
    if 'trump' in t and 'week' in t:
        return 'trump-weekly'
    if 'trump' in t:
        return 'trump-event'
    if 'earnings' in t:
        return 'earnings-call'
    if 'nfl' in t or 'announcer' in t or 'nba' in t or 'game' in t:
        return 'sports-announcers'
    return 'other'


def slim(e):
    """Reduce a gamma event to what the rule needs."""
    ms = []
    for m in e.get('markets', []):
        try:
            p = [float(x) for x in json.loads(m['outcomePrices'])]
            toks = json.loads(m['clobTokenIds'])
        except Exception:
            p, toks = [], []
        fs = m.get('feeSchedule') or {}
        ms.append(dict(cond=m.get('conditionId'), word=wkey(m.get('groupItemTitle') or m.get('question')),
                       label=m.get('groupItemTitle') or m.get('question'), prices=p, toks=toks,
                       closed=bool(m.get('closed')), start=m.get('startDate') or e.get('startDate') or '',
                       closedTime=m.get('closedTime') or m.get('endDate') or '', fee=(fs.get('rate') if m.get('feeType') == 'mentions_fees' or fs else 0) or 0))
    return dict(id=e['id'], title=e.get('title'), fam=fam(e.get('title')), closed=bool(e.get('closed')), markets=ms)


def start(ev):
    return min(ts(m['start']) for m in ev['markets'] if m['start'])


def settled_at(ev):
    try:
        return max(ts(m['closedTime']) for m in ev['markets'])
    except Exception:
        return float('inf')


def resolved(ev):
    """All markets closed and priced at >=0.99 on one side (live markets can sit at 0.995 before closing, so closed flag is required)."""
    return len(ev['markets']) >= 3 and all(m['closed'] and m['prices'] and max(m['prices']) >= .99 for m in ev['markets'])


def win(m):
    return 1 if m['prices'][0] > .5 else 0


def q_for(hist_events, ev, m):
    """Per-word base rate from the supplied (already causal) history of the same family."""
    wins = n = fw = ft = 0
    for h in hist_events:
        for hm in h['markets']:
            ft += 1
            fw += win(hm)
            if hm['word'] == m['word']:
                n += 1
                wins += win(hm)
    gp = fw / max(1, ft)
    return (wins + ALPHA * gp) / (n + ALPHA)


def pick_entry(ev, hist, trades, t0, thr=THR):
    """First qualifying BUY print in [t0, t0+WIN]. trades: cond -> list of (t, side, price, size, outcome_index)."""
    cand = []
    for m in ev['markets']:
        q = q_for(hist, ev, m)
        for (t, side, p, sz, oi) in trades.get(m['cond'], []):
            if not (t0 <= t <= t0 + WIN) or side != 'BUY' or sz <= 0 or not (.05 <= p <= .95):
                continue
            edge = (q - p) if oi == 0 else ((1 - q) - p)
            if edge >= thr:
                cand.append((t, m['cond'], oi, p, sz, q, m['word'], m['label'], m['fee'], m['toks']))
    return min(cand, key=lambda c: c[0]) if cand else None


def fee_of(rate, p, sz):
    return sz * rate * p * (1 - p)


def pnl(oi, p, sz, w, rate):
    return ((w if oi == 0 else 1 - w) - p) * sz - fee_of(rate, p, sz)


def placebo(ev, entry, trades, t0):
    """Same-event, same-side random-print placebo at the bet's own size (net of the same fee)."""
    _, cond, oi, _, sz, _, _, _, rate, _ = entry
    xs = []
    for m in ev['markets']:
        for (t, side, p, s, o) in trades.get(m['cond'], []):
            if t0 <= t <= t0 + WIN and side == 'BUY' and s > 0 and .05 <= p <= .95 and o == oi:
                xs.append(pnl(o, p, sz, win(m), m['fee']))
    return S.mean(xs) if xs else None


def tstat(v):
    if len(v) < 3 or S.stdev(v) == 0:
        return None
    return S.mean(v) / S.stdev(v) * math.sqrt(len(v))


def book_fill(entry, books):
    """Re-price at the first recorded book of the bet's own token with a qualifying ask. books: cond -> [(t, token_idx, asks[(price,size)])]."""
    t_e, cond, oi, p, sz, q, *_ = entry
    snaps = [b for b in books.get(cond, []) if b[1] == oi]
    if not snaps:
        return dict(status='no book of own token recorded')
    lim = (q - THR) if oi == 0 else ((1 - q) - THR)
    for (t, idx, asks) in sorted(snaps, key=lambda b: b[0]):
        lv = [(pr, s) for pr, s in sorted(asks) if .05 <= pr <= lim]
        if lv:
            take, cost, left = 0.0, 0.0, sz   # same size as the print, walking the asks
            for pr, s in lv:
                x = min(s, left)
                take += x
                cost += x * pr
                left -= x
                if left <= 0:
                    break
            return dict(status='filled' if take > 0 else 'no depth', t=t, size=take, avg=cost / take if take else None, best=lv[0][0], first_snapshot=sorted(snaps)[0][0])
    return dict(status='no qualifying ask in %d snapshots' % len(snaps))


def load_books(d):
    out = collections.defaultdict(list)
    for fn in sorted(glob.glob(os.path.join(d, 'books_*.jsonl*'))) if d else []:
        op = gzip.open if fn.endswith('.gz') else open
        with op(fn, 'rt') as f:
            for line in f:
                try:
                    r = json.loads(line)
                except Exception:
                    continue
                if r.get('venue') != 'polymarket':
                    continue
                b = r.get('book') or {}
                out[r['market']].append((r['t'], r.get('token_index', 0), [(float(a['price']), float(a['size'])) for a in b.get('asks', [])]))
    return out


def enum_closed(state, since):
    """Closed events (tag mention-markets) by end-date window, cached in state/events.json (slim)."""
    cache = {}
    fn = os.path.join(state, 'events.json')
    if os.path.exists(fn):
        cache = json.load(open(fn))
    d = since if cache else dt.date(2024, 6, 1)
    d = min(d, dt.date.today() - dt.timedelta(days=45)) if cache else d
    end = dt.date.today() + dt.timedelta(days=2)
    while d < end:
        e = d + dt.timedelta(days=15)
        off = 0
        while True:
            r = fetch(f'{GAMMA}/events?tag_slug=mention-markets&closed=true&end_date_min={d}&end_date_max={e}&limit=100&offset={off}')
            if r is None:
                raise SystemExit('gamma fetch failed for window %s' % d)
            for x in r:
                cache[x['id']] = slim(x)
            if len(r) < 100:
                break
            off += 100
        d = e
    json.dump(cache, open(fn, 'w'))
    return list(cache.values())


def open_events(page=50, maxpages=10):
    """R-076: open mention events paged at limit=50 (Gamma has answered HTTP 406 to limit=100). Returns None if any page failed, never a silent empty list."""
    out = []
    for i in range(maxpages):
        r = fetch(f'{GAMMA}/events?tag_slug=mention-markets&closed=false&limit={page}&offset={i * page}&order=startDate&ascending=false')
        if r is None:
            return None
        out += r
        if len(r) < page:
            break
    return out


def trades_url(cond, cur=None):
    """R-080: data-api v2 silently IGNORES unknown params; only condition_id / condition / conditionId filter. 'condition' is the one used here."""
    return f'{DATA}/v2/trades?condition={cond}&limit=500' + (f'&cursor={cur}' if cur else '')


def rows_match(rows, cond):
    """R-080: every returned row must belong to the requested condition (a wrongly named filter returns OTHER markets' trades)."""
    return all(x.get('condition_id') == cond for x in rows)


def pull_trades(cond):
    out, cur = [], None
    for _ in range(150):
        r = fetch(trades_url(cond, cur))
        if r is None:
            return cond, None
        if not rows_match(r['data'], cond):
            import sys
            sys.stderr.write('trades: rows for another condition than %s; treating as a failed read\n' % cond)
            return cond, None
        out += [(x['timestamp'], x['side'], x['price'], x['size'], x['outcome_index']) for x in r['data']]
        p = r['pagination']
        cur = p.get('next_cursor')
        if not p.get('has_more') or not cur:
            break
    return cond, out


def run(closed, open_ev, trades, books, freeze, asof):
    allev = {e['id']: e for e in closed}
    for e in open_ev:
        allev[e['id']] = e
    hist_pool = [e for e in allev.values() if resolved(e)]
    fwd = sorted([e for e in allev.values() if e['markets'] and start(e) >= freeze], key=start)
    rows = []
    for ev in fwd:
        t0 = start(ev)
        res = resolved(ev)
        window_done = asof >= t0 + WIN
        hist = [h for h in hist_pool if h['fam'] == ev['fam'] and h['id'] != ev['id'] and settled_at(h) <= t0]
        entry = pick_entry(ev, hist, trades, t0) if window_done else None
        r = dict(id=ev['id'], title=ev['title'], fam=ev['fam'], start=dt.datetime.fromtimestamp(t0, dt.timezone.utc).isoformat(), n_markets=len(ev['markets']),
                 status=('resolved' if res else 'open'), window_done=window_done, hist_events=len(hist), bet=None)
        if entry:
            t, cond, oi, p, sz, q, word, label, rate, toks = entry
            m = next(m for m in ev['markets'] if m['cond'] == cond)
            b = dict(word=label, side='YES' if oi == 0 else 'NO', price=p, size=sz, q=round(q, 4), t_offset_min=round((t - t0) / 60, 1), fee=round(fee_of(rate, p, sz), 4), cost=round(p * sz, 4))
            if res:
                w = win(m)
                b['won'] = (w if oi == 0 else 1 - w) == 1
                b['pnl_net'] = round(pnl(oi, p, sz, w, rate), 4)
                pl = placebo(ev, entry, trades, t0)
                b['placebo'] = None if pl is None else round(pl, 4)
            else:  # mark to the current price of the bet's own token (UNRESOLVED, information only)
                cur = m['prices'][oi] if len(m['prices']) > oi else None
                if cur is not None:
                    b['mark'] = round((cur - p) * sz - fee_of(rate, p, sz), 4)
            b['book'] = book_fill(entry, books) if books else dict(status='no --books given')
            r['bet'] = b
            r['_log'] = None
        # log score vs market first print, resolved events only (frozen definition)
        if res and window_done:
            ls = []
            for m in ev['markets']:
                pr = sorted([x for x in trades.get(m['cond'], []) if t0 <= x[0] <= t0 + WIN and x[1] == 'BUY' and x[3] > 0])
                if pr:
                    qq = min(max(q_for(hist, ev, m), .01), .99)
                    mk = pr[0][2] if pr[0][4] == 0 else 1 - pr[0][2]
                    mk = min(max(mk, .01), .99)
                    w = win(m)
                    ls.append((w * math.log(qq) + (1 - w) * math.log(1 - qq)) - (w * math.log(mk) + (1 - w) * math.log(1 - mk)))
            r['_log'] = ls
        rows.append(r)
    return rows


def summarize(rows, asof, freeze):
    done = [r for r in rows if r['status'] == 'resolved' and r['window_done']]
    bets_res = [r for r in done if r['bet']]
    bets_pend = [r for r in rows if r['bet'] and r['status'] == 'open']
    net = [r['bet']['pnl_net'] for r in bets_res]
    cost = sum(r['bet']['cost'] for r in bets_res)
    d = [r['bet']['pnl_net'] - r['bet']['placebo'] for r in bets_res if r['bet'].get('placebo') is not None]
    srt = sorted(net, reverse=True)
    wk = collections.defaultdict(float)
    for r in bets_res:
        wk[dt.datetime.fromisoformat(r['start']).strftime('%G-W%V')] += r['bet']['pnl_net']
    ls = [x for r in done for x in (r.get('_log') or [])]
    days = max(1.0, (asof - ts(freeze)) / 86400)
    s = dict(asof=dt.datetime.fromtimestamp(asof, dt.timezone.utc).strftime('%Y-%m-%d'), forward_events=len(rows), resolved_events=len(done),
             open_events=len(rows) - len(done), resolved_with_bet=len(bets_res), pending_bets=len(bets_pend),
             wins=sum(1 for r in bets_res if r['bet']['won']), cost=round(cost, 2), net_pnl=round(sum(net), 2),
             net_per_day=round(sum(net) / days, 3), pending_mark=round(sum(r['bet'].get('mark', 0) for r in bets_pend), 2),
             paired_t=None if tstat(d) is None else round(tstat(d), 2), top3_share=None if not net or sum(net) <= 0 else round(sum(srt[:3]) / sum(net), 2),
             week_cluster_t=None if tstat(list(wk.values())) is None else round(tstat(list(wk.values())), 2),
             logscore=None if len(ls) < 3 else round(S.mean(ls), 4), events_to_100_with_bet=max(0, 100 - len(bets_res)),
             books_with_fill=sum(1 for r in rows if r['bet'] and r['bet'].get('book', {}).get('status') == 'filled'),
             days_since_freeze=round(days, 2))
    s['verdict'] = ('PASS/FAIL not yet defined: needs 100 events with a bet (have %d)' % len(bets_res)) if len(bets_res) < 100 else 'DECISION DUE: apply PREREG rule (paired t>=2, log score>0, top3<50%, cluster t>1.5)'
    return s


def write(out, rows, s):
    os.makedirs(out, exist_ok=True)
    ev = [{k: v for k, v in r.items() if k != '_log'} for r in rows]
    json.dump(dict(summary=s, events=ev), open(os.path.join(out, 'mentions_pm_events_%s.json' % s['asof']), 'w'), indent=1)
    fn = os.path.join(out, 'mentions_pm_daily.csv')
    old = []
    if os.path.exists(fn):
        old = [r for r in csv.DictReader(open(fn)) if r['asof'] != s['asof']]
    cols = [k for k in s if k != 'verdict']
    with open(fn, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction='ignore')
        w.writeheader()
        w.writerows(old + [s])
    txt = ('Mentions forward test, Polymarket 10c arm, %s (freeze %s, paper only)\n' % (s['asof'], FREEZE) +
           'forward events %d (resolved %d, open %d); bets resolved %d (wins %d, cost $%.2f), pending bets %d\n' % (s['forward_events'], s['resolved_events'], s['open_events'], s['resolved_with_bet'], s['wins'], s['cost'], s['pending_bets']) +
           'NET P&L after fees (resolved only): $%.2f  = $%.3f/day over %.1f days since freeze\n' % (s['net_pnl'], s['net_per_day'], s['days_since_freeze']) +
           'pending entries marked to current price (UNRESOLVED, information only): $%.2f\n' % s['pending_mark'] +
           'paired t vs same-event placebo %s | log score %s | top3 share %s | week-cluster t %s | bets with a recorded own-token book fill %d\n' % (s['paired_t'], s['logscore'], s['top3_share'], s['week_cluster_t'], s['books_with_fill']) + s['verdict'] + '\n')
    open(os.path.join(out, 'LATEST.txt'), 'w').write(txt)
    return txt


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--state', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--books', default=None)
    ap.add_argument('--freeze', default=FREEZE)
    ap.add_argument('--asof', default=None)
    a = ap.parse_args()
    os.makedirs(a.state, exist_ok=True)
    asof = ts(a.asof) if a.asof else time.time()
    closed = enum_closed(a.state, dt.date.today() - dt.timedelta(days=45))
    open_raw = fetch(f'{GAMMA}/events?tag_slug=mention-markets&closed=false&limit=100&order=startDate&ascending=false') or []
    open_ev = [slim(e) for e in open_raw]
    fz = ts(a.freeze)
    allev = {e['id']: e for e in closed}
    allev.update({e['id']: e for e in open_ev})
    conds = [m['cond'] for e in allev.values() if e['markets'] and start(e) >= fz for m in e['markets']]
    with cf.ThreadPoolExecutor(8) as ex:
        trades = dict(ex.map(pull_trades, conds))
    miss = [c for c, v in trades.items() if v is None]
    if miss:
        raise SystemExit('trade pull failed for %d markets (e.g. %s): refusing to write a number' % (len(miss), miss[0]))
    rows = run(closed, open_ev, trades, load_books(a.books), fz, asof)
    s = summarize(rows, asof, a.freeze)
    print(write(a.out, rows, s))


if __name__ == '__main__':
    main()
