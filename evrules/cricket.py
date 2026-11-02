"""Cricket (T20, T10) win probability from score, wickets and balls.

Two logistic models, fitted on Cricsheet men's T20 international
ball-by-ball (fit_cricket.py; coefficients in params/cricket.json):
  innings 1: P(team batting first wins | runs, wickets, legal balls)
  innings 2: P(chasing team wins | runs needed, wickets left, balls left)
They describe an AVERAGE match. Team strength comes from the market:
  fair_after() takes the market price before an event, works out the
  strength offset that makes the model match it, and applies the event.
T10: no T10 data. We map a T10 state to T20 by resource fraction (balls x2,
runs x 160/120 since T10 totals run ~120 vs ~160 in T20). ESTIMATED.
"""
import json, math, os

_P = None


def _params():
    global _P
    if _P is None:
        _P = json.load(open(os.path.join(os.path.dirname(__file__), 'params', 'cricket.json')))
    return _P


def x1(runs, wkts, balls, total_balls=120):
    b = balls / total_balls
    r = runs / 100.0
    crr = runs / max(balls, 6) * 6.0 / 10.0     # current run rate / 10
    return [1.0, r, wkts / 10.0, b, r * b, (wkts / 10.0) * b, crr * b]


def x2(need, wkts_left, balls_left, total_balls=120):
    bl = balls_left / total_balls
    rrr = need / max(balls_left, 1) * 6.0
    return [1.0, need / 100.0, wkts_left / 10.0, bl, min(rrr, 36.0) / 10.0, math.log1p(need) / 5.0,
            (wkts_left / 10.0) * bl, min(rrr, 36.0) / 10.0 * wkts_left / 10.0]


def _sig(z):
    return 1.0 / (1.0 + math.exp(-z))


def p_bat_first(innings, runs, wkts, balls, target=None, fmt='T20'):
    """P(team batting first wins). innings=1: runs/wkts/balls of innings 1.
    innings=2: runs/wkts/balls of the chase and target (= first total + 1)."""
    P = _params()
    if fmt == 'T10':   # map to T20 equivalent (estimated)
        runs, balls = runs * 160 / 120.0, balls * 2
        if target is not None:
            target = target * 160 / 120.0
    if innings == 1:
        z = sum(a * b for a, b in zip(P['inn1']['beta'], x1(runs, wkts, balls)))
        return _sig(z)
    need = target - runs
    if need <= 0:
        return 0.0
    if wkts >= 10 or balls >= 120:
        return 1.0
    z = sum(a * b for a, b in zip(P['inn2']['beta'], x2(need, 10 - wkts, 120 - balls)))
    return 1.0 - _sig(z)


def _logit(p):
    p = min(max(p, 1e-4), 1 - 1e-4)
    return math.log(p / (1 - p))


def fair_after(state_before, state_after, price_bat_first_before):
    """States are dicts for p_bat_first(**state). Returns the market-anchored
    fair price of the batting-first team after the event."""
    off = _logit(price_bat_first_before) - _logit(p_bat_first(**state_before))
    return _sig(_logit(p_bat_first(**state_after)) + off)
