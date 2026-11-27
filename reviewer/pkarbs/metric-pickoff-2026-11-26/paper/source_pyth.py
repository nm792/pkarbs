"""Pyth source for Polymarket stock weekly-close markets ("<TICKER> closes week ... at ___", "<TICKER> finish week ... above ___").
Rules text (Gamma, 26 Nov): settlement = Pyth "Close" of the 1-minute candle for the FINAL minute of the regular (or shortened) session.
Fri 27 Nov 2026 is a 13:00 ET early close, so the release R = 18:00:00Z and the settling candle is the one that starts at R-60 s.
We read that candle from Pyth Benchmarks (TradingView shim, public). Symbol 'Equity.US.<TICKER>/USD'. Read-only GETs, polled once a second from R.
Config (optional) pyth_symbols.json in logdir: {slug: pyth_symbol} overrides the default symbol."""
import json, os, time, gzip, urllib.request, urllib.parse
URL = 'https://benchmarks.pyth.network/v1/shims/tradingview/history?symbol={sym}&resolution=1&from={a}&to={b}'
HERMES_FEEDS = 'https://hermes.pyth.network/v2/price_feeds?query={q}&asset_type=equity'
HERMES_AT = 'https://hermes.pyth.network/v2/updates/price/{ts}?ids[]={fid}&parsed=true'
HERMES_LATEST = 'https://hermes.pyth.network/v2/updates/price/latest?ids[]={fid}&parsed=true'
# P188 (26 Nov 15:55Z): benchmarks 404 and Hermes historical 401 on Prime; Hermes price_feeds 200. Method C 'latest' (pyth_method.txt = latest):
# poll Hermes LATEST once a second from R-30 s, keep the newest price whose publish_time lies in the final minute [R-60, R], emit it at R+3 s.
# The latest price published inside the final minute is the close of that minute's candle (candle close = last price of the minute).
# P185 (26 Nov 14:00Z): the TradingView shim returned 404 for 'Equity.US.NVDA/USD' unencoded. Method A now URL-encodes the symbol;
# method B (fallback, PRICE_METHOD=hermes in pyth_method.txt) reads Hermes' price published at R-1 s for the feed id of that symbol
# (close of the final minute ~ last price before R; the node's 0.2% edge guard covers the gap).


def ticker_of(slug):
    for k in ('-week-', '-above-on-'):
        if k in slug:
            return slug.split(k)[0].upper()
    return None


def fetch(url, timeout=5):
    h = {'Accept-Encoding': 'gzip', 'User-Agent': 'pickoff-paper'}
    if os.environ.get('PYTH_API_KEY'):          # Hermes requires a key since the Pyth Core upgrade (26 Aug 2026): Authorization: Bearer <key>
        h['Authorization'] = 'Bearer ' + os.environ['PYTH_API_KEY']
    req = urllib.request.Request(url, headers=h)
    raw = urllib.request.urlopen(req, timeout=timeout).read()
    try:
        raw = gzip.decompress(raw)
    except OSError:
        pass
    return json.loads(raw)


def candle_close(doc, t_start):
    """TradingView shim doc {s:'ok', t:[...], c:[...]} -> close of the candle starting at t_start (s), or None."""
    if not isinstance(doc, dict) or doc.get('s') != 'ok':
        return None
    for t, c in zip(doc.get('t') or [], doc.get('c') or []):
        if int(t) == int(t_start):
            return float(c)
    return None


class Source:
    def __init__(self, evs, logdir, release_s=None, fetcher=fetch, now=time.time):
        self.release = {s: release_s[s] for s in evs} if isinstance(release_s, dict) else {s: release_s for s in evs}
        over = {}
        p = os.path.join(logdir, 'pyth_symbols.json')
        if os.path.exists(p):
            over = json.load(open(p))
        self.sym = {s: over.get(s) or ('Equity.US.%s/USD' % ticker_of(s)) for s in evs if over.get(s) or ticker_of(s)}
        self.fetch, self.now = fetcher, now
        pm = os.path.join(logdir, 'pyth_method.txt')
        self.method = open(pm).read().strip() if os.path.exists(pm) else 'benchmarks'
        self.fid = {}
        self.best = {}      # slug -> (publish_time, price) newest seen inside [R-60, R] (method 'latest')

    def _fid(self, sym):
        if sym not in self.fid:
            feeds = self.fetch(HERMES_FEEDS.format(q=urllib.parse.quote(sym.split('.')[-1].split('/')[0])))
            hit = [f['id'] for f in feeds if (f.get('attributes') or {}).get('symbol') == sym]
            if len(hit) != 1:
                return None
            self.fid[sym] = hit[0]
        return self.fid[sym]

    def hermes_price(self, sym, ts):
        if self._fid(sym) is None:
            return None
        d = self.fetch(HERMES_AT.format(ts=ts, fid=self.fid[sym]))
        p = (d.get('parsed') or [{}])[0].get('price') or {}
        return float(p['price']) * 10 ** int(p['expo']) if 'price' in p else None

    def poll(self):
        out = []
        for slug, sym in self.sym.items():
            R = self.release.get(slug)
            if R is None:
                continue
            if self.method == 'latest':
                v = self._latest(slug, sym, R)
                if v is not None:
                    out.append((slug, None, v[1], dict(pyth=sym, method='latest', publish_time=v[0])))
                continue
            if self.now() < R:
                continue
            try:
                if self.method == 'hermes':
                    v = self.hermes_price(sym, int(R) - 1)
                else:
                    v = candle_close(self.fetch(URL.format(sym=urllib.parse.quote(sym, safe=''), a=int(R) - 180, b=int(R) + 60)), int(R) - 60)
            except Exception:
                continue
            if v is not None:
                out.append((slug, None, v, dict(pyth=sym, candle_start=int(R) - 60)))
        return out

    def _latest(self, slug, sym, R):
        now = self.now()
        if now < R - 30:
            return None
        if now <= R + 10:
            try:
                fid = self._fid(sym)
                d = self.fetch(HERMES_LATEST.format(fid=fid)) if fid else {}
                p = (d.get('parsed') or [{}])[0].get('price') or {}
                if 'price' in p:
                    pt = int(p['publish_time']); v = float(p['price']) * 10 ** int(p['expo'])
                    if R - 60 <= pt <= R and pt >= self.best.get(slug, (-1, None))[0]:
                        self.best[slug] = (pt, v)
            except Exception:
                pass
        return self.best.get(slug) if now >= R + 3 else None
