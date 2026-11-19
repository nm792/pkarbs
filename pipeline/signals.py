"""Point-in-time signals from OWN-token trades only. Every function sees trades with ts < decision time t.
NO is never derived from YES: each token's price comes from that token's own prints."""
import bisect, math


class TokenTape:
    def __init__(self, rows):
        # rows: (ts, side, price, size) for ONE token, any order
        rows = sorted(rows)
        self.ts = [r[0] for r in rows]; self.side = [r[1] for r in rows]
        self.px = [r[2] for r in rows]; self.sz = [r[3] for r in rows]

    def last_before(self, t):
        i = bisect.bisect_left(self.ts, t) - 1  # strictly before t
        return i

    def price_before(self, t):
        i = self.last_before(t)
        return self.px[i] if i >= 0 else None

    def window(self, a, b):  # prints with a <= ts < b
        i, j = bisect.bisect_left(self.ts, a), bisect.bisect_left(self.ts, b)
        return range(i, j)

    def fill_after(self, t, max_wait):
        """Causal fill: first BUY print at/after t within max_wait. Never the best print in a window."""
        i = bisect.bisect_left(self.ts, t)
        while i < len(self.ts) and self.ts[i] <= t + max_wait:
            if self.side[i] == "BUY": return self.px[i], self.ts[i]
            i += 1
        return None


def signals_at(tape, t, H):
    """Signal dict at decision time t for horizon H (seconds). None if no prior print."""
    p = tape.price_before(t)
    if p is None: return None
    w1, w4 = H, 4 * H
    p1 = tape.price_before(t - w1); p4 = tape.price_before(t - w4)
    r1 = tape.window(t - w1, t); r4 = tape.window(t - w4, t - w1)
    dv1 = sum(tape.px[i] * tape.sz[i] for i in r1); dv4 = sum(tape.px[i] * tape.sz[i] for i in r4)
    b = sum(tape.sz[i] for i in r1 if tape.side[i] == "BUY"); s = sum(tape.sz[i] for i in r1 if tape.side[i] == "SELL")
    pr = [tape.px[i] for i in r1]
    return {
        "price": p,
        "mom1": (p - p1) if p1 is not None else 0.0,
        "mom4": (p - p4) if p4 is not None else 0.0,
        "volratio": math.log((dv1 + 1.0) / (dv4 / 3.0 + 1.0)),
        "imbalance": (b - s) / (b + s) if (b + s) > 0 else 0.0,
        "range": (max(pr) - min(pr)) if pr else 0.0,
        "ntrades": float(len(pr)),
    }

SIGNAL_NAMES = ["price", "mom1", "mom4", "volratio", "imbalance", "range", "ntrades"]
