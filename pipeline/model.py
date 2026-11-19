"""Combine features with LightGBM, evaluate with qlib (calc_ic, calc_long_short_return), Alphalens-style quantiles, decay, feature mining + BH,
and size trades from the combined model. Purged expanding walk-forward (training rows must END before the test fold starts)."""
import hashlib, json, math, os, sys, warnings
import numpy as np, pandas as pd, lightgbm as lgb
warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import evalx
from qlib.contrib.eva.alpha import calc_ic, calc_long_short_return

META = {"outcome", "question", "fam", "grp", "h", "H", "cond", "event", "token", "ts", "end", "day", "fill", "win", "edge", "cap_sh"}


def feature_cols(df): return [c for c in df.columns if c not in META and df[c].dtype != object]


def one_token(df):  # one token per market (the two mirror each other): hash-chosen
    k = df["cond"].map(lambda c: int(hashlib.md5(c.encode()).hexdigest(), 16) % 2)
    return df[df["token"] == k]


PARAMS = dict(objective="regression", learning_rate=0.03, num_leaves=15, min_data_in_leaf=60, feature_fraction=0.7, bagging_fraction=0.8,
              bagging_freq=1, lambda_l2=10.0, verbose=-1, seed=7, num_threads=4)


def walk_forward(df, feats, params=PARAMS, rounds=250, n_folds=5, first=0.5):
    df = df.sort_values("ts").reset_index(drop=True)
    t0, t1 = df["ts"].min(), df["ts"].max()
    edges = [t0 + (t1 - t0) * (first + (1 - first) * i / n_folds) for i in range(n_folds + 1)]
    oos, imps = [], []
    for i in range(n_folds):
        a, b = edges[i], edges[i + 1]
        tr = df[(df["end"] < a)]  # purge: label known only after market end
        te = df[(df["ts"] >= a) & (df["ts"] < b)] if i < n_folds - 1 else df[df["ts"] >= a]
        if len(tr) < 500 or len(te) == 0: continue
        m = lgb.train(params, lgb.Dataset(tr[feats], tr["edge"]), rounds)
        te = te.copy(); te["pred"] = m.predict(te[feats]); te["fold"] = i; te["_imp"] = 0
        oos.append(te)
        imps.append(pd.Series(m.feature_importance("gain"), feats))
    out = pd.concat(oos)
    return out, sum(imps) / len(imps)


def qlib_eval(d, col="pred", min_rows=10):
    d = d.copy(); d["datetime"] = pd.to_datetime(d["day"] * 86400, unit="s"); d["instrument"] = d["cond"] + "_" + d["token"].astype(str)
    cnt = d.groupby("datetime")["instrument"].transform("count"); d = d[cnt >= min_rows]
    if d.empty: return dict(n=0)
    idx = pd.MultiIndex.from_frame(d[["datetime", "instrument"]])
    pred = pd.Series(d[col].values, index=idx); lab = pd.Series(d["edge"].values, index=idx)
    ic, ric = calc_ic(pred, lab)
    try:
        ls, lsr = calc_long_short_return(pred, lab, quantile=0.2)[:2] if False else (None, None)
    except Exception:
        ls = None
    r = dict(n=len(d), days=int(ic.shape[0]), IC=float(ic.mean()), ICIR=float(ic.mean() / ic.std()) if ic.std() > 0 else np.nan,
             IC_t=float(ic.mean() / ic.std() * math.sqrt(len(ic))) if ic.std() > 0 else np.nan, rankIC=float(ric.mean()))
    r["IC_p_t"] = evalx.t_sf2(r["IC_t"], len(ic) - 1) if r["IC_t"] == r["IC_t"] else 1.0
    try:
        lr = calc_long_short_return(pred, lab, quantile=0.2)
        r["long_short_edge"] = float(lr[0].mean()); r["long_edge"] = float(lr[1].mean()) if len(lr) > 1 else None
    except Exception as e:
        r["long_short_edge"] = None
    return r


def quantiles(d, q=5):
    d = d.copy(); d["q"] = pd.qcut(d["pred"], q, labels=False, duplicates="drop")
    g = d.groupby("q").apply(lambda x: pd.Series(dict(n=len(x), pred=x["pred"].mean(), fill=x["fill"].mean(), edge=x["edge"].mean(),
                                                     roi=x["edge"].sum() / x["fill"].sum())))
    return g


def size(d, thr, frac=0.10, fee_k=0.04, rng=np.random.default_rng(1), n_boot=4000, n_perm=300):
    d = d.copy(); d["fee"] = fee_k * d["fill"] * (1 - d["fill"]); d["net"] = d["pred"] - d["fee"]
    best = d.sort_values("net", ascending=False).groupby("cond").head(1)   # one side per market
    t = best[best["net"] >= thr].copy()
    t["shares"] = frac * t["cap_sh"]; t["pnl"] = (t["win"] - t["fill"] - t["fee"]) * t["shares"]; t["usd"] = t["fill"] * t["shares"]
    ndays = d["day"].nunique()
    if len(t) == 0: return dict(thr=thr, n=0)
    byday = t.groupby("day")["pnl"].sum().reindex(sorted(d["day"].unique()), fill_value=0.0).values
    boots = np.sort([rng.choice(byday, len(byday)).sum() / ndays for _ in range(n_boot)])
    # placebo: permute predictions within day (keeps cross-section sizes)
    plc = []
    for _ in range(n_perm):
        p = d.copy(); p["net"] = p.groupby("day")["net"].transform(lambda x: rng.permutation(x.values))
        bb = p.sort_values("net", ascending=False).groupby("cond").head(1); tt = bb[bb["net"] >= thr]
        plc.append(((tt["win"] - tt["fill"] - tt["fee"]) * frac * tt["cap_sh"]).sum() / ndays)
    top5 = t.groupby("day")["pnl"].sum().sort_values(ascending=False).head(5).sum() / t["pnl"].sum() if t["pnl"].sum() else np.nan
    return dict(thr=thr, n=int(len(t)), usd_deployed=float(t["usd"].sum()), usd_per_day=float(t["usd"].sum() / ndays), per_share=float(t["pnl"].sum() / t["shares"].sum()),
                pnl_per_day=float(t["pnl"].sum() / ndays), ci=[float(boots[100]), float(boots[3900])], placebo_mean=float(np.mean(plc)),
                placebo_p95=float(np.percentile(plc, 95)), top5_day_share=float(top5), n_days=int(ndays),
                by_grp={k: float(v / ndays) for k, v in t.groupby("grp")["pnl"].sum().items()})


def main(panel_path, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    df = pd.read_pickle(panel_path); feats = feature_cols(df)
    df["grp_code"] = df["grp"].astype("category").cat.codes; df["fam_code"] = df["fam"].astype("category").cat.codes
    feats += ["grp_code"]
    res = dict(n_rows=len(df), n_markets=int(df["cond"].nunique()), n_feats=len(feats), n_fams=int(df["fam"].nunique()))
    oos, imp = walk_forward(df, feats)
    imp = imp.sort_values(ascending=False)
    res["oos_rows"] = len(oos); res["oos_days"] = int(oos["day"].nunique())
    res["oos_start"] = pd.to_datetime(oos["ts"].min(), unit="s").isoformat()
    d1 = one_token(oos)
    res["qlib_all_rows"] = qlib_eval(oos); res["qlib_one_token"] = qlib_eval(d1)
    res["by_h"] = {h: qlib_eval(x) for h, x in d1.groupby("h")}
    res["by_grp"] = {g: qlib_eval(x) for g, x in d1.groupby("grp") if len(x) > 300}
    # baselines
    b = d1.copy(); b["bp"] = b["last"]; res["baseline_last_price_IC"] = qlib_eval(b, "bp")
    res["quantiles_one_token"] = quantiles(d1).round(4).reset_index().to_dict("records")
    res["quantiles_by_h"] = {h: quantiles(x).round(4).reset_index().to_dict("records") for h, x in d1.groupby("h") if len(x) > 200}
    res["importance_top15"] = imp.head(15).round(1).to_dict()
    res["sizing"] = [size(oos, thr) for thr in (0.02, 0.04, 0.06)]
    # per-feature OOS IC mining (Alpha158-style), BH over all feature x horizon cells
    mine = []
    for h, x in d1.groupby("h"):
        for f in feats:
            if f in ("grp_code",): continue
            xx = x.copy(); xx["fe"] = xx[f].fillna(xx[f].median())
            e = qlib_eval(xx, "fe")
            if e.get("n", 0) == 0 or e.get("IC") != e.get("IC"): continue
            mine.append(dict(feature=f, h=h, IC=e["IC"], t=e["IC_t"], p=e["IC_p_t"], days=e["days"]))
    mp = [m["p"] for m in mine]; keep = evalx.bh_fdr(mp, 0.1)
    for m, k in zip(mine, keep): m["BH"] = bool(k)
    res["mining_n_cells"] = len(mine); res["mining_BH_discoveries"] = sum(keep)
    res["mining_top"] = sorted(mine, key=lambda m: -abs(m["t"]))[:25]
    json.dump(res, open(f"{out_dir}/model_result.json", "w"), indent=1, default=float)
    oos[["cond", "token", "grp", "fam", "h", "ts", "day", "fill", "win", "edge", "pred", "cap_sh", "fold"]].to_pickle(f"{out_dir}/oos.pkl")
    return res


if __name__ == "__main__":
    r = main(sys.argv[1], sys.argv[2]); print(json.dumps({k: v for k, v in r.items() if k not in ("mining_top",)}, indent=1, default=float)[:6000])
