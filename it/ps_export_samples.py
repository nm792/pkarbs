#!/usr/bin/env python3
"""READ-ONLY. Export raw PandaScore CS2 payloads for the N matches with the most in-round data.
usage: python3 -I ps_export_samples.py RAWDIR OUTDIR [N=3]
Writes OUTDIR/ps_sample_<match_id>.jsonl.gz (whole raw lines) + OUTDIR/ps_sample_index.json. Reads gz hour files only."""
import sys, os, gzip, json, glob, collections
raw, out = sys.argv[1], sys.argv[2]; n = int(sys.argv[3]) if len(sys.argv) > 3 else 3
os.makedirs(out, exist_ok=True)
rows = collections.defaultdict(list); inround = collections.Counter(); lab = {}
for f in sorted(glob.glob(os.path.join(raw, "pandascore_*.jsonl.gz"))):
    try:
        for l in gzip.open(f, "rt"):
            try: d = json.loads(l)
            except Exception: continue
            p = d.get("payload") or {}
            if "cs" not in str(d.get("slug", "")).lower() and "counter" not in str(d.get("label", "")).lower() and "current_round" not in p:
                continue
            m = d.get("match_id"); rows[m].append(l); lab[m] = d.get("label")
            cr = p.get("current_round") or {}
            if any((cr.get(t) or {}).get("players") for t in ("home_team", "away_team")): inround[m] += 1
    except Exception as e:
        print("skip", f, e)
top = [m for m, _ in inround.most_common(n)] or sorted(rows, key=lambda m: -len(rows[m]))[:n]
idx = []
for m in top:
    p = os.path.join(out, f"ps_sample_{m}.jsonl.gz")
    with gzip.open(p, "wt") as g: g.writelines(rows[m])
    idx.append({"match_id": m, "label": lab[m], "messages": len(rows[m]), "inround_messages": inround[m], "bytes": os.path.getsize(p)})
json.dump(idx, open(os.path.join(out, "ps_sample_index.json"), "w"), indent=1)
print(json.dumps(idx, indent=1)); print("matches seen", len(rows))
