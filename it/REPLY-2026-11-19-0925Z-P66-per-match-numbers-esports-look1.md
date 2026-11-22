# PK arbs (Goalserve) to IT, 19 Nov 2026 09:25Z: P66, per-match numbers from esports look 1 (read-only, 1 minute, after P60/P65)

1. **Goal:** Nick asked what actually happened in the 6 CS2 matches. The numbers are already in the result file; I need them pasted.
2. **Where it stands:** `result-esports-look1.json`, sha256 cd46ef0e91bdfc1dccb32f012e3a6c9a8976fa43719a3452404833ec5b8f4c65. Read-only, no credentials.
3. **The one item:** run and paste the whole output under `## P66 look 1 per match (19 Nov)` in `agent/status/goalserve.md`:
```
python3 -I - <<'PY'
import json
r = json.load(open("/mnt/HC_Volume_107257520/pkarbs/scratch/goalserve-daily-esports/result-esports-look1.json"))
c = r["cells"]["cs2|Match Winner"]
for k in ("n_matches_used","n_matches_seen","n_events","mean_d_per_match","se","t_stat","z_eq","boundary_z","share_events_real_gt_placebo_pct","ties_d_zero","post_real","pre_real","post_placebo","pre_placebo","events_per_match","per_match_mean_d","matches_by_day","excluded_counts"):
    print(k, json.dumps(c.get(k)))
print([ (m["eid"], m["home"], m["away"], m.get("n_events"), m.get("n_pm_candidates")) for m in r["match_list"] if m["kind"]=="Match Winner"][:20])
PY
```
The same output is the base for Nick's per-match table. Do not rerun the look.
