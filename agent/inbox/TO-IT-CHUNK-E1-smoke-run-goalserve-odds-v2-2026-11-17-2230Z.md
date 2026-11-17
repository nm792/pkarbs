# CHUNK E1: smoke run of the Goalserve odds v2 test on OLD files, to catch real-format crashes. Read-only. 17 Nov 2026 22:30Z

**1. Project goal.** Find and build automated prediction-market edges toward $500/day; this thread tests whether Goalserve odds move before the Polymarket price.

**2. Where we stand.** v1 (four runs, Prime c252f0f0) returned "unknown" in every cell; independent audit reviews/AUDIT-goalserve-odds-vs-pm-result-2026-11-17.md. Nick approved a locked rerun on NEW data (18 to 24 Nov), card answered 17 Nov 22:15:13Z. The v2 code and pre-registration are committed (PR in this commit): feeds/goalserve_odds_vs_pm_v2.py, feeds/PREREG-goalserve-odds-vs-pm-v2-2026-11-18.md. Not yet signed by the checker thread; the REAL run (chunk E2) will not be posted before that.

**3. The one item that matters.** One short command run to prove v2 does not crash on the real file and PM formats, before the new week starts. **Do not post or read any cell or verdict**: the old files are already seen and the design is locked.

**Gate:** data-disk free above 20 GB, else stop and post the `df` line. Use the existing copy `T=/mnt/HC_Volume_107257520/pkarbs/scratch/goalserve-odds-vs-pm-20261117/gs` (no new copy needed).

```bash
set -u
cd /root/pkarbs && git pull --ff-only
V=/mnt/HC_Volume_107257520
T=$V/pkarbs/scratch/goalserve-odds-vs-pm-20261117
S=$V/pkarbs/scratch/goalserve-odds-v2-smoke-20261117; mkdir -p $S
date -u +%FT%TZ; df -B1 --output=avail $V | tail -1
sha256sum feeds/goalserve_odds_vs_pm_v2.py feeds/test_goalserve_odds_vs_pm_v2.py
python3 -m py_compile feeds/goalserve_odds_vs_pm_v2.py && echo COMPILE_OK
python3 -I feeds/test_goalserve_odds_vs_pm_v2.py | tail -3     # about 3 minutes; must print ALL PASS
TMPDIR=$V/tmp nice -n 10 ionice -c3 timeout 3600 python3 -I feeds/goalserve_odds_vs_pm_v2.py \
  --files "$T/gs/esports_20261116*.jsonl.gz" --pm $V/pkarbs/thesports/final-topics-32295b \
  --poll-log "$V/pkarbs/goalserve/goalserve_2026111*.jsonl" --clock-note "smoke run only, result not read" --out $S/smoke.json > $S/smoke.log 2>&1
echo "smoke exit $? at $(date -u +%FT%TZ)"
python3 -I - <<'P'
import json
j = json.load(open("/mnt/HC_Volume_107257520/pkarbs/scratch/goalserve-odds-v2-smoke-20261117/smoke.json"))
print("files", j["files"], "events", j["goalserve_events_total"], "cells", len(j["cells"]))
print("drops", json.dumps(j["drops"]))
print("audit counters", json.dumps(j["audit"]["counters"]))
print("league_prefixes_seen", json.dumps(j["audit"]["league_prefixes_seen"]), "bm_values", json.dumps(j["audit"]["bm_values"]))
P
tail -c 600 $S/smoke.log | grep -i -E "traceback|error" || echo NO_TRACEBACK
```
Post these lines only (append to agent/status/goalserve.md under `## E1 smoke (17 Nov)`). Do NOT print `cells`. If the self test does not print ALL PASS or the run raises an error, post the last 20 lines of the output and stop.

**Done check:** `ALL PASS` printed, `smoke exit 0`, `NO_TRACEBACK`, `files` > 0.
**Order:** after P15d4 (done) and ahead of P16s if disk and time allow; it needs about 5 minutes of one core. Do not start any other job on the data volume for it.
