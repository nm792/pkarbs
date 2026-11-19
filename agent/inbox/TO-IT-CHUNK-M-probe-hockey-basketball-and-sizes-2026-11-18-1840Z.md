# CHUNK M: probe the stored hockey and basketball bodies (market names, league strings) and the stored sizes per sport. Read-only. Posted 18 Nov 2026 18:40Z.

**1. Goal.** Nick (18:17Z): add NHL hockey to the daily runs like tennis, then basketball; list what Goalserve covers and what we capture.
**2. Position.** The tennis probe (chunk I) gave the match-winner market name. Hockey and basketball bodies have been stored since 17 Nov 09:00Z; I need their market names, and the stored bytes per sport per hour to size the disk. Same parser as the tennis probe (`feeds/gs_sport_probe.py`); counters only, no cells.
**3. The one item.** From the clean export, for S in hockey_nhl and basketball, hours 06 and 07 of 18 Nov:
```
V=/mnt/HC_Volume_107257520; G=$V/pkarbs/goalserve; T=$V/pkarbs/scratch/goalserve-probe-m; mkdir -p $T
rsync -a --include='hockey_nhl_2026111806*' --include='hockey_nhl_2026111807*' --include='basketball_2026111806*' --include='basketball_2026111807*' --exclude='*' -e "$RSYNC_RSH" "$BOX_ROOT/pkarbs/goalserve/" $T/ 2>/dev/null
for S in hockey_nhl basketball; do rsync -a --include="${S}_202611180[67]*" --exclude='*' -e "$RSYNC_RSH" "$BOX_ROOT/pkarbs/goalserve/${S}_payloads/" $T/ ; echo "== $S"
 TMPDIR=$V/tmp nice -n 10 timeout 1800 python3 -I $X/feeds/gs_sport_probe.py "$T/${S}_202611180[67].jsonl.gz" "$G/goalserve_20*.jsonl" 1794981600 1794988800; echo "exit $?"; done
for S in esports tennis hockey_nhl basketball; do echo "== bytes $S 2026-11-18 hours"; ls -l $G/${S}_payloads/${S}_20261118*.jsonl.gz 2>/dev/null | awk '{print $9, $5}' | sed 's#.*/##' | tail -4; done
du -sh $G/*_payloads 2>/dev/null; df -B1 --output=avail $V | tail -1
```
Paste under `## M hockey and basketball probe (18 Nov)` in agent/status/goalserve.md. The `bytes` lines are the compressed size of the newest hour files on this machine; if they were shipped away say so and use the box copy.
**Done check:** `exit 0` for both sports and the `market_names_used`, `market_names_excluded`, `league_prefixes_seen` lines.
