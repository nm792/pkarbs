"""Horizon-specific models (follow-up to the mining result: 16 BH discoveries at 6 h on 158 days). Same purged walk-forward, qlib IC, sizing."""
import json, sys, os
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import model as M
from sklearn.linear_model import Ridge
df = pd.read_pickle(sys.argv[1]); df["grp_code"] = df["grp"].astype("category").cat.codes
feats = M.feature_cols(df)
out = {}
for h in ("6h", "24h"):
    d = df[df["h"] == h].copy()
    P2 = dict(M.PARAMS, num_leaves=7, min_data_in_leaf=80, learning_rate=0.02)
    oos, imp = M.walk_forward(d, feats, P2, rounds=200, n_folds=5, first=0.5)
    # ridge on a fixed, pre-registered set: the Alpha158-style momentum/range features found at 6 h (chosen from the mining table, same data: see limits)
    ridge_f = ["CNTP_24h", "CNTP_6h", "SUMP_24h", "KMID_24h", "STD_5m", "KLEN_5m", "MAX_5m", "IMIN_24h", "MA_24h", "last", "other_last"]
    dd = d.sort_values("ts").reset_index(drop=True); t0, t1 = dd["ts"].min(), dd["ts"].max(); edges = [t0 + (t1 - t0) * (0.5 + 0.1 * i) for i in range(6)]
    rp = []
    for i in range(5):
        a, b = edges[i], edges[i + 1]; tr = dd[dd["end"] < a]; te = dd[(dd["ts"] >= a) & ((dd["ts"] < b) if i < 4 else True)].copy()
        med = tr[ridge_f].median(); sd = tr[ridge_f].std().replace(0, 1)
        X = ((tr[ridge_f].fillna(med) - med) / sd).values; Xt = ((te[ridge_f].fillna(med) - med) / sd).values
        r = Ridge(alpha=300.0).fit(X, tr["edge"]); te["pred"] = r.predict(Xt); rp.append(te)
    rp = pd.concat(rp)
    for name, o in (("lgbm", oos), ("ridge_discovered_features", rp)):
        d1 = M.one_token(o)
        out[f"{h}_{name}"] = dict(rows=len(o), qlib=M.qlib_eval(d1), quantiles=M.quantiles(d1).round(4).reset_index().to_dict("records"),
                                  sizing=[M.size(o, t, n_perm=200) for t in (0.02, 0.04)])
os.makedirs(sys.argv[2], exist_ok=True); json.dump(out, open(f"{sys.argv[2]}/model_h_result.json", "w"), indent=1, default=float)
for k, v in out.items():
    print(k, v["rows"], {a: (round(b, 4) if isinstance(b, float) else b) for a, b in v["qlib"].items()})
    print("   q", [(q["q"], round(q["edge"], 4), round(q["roi"], 3)) for q in v["quantiles"]])
    for s in v["sizing"]: print("   size", {a: (round(b, 3) if isinstance(b, float) else b) for a, b in s.items() if a != "by_grp"})
