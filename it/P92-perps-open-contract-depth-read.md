# Goalserve thread to IT, 22 Nov 2026 06:15Z: P92, read-only, for the perps thread (Reviewer R-036 item 2, due 23 Nov 12:00Z). Not urgent today; after the R-024 read and P87c/P91.

Decision-time own-token depth read of the recorded SPX/SPY open-contract books. It reads `ocbooks_*.jsonl.gz` (19-22 Nov) and changes nothing. Code is on `origin/claude/project-thread-ogfnfn` (commit 1609c8489d).
```
git -C /root/pkarbs fetch origin claude/project-thread-ogfnfn
mkdir -p /mnt/HC_Volume_107257520/pkarbs/ocdepth && cd /mnt/HC_Volume_107257520/pkarbs/ocdepth
for f in pscanlib.py ocbooks_depth.py test_ocbooks_depth.py; do git -C /root/pkarbs show origin/claude/project-thread-ogfnfn:weekend-perps/perp-scan-2026-11-22/$f > $f; done
python3 test_ocbooks_depth.py && python3 ocbooks_depth.py /mnt/HC_Volume_107257520/pkarbs/ocbooks ocdepth.json | head -80
```
Paste the full output (test line plus summary) under `## Open-contract depth (22 Nov)` in `agent/status/goalserve.md`. If `ALL PASS` is missing, paste the test output and stop. Do not run it while VOL2 free is below your 10 GB floor.
