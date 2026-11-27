"""IBKR live source for stock weekly-close markets (Nick 27 Nov 03:03Z: "stock prices should be using IBKR. live"). READ-ONLY market data.
Connects to a locally running IB Gateway (Nick's login) with readonly=True: no order can be sent through this connection.
Value = close of the 1-minute TRADES bar that starts at R-60 s (the final minute of the session), i.e. the last trade price of the final minute.
Settlement is Pyth's close of the same minute: they are not the same number (Pyth aggregates publishers; IBKR is consolidated last trade),
so run with a per-event guard ("guard": 0.003 in the spec) and compare with Pyth after the event.
Config: env IB_HOST (127.0.0.1), IB_PORT (4001 = Gateway live), IB_CLIENT_ID (77). Needs `pip install ib_async`."""
import os, time, datetime as dt
from source_pyth import ticker_of


def ib_bars(ticker, R, _ib=[None]):
    """[(start_epoch_s, close)] 1-min TRADES bars ending at R+60 (ib_async, read-only)."""
    from ib_async import IB, Stock
    if _ib[0] is None or not _ib[0].isConnected():
        ib = IB()
        ib.connect(os.environ.get('IB_HOST', '127.0.0.1'), int(os.environ.get('IB_PORT', '4001')), clientId=int(os.environ.get('IB_CLIENT_ID', '77')),
                   readonly=True, timeout=10)
        _ib[0] = ib
    ib = _ib[0]
    c = Stock(ticker, 'SMART', 'USD')
    ib.qualifyContracts(c)
    end = dt.datetime.fromtimestamp(int(R) + 60, dt.timezone.utc)
    bars = ib.reqHistoricalData(c, endDateTime=end, durationStr='300 S', barSizeSetting='1 min', whatToShow='TRADES', useRTH=False, formatDate=2, timeout=10)
    out = []
    for b in bars or []:
        d = b.date
        t = int(d.timestamp()) if hasattr(d, 'timestamp') else int(d)
        out.append((t, float(b.close)))
    return out


class Source:
    def __init__(self, evs, logdir, release_s=None, bars=ib_bars, now=time.time):
        self.release = {s: release_s[s] for s in evs} if isinstance(release_s, dict) else {s: release_s for s in evs}
        self.tk = {s: ticker_of(s) for s in evs if ticker_of(s)}
        self.bars, self.now = bars, now
        self.done = set()

    def poll(self):
        out = []
        for slug, tk in self.tk.items():
            R = self.release.get(slug)
            if slug in self.done or R is None or not (R + 2 <= self.now() <= R + 600):
                continue
            try:
                v = next((c for t, c in self.bars(tk, R) if t == int(R) - 60), None)
            except Exception:
                continue
            if v is not None:
                self.done.add(slug)
                out.append((slug, None, v, dict(src='ibkr', ticker=tk, bar_start=int(R) - 60, note='IBKR last trade of final minute; settlement is Pyth')))
        return out
