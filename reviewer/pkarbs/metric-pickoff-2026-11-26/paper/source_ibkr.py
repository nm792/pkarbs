"""IBKR live source for stock weekly-close markets (Nick 27 Nov 03:03Z: "stock prices should be using IBKR. live"). READ-ONLY market data.
Connects to a locally running IB Gateway (Nick's login) with readonly=True: no order can be sent through this connection.
Value = last trade price of the final minute = close of the newest 5-second real-time TRADES bar with volume that starts in [R-60, R-5].
Read live (Nick 27 Nov 09:27Z: replicate live conditions): bars are streamed from R-120 s (reqRealTimeBars, 5 s is IBKR's only real-time bar size),
and the value is released as soon as the bar that starts at R-5 (ends at R) has arrived, or any later bar has. No fixed wait; poll every 50 ms.
Settlement is Pyth's close of the same minute: not the same number (Pyth aggregates publishers), so run with "guard": 0.003 in the spec.
Config: env IB_HOST (127.0.0.1), IB_PORT (4001 = Gateway live), IB_CLIENT_ID (77). Needs `pip install ib_async`."""
import os, time, asyncio


class IBStream:
    """ib_async wrapper used from the source thread (own asyncio loop). bars(ticker) -> [(start_epoch_s, close, volume)]."""
    def __init__(self):
        self.ib, self.sub = None, {}

    def _conn(self):
        from ib_async import IB
        if self.ib is None or not self.ib.isConnected():
            try:
                asyncio.get_event_loop()
            except RuntimeError:
                asyncio.set_event_loop(asyncio.new_event_loop())
            self.ib = IB()
            self.ib.connect(os.environ.get('IB_HOST', '127.0.0.1'), int(os.environ.get('IB_PORT', '4001')),
                            clientId=int(os.environ.get('IB_CLIENT_ID', '77')), readonly=True, timeout=10)
            self.sub = {}
        return self.ib

    def subscribe(self, ticker):
        from ib_async import Stock
        ib = self._conn()
        if ticker not in self.sub:
            c = Stock(ticker, 'SMART', 'USD'); ib.qualifyContracts(c)
            self.sub[ticker] = ib.reqRealTimeBars(c, 5, 'TRADES', False)

    def bars(self, ticker):
        self._conn().sleep(0)          # let ib_async process incoming bars
        return [(int(b.time.timestamp()), float(b.close), float(b.volume)) for b in self.sub.get(ticker, [])]


def final_minute_close(bars, R):
    """bars [(start, close, volume)] -> last-trade price of [R-60, R) once the bar ending at R (or any later bar) is in, else None."""
    if not any(t >= R - 5 for t, _, _ in bars):
        return None
    inmin = [(t, c) for t, c, v in bars if R - 60 <= t <= R - 5 and v > 0]
    return max(inmin)[1] if inmin else None


class Source:
    POLL_S = 0.05

    def __init__(self, evs, logdir, release_s=None, stream=None, now=time.time):
        self.release = {s: release_s[s] for s in evs} if isinstance(release_s, dict) else {s: release_s for s in evs}
        self.tk = {s: s.split('-week-')[0].split('-above-on-')[0].upper() for s in evs if '-week-' in s or '-above-on-' in s}
        self.st, self.now = stream or IBStream(), now
        self.done, self.subbed = set(), set()

    def poll(self):
        out = []
        for slug, tk in self.tk.items():
            R = self.release.get(slug)
            if slug in self.done or R is None:
                continue
            n = self.now()
            try:
                if tk not in self.subbed and R - 120 <= n <= R + 600:
                    self.st.subscribe(tk); self.subbed.add(tk)
                if n < R or tk not in self.subbed:
                    continue
                v = final_minute_close(self.st.bars(tk), int(R))
            except Exception:
                continue
            if v is not None:
                self.done.add(slug)
                out.append((slug, None, v, dict(src='ibkr', ticker=tk, bars='5s realtime TRADES', note='IBKR last trade of final minute; settlement is Pyth')))
        return out
