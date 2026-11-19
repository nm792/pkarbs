"""Freeze factor sets and score them only on data after selection.
select(): per horizon, per feature, one-token Pearson IC per day (rows with ts and end before cutoff), BH q=0.10, sign = sign of IC.
Composite = mean over selected features at that horizon of sign * clipped z-score (median/sd from the selection window only)."""
import hashlib, json, sys, os, datetime as dt
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import model as M, evalx
from qlib.contrib.eva.alpha import calc_ic


def day_ic(d, col, min_rows=10):
    d = d.copy(); d["datetime"] = pd.to_datetime(d["day"] * 86400, unit="s"); d["instrument"] = d["cond"] + "_" + d["token"].astype(str)
    cnt = d.groupby("datetime")["instrument"].transform("count"); d = d[cnt >= min_rows]
    if d.empty: return None
    idx = pd.MultiIndex.from_frame(d[["datetime", "instrument"]])
    ic, _ = calc_ic(pd.Series(d[col].values, index=idx), pd.Series(d["edge"].values, index=idx))
    return ic.dropna()


def select(panel, cutoff_ts, q=0.10, min_days=8, lo_ts=-1e18):
    sel = panel[(panel["end"] < cutoff_ts) & (panel["ts"] >= lo_ts)]
    feats = [c for c in M.feature_cols(panel) if c != "grp_code"]
    cells = []
    for h, x in M.one_token(sel).groupby("h"):
        for f in feats:
            xx = x[["day", "cond", "token", "edge"]].copy(); xx["fe"] = x[f].fillna(x[f].median())
            ic = day_ic(xx, "fe")
            if ic is None or len(ic) < min_days or ic.std() == 0: continue
            t = ic.mean() / ic.std() * np.sqrt(len(ic))
            cells.append(dict(h=h, feature=f, ic=float(ic.mean()), t=float(t), p=evalx.t_sf2(t, len(ic) - 1), days=int(len(ic))))
    keep = evalx.bh_fdr([c["p"] for c in cells], q)
    for c, k in zip(cells, keep): c["bh"] = bool(k)
    chosen = [dict(h=c["h"], feature=c["feature"], sign=1 if c["ic"] > 0 else -1, ic=c["ic"], t=c["t"], days=c["days"]) for c in cells if c["bh"]]
    params = {}
    for h, x in sel.groupby("h"):
        for f in {c["feature"] for c in chosen if c["h"] == h}:
            params[f"{h}|{f}"] = dict(med=float(x[f].median()), sd=float(x[f].std() or 1.0))
    return dict(cutoff_ts=cutoff_ts, n_cells=len(cells), n_selected=len(chosen), selected=chosen, params=params)


def score(rows, frozen):
    out = pd.Series(0.0, index=rows.index); cnt = pd.Series(0, index=rows.index)
    for c in frozen["selected"]:
        m = rows["h"] == c["h"]; p = frozen["params"][f"{c['h']}|{c['feature']}"]
        z = ((rows.loc[m, c["feature"]].fillna(p["med"]) - p["med"]) / p["sd"]).clip(-5, 5) * c["sign"]
        out[m] += z; cnt[m] += 1
    return out / cnt.replace(0, np.nan)


def evaluate(rows, frozen, n_boot=4000, seed=1):
    rows = rows.copy(); rows["sc"] = score(rows, frozen); res = {}
    rng = np.random.default_rng(seed)
    for h, x in M.one_token(rows).groupby("h"):
        x = x[x["sc"].notna()]
        if len(x) < 50: res[h] = dict(n=len(x), note="too few"); continue
        ic = day_ic(x.assign(fe=x["sc"]), "fe")
        r = dict(n=int(len(x)), days=int(len(ic)) if ic is not None else 0)
        if ic is not None and len(ic) > 3 and ic.std() > 0:
            t = ic.mean() / ic.std() * np.sqrt(len(ic)); r.update(IC=float(ic.mean()), t=float(t), p_two_sided=evalx.t_sf2(t, len(ic) - 1))
        top = x[x["sc"] >= x["sc"].quantile(0.8)]; bot = x[x["sc"] <= x["sc"].quantile(0.2)]
        def roi_ci(z):
            g = {d: v for d, v in z.groupby("day")}; ds = list(g); b = []
            for _ in range(n_boot):
                pick = pd.concat([g[ds[i]] for i in rng.integers(0, len(ds), len(ds))]); b.append(pick["edge"].sum() / pick["fill"].sum())
            b = np.sort(b); return float(b[int(0.025 * n_boot)]), float(b[int(0.975 * n_boot)])
        r.update(top_quintile=dict(n=int(len(top)), mean_edge=float(top["edge"].mean()), roi=float(top["edge"].sum() / top["fill"].sum()), roi_ci=roi_ci(top), mean_fill=float(top["fill"].mean())),
                 bottom_quintile=dict(n=int(len(bot)), mean_edge=float(bot["edge"].mean()), roi=float(bot["edge"].sum() / bot["fill"].sum())),
                 all=dict(mean_edge=float(x["edge"].mean()), roi=float(x["edge"].sum() / x["fill"].sum())))
        res[h] = r
    return res


if __name__ == "__main__":
    panel = pd.read_pickle(sys.argv[1]); out = sys.argv[2]; os.makedirs(out, exist_ok=True)
    mode = sys.argv[3]
    if mode == "freeze_all":
        fz = select(panel, float(panel["end"].max()) + 1)
        fz["frozen_at_utc"] = dt.datetime.now(dt.timezone.utc).isoformat(); fz["panel_last_decision_ts"] = float(panel["ts"].max())
        fz["rule"] = "composite = mean(sign*clip((x-med)/sd,-5,5)) over selected features of the row's horizon; params fixed from selection window; pre-registered forward test: Pearson IC per day of composite vs edge (win - causal fill) on days AFTER panel_last_decision_ts, one-sided p<0.05 per horizon, plus top-quintile ROI CI"
        json.dump(fz, open(f"{out}/FROZEN-ALL.json", "w"), indent=1); print(fz["n_cells"], fz["n_selected"])
    elif mode == "backward":
        T = pd.Timestamp(sys.argv[4], tz="UTC").timestamp()
        fz = select(panel, float(panel["end"].max()) + 1, lo_ts=T); fz["frozen_at_utc"] = dt.datetime.now(dt.timezone.utc).isoformat()
        fz["selection_window"] = [T, float(panel["ts"].max())]
        json.dump(fz, open(f"{out}/FROZEN-23.json", "w"), indent=1)
        test = panel[panel["end"] < T]; ev = evaluate(test, fz); json.dump(ev, open(f"{out}/BACKWARD-RESULT.json", "w"), indent=1, default=float)
        print("selected", fz["n_selected"], "of", fz["n_cells"], "| held-out rows (before selection window)", len(test), "days", test["day"].nunique())
        for c in fz["selected"]: print(c["h"], c["feature"], c["sign"], round(c["ic"], 3), round(c["t"], 2), c["days"])
        print(json.dumps(ev, indent=1, default=float))
    else:
        cut = pd.Timestamp(sys.argv[4], tz="UTC").timestamp()
        fz = select(panel, cut); json.dump(fz, open(f"{out}/FROZEN-CUT.json", "w"), indent=1)
        test = panel[panel["ts"] >= cut]
        ev = evaluate(test, fz); json.dump(ev, open(f"{out}/HELDBACK-RESULT.json", "w"), indent=1, default=float)
        print("selected", fz["n_selected"], "of", fz["n_cells"], "test rows", len(test), "test days", test["day"].nunique())
        for c in fz["selected"][:30]: print(c)
        print(json.dumps(ev, indent=1, default=float))
