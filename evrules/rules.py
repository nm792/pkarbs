"""The per-sport trading rules for paper trading (7-12 Nov 2026).

One function, on_event(), turns a game event plus the order book into a
decision. Every sport uses the same pattern:
  1. anchor = book mid at the moment the event happened in the game
     (not when we received it), so a market that moved first is not
     counted as edge;
  2. fair  = the sport model's fair price after the event, anchored on
     that mid (team strength comes from the market);
  3. trade only if the CURRENT best ask/bid still leaves edge after the
     taker fee, above the sport's minimum, inside the risk caps (ev.py).
Thresholds below are set from the tests in params/*.json; see
/mnt/project-files/ev-rules/NOTE-ev-rules-2026-11-02.md.
"""
import json, math, os
from evrules import ev, cs2, cricket, rugby

_HERE = os.path.dirname(__file__)

RULES = {
    # LoL: LOGO event test, median abs error 3.8c (naive 5.0c); 86% direction
    # hit when the model calls >= 4c. Taker only; makers lose on LoL (markouts).
    'lol': ev.SportRule('lol', min_edge_taker=0.04, min_edge_maker=0.99, model_sd=0.04, z=1.0, maker_adverse=0.08),
    # CS2: realised move after a round ~0.5x the raw model; price moves with the
    # WS score (median +0.4 s), so taker edge is small. High taker bar;
    # maker quotes cancelled on every round end.
    'cs2': ev.SportRule('cs2', min_edge_taker=0.05, min_edge_maker=0.02, model_sd=0.02, z=1.0, maker_adverse=0.02),
    # Cricket: out-of-sample calibration within ~2-5 pp; no live feed yet.
    'cricket': ev.SportRule('cricket', min_edge_taker=0.04, min_edge_maker=0.99, model_sd=0.04, z=1.0),
    # Rugby union: sigma fitted, strength from market; feed lag unknown.
    'rugby': ev.SportRule('rugby', min_edge_taker=0.05, min_edge_maker=0.99, model_sd=0.05, z=1.0),
}


def _load(name):
    return json.load(open(os.path.join(_HERE, 'params', name)))


def lol_fair(dx, anchor):
    """dx = state change blue-minus-red: kills, towers, dragons, barons, inhibs, gold.
    Returns fair price of the BLUE side token."""
    b = _load('lol_events.json')['beta']
    z = math.log(anchor / (1 - anchor)) + sum(b[k] * dx.get(k, 0) / (1000.0 if k == 'gold' else 1.0) for k in b)
    return 1 / (1 + math.exp(-z))


def cs2_fair(score_before, score_after, anchor):
    shrink = _load('cs2_event_test.json').get('shrink_logit', 0.5)
    return cs2.fair_after(score_before, score_after, anchor, shrink=shrink)


def fair(sport, before, after, anchor):
    if sport == 'lol':
        return lol_fair(after, anchor)             # `after` is dx for LoL
    if sport == 'cs2':
        return cs2_fair(before, after, anchor)
    if sport == 'cricket':
        return cricket.fair_after(before, after, anchor)
    if sport == 'rugby':
        r = rugby.fair_after(before, after, anchor)
        return None if r is None else r[0]         # home-win token; draw/away via rugby.fair_after
    raise ValueError(sport)


def on_event(sport, before, after, anchor_mid, book, lim=ev.Limits(), **pos):
    """book = dict(bid, bid_size, ask, ask_size, feed_age_s)."""
    if anchor_mid is None or not 0.02 < anchor_mid < 0.98:
        return ev.Decision('none', reason='no usable anchor')
    q = fair(sport, before, after, anchor_mid)
    if q is None:
        return ev.Decision('none', reason='event not tradeable (between maps / full time)')
    d = ev.decide_taker(q, book.get('bid'), book.get('bid_size'), book.get('ask'), book.get('ask_size'),
                        RULES[sport], lim, feed_age_s=book.get('feed_age_s', 0.0), **pos)
    d.detail['fair'] = q
    return d
