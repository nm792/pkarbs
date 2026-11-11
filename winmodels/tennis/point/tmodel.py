"""Point-level tennis win probability (Markov / Klaassen-Magnus style). s1, s2 = P(player wins a point on own serve).
State: sets (k1,k2), games (g1,g2), points (a,b) in the current game or tiebreak, server (1|2), tb flag.
Best of 3. doubles=True: no-ad games (deciding point at deuce) and a 10-point match tiebreak at one set all."""
from functools import lru_cache

def _r(x): return round(x, 3)

@lru_cache(maxsize=None)
def game(p, a, b, noad):
    """P(server wins game) from points a (server), b (returner)."""
    if a >= 4 and a - b >= 2: return 1.0
    if b >= 4 and b - a >= 2: return 0.0
    if a >= 3 and b >= 3:
        if noad: return p
        d = a - b
        w = p * p / (p * p + (1 - p) * (1 - p))     # from deuce
        if d == 0: return w
        if d == 1: return p + (1 - p) * w
        return p * w                                 # d == -1
    return p * game(p, a + 1, b, noad) + (1 - p) * game(p, a, b + 1, noad)

@lru_cache(maxsize=None)
def tiebreak(s1, s2, a, b, first, to):
    """P(player1 wins tiebreak to `to` (win by 2); `first` served point 1. Points a (p1), b (p2)."""
    if a >= to and a - b >= 2: return 1.0
    if b >= to and b - a >= 2: return 0.0
    if a >= to - 1 and b >= to - 1 and a == b:      # equal at to-1 or later: serve pattern repeats every 2 points
        n = a + b
        sv = lambda k: first if ((k + 1) // 2) % 2 == 0 else 3 - first
        q1 = s1 if sv(n) == 1 else 1 - s2; q2 = s1 if sv(n + 1) == 1 else 1 - s2
        return q1 * q2 / (q1 * q2 + (1 - q1) * (1 - q2))
    n = a + b
    srv = first if ((n + 1) // 2) % 2 == 0 else 3 - first
    q = s1 if srv == 1 else 1 - s2
    return q * tiebreak(s1, s2, a + 1, b, first, to) + (1 - q) * tiebreak(s1, s2, a, b + 1, first, to)

@lru_cache(maxsize=None)
def set_(s1, s2, g1, g2, srv, noad):
    """P(p1 wins set) at games g1-g2 with `srv` serving the next game (start of game)."""
    if g1 >= 6 and g1 - g2 >= 2 or g1 == 7: return 1.0
    if g2 >= 6 and g2 - g1 >= 2 or g2 == 7: return 0.0
    if g1 == 6 and g2 == 6: return tiebreak(s1, s2, 0, 0, srv, 7)
    pg = game(s1, 0, 0, noad) if srv == 1 else 1 - game(s2, 0, 0, noad)
    return pg * set_(s1, s2, g1 + 1, g2, 3 - srv, noad) + (1 - pg) * set_(s1, s2, g1, g2 + 1, 3 - srv, noad)

def set_in(s1, s2, g1, g2, a, b, srv, tb, noad):
    """P(p1 wins current set) mid-game: points a (p1), b (p2)."""
    if tb: return tiebreak(s1, s2, a, b, srv, 7)          # srv = who served the first tiebreak point (approx: current server)
    if srv == 1: pg = game(s1, a, b, noad)
    else: pg = 1 - game(s2, b, a, noad)
    return pg * set_(s1, s2, g1 + 1, g2, 3 - srv, noad) + (1 - pg) * set_(s1, s2, g1, g2 + 1, 3 - srv, noad)

def match(s1, s2, k1, k2, g1, g2, a, b, srv, tb, doubles=False, mtb=None):
    """P(p1 wins match), best of 3. mtb = (a, b) points in a 10-point match tiebreak (doubles at 1-1)."""
    s1, s2 = _r(s1), _r(s2); noad = doubles
    if k1 == 2: return 1.0
    if k2 == 2: return 0.0
    if doubles and k1 == 1 and k2 == 1:
        a_, b_ = mtb if mtb else (a, b)
        return tiebreak(s1, s2, a_, b_, srv, 10)
    ps = set_in(s1, s2, g1, g2, a, b, srv, tb, noad)
    nxt = 3 - srv                                          # approx: next set's first server alternates
    return ps * m_start(s1, s2, k1 + 1, k2, nxt, doubles) + (1 - ps) * m_start(s1, s2, k1, k2 + 1, nxt, doubles)

@lru_cache(maxsize=None)
def m_start(s1, s2, k1, k2, srv, doubles):
    """P(p1 wins match) at the start of a set (sets k1-k2), `srv` serving first."""
    if k1 == 2: return 1.0
    if k2 == 2: return 0.0
    if doubles and k1 == 1 and k2 == 1: return tiebreak(s1, s2, 0, 0, srv, 10)
    ps = set_(s1, s2, 0, 0, srv, doubles)
    return ps * m_start(s1, s2, k1 + 1, k2, 3 - srv, doubles) + (1 - ps) * m_start(s1, s2, k1, k2 + 1, 3 - srv, doubles)

def fit(target, total, st, doubles=False):
    """Find s1 - s2 (with s1 + s2 = total) so match prob at state st equals target. Returns (s1, s2)."""
    lo, hi = -0.45, 0.45
    f = lambda d: match((total + d) / 2, (total - d) / 2, *st, doubles=doubles)
    if f(lo) >= target: return (total + lo) / 2, (total - lo) / 2
    if f(hi) <= target: return (total + hi) / 2, (total - hi) / 2
    for _ in range(22):
        mid = (lo + hi) / 2
        if f(mid) < target: lo = mid
        else: hi = mid
    d = (lo + hi) / 2; return (total + d) / 2, (total - d) / 2
