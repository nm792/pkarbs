"""Alert-only MECE scanner loop. Never places orders.

  python3 scanner/run.py --minutes 2880 --poll 60 --log alerts.jsonl [--venues pm,kalshi]

Each cycle: fetch books for every leg in the hot list (one POST /books batch for Polymarket,
one GET per Kalshi market), price every structure at executable depth, apply guards, update
alert state. Structures whose venues are not all in --venues are still priced and logged but
marked alert_only (e.g. Kalshi pairs while the Kalshi account is not verified)."""
import argparse, json, os, sys, time, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from books import pm_book, kalshi_books
from engine import walk
from guards import check, tradeable
from persist import Tracker
from structures import senate_structures, race_structures
from discover import screen_negrisk, auto_ladders

UA = {'User-Agent': 'Mozilla/5.0', 'Content-Type': 'application/json'}
CLOB = 'https://clob.polymarket.com'; GAMMA = 'https://gamma-api.polymarket.com'
KAL = 'https://api.elections.kalshi.com/trade-api/v2'

def _get(url, body=None, timeout=20):
    req = urllib.request.Request(url, data=None if body is None else json.dumps(body).encode(), headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r: return json.loads(r.read())

def legs_of(structs):
    return sorted({l for s in structs for b in s['buckets'] for i in b['instruments'] for l in i['legs']})

def fetch_books(legs, fee_rates=None):
    now = time.time(); out = {}
    pm = [l[3:] for l in legs if l.startswith('pm:')]
    for i in range(0, len(pm), 200):
        for raw in _get(CLOB + '/books', [{'token_id': t} for t in pm[i:i + 200]]):
            out['pm:' + raw['asset_id']] = pm_book(raw, fetched=now, fee_rate=(fee_rates or {}).get(raw['asset_id'], 0.0))
    for t in sorted({l.split(':')[1] for l in legs if l.startswith('k:')}):
        y, n = kalshi_books(_get(f'{KAL}/markets/{t}/orderbook'), fetched=time.time())
        out[f'k:{t}:yes'] = y; out[f'k:{t}:no'] = n
    return out

def discover(tags=('midterms', 'politics')):
    evs = {}
    for tag in tags:
        cur = None
        for _ in range(30):
            q = f'{GAMMA}/events/keyset?tag_slug={tag}&closed=false&limit=100' + (f'&after_cursor={cur}' if cur else '')
            d = _get(q, timeout=60); evs.update({e['id']: e for e in d.get('events', [])})
            cur = d.get('next_cursor')
            if not cur: break
    evs = list(evs.values())
    fee = {}
    for e in evs:
        for m in e.get('markets', []):
            r = (m.get('feeSchedule') or {}).get('rate') or 0
            for t in json.loads(m.get('clobTokenIds') or '[]'): fee[t] = r
    return screen_negrisk(evs) + auto_ladders(evs), fee

def evaluate(structs, books, now, venues_ok, min_edge, min_profit):
    rows = []
    for s in structs:
        bad = check(s, books, now)
        r = walk(s, books, min_edge=min_edge) if not any(b.startswith('missing') for b in bad) else dict(ok=False)
        if not r.get('ok'): continue
        snap = dict(profit=round(r['profit'], 2), sets=round(r['sets'], 1), cost=round(r['cost'], 2),
                    ret=round(r['ret'], 5), edge=round(1 - (r['best_px'] or 1), 4),
                    tradeable=tradeable(s, venues_ok), used={k: round(v) for k, v in r['used'].items()})
        q = (not bad) and r['profit'] >= min_profit and s.get('reviewed', True)
        rows.append((s, snap, q, bad))
    return rows

def main(argv=None, fetcher=None, clock=time.time, sleep=time.sleep, structs=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--minutes', type=float, default=60); ap.add_argument('--poll', type=float, default=60)
    ap.add_argument('--discover-every', type=float, default=360, help='minutes between gamma discovery passes')
    ap.add_argument('--log', default='alerts.jsonl'); ap.add_argument('--snapshots', default='snapshots.jsonl')
    ap.add_argument('--venues', default='pm'); ap.add_argument('--tags', default='midterms,politics'); ap.add_argument('--min-edge', type=float, default=0.005)
    ap.add_argument('--min-profit', type=float, default=5.0); ap.add_argument('--no-discover', action='store_true')
    a = ap.parse_args(argv)
    venues_ok = a.venues.split(',')
    base = structs if structs is not None else senate_structures() + race_structures()
    tr = Tracker(a.log, polls=3, min_secs=120)
    t_end = clock() + a.minutes * 60; last_disc = -1e18; extra = []; fees = {}
    while clock() < t_end:
        t0 = clock()
        if not a.no_discover and t0 - last_disc >= a.discover_every * 60:
            try: extra, fees = discover(tuple(a.tags.split(','))); last_disc = t0
            except Exception as ex: print('discover failed', ex, file=sys.stderr)
        allst = base + extra
        try: books = fetcher(legs_of(allst)) if fetcher else fetch_books(legs_of(allst), fees)
        except Exception as ex:
            print('fetch failed', ex, file=sys.stderr); sleep(a.poll); continue
        now = clock()
        rows = evaluate(allst, books, now, venues_ok, a.min_edge, a.min_profit)
        with open(a.snapshots, 'a') as f:
            for s, snap, q, bad in rows:
                if snap['profit'] > 0 or q: f.write(json.dumps(dict(ts=now, sid=s['id'], q=q, bad=bad[:3], **snap)) + '\n')
        for s, snap, q, bad in rows:
            ev = tr.update(s['id'], now, q, snap)
            if ev:
                tag = 'TRADEABLE' if snap['tradeable'] else 'ALERT-ONLY'
                print(f"[{time.strftime('%H:%M:%S', time.gmtime(now))}] {ev.upper()} {tag} {s['id']} profit ${snap['profit']} on ${snap['cost']} ({snap['ret']*100:.2f}%) edge {snap['edge']}", flush=True)
        sleep(max(0, a.poll - (clock() - t0)))
    for sid in list(tr.open): tr.update(sid, clock(), False)

if __name__ == '__main__':
    main()
