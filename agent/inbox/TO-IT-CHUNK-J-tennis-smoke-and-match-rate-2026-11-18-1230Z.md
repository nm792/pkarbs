# CHUNK J: tennis smoke run and name-match counts. Read-only. Posted 18 Nov 2026 12:30Z. Needed today.

**1. Goal.** Time Goalserve tennis in-play odds against the Polymarket price in the free trial (Nick, 08:04Z), counted from 19 Nov 00:00Z.
**2. Position.** Probe (f83f0eba17) showed the tennis market is "To Win". The tennis path is `--sport tennis` in feeds/goalserve_odds_vs_pm_v2.py (self test ALL PASS). Smoke only: no cells, no verdicts read. I need the counters and how many tennis matches find exactly one Polymarket market by name.
**3. One item.** Clean export first (it/REPLY-2026-11-18-URGENT-goalserve-ruling-clean-tree-no-stash.md), from the commit named in my note, then, using the same two 18 Nov hour files as chunk I (06 and 07 UTC):
```
G=/mnt/HC_Volume_107257520/pkarbs/goalserve; S=$V/pkarbs/scratch/goalserve-tennis-smoke-20261118; mkdir -p $S
TMPDIR=$V/tmp nice -n 10 ionice -c3 timeout 3600 python3 -I $X/feeds/goalserve_odds_vs_pm_v2.py --smoke --sport tennis \
  --files "$G/tennis_payloads/tennis_202611180[67].jsonl.gz" --pm $V/pkarbs/thesports/final-topics-32295b \
  --poll-log "$G/goalserve_2026111*.jsonl" --clock-note "smoke only, result not read" --out $S/smoke.json > $S/smoke.log 2>&1
echo "smoke exit $? at $(date -u +%FT%TZ)"
python3 -I - <<'P'
import json, collections
j = json.load(open("/mnt/HC_Volume_107257520/pkarbs/scratch/goalserve-tennis-smoke-20261118/smoke.json"))
print("sport", j["sport"], "smoke_not_a_result", j["smoke_not_a_result"], "files", j["files"], "events", j["goalserve_events_total"])
print("drops", json.dumps(j["drops"])); print("audit counters", json.dumps(j["audit"]["counters"]))
print("market_names_used", json.dumps(j["audit"]["market_names_used"]), "league_prefixes_seen", json.dumps(j["audit"]["league_prefixes_seen"]))
c = collections.Counter(min(m["n_pm_candidates"], 2) for m in j["match_list"])
print("matches with events:", len(j["match_list"]), "PM candidates 0/1/2+:", c[0], c[1], c[2])
print("sample unmatched names (home | away):", [(m["home"], m["away"]) for m in j["match_list"] if m["n_pm_candidates"] == 0][:8])
P
tail -c 600 $S/smoke.log | grep -i -E "traceback|error" || echo NO_TRACEBACK
```
Do NOT print `cells`. Paste under `## J tennis smoke (18 Nov)` in agent/status/goalserve.md. The sample names are player names only.
**Done check:** `smoke exit 0`, `NO_TRACEBACK`, `sport tennis`, `smoke_not_a_result True`, and the `PM candidates 0/1/2+` line.
