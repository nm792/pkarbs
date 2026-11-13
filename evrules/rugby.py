"""Rugby union win/draw/lose probability from score margin and clock.

Model: the final margin (home minus away) is
    M = m_now + mu * r + sigma * sqrt(r) * Z,   r = minutes left / 80
i.e. scoring as a random walk with drift. sigma is fitted on ESPN
scoreboards (20-minute checkpoints, fit_rugby.py, params/rugby.json).
mu (team strength, incl. home advantage) comes from the market: we solve
for the mu that makes P(home win) equal the home-win price, then apply
the new score/clock. Polymarket rugby events are 3-way (home / draw / away),
so we return all three. Draw = P(|M| < 0.5) under the normal (continuity
correction); scoring is lumpy (3, 5, 7), so this is ESTIMATED.
Rugby league (NRL, Super League) is NOT covered: different scoring.
"""
import json, math, os

_P = None


def sigma_full():
    global _P
    if _P is None:
        f = os.path.join(os.path.dirname(__file__), 'params', 'rugby.json')
        _P = json.load(open(f)) if os.path.exists(f) else {'sigma_full': 14.0}
    return _P['sigma_full']


def _Phi(x):
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def probs(margin, minutes_left, mu, sigma=None):
    """(P home win, P draw, P away win)."""
    s = (sigma or sigma_full()) * math.sqrt(max(minutes_left, 0.0) / 80.0)
    m = margin + mu * max(minutes_left, 0.0) / 80.0
    if s < 1e-6:
        return (1.0, 0.0, 0.0) if m > 0 else ((0.0, 1.0, 0.0) if m == 0 else (0.0, 0.0, 1.0))
    ph = 1 - _Phi((0.5 - m) / s)
    pa = _Phi((-0.5 - m) / s)
    return ph, 1 - ph - pa, pa


def implied_mu(margin, minutes_left, p_home, lo=-60.0, hi=60.0):
    for _ in range(60):
        mid = (lo + hi) / 2
        if probs(margin, minutes_left, mid)[0] < p_home: lo = mid
        else: hi = mid
    return (lo + hi) / 2


def fair_after(before, after, p_home_before):
    """before/after = (margin, minutes_left). Market-anchored fair (home, draw, away)."""
    if before[1] <= 0.5:
        return None
    mu = implied_mu(before[0], before[1], p_home_before)
    return probs(after[0], after[1], mu)
