"""Fast checks: python3 -m pytest -q evrules  (or python3 -m evrules.test_evrules)"""
from evrules import ev, cs2, cricket, rugby, rules


def test_fee():
    assert abs(ev.taker_fee(0.5) - 0.0125) < 1e-12          # 0.05 * .5 * .5
    assert abs(ev.ev_take_buy(0.60, 0.50) - (0.10 - 0.0125)) < 1e-12


def test_decide_threshold_and_caps():
    r = rules.RULES['lol']
    d = ev.decide_taker(0.53, 0.49, 1000, 0.50, 1000, r)
    assert d.action == 'none'                               # 3c - fee < 4c
    d = ev.decide_taker(0.62, 0.49, 1000, 0.50, 1000, r)
    assert d.action == 'buy' and d.shares * 0.5125 <= 0.01 * 10000 + 1e-6
    d = ev.decide_taker(0.38, 0.49, 1000, 0.50, 1000, r)
    assert d.action == 'sell'
    d = ev.decide_taker(0.62, 0.49, 1000, 0.50, 1000, r, day_pnl=-400)
    assert d.action == 'none'
    d = ev.decide_taker(0.62, 0.49, 1000, 0.50, 1000, r, feed_age_s=9)
    assert d.action == 'none'
    d = ev.decide_taker(0.62, 0.49, 1000, 0.50, 1000, r, market_pos=200)
    assert d.action == 'none'                               # market cap used up


def test_cs2():
    assert abs(cs2.map_win(0, 0, 0.5) - 0.5) < 1e-9
    assert cs2.map_win(12, 3, 0.5) > 0.99
    assert abs(cs2.win_prob('0-0|1-1|Bo3', 0.5) - 0.5) < 1e-9
    assert cs2.fair_after('6-12|1-0|Bo3', '000-000|1-0|Bo3', 0.5) is None
    assert cs2.fair_after('5-5|0-0|Bo3', '6-5|0-0|Bo3', 0.5) > 0.5


def test_cricket():
    assert cricket.p_bat_first(2, 199, 0, 114, target=200) < 0.05      # need 1 off 6, 10 wkts
    assert cricket.p_bat_first(2, 120, 9, 114, target=200) > 0.95      # need 80 off 6
    a = cricket.p_bat_first(1, 60, 1, 36); b = cricket.p_bat_first(1, 60, 5, 36)
    assert a > b


def test_rugby():
    h, d, a = rugby.probs(0, 80, 0)
    assert abs(h + d + a - 1) < 1e-9 and abs(h - a) < 1e-9
    assert rugby.probs(10, 5, 0)[0] > 0.9
    q = rugby.fair_after((0, 40), (7, 39), 0.5)
    assert q[0] > 0.6


def test_maker_quotes():
    b, a = ev.maker_quotes(0.5, rules.RULES['cs2'])
    assert b is not None and a is not None and b < 0.5 < a


if __name__ == '__main__':
    for k, f in list(globals().items()):
        if k.startswith('test_'):
            f(); print('ok', k)
