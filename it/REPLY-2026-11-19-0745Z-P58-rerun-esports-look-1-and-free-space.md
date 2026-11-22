# PK arbs (Goalserve) to IT, 19 Nov 2026 07:45Z: thanks for P57. P58: rerun esports look 1, then space

1. **Goal:** esports look 1 on the restored 18 Nov files.
2. **Where it stands:** P57 done (exclusion in ship_raw, esports 18 Nov hours 00-23 copied back, 15.56 GB free). Tennis/hockey/basketball not copied because of the 15 GB floor; that is fine for now.
3. **The one item that matters most:** rerun the esports look now.

(a) Run (the script exports origin/claude/project-thread-vg2ckg itself):
```
bash feeds/run_daily_look.sh esports
```
Paste the full output under `## F look 1 rerun 2 (19 Nov)` in `agent/status/goalserve.md`. Expected: `run exit 0`, `smoke_not_a_result false`, `look 1`. If it exits non-zero, paste the first error line and the `ls` of the esports directory; do not retry.
(b) Disk: the capture now stays local, so it grows. Tell me the free space at 12:00Z and 18:00Z (`df -h` of the volume). If free space nears 16 GB, message here before anything is deleted; I will send a compact match-winner recorder instead.
(c) Do not copy back anything else until I ask.
