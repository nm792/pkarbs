"""Metric 5 (sample B) of LOCKED-RULE-funding-window-divergence-2026-11-17.md. usage: sample_an.py [sample.jsonl.gz]
Per symbol and per UTC hour-window: max |mid-oracle|, max |mark-oracle| (bp); seconds for |mid-oracle| to fall below 5 bp after it exceeded 25 bp
(only if it does within the sample); share of exceedances (>=25 bp) that revert (<5 bp) before the next top of the hour."""
import gzip, json, sys, collections, numpy as np
f = sys.argv[1] if len(sys.argv) > 1 else "sample.jsonl.gz"
rows = [json.loads(l) for l in gzip.open(f, "rt")]
by = collections.defaultdict(list)
for r in rows: by[(r["v"], r.get("d", ""), r["s"], int(r["t"] // 3600))].append(r)
res = {}
print("venue/dex/sym | hour(UTC) | n | max|mid-orc| | max|mark-orc| | oracle changes | exceed>=25 | secs to <5bp after first >=25 | reverted before next top of hour")
for k, v in sorted(by.items()):
    v.sort(key=lambda x: x["t"]); ts = np.array([x["t"] for x in v]); orc = np.array([x["oracle"] for x in v], float)
    mid = np.array([(x["mid"] / x["oracle"] - 1) * 1e4 if x.get("mid") else np.nan for x in v]); mk = np.array([(x["mark"] / x["oracle"] - 1) * 1e4 for x in v])
    if np.all(np.isnan(mid)): continue
    ex = np.where(np.abs(mid) >= 25)[0]; secs = None; rev = None
    if len(ex):
        i0 = ex[0]; after = np.where(np.abs(mid[i0:]) < 5)[0]
        rev = bool(len(after)); secs = float(ts[i0 + after[0]] - ts[i0]) if rev else None
    r = dict(n=len(v), max_mid=float(np.nanmax(np.abs(mid))), max_mark=float(np.max(np.abs(mk))), oracle_changes=int((np.diff(orc) != 0).sum()), exceeded=bool(len(ex)), secs_to_revert=secs, reverted=rev)
    res["/".join(map(str, k))] = r
    print(k, r)
ex_cells = [r for r in res.values() if r["exceeded"]]
print("windows", len(res), "with exceedance", len(ex_cells), "share reverting before the next top of the hour", (sum(1 for r in ex_cells if r["reverted"]) / len(ex_cells)) if ex_cells else None)
json.dump(res, open("sample_result.json", "w"), indent=1)
