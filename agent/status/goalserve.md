

## P15d2 step 1/3 (2026-11-17 13:36–13:40Z)

- Data-volume free bytes: 41,877,303,296 at 13:36Z; 40,790,061,056 after input copy; both above the 20 GB gate. Code commit: `1cb5c8474b1f64040ec0a8978d866f5b5bc43e2e`.
- Source SHA-256: `feeds/goalserve_odds_vs_pm.py` `a556636fbd0e57a2fa622c9c9eda20a564baab1acf01cffd1e3a9b955c1300c5`; `feeds/test_goalserve_odds_vs_pm.py` `b977ea1bea9edb4aa63b5444da87a1fda08b068e5ff3542f4370fd99cfc97e8e`; `feeds/ps_lead_test.py` `0cbd918ed6e346c91293edbac8f648a30c47a5b3e244fb8af7a08f81804cfc99`.
- `py_compile`: COMPILE_OK. Isolated test: exit 0, `ALL PASS`. First test attempt exhausted `/tmp` (4,096 bytes free); unchanged retry with `TMPDIR` on the data volume passed.
- Inputs collected by prescribed rsync plus `cp -n`: 95 files, first `esports_2026111315.jsonl.gz`, last `esports_2026111713.jsonl.gz`, `du -sh` 550M. `$T/gs` retained at `$T/gs`.
- The four runs were not started; no result JSON/logs exist yet. No script, process or configuration changed. Step 1 complete; P15d3/P15d4 remain queued.


## Disk inventory (18 Nov) — measured 03:58Z

- P18 data-volume gate mount: `/mnt/HC_Volume_107257520` (`/dev/sdc`). At 03:58Z: root 13G free, `/mnt/HC_Volume_107247271` 11G free, `/mnt/HC_Volume_107257520` 27G free. P18 measured the same mount at 10,917,199,872 bytes free at 02:12Z; the current reading is above its 20 GB threshold.
- `du` top-level/depth-2 inventory on that mount (measured 03:58Z): total 67G; `pkarbs` 61G; `pkarbs/thesports` 41G; `pkarbs/scratch` 8.4G; `pkarbs/from-vol` 6.4G; `pkarbs-ps-step2` 3.2G; `pkarbs/tennis` 1.9G; `pkarbs/thesports-cricket` 1.5G; `pkarbs/charts` 648M; `pkarbs/goalserve` 520M. Full measured top-40 is in `/root/p22-disk-inventory-20261118.txt`; it is not copied into the repo because it includes command output with infrastructure paths. The specified `du -sh --max-depth=2` fails on this GNU du (`summarizing conflicts with --max-depth`); equivalent `du -h --max-depth=2` succeeded (exit 0).
- `ship_raw.sh`: no live process found by direct process inspection at 03:58Z (shell self-match excluded). Crontab contains `50:*/30 * * * * SHIP_HOME=/root/ship /root/ship/ship_raw.sh >> /root/ship/ship.log 2>&1  # note 252`. Source folder from `/root/ship/writers.conf`: `/mnt/HC_Volume_107257520/pkarbs/goalserve`; newest three: `goalserve_20261117.jsonl`, `tennis_payloads`, `hockey_nhl_payloads`; oldest three: `hockey_nhl_payloads`, `esports_payloads`, `basketball_payloads`; top-level entry count: 5.
- No files, processes, crontab lines or data were changed by the inventory. No deletion list was produced; do not resume P18 from this read alone without reconciling its stated reopen condition.

## P15d3 step 2/3 (2026-11-17)

- The four runs were already complete by this check. `runs.log` records shift 0 exit 0 at 14:29:43Z, shift 5 exit 0 at 14:35:58Z, shift 15 exit 0 at 14:42:18Z, and shift 25 exit 0 at 14:48:47Z. The runner file was created 14:22:46Z and the shift-0 log began 14:23:18Z; the process PID and exact process start UTC were not retained, and no matching process remained at inspection. No PID is inferred.
- Four valid result JSONs are present, each >1 KB and each with 214 `match_list` rows: shift0 113,234 bytes; shift5 112,693; shift15 112,698; shift25 112,804. Results remain UNCHECKED pending the independent audit. A scan found no IP-like values, hostnames, or credential-like fields.
- Data volume free: 33,892,593,664 bytes at 15:03Z. The retained input set is 95 files, `esports_2026111315.jsonl.gz` through `esports_2026111713.jsonl.gz`, 550 MB; scratch directory 551 MB. Inputs and outputs remain in the Goalserve scratch directory on the data volume for the next step.
- Code commit: `1cb5c8474b1f64040ec0a8978d866f5b5bc43e2e`. SHA-256 matches: `feeds/goalserve_odds_vs_pm.py` `a556636fbd0e57a2fa622c9c9eda20a564baab1acf01cffd1e3a9b955c1300c5`; `feeds/test_goalserve_odds_vs_pm.py` `b977ea1bea9edb4aa63b5444da87a1fda08b068e5ff3542f4370fd99cfc97e8e`; `feeds/ps_lead_test.py` `0cbd918ed6e346c91293edbac8f648a30c47a5b3e244fb8af7a08f81804cfc99`. `py_compile` passed and the isolated test ended `ALL PASS` at 15:03Z.
- At the time of the P15d3 report, no script, process, or configuration changed and the four JSONs had not yet been copied into `agent/status/`; the copy was completed in P15d4 below.


## P15d4 step 3/3 (2026-11-17 16:16Z)

- P15d4 outputs copied from the retained scratch run into `agent/status/`: shift0 113,234 bytes; shift5 112,693; shift15 112,698; shift25 112,804. Each contains 214 `match_list` rows and is greater than 1 KB. SHA-256: shift0 `05034c393a8278f4dff3f14d20015b2702f961ef0d113a41eea92bc87369a4bb`; shift5 `16b049f8212f605225d02f83d7043f21035f14cd58c12aa692fb7acf0eb3417c`; shift15 `a6cca6b2239927ede55f6e36157ef9bbff844ee00700ab65168a892a4a28e9f9`; shift25 `7ae134ee87ceec15103be7d5f53bb49c7b79fa039aaad658d02d34dd590da1d8`.
- Run exits/times from the already-recorded P15d3 evidence: shift0 exit 0 at 14:29:43Z; shift5 exit 0 at 14:35:58Z; shift15 exit 0 at 14:42:18Z; shift25 exit 0 at 14:48:47Z. Results remain UNCHECKED pending the independent audit; no interpretation added.
- Privacy scan of all four result files: clear. Scratch inputs and outputs remain on the data volume for the audit. No code, process, or configuration changed.

## Disk inventory (18 Nov)

Capture time: 2026-11-18 04:35Z. P18 measured the data-volume mount at 10,917,199,872 bytes free at 02:12Z; the same mount is `/mnt/HC_Volume_107257520` and now reports 28G free (above P18's 20 GB gate). This inventory does not authorize deletion or by itself reopen P18; no deletion list was produced.

`df -B1 -h / /mnt/HC_Volume_107247271 /mnt/HC_Volume_107257520`:
```text
Filesystem      Size  Used Avail Use% Mounted on
/dev/sda1        38G   23G   13G  65% /
/dev/sdb         49G   37G   11G  79% /mnt/HC_Volume_107247271
/dev/sdc         98G   69G   28G  74% /mnt/HC_Volume_107257520
```

Data-volume depth-2 usage (`du -sh --max-depth=2` failed: `du: summarizing conflicts with --max-depth=2`; GNU du rejects `-s` with `--max-depth`. Equivalent `du -h --max-depth=2`, sorted descending, top 40):
```text
66G	/mnt/HC_Volume_107257520
60G	/mnt/HC_Volume_107257520/pkarbs
40G	/mnt/HC_Volume_107257520/pkarbs/thesports
8.4G	/mnt/HC_Volume_107257520/pkarbs/scratch
6.4G	/mnt/HC_Volume_107257520/pkarbs/from-vol
3.2G	/mnt/HC_Volume_107257520/pkarbs-ps-step2
2.8G	/mnt/HC_Volume_107257520/pkarbs-ps-step2/rn1
1.9G	/mnt/HC_Volume_107257520/pkarbs/tennis
1.5G	/mnt/HC_Volume_107257520/pkarbs/thesports-cricket
650M	/mnt/HC_Volume_107257520/pkarbs/charts
432M	/mnt/HC_Volume_107257520/pkarbs/dotacap
327M	/mnt/HC_Volume_107257520/pkarbs/goalserve
275M	/mnt/HC_Volume_107257520/pkarbs-ps-step2/winmodels
140M	/mnt/HC_Volume_107257520/pmhl5s
115M	/mnt/HC_Volume_107257520/pkarbs-ps-step2/live
94M	/mnt/HC_Volume_107257520/weekend-perps
88M	/mnt/HC_Volume_107257520/pkarbs/lol
64M	/mnt/HC_Volume_107257520/.p4-20261116T2246Z
46M	/mnt/HC_Volume_107257520/pkarbs/goalserve-audit-20261117
18M	/mnt/HC_Volume_107257520/pkarbs/oddspapi
17M	/mnt/HC_Volume_107257520/oddspapi
16M	/mnt/HC_Volume_107257520/oddspapi/hist
13M	/mnt/HC_Volume_107257520/nt_live_fire
9.3M	/mnt/HC_Volume_107257520/nvda-huang
9.2M	/mnt/HC_Volume_107257520/nvda-huang/raw
8.8M	/mnt/HC_Volume_107257520/pkarbs/cricket
7.0M	/mnt/HC_Volume_107257520/pkarbs-ps-step2/rugby
5.6M	/mnt/HC_Volume_107257520/pkarbs-ps-step2/reports
3.9M	/mnt/HC_Volume_107257520/pkarbs-ps-step2/agent
3.5M	/mnt/HC_Volume_107257520/pkarbs-ps-step2/weekend-perps
3.4M	/mnt/HC_Volume_107257520/pkarbs-ps-step2/mentions
2.9M	/mnt/HC_Volume_107257520/pkarbs-ps-step2/chess
1.7M	/mnt/HC_Volume_107257520/pkarbs-ps-step2/forecast-edges
1.3M	/mnt/HC_Volume_107257520/pkarbs-ps-step2/reviews
688K	/mnt/HC_Volume_107257520/nt_live_fire/.t40a-stage-224410
664K	/mnt/HC_Volume_107257520/nt_live_fire/live
632K	/mnt/HC_Volume_107257520/pkarbs-ps-step2/shadow
604K	/mnt/HC_Volume_107257520/pkarbs-ps-step2/agent
456K	/mnt/HC_Volume_107257520/pkarbs/mentions
```

`ship_raw` check: no live `ship_raw.sh` process found (the first `pgrep -af` invocation also matched its own checker command; that self-match was excluded). Crontab has:
```text
50:*/30 * * * * SHIP_HOME=/root/ship /root/ship/ship_raw.sh >> /root/ship/ship.log 2>&1  # note 252
```

`/root/ship/writers.conf` identifies the `goalserve` source folder as `/mnt/HC_Volume_107257520/pkarbs/goalserve`. Listing results:
```text
$ ls -1t <folder> | head -3
goalserve_20261117.jsonl
tennis_payloads
hockey_nhl_payloads
$ ls -1t <folder> | tail -3
hockey_nhl_payloads
esports_payloads
basketball_payloads
$ ls -1 <folder> | wc -l
5
```

Largest measured consumers are `pkarbs/thesports` (40G) and `pkarbs/scratch` (8.4G). No files or processes were changed and nothing was deleted. Reviewer deletion list is still required before P18 is reopened.


## P49 Goalserve live probe v2 relaunch (19 Nov)

- Stopped the prior 90-minute probe PID 2689593 (cmdline matched the exact probe and output path named by the reviewer).
- Refetched reviewer branch; offline test printed `ALL PASS` (22 checks). Relaunched v2 at 04:15:59Z, PID 2766271, duration 120 minutes, output `/mnt/HC_Volume_107257520/pkarbs/probe/goalserve-live-probe-v2-2026-11-19.json`; live log `/mnt/HC_Volume_107257520/pkarbs/probe/goalserve-live-probe-v2-2026-11-19.log`.
- First observed preflight (04:18Z): hockey_nhl passed all checks, 4/4 games matched and books present; accepted market `Home/Away`. Tennis had 15/20 matches but failed polling health: 35 HTTP 429 errors across 51 polls. Esports had no live games or accepted markets at that instant and 38 HTTP 429 errors across 48 polls. `NO NUMBER` was emitted for esports and tennis. Probe remained alive at 04:30Z; 120-minute run not complete.

## P50 esports look 1 diagnostic rerun (19 Nov)

- Re-fetched `feeds/run_daily_look.sh` from `origin/claude/project-thread-vg2ckg`; signed self-test printed `ALL PASS`. Exact full run exit: 1 at 04:26:57Z.
- It found zero local esports payload files for 2026-11-18; the named esports payload directory contained no matching files. No 2026-11-18 files were listed in the output. Other payload directories (basketball, esports, hockey_nhl, tennis) existed, timestamped around 04:00Z.
- The script copied zero rows into the run input (`gs` remained 4.0K) and the analyzer exited 1; no result JSON/hash or verdict was produced. Its stdout then showed a `FileNotFoundError` while the wrapper tried to read the absent result JSON. The separate 03:34Z attempt had stopped at the signed-file gate; this 04:26Z run passed the signed checks, so the current blocker is missing esports capture files for the requested day.


## P51 capture health and esports files (19 Nov)

```text
probe_stopped
goalserve_20261117.jsonl ok 449078 err 6106
2026-11-19T03:59:57Z 158277 esports_2026111903.jsonl.gz
2026-11-19T04:59:58Z 100237 esports_2026111904.jsonl.gz
2026-11-19T05:05:28Z 10563 esports_2026111905.jsonl.gz
3
<VOL2>/pkarbs/goalserve-audit-20261117/esports_2026111705.jsonl.gz
Filesystem      Size  Used Avail Use% Mount
VOL2             98G   78G   16G  84% <VOL2>
REPO             49G   38G  9.3G  81% <REPO>
```

- Correction to the pasted command's glob: only `goalserve_20261117.jsonl` exists; no 18 or 19 files matched, so the requested last-two-log comparison was unavailable. The sole file had 449,078 ok and 6,106 err rows; recent err rows included HTTP 429 in minute buckets 04:56–05:05 UTC. This file is dated 17 Nov, so it cannot establish whether the probe increased errors during 19 Nov.
- `esports_payloads` contained 3 files, all dated 19 Nov; the bounded volume search found only an audit file for 17 Nov and no 18 Nov payload. Capture PID 4045212 remained running (started 17 Nov 09:00:06Z).
- Probe PID 2766271 was stopped as directed; no other process was stopped.


## P51 capture health and esports files (19 Nov)

```text
probe_stopped
goalserve_20261117.jsonl ok 449078 err 6106
2026-11-19T03:59:57Z 158277 esports_2026111903.jsonl.gz
2026-11-19T04:59:58Z 100237 esports_2026111904.jsonl.gz
2026-11-19T05:05:28Z 10563 esports_2026111905.jsonl.gz
3
<VOL2>/pkarbs/goalserve-audit-20261117/esports_2026111705.jsonl.gz
Filesystem      Size  Used Avail Use% Mount
VOL2             98G   78G   16G  84% <VOL2>
REPO             49G   38G  9.3G  81% <REPO>
```

- Correction to the pasted command's glob: only `goalserve_20261117.jsonl` exists; no 18 or 19 files matched, so the requested last-two-log comparison was unavailable. The sole file had 449,078 ok and 6,106 err rows; recent err rows included HTTP 429 in minute buckets 04:56–05:05 UTC. This file is dated 17 Nov, so it cannot establish whether the probe increased errors during 19 Nov.
- `esports_payloads` contained 3 files, all dated 19 Nov; the bounded volume search found only an audit file for 17 Nov and no 18 Nov payload. Capture PID 4045212 remained running (started 17 Nov 09:00:06Z).
- Probe PID 2766271 was stopped as directed; no other process was stopped.

## P72 hold (19 Nov)

Decision recorded per reviewer notes P72 and P72b. No files were shipped or deleted and no writer was stopped.

- **36 h hold, then eligible to ship only after checksum verification:** `/mnt/HC_Volume_107257520/pkarbs/goalserve/esports_payloads`, `tennis_payloads`, `hockey_nhl_payloads`, `basketball_payloads`; and `/mnt/HC_Volume_107257520/pkarbs/thesports/final-topics-32295b/markets.jsonl` and `books.jsonl` only. These are retained for the daily look's previous-full-day inputs.
- **Protected, not included in any ship rule:** `/mnt/HC_Volume_107257520/pkarbs/pmdota` (Dota capture), `pmcs2` (CS2 books), `probe` and `pandascore/raw` (PandaScore probe/capture), `scratch/goalserve-daily-logs` (not present in this inventory), and every `result-*.json` (none found in the listed active capture directories).
- **Gas/listing-book recorders protected:** `/mnt/HC_Volume_107257520/gas_watch`, `/mnt/HC_Volume_107257520/gas_books_pmxt`, `/mnt/HC_Volume_107257520/pkarbs/ocbooks`, `/mnt/HC_Volume_107257520/pkarbs/netflix`, `/mnt/HC_Volume_107257520/pkarbs/mentions`, and `/mnt/HC_Volume_107257520/pkarbs/oddspapi`. The other top-level inventory is recorded in this P0 status section; any path not explicitly classified here stays protected.
- **Capacity gate fails:** two `du -sb` reads of `final-topics-32295b` were 50,831,223,158 bytes at 11:57:12Z and 52,152,370,706 bytes at 12:09:09Z. Measured growth is about 6.59 GB/hour; 36 h projects to 237.36 GB. VOL2 free space was 21,110,800,384 bytes at 11:57:12Z, 19,737,276,416 bytes at 12:09:09Z, and 23,455,006,720 bytes at 12:11:11Z; the last read is 13.46 GB above the 10 GB floor. `du` totals are non-monotone as capture files roll over, but even the last headroom is far below measured 6.6–6.8 GB/hour growth for 36 hours. Therefore 36 h does not fit. Per P72, no shipping or deletion is authorized until PK arbs provides a filter.
- Shipper cron: **not installed**; no shipment run.

## P68 thesports folder (19 Nov)

Read-only identification at 14:04Z. No files shipped/deleted and no process stopped.

```text
Largest entries under /mnt/HC_Volume_107257520/pkarbs/thesports (8 requested):
49G /mnt/HC_Volume_107257520/pkarbs/thesports/final-topics-32295b
Only one immediate entry was present.

Last six lines of final-topics-32295b:
-rw-r--r-- 1 root root 74267986 2026-11-19 14:04:28.109232146 +0000 pmws.jsonl
drwxr-xr-x 2 root root 4096 2026-11-19 13:32:43.236690855 +0000 share
-rw-r--r-- 1 root root 1022747801 2026-11-19 14:04:20.994215794 +0000 trades.jsonl
-rw-r--r-- 1 root root 211024 2026-11-19 14:04:21.569217116 +0000 trades.watermark.json
-rw-r--r-- 1 root root 17088904344 2026-11-19 10:11:12.992746190 +0000 ts_mqtt.jsonl
-rw-r--r-- 1 root root 57645071 2026-11-19 10:11:14.239742426 +0000 ts_poll.jsonl

Processes (command lines truncated to 160 chars):
root 3243759 2.8 0.4 53016 38956 ? Ss 10:11 6:32 /usr/bin/python3 -I /root/pkarbs/live/thesports/pm_trades_capture.py /mnt/HC_Volume_107257520/pkarbs/thesports/final-topics-32295b --interval 30
root 3243761 84.4 2.2 570484 179932 ? Ssl 10:11 196:59 /usr/bin/python3 -I /root/pkarbs/live/thesports/capture.py /mnt/HC_Volume_107257520/pkarbs/thesports/final-topics-32295b 160 --share /mnt/HC_Volume_107257520/pkarbs/thesports/final-topics-32295b/share
root 3543459 0.0 0.0 2888 1816 ? Ss 14:00 0:00 /bin/sh -c bash /root/pkarbs/live/thesports/export_timer_2h.sh >> /var/log/thesports_export_timer.log 2>&1
root 3543479 0.0 0.0 7668 2312 ? S 14:00 0:00 bash /root/pkarbs/live/thesports/export_timer_2h.sh
root 3559437 56.8 45.3 3632652 3599044 ? R 14:02 1:05 /usr/bin/python3 /root/pkarbs/live/thesports/export_slim_32295_plumb.py /mnt/HC_Volume_107257
```

`thesports-capture-b.service` (PID 3243761) and `thesports-pmtrades.service` (PID 3243759) were active at 14:04Z. The capture process writes both Polymarket books/markets and TheSports feed files; the separate trades process also writes into this directory. A 14:05Z stat confirmed books and trades continued growing. No process was stopped.

## P74 final-topics profile (19 Nov)

At 14:04:43Z the supplied `it/pm_folder_stats.py` reported 16 files totaling 52,426,205,554 bytes. Largest files included `books.jsonl` 24,996,748,464 bytes, `ts_mqtt.jsonl` 17,088,904,344 bytes, `share/books.jsonl.gz` 3,946,494,727 bytes, `share/books.jsonl.gz.tmp` 3,331,064,388 bytes, and `share/ts_mqtt.jsonl.gz` 1,762,550,643 bytes. `markets.jsonl` had 6,766 rows: tennis 4,607; CS2 1,268; Dota2 598; cricket 132; NBA 89; NFL 27; LoL 45.

The supplied script exited 1 after printing its book profile: `AttributeError: 'int' object has no attribute 'keys'` while processing a non-object JSON value. Its printed 20 MB-tail result was 21,395 rows with keys `ms,sent,tk,ts,bids,asks`; mapped byte shares tennis 57.7%, CS2 25.1%, Dota2 13.5%, cricket 3.6%. A separate bounded 20 MB tail read completed: 22,298 rows, one malformed/truncated JSON line, zero non-object values; mapped byte shares tennis 57.4%, CS2 25.1%, Dota2 13.8%, cricket 3.7%.

The required stopgap eligibility scan found zero regular non-look files older than six hours at 14:06Z. No files were transferred or deleted. A follow-up `du -sb` measured 52,675,757,561 bytes at 14:06:57Z; the directory is being concurrently written/exported. The `pkarbs-capture` archive destination exists. No change was made to `markets.jsonl` or `books.jsonl`.
P74 stopgap current state (14:16Z): no eligible non-look files older than 6 h; none shipped/deleted. Both writer units remain active; VOL2 free 21,005,606,912 B. The folder is actively written and the profile script had one malformed/non-object JSON handling failure; P74 partial report is in agent/outbox/P74-final-topics.md.


## P75 free ts_mqtt (19 Nov)

Correction (19 Nov 16:45Z): P77 did NOT free local space. At 16:38:31Z and 16:39:31Z both local feed files were already 0 bytes (mtime 14:59:45Z); PID 3243761 held `ts_poll.jsonl` open at fd 7, position 57,645,071. Before my copy, the storage-box destination held the expected nonempty copies: MQTT 17,088,904,344 bytes and poll 57,645,071 bytes. The 16:39:36Z rsync copied the already-empty local files over those nonempty remote files. A subsequent remote listing and checksum run confirmed both remote files are now 0 bytes. This was a destructive overwrite and lost the only verified archive copy found in the checked locations. The exact prior payloads are not available in the local files, the searched project-volume paths, or the checked storage-box capture tree; recovery is unverified. No local truncation ran. Do not repeat the copy or write to these paths pending IT/reviewer direction. PID 3243761 remains running; books continue growing.

## P75 book growth (19 Nov)

P77b completed its 60-minute read-only sample (16:41:43Z–17:41:43Z; output `/mnt/HC_Volume_107257520/pkarbs/p77b-growth.txt`). Readings, in bytes:

| UTC | books.jsonl | trades.jsonl | pmws.jsonl | VOL2 free |
|---|---:|---:|---:|---:|
| 16:41:43Z | 25,838,865,518 | 1,041,318,278 | 75,013,176 | 32,830,865,408 |
| 17:11:43Z | 25,987,108,705 | 1,044,819,232 | 75,182,614 | 34,538,663,936 |
| 17:41:43Z | 26,130,581,965 | 1,048,216,328 | 75,340,190 | 35,370,549,248 |

60-minute deltas: books +291,716,447 B; trades +6,898,050 B; pmws +327,014 B; VOL2 free +2,539,683,840 B. The source output ended with `done`. Read-only; no files or processes changed by this measurement.

## Perp open-contract recorder (19 Nov)

P76 read-only check at 16:41Z: recorder PID 2701410 was running (`python3 book_recorder.py --out /mnt/HC_Volume_107257520/pkarbs/ocbooks --interval 10`). `ocbooks_20261119.jsonl.gz` was 3,062,666 bytes and contained 18,578 rows; zero rows contained `"err"`; the first record timestamp converts to 2026-11-19 03:30:28Z and the last to 2026-11-19 16:41:59Z. The command `grep -c '"t": 17'` returned 18,578 because the epoch values begin with 17; it does not establish that the 14:30Z open was captured. The checked first-to-last timestamps span 03:30:28Z–16:41:59Z. No restart or file edit.

## P77r box snapshot check (19 Nov)

The required read-only command `rsync --list-only "${BOX}.zfs/snapshot/"` failed with exit 23: the requested snapshot directory was unavailable (`No such file or directory`, rsync sender error 2). Per the instruction, stopped here; did not list a dated snapshot or access, copy, restore, write, or delete anything under the snapshot paths.


## P67 store gap (19 Nov)

Command from reviewer note it/REPLY-2026-11-19-0935Z-P67-store-gap-check-and-daily-look-row.md; run at 2026-11-19 18:58Z UTC. All 12 required sport-hour rows returned exit 0. Output:

```text
esports 2026111907 rows 1011 first 07:17:29 last 07:52:33
esports 2026111908 rows 616 first 08:15:01 last 08:42:39
esports 2026111909 rows 1400 first 09:12:07 last 09:59:58
tennis 2026111907 rows 1030 first 07:17:30 last 07:52:35
tennis 2026111908 rows 620 first 08:15:03 last 08:42:43
tennis 2026111909 rows 1414 first 09:12:06 last 09:59:59
hockey_nhl 2026111907 rows 1017 first 07:17:29 last 07:52:31
hockey_nhl 2026111908 rows 614 first 08:15:01 last 08:42:39
hockey_nhl 2026111909 rows 1392 first 09:12:07 last 09:59:58
basketball 2026111907 rows 1048 first 07:17:29 last 07:52:33
basketball 2026111908 rows 621 first 08:15:03 last 08:42:45
basketball 2026111909 rows 1427 first 09:12:07 last 09:59:58
```
