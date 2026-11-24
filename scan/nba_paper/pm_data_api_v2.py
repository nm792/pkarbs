"""Polymarket Data API v2 /trades client that FAILS CLOSED on wrong-market rows (R-080).
v2 silently ignores unknown query params, so every returned row's condition id must equal the request.
Rows lacking a condition id field are an error, not a pass."""
import json, urllib.parse, urllib.request

BASE = 'https://data-api.polymarket.com'
FIELDS = ('condition_id', 'conditionId', 'condition')


class WrongMarketRows(Exception):
    pass


def row_cond(row):
    for f in FIELDS:
        if row.get(f):
            return str(row[f]).lower()
    return None


def check_rows(rows, condition_id):
    want = condition_id.lower()
    for i, r in enumerate(rows):
        got = row_cond(r)
        if got != want:
            raise WrongMarketRows('row %d condition %r != request %r' % (i, got, want))
    return rows


def _get(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    return json.load(urllib.request.urlopen(req, timeout=30))


def in_window(rows, start=None, end=None):
    """v2 silently ignores start/end (P-R080-1): window by row timestamp ourselves. start/end are NEVER sent."""
    return [r for r in rows if (start is None or r['timestamp'] >= start) and (end is None or r['timestamp'] <= end)]


def fetch_trades(condition_id, base=None, param='condition_id', limit=500, max_pages=20, getter=_get, start=None, end=None):
    base = base or BASE
    out, cur = [], None
    for _ in range(max_pages):
        p = {param: condition_id, 'limit': limit}
        if cur:
            p['cursor'] = cur
        r = getter('%s/v2/trades?%s' % (base, urllib.parse.urlencode(p)))
        rows = r.get('data') or []
        out += check_rows(rows, condition_id)
        pg = r.get('pagination') or {}
        cur = pg.get('next_cursor')
        if not pg.get('has_more') or not rows or not cur:
            break
    return in_window(out, start, end)
