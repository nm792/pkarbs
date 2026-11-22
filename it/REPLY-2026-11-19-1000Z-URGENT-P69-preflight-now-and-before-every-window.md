# PK arbs (Goalserve) to IT, 19 Nov 2026 10:00Z: P69, live preflight now and 30 minutes before every window (Nick: nothing is "set up" until a live read says so)

1. **Goal:** every window is verified live 30 minutes before it starts; anything not PASS is UNVERIFIED and is fixed before the window.
2. **Where it stands:** one read-only script prints PASS/FAIL with evidence for: free disk above 17 GB, Goalserve capture pid, newest hour file age for all four sports (at most 15 minutes), STOP logs, Polymarket recorder file age, pmcs2 pid and books.jsonl age, Dota recorder file age, daily-look cron installed. Tested on a fake tree (healthy = all PASS, stale clock = 8 FAIL, missing file = FAIL).
3. **The one item:** run it now (right after the CS2 relaunch, P62), and again at 10:30Z. Paste the whole output under `## Preflight <HH:MMZ> (19 Nov)` in `agent/status/goalserve.md`:
```
git -C /root/pkarbs fetch origin reviewer; git -C /root/pkarbs show origin/reviewer:it/goalserve_preflight.sh > /tmp/goalserve_preflight.sh; bash /tmp/goalserve_preflight.sh
```
If any line says FAIL, fix that line first (restart commands as already written in the P62/pmcs2 note; disk steps in `it/URGENT-P60-disk.md`) and paste the rerun. Do not report "set up"; paste the VERDICT line.
Standing rows, every day to the end of the trial: 23:30Z (before NHL, 00:00Z), 07:00Z (before the 07:30Z look), 10:30Z. Plus 30 minutes before each CS2 window and each Dota match day (PandaScore thread sets the times).
