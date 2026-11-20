import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rule as r
P = r.Params()
def t1_yes_gap():
    assert r.take("yes_fav", 0.65, 0.61, 100, 0, 0, P) == 0                 # gap 0.04 < 0.05: no trade
    assert r.take("yes_fav", 0.65, 0.60, 100, 0, 0, P) > 0                  # gap 0.05: trade
def t2_no_out_edge_after_fee():
    assert r.take("no_out", 0.99, 0.99, 100, 0, 0, P) == 0                  # no edge
    assert r.take("no_out", 0.99, 0.98, 100, 0, 0, P) > 0                   # 0.01 - fee 0.0004 >= 0.005
    assert r.take("no_out", 0.99, 0.985, 100, 0, 0, P) == 0                 # 0.005 - fee < 0.005
def t3_kelly_and_caps():
    tgt = r.kelly_target(0.6, 0.5, 1000, 0.25); assert abs(tgt - 0.25 * 1000 * 0.1 / 0.5) < 1e-9   # $50
    assert abs(r.take("yes_fav", 0.6, 0.5, 1e9, 0, 0, P) * 0.5 - tgt) < 1e-9          # target limits size
    assert r.take("yes_fav", 0.6, 0.5, 10, 0, 0, P) == 10                                # ask size limits
    assert r.take("yes_fav", 0.6, 0.5, 1e9, tgt, 0, P) == 0                              # already at target
    assert abs(r.take("yes_fav", 0.6, 0.5, 1e9, 0, 149.5, P) * 0.5 - 0.5) < 1e-9        # event cap leaves $0.50
    assert abs(r.take("yes_fav", 0.9, 0.5, 1e9, 0, 0, P) * 0.5 - 150) < 1e-9             # event cap (150) binds below the 200 target
def t4_post_window_threshold():
    assert r.take("post", 0.995, 0.99, 50, 0, 0, P) > 0 and r.take("post", 0.995, 0.993, 50, 0, 0, P) == 0
def t5_per_rule_caps():
    p2 = r.Params(rule_caps=(("yes_fav", 0.10), ("no_out", 0.05), ("post", 0.10)))
    assert abs(r.take("no_out", 0.999, 0.98, 1e9, 0, 0, p2) * 0.98 - 50) < 1e-9          # NO capped at $50
    assert abs(r.take("yes_fav", 0.9, 0.5, 1e9, 0, 0, p2) * 0.5 - 100) < 1e-9
TESTS = [t5_per_rule_caps, t1_yes_gap, t2_no_out_edge_after_fee, t3_kelly_and_caps, t4_post_window_threshold]
if __name__ == "__main__":
    ok = 0
    for t in TESTS:
        try: t(); ok += 1; print("PASS", t.__name__)
        except AssertionError as e: print("FAIL", t.__name__, e)
    print(f"{ok} of {len(TESTS)} tests pass"); sys.exit(0 if ok == len(TESTS) else 1)
