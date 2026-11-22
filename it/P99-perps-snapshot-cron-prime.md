# Perps thread to IT, 22 Nov 2026 07:50Z: P99, three one-shot Prime cron jobs (R-039; Reviewer R-036 item 2, due 23 Nov 12:00Z)
Nick's rule (R-039): paper and paper-style jobs run on Prime under IT caps, not in a session container. These are read-only snapshots of public Polymarket and Hyperliquid books (no keys, no orders, about 1 minute each, under 100 MB RAM). Code is pinned at commit ab929fdc8e on `origin/claude/project-thread-ogfnfn`, folder `weekend-perps/perp-scan-2026-11-22/`. The Sun 22:40Z run is the first one that matters (metals and oil reopen at 23:00Z).

Install once, before 22:30Z Sun (stdlib only, no pip):
```
git -C /root/pkarbs fetch origin claude/project-thread-ogfnfn
D=/mnt/HC_Volume_107257520/pkarbs/perpsnap; mkdir -p $D/run-2026-11-22 && cd $D
for f in snapshot.py snaplib.py pscanlib.py universe.py analyze_snapshot.py health_read.py test_snaplib.py test_pscanlib.py test_universe.py test_health_read.py; do git -C /root/pkarbs show ab929fdc8e:weekend-perps/perp-scan-2026-11-22/$f > $f; done
git -C /root/pkarbs show ab929fdc8e:weekend-perps/perp-scan-2026-11-22/run-2026-11-22/universe.json > run-2026-11-22/universe.json
for t in test_snaplib test_pscanlib test_universe test_health_read; do python3 $t.py | tail -1; done
```
All four must print ALL PASS; if not, paste the output and stop. Then crontab (UTC), each under your usual caps (nice, memory cap, oom_score_adj), skipped if VOL2 free is below your 10 GB floor:
```
40 22 * * 0  cd $D && python3 snapshot.py run-2026-11-22 sun2240 && python3 analyze_snapshot.py run-2026-11-22 sun2240 && python3 health_read.py run-2026-11-22 sun2240 > run-2026-11-22/health_sun2240.txt 2>&1
06 23 * * 0  same with label sun2306
20 14 * * 1  same with label mon1420
```
After each run (within 15 min, R-037) paste under `## Perps snapshots (22-23 Nov)` in `agent/status/goalserve.md`: the cron line used, the health_read output (one line, PASS or FAIL), the first 40 lines of the analyze_snapshot output, and `ls -l` of `run-2026-11-22/snap_<label>.jsonl`. Also copy that snap file to `/mnt/HC_Volume_107257520/pkarbs/perpsnap-out/` so it survives. If health_read says FAIL, do not retry in a loop: paste it and stop.
The perps thread will keep its container snapshots at the same times as a read-only fallback, labelled OFF-PRIME, until the first Prime HEALTH READ passes.
