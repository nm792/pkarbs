# Status: rugby Top 14 capture (task TASK-rugby-top14-capture-2026-11-07)

state: AB WINDOW RUNNING since 2026-11-07T13:00:30Z; preflight re-measured 13:02Z
last agent write: 2026-11-07 13:03 UTC (cron; preflight results + AB launch confirmed)

## Preflight (measured 13:02Z, this pass)
1. Disk: root `/` = 38G total, 17G used, 19G avail (47%). `/mnt/project-files` is on `/` (findmnt TARGET=`/`). Well above the ~2GB AB needs. PASS.
2. ESPN scoreboard 270559: 200 OK, league "French Top 14" (270559). Events present, all STATUS_SCHEDULED: 604423 STA-VS-ASM, 604881 PERPI-VS-SECTI, 604418 CAS-VS-RAC, 604420 MON-VS-LYO, 604421 SEC-VS-USA, 604422 RC-VS-STA (6 events, matches 6-match/36-token AB plan). PASS.
3. /mnt/project-files/rugby/live-2026-11/ = writable (root, drwxr-xr-x). PASS.

## Windows
- AB: RUNNING since 13:00:30Z, bounded timeout 18000s (~5h), 1 window 13:15-18:05Z. Matches kick 13:30Z (2) + 15:35Z (4).
- D: 8 Nov 13:45-16:30 UTC, Vannes v Bordeaux (61243), 6 tokens.
- C: 8 Nov 19:50-22:35 UTC, La Rochelle v Bayonne (61238), 6 tokens.
- Each starts only after the prior is reviewed and processes gone.

## AB launch issue — DUPLICATE PROCESS RACE (needs consolidate)
capture.py has NO single-instance guard. The dispatch loop launched AB 4 extra times: 5 live `rugby-top14-capture.py AB` python procs (pids 1312662, 1323749, 1335187, 1335303, 1360168) all appending to the SAME `rugby/AB_{espn,clob,rugbyrama,rugbyrama_events}.jsonl`. Five concurrent append writers => interleaved/corrupt jsonl + duplicated score/price rows. Data from this window is not trustworthy until cut down to ONE writer.

## Consent-gated item
Kill 4 of the 5 duplicate AB writers, keep ONE, so AB jsonl is single-writer clean. This is a restart/kill (protocol step 4) => needs Nick's tap. NOT done this cron.

## Outputs
- Scratch: rugby/AB_*.jsonl (growing; espn 512KB, rugbyrama 16.6MB at 13:02Z) + rugby/AB_log.txt ("SPORTS open", "CLOB open").
- 10-min copies to /mnt/project-files/rugby/live-2026-11/.
- Final commit under reports/rugby-capture/ at window end.
- Next: status line ~every 10 min in-window; report measured rugbyrama first-seen + ESPN/sports + CLOB lag at end.
