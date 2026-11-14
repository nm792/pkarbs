#!/usr/bin/env python3
"""Polymarket TRADE recorder for the TheSports capture dir (pkarbs note #315 item 1).

Why it exists: live/thesports/capture.py has no trade reader at all (its file list is
ts_mqtt, ts_poll, books, markets, pmws, log), so no PM trade row was recorded for any
esports match. The benchmark in feeds/STANDARD-feed-latency-test.md prices off Polymarket
and the LoL Worlds final (14 Nov 19:00Z) needs trade rows, so this is a second, separate
process - capture.py itself is untouched.

What it does: every --interval seconds it reads OUT/markets.jsonl (the markets capture.py
registered), keeps the conditions whose event start is inside [--behind, +--ahead] hours,
and pulls data-api /v2/trades for each (data-api v1 /trades was retired 3 Nov 2026).
New trades are appended to OUT/trades.jsonl, one JSON per trade, "ms" = our receipt time
(UTC epoch ms, the same clock as capture.py's streams), "ts" = the exchange timestamp.
Trader identity fields (wallet, name, pseudonym, profile image) are deliberately dropped.

Dedup: an in-memory key set (tx, token_id, ts, size, price) trimmed to --seen-max keys, plus
OUT/trades.watermark.json = the max exchange ts written per condition, saved every cycle and
applied ONLY on the first cycle after a start, so a restart re-appends nothing while trades
that arrive late inside a run are still written.

Class: Type A / CHARTER clause 22A (data plumbing, no trading decision touched) - IT reply to
note #315 2026-11-14 00:10Z, OPEN row P11. Disk gate: GO at 50 MB/day, output on VOL2, never root.

Revert:
    kill the pm_trades_capture.py process (guard relaunches only after these lines are removed)
    rm -f OUT/trades.jsonl OUT/trades.watermark.json
    rm -f /root/pkarbs/live/thesports/pm_trades_capture.py
    guard trade lines: cp guard_capture_b.sh.bak-p11-<stamp> guard_capture_b.sh
"""
import argparse, json, os, ssl, time, urllib.parse, urllib.request

ap = argparse.ArgumentParser()
ap.add_argument('out')
ap.add_argument('--interval', type=float, default=30.0, help='seconds between cycles')
ap.add_argument('--limit', type=int, default=200, help='trades per page')
ap.add_argument('--hours', type=float, default=160.0, help='bound the run; the guard relaunches')
ap.add_argument('--behind', type=float, default=6.0, help='poll markets started up to this many hours ago')
ap.add_argument('--ahead', type=float, default=48.0, help='poll markets starting up to this many hours ahead')
ap.add_argument('--max-pages', type=int, default=5, help='pagination cap per condition per cycle')
ap.add_argument('--seen-max', type=int, default=20000, help='in-memory dedup key cap')
A = ap.parse_args()

OUT = A.out
MKTS = os.path.join(OUT, 'markets.jsonl')
TRADES = os.path.join(OUT, 'trades.jsonl')
WM = os.path.join(OUT, 'trades.watermark.json')
END = time.time() + A.hours * 3600
DATA = 'https://data-api.polymarket.com'
UA = 'pkarbs-thesports-trades/1.0'
CA = os.environ.get('SSL_CERT_FILE') or ('/root/.ccr/ca-bundle.crt' if os.path.exists('/root/.ccr/ca-bundle.crt') else None)
CTX = ssl.create_default_context(cafile=CA)


def log(*a):
    print(time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), *a, flush=True)


def ep(s):
    try:
        return time.mktime(time.strptime(s[:19], '%Y-%m-%d %H:%M:%S')) - time.timezone
    except Exception:
        return None


def load_markets():
    """cond -> (sport, question, title, start) for markets inside the poll window."""
    now = time.time()
    out = {}
    try:
        with open(MKTS) as f:
            for ln in f:
                try:
                    m = json.loads(ln)
                except Exception:
                    continue
                st = ep(m.get('start') or '')
                if st is None:
                    continue
                if now - A.behind * 3600 <= st <= now + A.ahead * 3600:
                    out[m.get('cond')] = (m.get('sport', ''), m.get('q', ''),
                                          m.get('title', ''), m.get('start', ''))
    except FileNotFoundError:
        pass
    return out


def wm_load():
    try:
        with open(WM) as f:
            return {k: float(v) for k, v in json.load(f).items()}
    except Exception:
        return {}


def wm_save(wm):
    tmp = WM + '.tmp'
    with open(tmp, 'w') as f:
        json.dump(wm, f)
    os.replace(tmp, WM)


def get(url):
    req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept': 'application/json'})
    with urllib.request.urlopen(req, context=CTX, timeout=20) as r:
        return json.loads(r.read())


def pull(cond, seen, fh, meta, wm, boot):
    """One condition: page /v2/trades while pages reach inside the 10 min window; append new rows."""
    wrote = 0
    cur = None
    floor = time.time() - 600
    w = wm.get(cond, 0.0)
    for _ in range(A.max_pages):
        params = dict(condition=cond, limit=A.limit)
        if cur:
            params['cursor'] = cur
        q = urllib.parse.urlencode(params)
        try:
            r = get('%s/v2/trades?%s' % (DATA, q))
        except Exception as e:
            log('ERR', cond[:14], repr(e)[:160])
            return wrote
        rows = r.get('data') or []
        oldest = None
        for t in rows:
            ts = t.get('timestamp')
            if ts is None:
                continue
            oldest = ts if oldest is None else min(oldest, ts)
            if boot and ts <= w:
                continue                      # already written by the run before this start
            key = (t.get('transaction_hash'), t.get('token_id'), ts, t.get('size'), t.get('price'))
            if key in seen:
                continue
            seen[key] = 1
            rec = dict(ms=int(time.time() * 1000), ts=ts, cond=cond, token_id=t.get('token_id'),
                       side=t.get('side'), price=t.get('price'), size=t.get('size'),
                       outcome=t.get('outcome'), outcome_index=t.get('outcome_index'),
                       title=t.get('title'), slug=t.get('slug') or t.get('event_slug'),
                       sport=meta[0], q=meta[1], tx=t.get('transaction_hash'))
            fh.write(json.dumps(rec, separators=(',', ':')) + '\n')
            wrote += 1
            if ts > w:
                w = ts
        pg = r.get('pagination') or {}
        if not pg.get('has_more') or not rows:
            break
        cur = pg.get('next_cursor')
        if oldest is None or oldest <= floor:
            break
    if wrote:
        wm[cond] = w
    return wrote


def main():
    os.makedirs(OUT, exist_ok=True)
    seen = {}
    wm = wm_load()
    last_mk, mk_cache, mk_at = None, {}, 0.0
    cycles = 0
    while time.time() < END:
        try:
            if os.path.getmtime(MKTS) != last_mk or time.time() - mk_at > 60:
                mk_cache = load_markets()
                last_mk = os.path.getmtime(MKTS)
                mk_at = time.time()
        except OSError:
            pass
        boot = (cycles == 0)
        wrote = 0
        with open(TRADES, 'a', buffering=1) as fh:
            for cond, meta in mk_cache.items():
                if time.time() >= END:
                    break
                wrote += pull(cond, seen, fh, meta, wm, boot)
        cycles += 1
        while len(seen) > A.seen_max:
            seen.pop(next(iter(seen)))
        wm_save(wm)
        if wrote:
            log('cycle', cycles, 'conds', len(mk_cache), 'new', wrote,
                'bytes', os.path.getsize(TRADES), 'seen', len(seen))
        time.sleep(max(1.0, A.interval))
    log('END bound reached, conds', len(mk_cache), 'bytes', os.path.getsize(TRADES))


if __name__ == '__main__':
    main()
