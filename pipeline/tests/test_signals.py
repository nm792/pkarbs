import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import signals as S


def tape():
    return S.TokenTape([(100, "BUY", 0.40, 10), (200, "SELL", 0.42, 5), (300, "BUY", 0.50, 20), (400, "BUY", 0.60, 10)])


def test_no_lookahead_strictly_before():
    t = tape()
    assert t.price_before(300) == 0.42      # print AT 300 is not visible at 300
    assert t.price_before(301) == 0.50
    assert t.price_before(100) is None


def test_signals_use_only_past():
    t = tape()
    a = S.signals_at(t, 350, 100)
    b = S.TokenTape([(100, "BUY", 0.40, 10), (200, "SELL", 0.42, 5), (300, "BUY", 0.50, 20)])
    assert S.signals_at(b, 350, 100) == a    # removing the future print changes nothing


def test_fill_is_first_buy_not_best():
    t = S.TokenTape([(10, "SELL", 0.30, 1), (20, "BUY", 0.55, 1), (30, "BUY", 0.40, 1)])
    assert t.fill_after(5, 100) == (0.55, 20)
    assert t.fill_after(5, 10) is None


def test_own_token_only():  # YES at .70 and NO at .35 must stay as printed (1-YES would be .30)
    no = S.TokenTape([(1, "BUY", 0.35, 1)]); assert no.price_before(2) == 0.35
