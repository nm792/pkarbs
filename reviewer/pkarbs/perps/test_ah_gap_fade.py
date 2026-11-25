"""Can-fail tests for ah_gap_fade.py: planted 30 bp recovered, planted 0 not a pass, placebo/verdict logic, real-move fade sign."""
import datetime as dt, random, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ah_gap_fade as A

def synth(n_weekends=20, gap=0.02, revert=0.5, seed=3):
    """Friday close 100; perp at Fri 20:00 ET = 100*(1+gap*sign); Monday 09:35 ET perp reverts by `revert` of the gap."""
    rnd = random.Random(seed); daily = []; candles = []
    d = dt.date(2026, 5, 1)  # a Friday
    for k in range(n_weekends):
        fri = d + dt.timedelta(days=7 * k); mon = fri + dt.timedelta(days=3)
        daily += [dict(date=fri, open=100, close=100.0), dict(date=mon, open=100, close=100.0)]
        s = rnd.choice((-1, 1)); pin = 100 * (1 + s * gap); pout = 100 + (pin - 100) * (1 - revert)
        t_in = A.et(fri, 20, 0); t_out = A.et(mon, 9, 35)
        candles.append(dict(t=(t_in - 3600) * 1000, o=pin, h=pin, l=pin, c=pin))
        candles.append(dict(t=(t_out - 3600) * 1000, o=pout, h=pout, l=pout, c=pout))
    candles.sort(key=lambda c: c["t"]); return candles, [], daily

def test_fade_sign_and_gross():
    c, f, d = synth(revert=0.5, gap=0.02)
    rows, v = A.run(c, f, d, 0.01, (9, 35), 0.0)
    assert len(v) == 20
    # gap 2%, half reverts: fade earns ~1% = ~100 bp gross (slightly less for the short side in return terms), minus 1.8 bp fee
    assert all(95 < x < 105 for x in v), v[:3]

def test_no_reversion_is_not_pass():
    c, f, d = synth(revert=0.0)
    rows, v = A.run(c, f, d, 0.01, (9, 35), 0.0)
    vd, b = A.verdict(v, A.placebo(c, f, d, 0.0, n=500))
    assert vd != "PASS" and b["mean"] < 0, (vd, b)

def test_planted_30bp_recovered():
    c, f, d = synth(revert=0.0)
    _, v = A.run(c, f, d, 0.01, (9, 35), 5.0, plant_bp=30)
    m = sum(v) / len(v)
    assert abs(m - 30) <= 5, m

def test_planted_zero():
    c, f, d = synth(revert=0.3)
    _, v = A.run(c, f, d, 0.01, (9, 35), 5.0, plant_bp=0)
    assert abs(sum(v) / len(v)) <= 1, v[:3]

def test_threshold_excludes_small_gaps():
    c, f, d = synth(gap=0.005)
    _, v = A.run(c, f, d, 0.01, (9, 35), 0.0)
    assert v == []

def test_underpowered_below_13():
    c, f, d = synth(n_weekends=10, revert=0.5)
    _, v = A.run(c, f, d, 0.01, (9, 35), 0.0)
    vd, _ = A.verdict(v, None)
    assert vd == "UNDERPOWERED"

def test_real_reversion_passes():
    c, f, d = synth(n_weekends=20, revert=0.5)
    _, v = A.run(c, f, d, 0.01, (9, 35), 5.0)
    vd, b = A.verdict(v, A.placebo(c, f, d, 5.0, n=500))
    assert vd == "PASS", (vd, b)

if __name__ == "__main__":
    for k, fn in list(globals().items()):
        if k.startswith("test_"): fn(); print("PASS", k)
    print("ALL OK")
