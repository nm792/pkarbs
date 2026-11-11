"""CS2 win-probability from the score the Polymarket sports WS gives us.

WS score string: "<home rounds>-<away rounds>|<home maps>-<away maps>|Bo<N>"
(read confirmed 42/43 on direction, rn1/scores/cs2/live/NOTE-lag-2026-11-02.md).

Model (built from game rules, not fitted):
- A map is MR12: first to 13 rounds. At 12-12, overtime is best of 6
  (first to 4); 3-3 in overtime starts a new overtime.
- Each round is won by home with probability p_r, independent of the
  others. Side (CT/T), economy and pistol rounds are IGNORED: that is the
  main known error.
- Future maps are won by home with probability p_m, also independent.
- Series: first to ceil(N/2) maps.
Team strength comes from the market: invert the last trade before an event
to get p_r, then apply the event. So the model only says how much a round
or map result should move the price.
"""
from functools import lru_cache
import math


@lru_cache(maxsize=None)
def _ot(a, b, p):
    """P(home wins an overtime block from a-b), first to 4, 3-3 resets."""
    if a == 4: return 1.0
    if b == 4: return 0.0
    if a == 3 and b == 3:
        # from 3-3 a fresh block: x = P(win block from 0-0); solve fixed point
        # P(3-3 -> win) = p^2 + 2p(1-p) * P(3-3 -> win) => closed form below
        return p * p / (p * p + (1 - p) * (1 - p))
    return p * _ot(a + 1, b, p) + (1 - p) * _ot(a, b + 1, p)


@lru_cache(maxsize=None)
def _map(a, b, p):
    if a >= 13 and a - b >= 1 and b < 12: return 1.0
    if b >= 13 and b - a >= 1 and a < 12: return 0.0
    if a == 12 and b == 12:
        return _ot(0, 0, p)
    if a >= 12 and b >= 12:     # inside overtime, feed reports cumulative rounds
        # map cumulative rounds into the current overtime block
        da = (a - 12) - 3 * ((min(a, b) - 12) // 3); db = (b - 12) - 3 * ((min(a, b) - 12) // 3)
        return _ot(min(da, 4), min(db, 4), p)
    return p * _map(a + 1, b, p) + (1 - p) * _map(a, b + 1, p)


def map_win(a, b, p_r):
    return _map(int(a), int(b), round(p_r, 4))


def series_win(ma, mb, need, p_cur, p_m):
    """P(home wins series) at maps ma-mb, first to `need`, current map
    won by home with p_cur, later maps with p_m."""
    @lru_cache(maxsize=None)
    def s(x, y):
        if x >= need: return 1.0
        if y >= need: return 0.0
        return p_m * s(x + 1, y) + (1 - p_m) * s(x, y + 1)
    if ma >= need: return 1.0
    if mb >= need: return 0.0
    return p_cur * s(ma + 1, mb) + (1 - p_cur) * s(ma, mb + 1)


def parse(score):
    r, m, f = score.split('|')
    ra, rb = (int(v) for v in r.split('-'))
    ma, mb = (int(v) for v in m.split('-'))
    n = int(f.lower().replace('bo', ''))
    return ra, rb, ma, mb, n


def win_prob(score, p_r, p_m=None):
    ra, rb, ma, mb, n = parse(score)
    if p_m is None:
        p_m = map_win(0, 0, p_r)
    return series_win(ma, mb, n // 2 + 1, map_win(ra, rb, p_r), p_m)


def implied_pr(score, price, lo=0.2, hi=0.8):
    """Round-win prob for home that makes the model equal the market price."""
    f = lambda p: win_prob(score, p) - price
    flo, fhi = f(lo), f(hi)
    if flo > 0: return lo
    if fhi < 0: return hi
    for _ in range(40):
        mid = (lo + hi) / 2
        if f(mid) > 0: hi = mid
        else: lo = mid
    return (lo + hi) / 2


def is_between_maps(score):
    """The WS sends '000-000' when a map has just ended, before the map
    count updates. Do not trade on those frames."""
    return score.split('|')[0] == '000-000'


def fair_after(score_before, score_after, price_before, shrink=1.0):
    """Market-anchored fair price after a score change. `shrink` scales
    the modelled move in logit space (fitted in eval_cs2)."""
    if is_between_maps(score_before) or is_between_maps(score_after):
        return None
    p_r = implied_pr(score_before, price_before)
    raw = win_prob(score_after, p_r)
    if shrink == 1.0:
        return raw
    lg = lambda x: math.log(min(max(x, 1e-4), 1 - 1e-4) / (1 - min(max(x, 1e-4), 1 - 1e-4)))
    z = lg(price_before) + shrink * (lg(raw) - lg(price_before))
    return 1 / (1 + math.exp(-z))
