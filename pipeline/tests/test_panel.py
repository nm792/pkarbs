import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import panel


def tape(rows): return panel.Tape([(t, s, p, z) for t, s, p, z in rows])


def test_features_ignore_the_future():
    rows0 = [(100 + 60 * i, "BUY" if i % 2 else "SELL", 0.4 + 0.01 * (i % 7), 10 + i) for i in range(80)]
    rows1 = [(100 + 70 * i, "BUY" if i % 3 else "SELL", 0.55 - 0.01 * (i % 5), 5 + i) for i in range(70)]
    t = 100 + 60 * 50 + 0.5
    full = [tape(rows0), tape(rows1)]
    cut = [tape([r for r in rows0 if r[0] < t]), tape([r for r in rows1 if r[0] < t])]
    a = panel.row_feats(full, 0, t, 3600, None); b = panel.row_feats(cut, 0, t, 3600, None)
    assert a.keys() == b.keys()
    for k in a:
        assert (a[k] == b[k]) or (isinstance(a[k], float) and math.isnan(a[k]) and math.isnan(b[k])), k


def test_print_at_decision_time_is_not_visible():
    tp = tape([(10, "BUY", 0.40, 1), (20, "BUY", 0.90, 1)])
    assert tp.last_before(20) == 0.40 and tp.last_before(20.01) == 0.90


def test_other_token_uses_its_own_prints():
    a = tape([(1, "BUY", 0.70, 1)]); b = tape([(1, "BUY", 0.35, 1)])
    f = panel.row_feats([a, b], 0, 5, 600, None)
    assert f["other_last"] == 0.35 and abs(f["sum_last"] - 1.05) < 1e-9  # not 1 - 0.70


def test_walk_forward_purges_unresolved_labels():
    import numpy as np, pandas as pd, model as M
    rng = np.random.default_rng(0); n = 3000
    ts = np.sort(rng.uniform(0, 1e6, n)); end = ts + rng.uniform(1e3, 2e5, n)
    df = pd.DataFrame(dict(ts=ts, end=end, f1=rng.normal(size=n), edge=rng.normal(size=n), day=(ts // 86400).astype(int),
                           cond=[f"c{i}" for i in range(n)], token=0, h="1h", grp="g", fill=0.5, win=0.0, cap_sh=1.0, fam="f"))
    seen = {}
    orig = M.lgb.train
    def spy(params, ds, rounds): seen.setdefault("n", []).append(len(ds.data)); return orig(params, ds, rounds)
    M.lgb.train = spy
    try: oos, _ = M.walk_forward(df, ["f1"], rounds=5)
    finally: M.lgb.train = orig
    assert oos["fold"].nunique() >= 4 and (oos["ts"] >= df["ts"].min()).all()
    # with purge the first fold trains on fewer rows than all rows before its start
    a = df["ts"].min() + (df["ts"].max() - df["ts"].min()) * 0.5
    assert seen["n"][0] == int((df["end"] < a).sum()) and seen["n"][0] < int((df["ts"] < a).sum())
