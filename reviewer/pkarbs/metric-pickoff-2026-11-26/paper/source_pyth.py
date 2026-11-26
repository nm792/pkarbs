"""Pyth source for Polymarket stock weekly-close markets ("<TICKER> closes week ... at ___", "<TICKER> finish week ... above ___").
Rules text (Gamma, 26 Nov): settlement = Pyth "Close" of the 1-minute candle for the FINAL minute of the regular (or shortened) session.
Fri 27 Nov 2026 is a 13:00 ET early close, so the release R = 18:00:00Z and the settling candle is the one that starts at R-60 s.
We read that candle from Pyth Benchmarks (TradingView shim, public). Symbol 'Equity.US.<TICKER>/USD'. Read-only GETs, polled once a second from R.
Config (optional) pyth_symbols.json in logdir: {slug: pyth_symbol} overrides the default symbol."""
import json, os, time, gzip, urllib.request
URL = 'https://benchmarks.pyth.network/v1/shims/tradingview/history?symbol={sym}&resolution=1&from={a}&to={b}'


def ticker_of(slug):
    for k in ('-week-', '-above-on-'):
        if k in slug:
            return slug.split(k)[0].upper()
    return None


def fetch(url, timeout=5):
    req = urllib.request.Request(url, headers={'Accept-Encoding': 'gzip', 'User-Agent': 'pickoff-paper'})
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

    def poll(self):
        out = []
        for slug, sym in self.sym.items():
            R = self.release.get(slug)
            if R is None or self.now() < R:
                continue
            try:
                v = candle_close(self.fetch(URL.format(sym=sym, a=int(R) - 180, b=int(R) + 60)), int(R) - 60)
            except Exception:
                continue
            if v is not None:
                out.append((slug, None, v, dict(pyth=sym, candle_start=int(R) - 60)))
        return out
