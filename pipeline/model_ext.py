"""Ablation on finance Up/Down rows with Yahoo underlying coverage (last ~60 days): PM-only features vs PM + external drivers."""
import json, sys, os
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import model as M

df = pd.read_pickle("/home/user/pk_cache/panel_ext.pkl")
df = df[df["ext_x"].notna()].copy()
df["grp_code"] = df["grp"].astype("category").cat.codes
base = [c for c in M.feature_cols(df) if not c.startswith("ext_")]
extf = [c for c in df.columns if c.startswith("ext_")]
P2 = dict(M.PARAMS, num_leaves=7, min_data_in_leaf=40)
out = {"n_rows": len(df), "n_markets": int(df["cond"].nunique()), "n_fams": int(df["fam"].nunique()), "days": int(df["day"].nunique())}
for name, fs in (("PM_only", base), ("PM_plus_ext", base + extf), ("ext_only", extf + ["last", "logH"])):
    oos, imp = M.walk_forward(df, fs, P2, rounds=150, n_folds=4, first=0.5)
    d1 = M.one_token(oos)
    out[name] = dict(oos_rows=len(oos), qlib_one_token=M.qlib_eval(d1, min_rows=6), qlib_all=M.qlib_eval(oos, min_rows=6),
                     by_h={h: M.qlib_eval(x, min_rows=6) for h, x in d1.groupby("h")},
                     quantiles=M.quantiles(d1).round(4).reset_index().to_dict("records"),
                     sizing=[M.size(oos, t, n_perm=200) for t in (0.02, 0.04, 0.06)],
                     top_imp=imp.sort_values(ascending=False).head(8).round(1).to_dict())
# raw single-feature OOS IC of the external z score (no model)
oos_all = M.walk_forward(df, base + extf, P2, rounds=50, n_folds=4, first=0.5)[0]
d1 = M.one_token(oos_all)
for f in ("ext_z", "ext_x", "ext_ret1h"):
    out[f"raw_IC_{f}"] = M.qlib_eval(d1.assign(fe=d1[f].fillna(0)), "fe", min_rows=6)
os.makedirs(sys.argv[1], exist_ok=True)
json.dump(out, open(f"{sys.argv[1]}/model_ext_result.json", "w"), indent=1, default=float)
for k in ("n_rows", "n_markets", "n_fams", "days"): print(k, out[k])
for k in ("PM_only", "PM_plus_ext", "ext_only"):
    o = out[k]; print(k, "oos_rows", o["oos_rows"], {a: (round(b, 4) if isinstance(b, float) else b) for a, b in o["qlib_one_token"].items()})
    for s in o["sizing"]: print("   size", {a: (round(b, 3) if isinstance(b, float) else b) for a, b in s.items() if a != "by_grp"})
    print("   top", o["top_imp"])
for f in ("ext_z", "ext_x", "ext_ret1h"): print("raw", f, {a: (round(b, 4) if isinstance(b, float) else b) for a, b in out[f"raw_IC_{f}"].items()})
