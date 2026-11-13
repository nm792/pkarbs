"""CS2 win-probability library (10 Nov 2026).  Round-level state model + map DP (MR12, MR3 overtime, side swap) + series DP."""
import functools, math

def sig(x): return 1 / (1 + math.exp(-x))
def logit(p): p = min(max(p, 1e-4), 1 - 1e-4); return math.log(p / (1 - p))

def home_is_T(o, n):
    """o = home side (1=T,2=CT) during the first half. n = rounds already played (0-based round index of the round being played).
    Regulation: sides swap after round 12. Overtime (MR3): n=24-26 same side as 12-23, then swap every 3 rounds (observed: side flips at n=27, 30, ...)."""
    first = (o == 1)
    if n < 12: return first
    if n < 24: return not first
    j = ((n - 24) // 3) % 2
    return (not first) if j == 0 else first

def make_map_dp(o, pT, pCT):
    """pT / pCT: P(home wins a round) when home is on T / CT side. Returns V(h,a) = P(home wins map | score h-a, round h+a about to start)."""
    @functools.lru_cache(maxsize=None)
    def V_reg(h, a):
        if h >= 13: return 1.0
        if a >= 13: return 0.0
        if h == 12 and a == 12: return OTW
        n = h + a
        p = pT if home_is_T(o, n) else pCT
        return p * V_reg(h + 1, a) + (1 - p) * V_reg(h, a + 1)
    # overtime period: first to 4 of up to 6 rounds, sides: first 3 rounds side s0 (= side at n=12..23), next 3 flipped, 3-3 repeats the period
    s0T = home_is_T(o, 24)
    def ot_round_p(j):
        homeT = s0T if j < 3 else (not s0T)
        return pT if homeT else pCT
    @functools.lru_cache(maxsize=None)
    def OT(x, y, w0):
        if x >= 4: return 1.0
        if y >= 4: return 0.0
        if x == 3 and y == 3: return w0
        p = ot_round_p(x + y)
        return p * OT(x + 1, y, w0) + (1 - p) * OT(x, y + 1, w0)
    # solve fixed point W0 = P(win period outright) + P(3-3)*W0
    OT.cache_clear()
    a0 = OT(0, 0, 0.0); b0 = OT(0, 0, 1.0)      # linear in w0: f(w0) = a0 + (b0 - a0) * w0
    W0 = a0 / (1 - (b0 - a0)) if (b0 - a0) < 1 else 0.5
    OTW = W0
    @functools.lru_cache(maxsize=None)
    def V_ot(h, a, x, y):   # not needed beyond 12-12 start; kept for completeness
        return OT(x, y, W0)
    def V(h, a):
        # overtime states: map score >= 12-12 means n >= 24
        if h >= 12 and a >= 12:
            n = h + a - 24                       # rounds played in overtime, periods of 6
            r = n % 6; x = y = 0
            # rounds played within the current period are unknown from the score alone; assume the period is level at its start
            # (exact tracking needs per-period tallies; the pilot's old model used a lead rule). Approximation: lead d=h-a inside period.
            d = h - a
            return OT(max(0, d), max(0, -d), W0) if r else W0 if d == 0 else (1.0 if d > 0 else 0.0) if abs(d) >= 4 else OT(max(0, d), max(0, -d), W0)
        return V_reg(h, a)
    V.OTW = W0
    return V

def solve_z0(o, delta, price, tol=1e-6):
    """Find z0 so that map-win prob at 0-0 equals price, with pT = sig(z0 - delta), pCT = sig(z0 + delta) (home advantage on CT when delta>0)."""
    lo, hi = -2.0, 2.0
    for _ in range(50):
        z = (lo + hi) / 2
        v = make_map_dp(o, sig(z - delta), sig(z + delta))(0, 0)
        if v < price: lo = z
        else: hi = z
    return (lo + hi) / 2

def series_win(maps_h, maps_a, w_cur, bo, p_future=0.5):
    """P(home wins series | maps already won, probability w_cur of winning the current map, p_future for later maps)."""
    need = bo // 2 + 1
    @functools.lru_cache(maxsize=None)
    def rest(x, y):
        if x >= need: return 1.0
        if y >= need: return 0.0
        return p_future * rest(x + 1, y) + (1 - p_future) * rest(x, y + 1)
    return w_cur * rest(maps_h + 1, maps_a) + (1 - w_cur) * rest(maps_h, maps_a + 1)
