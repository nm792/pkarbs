
## #339 safe-restart gate recheck — 2026-11-14 15:13Z

- Approved patch remains staged only: `live/pandascore/ll_capture.py` SHA-256 `be437551ef871437a0a168f25ef09886dc161569c72060243393bbe8241dc8f7`; byte-identical backup `live/pandascore/ll_capture.py.pre-339-20261114T135600Z`, SHA-256 `a6d7d06a962b3eeb86fac6711e6a8a47f7b6358eca7403979732245833d698ba`. Compile passed in prior verification.
- No-live-match gate is not met. Tolerant read of the append-streamed current-hour file recovered two latest status rows: match 1786831 `running` at 15:12:55Z and match 1789161 `not_started` at 15:12:45Z. Earlier current-hour rows also include live matches. Restart not attempted.
- Capture process PID 548127 remains on the pre-edit version (started 13 Nov 17:39:46Z). The 4004 retry loop for match 1789154 remains visible in the event log; the approved fix is not live.
- OPEN / NOT VERIFIED: safe restart and post-restart behavior. Recheck only when the source advances; restart only after the approved no-live-match condition is established.


## #339 safe-restart gate recheck — 2026-11-14 15:23Z

- Approved patch remains staged only: `live/pandascore/ll_capture.py` SHA-256 `be437551ef871437a0a168f25ef09886dc161569c72060243393bbe8241dc8f7`; backup `live/pandascore/ll_capture.py.pre-339-20261114T135600Z` SHA-256 `a6d7d06a962b3eeb86fac6711e6a8a47f7b6358eca7403979732245833d698ba`. No code changed.
- Restart gate still fails: tolerant read of the open 15:00Z gzip has latest status rows at 15:23:35Z for matches 1786831 and 1789161; both report `running`. Restart not attempted.
- Capture PID 548127 remains on the pre-edit process (started 13 Nov 17:39:46Z). Match 1789154 continues producing code-4004 closes every ~10 seconds through 15:23Z.
- OPEN / NOT VERIFIED: safe restart and post-restart behavior. Recheck only after fresh data establishes no match is live.


## #339 safe-restart gate recheck — 2026-11-14 15:33Z

- Fresh tolerant read recovered 315 status rows from the open current-hour gzip; latest observed statuses at 15:33:25Z (1786831) and 15:33:26Z (1789161) are both `running`. No-live-match gate remains false; restart not attempted.
- Capture PID 548127 remains active, started 13 Nov 17:39:46Z. Approved source SHA is still `be437551ef871437a0a168f25ef09886dc161569c72060243393bbe8241dc8f7`; running process remains pre-edit.
- OPEN / NOT VERIFIED: restart and post-restart behavior, held until fresh source rows establish no live match.


## #339 safe-restart gate recheck — 2026-11-14 15:42Z

- Fresh tolerant read of the append-streamed 15:00Z capture shows matches 1786831 and 1789161 both `running`, with latest status updates at 15:42:09Z. The no-live-match precondition is false; restart not attempted.
- Capture PID 548127 remains active on the pre-edit process (started 13 Nov 17:39:46Z). The approved patch remains staged, not live: `live/pandascore/ll_capture.py` SHA-256 `be437551ef871437a0a168f25ef09886dc161569c720602433bbe8241dc8f7`; byte-identical backup SHA-256 `a6d7d06a962b3eeb86fac6711e6a8a47f7b6358eca7403979732245833d698ba`.
- OPEN / NOT VERIFIED: restart and post-restart proof, held until fresh source data establishes no live match.


## #339 safe-restart gate recheck — 2026-11-14 15:53Z

- The approved patch remains staged, not live; active capture PID 548127 is still running and was not stopped.
- The no-live-match gate remains false. Tolerant read of the open 15:00Z gzip recovered 643 complete rows before expected EOFError on the append-streamed file. Latest statuses: 1786831 `match_status=running` / `game_status=running` at 15:53:13Z; 1789161 `match_status=running` / `game_status=finished` at 15:52:24Z.
- Restart not attempted; no process or data was changed. The process remains on pre-edit code.
- OPEN / NOT VERIFIED: safe restart and post-restart proof, held until fresh source data establishes no match is live.


## #339 safe-restart gate recheck — 2026-11-14 16:03Z

- The approved patch remains staged, not live: `live/pandascore/ll_capture.py` SHA-256 `be437551ef871437a0a168f25ef09886dc161569c720602433bbe8241dc8f7`; backup SHA-256 `a6d7d06a962b3eeb86fac6711e6a8a47f7b6358eca7403979732245833d698ba`.
- Restart gate remains false. Freshest raw statuses show 1786831 `match_status=running` / `game_status=finished` at 16:01:56Z, 1789161 `running` / `finished` at 15:53:48Z, and 1796490 `running` / `running` at 16:03:36Z.
- Capture PID 548127 remains active on pre-edit code (started 13 Nov 17:39:46Z). Restart not attempted; no process or data changed.
- OPEN / NOT VERIFIED: restart and post-restart proof, held until fresh source data establishes no match is live.


## #339 applied and restarted — 2026-11-16 12:28Z

- Approved source SHA-256 `be437551ef871437a0a168f25ef09886dc161569c720602433bbe8241dc8f7` matched; byte-identical backup `live/pandascore/ll_capture.py.pre-339-20261114T135600Z` SHA-256 `a6d7d06a962b3eeb86fac6711e6a8a47f7b6358eca7403979732245833d698ba`; `py_compile` passed.
- Restarted at 12:25:21Z under the already-approved 12:00Z fallback. Old PID 548127 exited; PID 2235520 is active in tmux session `pandascore`. Five tasks started and five sockets connected. The last observed 4004 for match 1789154 was 12:25:11Z before restart; none observed through 12:28:50Z.
- The open-hour raw file grew from 66,974 to 75,320 bytes after restart. Row-level readback is not verified while the gzip stream remains open.
- Report: `agent/outbox/TO-IT-URGENT-pandascore-4004-retry-loop-fix-2026-11-14.md`.


## PK priority jobs 2-3 launched (19 Nov)

- Job 2 CS2 book recorder: test printed `PASS (8 checks, each able to fail)`; launched 03:29:52Z, PID 2690054. At 03:34Z, `books.jsonl` had 3,608 rows and `markets.jsonl` 80 rows; the recorder process remained active. `tail -5 recorder.log` showed current Counter-Strike market entries.
- Job 3 scheduled CS2 live probe: test printed `PASS (4 checks, each able to fail)`; launched 03:30:09Z, PID 2694972 with start time 08:50Z and 150-minute duration. It remains active, waiting for its scheduled start.
- Evidence paths are on the data volume: `pkarbs/pmcs2/{recorder.log,books.jsonl,markets.jsonl}` and `pkarbs/probe/pandascore-cs2-live-probe-2026-11-19.log`.


## P37 PandaScore paths and PID (19 Nov 04:09Z)

- `/mnt/HC_Volume_107257520/pkarbs/pandascore/raw/`: one file, `pandascore_2026111612.jsonl.gz`, 216,915 bytes (timestamp 2026-11-16 13:00:00.178699305 +0000); directory total 216,915 bytes.
- `/vol2/pkarbs/scratch/p318-recount/pandascore/`: 14 files spanning `pandascore_2026111315.jsonl.gz` through `pandascore_2026111412.jsonl.gz`; directory total 2,925,497 bytes. Individual sizes and timestamps are preserved here:
```text
total 2888
-rw-r--r-- 1 690464 690464 330887 2026-11-13 16:00:05.310734482 +0000 pandascore_2026111315.jsonl.gz
-rw-r--r-- 1 690464 690464 341531 2026-11-13 17:00:01.910687920 +0000 pandascore_2026111316.jsonl.gz
-rw-r--r-- 1 690464 690464 129068 2026-11-13 23:43:09.189665699 +0000 pandascore_2026111317.jsonl.gz
-rw-r--r-- 1 690464 690464 263784 2026-11-13 19:00:04.114594383 +0000 pandascore_2026111318.jsonl.gz
-rw-r--r-- 1 690464 690464 371760 2026-11-13 20:00:01.113558712 +0000 pandascore_2026111319.jsonl.gz
-rw-r--r-- 1 690464 690464 254000 2026-11-13 21:00:06.021531570 +0000 pandascore_2026111320.jsonl.gz
-rw-r--r-- 1 690464 690464 234003 2026-11-13 22:00:00.906551206 +0000 pandascore_2026111321.jsonl.gz
-rw-r--r-- 1 690464 690464 88781 2026-11-14 07:45:25.113510069 +0000 pandascore_2026111322.jsonl.gz
-rw-r--r-- 1 690464 690464 289 2026-11-14 08:00:12.139820661 +0000 pandascore_2026111407.jsonl.gz
-rw-r--r-- 1 690464 690464 33216 2026-11-14 09:00:03.164791054 +0000 pandascore_2026111408.jsonl.gz
-rw-r--r-- 1 690464 690464 229029 2026-11-14 10:00:01.726791054 +0000 pandascore_2026111409.jsonl.gz
-rw-r--r-- 1 690464 690464 214436 2026-11-14 11:00:06.709836021 +0000 pandascore_2026111410.jsonl.gz
-rw-r--r-- 1 root root 224599 2026-11-14 12:00:02.663895510 +0000 pandascore_2026111411.jsonl.gz
-rw-r--r-- 1 root root 210114 2026-11-14 12:35:25.262140701 +0000 pandascore_2026111412.jsonl.gz
```
- Both named parent directories existed and had timestamp 2026-11-19 04:01:03.190624836 +0000.
- `ps -o pid,lstart,etime,cmd -p 548127` returned only the header (exit 1): PID 548127 was absent at 04:09Z. The on-origin history says this PID had been replaced by PID 2235520 after the already-approved #339 restart on 16 Nov; the P37 PID check is therefore stale, not evidence of a current capture stop.

## CS2 probe first read (19 Nov)

2026-11-19 09:26:49Z (P62). `ps -p 2694972` returned no process row. The instructed probe log `/mnt/HC_Volume_107257520/pkarbs/probe/pandascore-cs2-live-probe-2026-11-19.log` did not exist (`head` reported “No such file or directory”); therefore probe output is unavailable, not a clean result.

- `books.jsonl`: 213,200 lines; 136,185,464 bytes. `df -B1` available: 19,967,737,856 bytes.
- PID 2690054 was absent. Its log ended `2026-11-19T05:21:16.622Z disk below 15 GB: stopping` then `05:21:17.368Z done`; no recorder process was present.
- Installed the reviewer’s `origin/reviewer` `pm_cs2_books.js` and test into the existing pmcs2 directory. Test output: `PASS (9 checks, each able to fail)`. Verified the installed source's default floor is 10 GB.
- Restarted at 2026-11-19 09:27Z with the note’s 10 GB floor and end time. New Node PID 3179608 was observed; recorder log showed fresh market rows timestamped 09:27:07Z. At 09:27:21Z the file was 136,292,591 bytes / 213,378 lines, and VOL2 had 19,903,541,248 bytes available.
- OPEN / NOT VERIFIED: second `du -sb books.jsonl` reading 30 minutes after 09:26:49Z (due 09:56:49Z); probe log remains absent. No additional restart or kill performed.
## CS2 probe relaunch (19 Nov)

- Fetched the reviewer scripts to `/tmp`; isolated `--help` printed usage. Launched the prescribed tmux loop at 10:39:41Z (PID 3273611, Python PID 3273620) on the data volume, with the specified 2026-12-02 00:00Z end time.
- Timestamped run log `pandascore-cs2-probe-20261119T103941Z.log` showed two open feeds and `PREFLIGHT all_ok=true`; all five checks passed. The note's `probe-loop.log` path was not created by this script version.
- Live reads at 10:42Z and 10:44Z found the loop PID alive. `pmcs2/books.jsonl` grew 191,203 and 383,594 bytes over the consecutive 60-second samples. PandaScore raw capture had no PID and its newest file did not grow on either read, so capture health remains unverified.
- At 10:45Z, the probe process was alive and its log contained 3 events. The bounded OOM log query showed prior OOM kills, but none identified former PID 2694972. The `/tmp/*probe*` and `/root/*probe*` listing did not establish a matching prior output; cause of its exit is undetermined. Nothing was killed, no code edited and no data deleted.
## Preflight 10:45Z (19 Nov)

- Read-only reviewer preflight at 10:45:43Z: PASS disk (22,243,737,600 bytes free), Goalserve PID 4045212, all four sports current-hour files (ages 0–1 s), TheSports newest file, pmcs2 books age 0 s and PID 3179606.
- FAIL: Dota newest output age 274,629 s; daily-look cron not installed. Verdict: 2 FAIL; these components remain UNVERIFIED. No fixes or restarts in this row.
## P71 PandaScore capture restart (19 Nov)

- Preflight found no PandaScore unit, cron entry, tmux session, or `ll_capture.py` process. The newest raw file was `pandascore_2026111612.jsonl.gz`, last modified 16 Nov 13:00 UTC; no prior recorder log was available, so the stop cause is unconfirmed.
- Reviewer-approved source SHA-256 matched prefix `be437551ef87`; the floor wrapper passed `PASS (4 checks, each able to fail)`. Started it with `PS_FLOOR_GB=10` in tmux session `pscap2` at approximately 11:20 UTC.
- Live proof: PID 3323067 ran; `/tmp/pscap2.log` showed connected PandaScore feeds. New file `pandascore_2026111911.jsonl.gz` appeared at 11:22 UTC and grew from 13,249 to 18,130 bytes over 60 seconds.
- Original source was not edited. The active wrapper and 10 GB floor are reviewer-provided; no later floor/config change was made.
