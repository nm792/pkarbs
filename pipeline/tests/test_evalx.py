import os, random, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import evalx


def synth(planted, seed=1, days=40, per_day=30):
    rnd = random.Random(seed); rows = []
    for d in range(days):
        for i in range(per_day):
            s = rnd.gauss(0, 1)
            ret = (0.5 * s if planted else 0.0) + rnd.gauss(0, 1)
            rows.append(dict(day=d, event=f"e{d}_{i // 3}", ts=d * 86400 + i, sig=s, ret=ret))
    return rows


def test_spearman_basic():
    assert abs(evalx.spearman([1, 2, 3, 4], [1, 2, 3, 4]) - 1) < 1e-9
    assert abs(evalx.spearman([1, 2, 3, 4], [4, 3, 2, 1]) + 1) < 1e-9
    assert abs(evalx.spearman([1, 1, 2, 2], [1, 2, 1, 2])) < 1e-9


def test_planted_edge_detected_oos():
    r = evalx.evaluate(synth(True))
    assert r["ic_test"] > 0.15 and r["p_test"] < 0.001


def test_null_not_detected():  # must be able to FAIL: with no edge the OOS IC is ~0 and p is large
    ps = [evalx.evaluate(synth(False, seed=s))["p_test"] for s in range(20)]
    assert sum(p < 0.05 for p in ps) <= 3  # ~1 expected by chance


def test_sign_chosen_on_train_only():
    rows = synth(True)
    for r in rows: r["sig"] = -r["sig"]  # inverted signal
    r = evalx.evaluate(rows)
    assert r["sign"] == -1 and r["ic_test"] > 0.15


def test_bh_penalty_kills_lucky_cells():
    import random as R
    rnd = R.Random(5); p = [rnd.random() for _ in range(200)] + [1e-8]
    keep = evalx.bh_fdr(p, 0.1)
    assert keep[-1] and sum(keep) <= 3


def test_cluster_t_smaller_than_naive_when_clustered():
    rows = [dict(event=f"e{i//10}", ret=(1.0 if i // 10 % 2 else -1.0) + 0.1 * (i % 3)) for i in range(200)]
    m, t, n = evalx.cluster_mean(rows)
    assert n == 20


def test_t_pvalue_small_df():
    assert abs(evalx.t_sf2(2.5706, 5) - 0.05) < 0.002
    assert abs(evalx.t_sf2(2.0, 1000) - evalx.norm_sf2(2.0)) < 0.002
    assert evalx.t_sf2(6.8, 5) > evalx.norm_sf2(6.8)  # normal would overstate significance
