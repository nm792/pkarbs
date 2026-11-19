"""Alphalens (alphalens-reloaded) analysis of the OOS combined-model score with edge (win - fill) as the 'forward return' (period '1D' label only)."""
import json, sys, warnings
import numpy as np, pandas as pd
warnings.filterwarnings("ignore")
import alphalens.utils as au, alphalens.performance as ap
import model as M
oos = pd.read_pickle(sys.argv[1]); d = M.one_token(oos)
d = d.copy(); d["date"] = pd.to_datetime(d["day"] * 86400, unit="s", utc=True); d["asset"] = d["cond"] + "_" + d["token"].astype(str)
cnt = d.groupby("date")["asset"].transform("count"); d = d[cnt >= 10]
factor = d.set_index(["date", "asset"])["pred"]
fwd = pd.DataFrame({"1D": d.set_index(["date", "asset"])["edge"]})
out = {}
try:
    clean = au.get_clean_factor(factor, fwd, quantiles=5, max_loss=0.6, zero_aware=False)
    ic = ap.factor_information_coefficient(clean); mq, se = ap.mean_return_by_quantile(clean, by_date=False)
    out = dict(n=int(len(clean)), IC_mean=float(ic["1D"].mean()), IC_std=float(ic["1D"].std()), IC_days=int(len(ic)),
               mean_edge_by_quantile=mq["1D"].round(4).to_dict(), stderr_by_quantile=se["1D"].round(4).to_dict())
except Exception as e:
    out = dict(error=str(e)[:300])
json.dump(out, open(sys.argv[2], "w"), indent=1, default=float); print(out)
