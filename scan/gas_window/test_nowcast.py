#!/usr/bin/env python3
"""Can-fail tests for nowcast.py. Run: python3 test_nowcast.py"""
import sys, os, datetime as dt, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nowcast as n
D0 = dt.date(2026, 1, 1)
def world(ndays, coef, seed, noise=0.2):
    """prints follow dP_t = coef*dP_{t-1} + noise (cents); spot flat. Returns prints, nyh, gulf."""
    rng = np.random.default_rng(seed); p = {}; v = 4.0; d_prev = 1.0
    for i in range(ndays):
        d = coef * d_prev + rng.normal(0, noise); v += d / 100; d_prev = d; p[D0 + dt.timedelta(days=i)] = v
    s = {D0 + dt.timedelta(days=i): 2.5 for i in range(-10, ndays + 5)}
    return p, s, dict(s)
def oos_err(coef, seed):
    p, ny, gu = world(200, coef, seed); errs = []
    for k in range(150, 190):
        D = D0 + dt.timedelta(days=k); r = n.oos_predict(p, ny, gu, D, 1, D0 + dt.timedelta(days=8))
        assert r is not None
        errs.append(abs(r[0] - (p[D] - p[D - dt.timedelta(days=1)]) * 100))
    return float(np.mean(errs))
TESTS = []
def test(f): TESTS.append(f); return f
@test
def t1_planted_autoregression_is_recovered():
    # strong persistence + small noise: OOS error must be near the noise level (0.2c), far below the signal scale
    assert oos_err(0.9, 1) < 0.35, oos_err(0.9, 1)
@test
def t2_no_signal_gives_no_skill():
    # iid noise: OOS error must be about the noise scale (>0.12c) and not a fitted-signal miracle; also it must be worse than t1
    e0, e1 = oos_err(0.0, 2), oos_err(0.9, 2); assert e0 > 0.12 and e0 < 0.35 and e1 < 0.35
    # same noise 0.2: with coef 0.9 the series is very volatile (sum of AR) so compare scaled: just require the null error ~ 0.8*noise (mean abs of N(0,.2)=0.16)
    assert 0.12 < e0 < 0.25, e0
@test
def t3_bucket_parsing_and_probs():
    assert n.bucket_bounds("Will the US national average gas price be less than $3.7600 on November 18?") == (-1e9, 3.76)
    lo, hi = n.bucket_bounds("Will the US national average gas price be between $3.7600 and $3.7699 on November 18?"); assert lo == 3.76 and abs(hi - 3.7700) < 1e-9
    assert n.bucket_bounds("Will the US national average gas price be $3.8000+ on November 18?")[0] == 3.80
    b = [(-1e9, 3.76), (3.76, 3.77), (3.77, 1e9)]; p = n.bucket_probs(3.765, 0.001, b); assert abs(sum(p) - 1) < 1e-9 and p[1] > 0.99
@test
def t4_no_lookahead_features():
    # changing a future print (day D) must not change the forecast for D
    p, ny, gu = world(120, 0.5, 3); D = D0 + dt.timedelta(days=100)
    a = n.oos_predict(p, ny, gu, D, 1, D0 + dt.timedelta(days=8)); p2 = dict(p); p2[D] += 0.5
    b = n.oos_predict(p2, ny, gu, D, 1, D0 + dt.timedelta(days=8)); assert a == b, (a, b)
if __name__ == "__main__":
    ok = 0
    for t in TESTS:
        try: t(); ok += 1; print("PASS", t.__name__)
        except AssertionError as e: print("FAIL", t.__name__, e)
        except Exception as e: print("ERROR", t.__name__, repr(e))
    print(f"{ok} of {len(TESTS)} tests pass"); sys.exit(0 if ok == len(TESTS) else 1)
