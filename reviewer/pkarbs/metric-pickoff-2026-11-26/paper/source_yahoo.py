"""PAPER-ONLY proxy source for stock weekly-close markets when Pyth is unreachable (P189, 26 Nov: all Pyth methods 401/404 from Prime).
NOT the settlement source (settlement = Pyth close of the final-minute candle). Reads Yahoo chart 1-minute bars and takes the close of the
candle starting at R-60 s. Use with a wider per-event edge guard in the spec ("guard": 0.003) so markets near the line are skipped.
Read-only GETs, polled once a second from R+5 s until R+600 s."""
import json, gzip, time, urllib.request
from source_pyth import ticker_of
URL = 'https://query1.finance.yahoo.com/v8/finance/chart/{t}?period1={a}&period2={b}&interval=1m'


def fetch(url, timeout=5):
    req = urllib.request.Request(url, headers={'Accept-Encoding': 'gzip', 'User-Agent': 'Mozilla/5.0'})
    raw = urllib.request.urlopen(req, timeout=timeout).read()
    try:
        raw = gzip.decompress(raw)
    except OSError:
        pass
    return json.loads(raw)


def bar_close(doc, t_start):
    try:
        r = doc['chart']['result'][0]
        for t, c in zip(r['timestamp'], r['indicators']['quote'][0]['close']):
            if int(t) == int(t_start) and c is not None:
                return float(c)
    except (KeyError, IndexError, TypeError):
        return None
    return None


class Source:
    def __init__(self, evs, logdir, release_s=None, fetcher=fetch, now=time.time):
        self.release = {s: release_s[s] for s in evs} if isinstance(release_s, dict) else {s: release_s for s in evs}
        self.tk = {s: ticker_of(s) for s in evs if ticker_of(s)}
        self.fetch, self.now = fetcher, now

    def poll(self):
        out = []
        for slug, tk in self.tk.items():
            R = self.release.get(slug)
            if R is None or not (R + 5 <= self.now() <= R + 600):
                continue
            try:
                v = bar_close(self.fetch(URL.format(t=tk, a=int(R) - 300, b=int(R) + 60)), int(R) - 60)
            except Exception:
                continue
            if v is not None:
                out.append((slug, None, v, dict(proxy='yahoo', ticker=tk, candle_start=int(R) - 60, note='paper proxy, not settlement source')))
        return out
