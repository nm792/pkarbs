

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
- **Gas/listing-book recorders protected:** `/mnt/HC_Volume_107257520/gas_watch`, `/mnt/HC_Volume_107257520/gas_books_pmxt`, `/mnt/HC_Volume_107257520/pkarbs/ocbooks`, `/mnt/HC_Volume_107257520/pkarbs/netflix`, `/mnt/HC_Volume_107257520/pkarbs/mentions`, and `/mnt/HC_Volume_107257520/pkarbs/oddspapi`, and `/mnt/HC_Volume_107257520/pkarbs/pmsport` (P86 NHL recorder). The other top-level inventory is recorded in this P0 status section; any path not explicitly classified here stays protected.
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

## P68 daily look cron (19 Nov)

- Installed the reviewer wrapper at `/root/ship/daily_look_cron.sh` from `origin/reviewer:it/daily_look_cron.sh`; `bash -n` printed `ok`.
- Preserved the existing Prime crontab and added `30 7 * * * ENVFILE=/root/ship/ship.env bash /root/ship/daily_look_cron.sh`; readback matches exactly. `ship.env` is the env file used by `ship_raw.sh`; only variable names were checked, and no values were printed.
- Manual run started at 21:24:07Z. Esports passed signed checks and the analysis started for 24 hour files; at 21:27Z its analyzer was still active (PID 4096160, 137 MB staged input). The wrapper had not finished esports, so tennis and the required `LATEST-esports.tail` are not yet verified. No process was stopped.


- Status: partial — cron installed; manual analysis has a live 7,200 s timeout and is still running. Tennis and completion tail are not verified; no process was stopped.

## P79 copy-back 19 Nov (19 Nov)

Step 0 local listing at 23:46Z: esports has 2026111906-23; tennis has 2026111906-23; hockey_nhl has 2026111906-23; basketball has 2026111906-23. Hours 00-05 were missing in all four folders. VOL2 before copy: 25 GB free.

Copied only the 24 missing hour files (00-05 for esports, tennis, hockey_nhl and basketball) from the existing box archive with rsync --ignore-existing; no local file was overwritten and hours 06+ were untouched. Verified all 24 local files exist and are nonempty; per-file rsync --checksum dry-run returned no differences. VOL2 after copy: 24 GB free. Hour 06 was already present in each folder, so it was not copied.


## Preflight cron (20 Nov)

- Installed `/root/ship/preflight_cron.sh` from the reviewer branch; `bash -n` passed.
- Installed and read back the Prime crontab line: `20 * * * * bash /root/ship/preflight_cron.sh`.
- Manual run at 00:21:04Z exited 0. `PREFLIGHT-LATEST.txt` reports `VERDICT ALL PASS (live read at 00:21Z)`: disk free 19,271,364,608 bytes; Goalserve capture alive; newest esports, tennis, hockey_nhl, basketball, Polymarket books, and PMCS2 books are current; PMCS2 recorder alive; daily-look cron installed.
- Evidence: `/mnt/HC_Volume_107257520/pkarbs/scratch/goalserve-daily-logs/PREFLIGHT-LATEST.txt`.

## P84 Goalserve interim table (20 Nov)

P84a scope completed: steps 1, 2, 3 and 6. Status commit: 7b80fa22298f89b0247854bec51259883ee88235.

- Step 1: PASS. Reviewer-script checks ended `ALL PASS` (reversed outcome order, sign, and no-PM-market cases). SHA256 `goalserve_descriptive_by_sport.py`: 8a494f8c833917d53c1cad0c9d7bc489d43d2a9c623bcdd378206a4bf4f61c80; `test_goalserve_descriptive_by_sport.py`: b8c4f4efd1d715ad3e97d3bb5c619b8d43c0e987cb6a4a2aa969460cd9fdd889.
- Step 2: The note's exact `goalserve_20261119.jsonl` path does not exist. The only matching poll log is `goalserve_20261117.jsonl`; its last row has keys `t, tennis, soccer, baseball, hockey_nhl, esports, basketball`. At 02:45Z payload-hour counts were esports 51 (18 Nov 00 through 20 Nov 02), tennis 27 (19 Nov 00 through 20 Nov 02), hockey_nhl 27 (19 Nov 00 through 20 Nov 02), basketball 27 (19 Nov 00 through 20 Nov 02). The 20 Nov 02:20Z preflight independently reported current 20 Nov 02 files for all four.
- Step 3: The recorder market inventory contains tennis, NBA, and no hockey or basketball markets. Leading categories: tennis moneyline 4,700; CS2 child moneyline 772; CS2 moneyline 544; Dota2 child moneyline 410; Dota2 moneyline 202; cricket moneyline 138; NBA moneyline 93; NFL moneyline 28; LoL child moneyline 36; LoL moneyline 9. Steps 4–5 were outside P84a scope and were not required.
- Step 6: Existing look-1 cells: `cs2|Map 1 Winner` (6 matches, 240 events; informational, no boundary); `cs2|Map 2 Winner` (6, 239; informational, no boundary); `cs2|Match Winner` (6, 215; unknown, below 12-match/60-event minimum); `unparsed|Map 3 Winner` (1, 13; informational, no boundary); `unparsed|Map 4 Winner` (1, 6; informational, no boundary).
- Scope deviation: I mistakenly launched the separate P84b esports/tennis scans. They had not completed when VOL2 fell from 17,654,091,776 bytes free at 02:43Z to 14,852,890,624 bytes at 02:47Z. Both were stopped at 02:48Z; no new result was produced and no files were deleted. Existing scan JSON files predate these attempted runs. The 17 GB gate now fails; no further scan was run.

Status: P84a complete. P84b scan outputs remain outstanding, not part of this P84a row.


## P88x Goalserve match samples (20 Nov 2026)

Reviewer exporter tests: ALL PASS. Exported winner-market-only change samples from available raw hours: tennis 25 input files, 3 matches; CS2 48 files, 3 matches; Dota 2 48 files, 3 matches; hockey 24 files, 3 matches. Indices and compressed samples are under `it/samples-2026-11-20/` on origin/reviewer. Output total: 1,010,840 bytes. All 12 serialized files passed an IP-like dotted-quad scan (0 findings). VOL2 free after generation: 12,291,629,056 bytes. The first Dota invocation hit the 600-second command timeout while continuing in the background; verified the exporter process exited and its output/index completed before proceeding.

## Perps loggers persistence (20 Nov)

Read-only checks at 2026-11-20 07:13Z (UTC):

1. `pm-hl-5s-logger`: active; enabled state `transient`; PID 3618574 running `pm_hl_5s_logger.py` with 5-second interval. The transient unit is not enabled across reboot. Latest listing included `pmhl5s_20261120.jsonl.gz` (42,254,850 bytes at 07:13Z).
2. `pmhl5s_20261120.jsonl.gz`: 4,040 rows; final row timestamp 1795158786.7130497 (07:13Z).
3. Hyperliquid weekend-perps logger: PID 2907769 running `hl_weekend_logger.py` with 60-second interval; `hl_20261120.jsonl.gz` was 7,189,057 bytes at 07:13Z.
4. Open-contract book recorder: PID 2701410 running `book_recorder.py` with 10-second interval; `ocbooks_20261120.jsonl.gz` was 1,504,155 bytes and contained 10,400 rows. One row contains an error: temporary DNS resolution failure.

Read-only; no process or file was changed.

## P86 NHL recorder (20 Nov)

- Reviewer tests: `node test_pm_sport_books.js` passed all 7 checks on Node 22.23.1.
- Started the NHL-only recorder at 14:13:56Z; process PID 1081549 ran from `pkarbs/pmsport`. The WebSocket opened. Its initial log says `tokens 0`; the subsequent market discovery found 12 NHL markets and dynamically subscribed to their tokens. This differs from the note's initial-open `tokens > 0` wording, so that exact log criterion was not met.
- Despite that initial count, book data was received: `books.jsonl.gz` passed `gzip -t`, had 110 rows at 14:16Z, and grew from 5,454 bytes at 14:15:26Z to 9,301 bytes at 14:16:26Z. No repeating `ws error` was observed. `markets.jsonl` has 12 entries.
- Protection check: `pkarbs/pmsport` is not a `writers.conf` source; `ship_raw.sh` processes only configured source directories, so this folder is not eligible for shipping or deletion. The project status protection list now includes it. No shipper or live data was changed.
- The scheduled 21 Nov 17:30Z pre-window read is not yet due.


## P90a pair_score (20 Nov 15:16Z)

Reviewer scorer `pair_score.py` passed `py_compile`. On pmcs2: delay 0, 53 markets, 1,201,634 observations, minimum askA+askB 0.93, 22 detections, 18 runs, net $46.67, 2,278.5 shares. At 1,000 ms delay: 53 markets, 1,203,044 observations, 22 detections, 18 runs, net $0, 0 shares. Immediate-detection top rows included SEGA.dll vs ABT Esports and ex-INOX Division vs WBT. These are scorer outputs, not independently audited trades.

The same scorer failed on pmdota with `KeyError: 'asset'` at `pair_score.py:24`; the available Dota rows do not match its expected schema. No workaround or data edit was made.

## P87 coverage matrix (20 Nov)

Read-only run used the reviewer runner from the reviewer branch (note/code context `708a410`). The supplied self-test ended `ALL PASS` (4 checks). The scan read 10 recent Goalserve hour files per sport and sampled every 20th row; counts are lower bounds.

| Feed | Goalserve matches | Final-folder unique PM market | Of those tokens with book rows | PMCS2 unique market | PMCS2 book rows | PmDota unique market |
|---|---:|---:|---:|---:|---:|---:|
| Esports | 4 | 3 (75.0%) | 6/6 | 2 (50.0%) | no books file | 0 |
| Tennis | 164 | 70 (42.68%) | 128/140 | 0 | no books file | 0 |
| Hockey NHL | 44 | 0 (0%) | 0 | 0 | no books file | 0 |

Evidence: `<VOL2>/pkarbs/scratch/goalserve-desc/coverage.json`; SHA256 `c69926e805941b1f9dae3e9845c7c0ecd4f8d5c193ae737ae0c500bef68dbb98`. The scan covered esports, tennis, and hockey NHL only; basketball was excluded as required. P87b restart was not part of this read-only row.


## P84b (20 Nov)

Read-only descriptive scans completed sequentially from the reviewer script. No code, recorder, service, or source data was changed. The reviewer replaced the earlier 17 GB gate for this bounded scan with a 10 GB VOL2 stop floor.

No-scan disk readings 60 seconds apart:
```
Filesystem        1B-blocks        Used   Available Use% Mounted on
/dev/sdc       105089261568 88947171328 10756603904  90% <VOL2>
/dev/sdc       105089261568 88958603264 10745171968  90% <VOL2>
```

Esports scan exited 0. JSON SHA256: `6fc2aa6a76fe0fc59033c371d0724c279f37a2219e76eaef5c2b17802efa0d60`.
Tennis scan exited 0. JSON SHA256: `4e7e0cfc53024da4ac5fcf022d685d7338b549b982d278f00a230ce8c1970b3d`.

The required `tail -14` output for each log follows. These are exploratory/interim descriptive results, not the signed v2 test, a verdict, or a pass.

### desc-esports.log
- EXPLORATORY/INTERIM descriptive table; NOT the signed v2 test, no verdict, no pass; UNCHECKED until an independent checker signs
- sport "esports"
- files 48
- goalserve_events_total 5590
- match_markets_seen 69
- unmatched_markets 35
- ambiguous_markets 6
- drops {"pm_book_rows_time_from_ms": 266440, "book_rows_one_sided": 16176, "events_no_pm_market_or_ambiguous": 3134}
- CELL cs2|Map 1 Winner {"goalserve_events_total": 1396, "events_usable": 619, "matches_usable": 11, "mean_pm_before_c": 2.054, "mean_pm_after_c": 0.593, "mean_net_c": -1.462, "mean_net_per_match_c": -1.639, "placebo_mean_net_c": -0.023, "share_net_gt_placebo_pct": 42.003, "median_best_ask": 0.55, "median_ask_shares_at_best": 75.4, "median_ask_shares_within_2c": 685.16, "median_ask_usd_within_2c": 344.938, "share_events_ask_shares_within_2c_ge_100_pct": 90.145}
- CELL cs2|Map 2 Winner {"goalserve_events_total": 1270, "events_usable": 652, "matches_usable": 11, "mean_pm_before_c": 2.342, "mean_pm_after_c": 1.411, "mean_net_c": -0.931, "mean_net_per_match_c": -1.319, "placebo_mean_net_c": -0.059, "share_net_gt_placebo_pct": 44.632, "median_best_ask": 0.54, "median_ask_shares_at_best": 65.9, "median_ask_shares_within_2c": 562.09, "median_ask_usd_within_2c": 302.806, "share_events_ask_shares_within_2c_ge_100_pct": 92.331}
- CELL cs2|Match Winner {"goalserve_events_total": 2449, "events_usable": 1047, "matches_usable": 11, "mean_pm_before_c": 1.5, "mean_pm_after_c": 0.717, "mean_net_c": -0.784, "mean_net_per_match_c": -0.824, "placebo_mean_net_c": 0.091, "share_net_gt_placebo_pct": 42.311, "median_best_ask": 0.52, "median_ask_shares_at_best": 137.46, "median_ask_shares_within_2c": 1218.78, "median_ask_usd_within_2c": 598.249, "share_events_ask_shares_within_2c_ge_100_pct": 96.466}
- CELL unparsed|Map 1 Winner {"goalserve_events_total": 71, "events_usable": 36, "matches_usable": 1, "mean_pm_before_c": 2.004, "mean_pm_after_c": 0.926, "mean_net_c": -1.078, "mean_net_per_match_c": -1.078, "placebo_mean_net_c": 0.007, "share_net_gt_placebo_pct": 44.444, "median_best_ask": 0.545, "median_ask_shares_at_best": 35.0, "median_ask_shares_within_2c": 724.32, "median_ask_usd_within_2c": 310.339, "share_events_ask_shares_within_2c_ge_100_pct": 100.0}
- CELL unparsed|Map 2 Winner {"goalserve_events_total": 85, "events_usable": 75, "matches_usable": 1, "mean_pm_before_c": 2.233, "mean_pm_after_c": 0.147, "mean_net_c": -2.087, "mean_net_per_match_c": -2.087, "placebo_mean_net_c": -0.229, "share_net_gt_placebo_pct": 41.333, "median_best_ask": 0.51, "median_ask_shares_at_best": 59.0, "median_ask_shares_within_2c": 968.0, "median_ask_usd_within_2c": 408.598, "share_events_ask_shares_within_2c_ge_100_pct": 94.667}
- CELL unparsed|Map 3 Winner {"goalserve_events_total": 13, "events_usable": 13, "matches_usable": 1, "mean_pm_before_c": 1.923, "mean_pm_after_c": 0.615, "mean_net_c": -1.308, "mean_net_per_match_c": -1.308, "placebo_mean_net_c": -1.131, "share_net_gt_placebo_pct": 46.154, "median_best_ask": 0.59, "median_ask_shares_at_best": 438.94, "median_ask_shares_within_2c": 3405.58, "median_ask_usd_within_2c": 2592.722, "share_events_ask_shares_within_2c_ge_100_pct": 100.0}
- CELL unparsed|Map 4 Winner {"goalserve_events_total": 6, "events_usable": 6, "matches_usable": 1, "mean_pm_before_c": 0.167, "mean_pm_after_c": 1.658, "mean_net_c": 1.492, "mean_net_per_match_c": 1.492, "placebo_mean_net_c": -0.382, "share_net_gt_placebo_pct": 66.667, "median_best_ask": 0.675, "median_ask_shares_at_best": 1461.255, "median_ask_shares_within_2c": 26347.405, "median_ask_usd_within_2c": 15712.346, "share_events_ask_shares_within_2c_ge_100_pct": 100.0}
- CELL unparsed|Match Winner {"goalserve_events_total": 102, "events_usable": 79, "matches_usable": 1, "mean_pm_before_c": 1.418, "mean_pm_after_c": 0.709, "mean_net_c": -0.709, "mean_net_per_match_c": -0.709, "placebo_mean_net_c": -0.165, "share_net_gt_placebo_pct": 46.835, "median_best_ask": 0.48, "median_ask_shares_at_best": 198.0, "median_ask_shares_within_2c": 1149.88, "median_ask_usd_within_2c": 532.985, "share_events_ask_shares_within_2c_ge_100_pct": 97.468}
- CELL dota2|Map 1 Winner {"goalserve_events_total": 84, "events_usable": 0, "matches_usable": 0}
- CELL dota2|Match Winner {"goalserve_events_total": 103, "events_usable": 0, "matches_usable": 0}
- CELL dota2|Map 2 Winner {"goalserve_events_total": 82, "events_usable": 0, "matches_usable": 0}

### desc-tennis.log
- EXPLORATORY/INTERIM descriptive table; NOT the signed v2 test, no verdict, no pass; UNCHECKED until an independent checker signs
- sport "tennis"
- files 24
- goalserve_events_total 19792
- match_markets_seen 340
- unmatched_markets 124
- ambiguous_markets 6
- drops {"pm_book_rows_time_from_ms": 2002360, "book_rows_one_sided": 49233, "events_no_pm_market_or_ambiguous": 6504, "events_pm_recorder_silent_pm300s": 590}
- CELL tennis|Match Winner {"goalserve_events_total": 19792, "events_usable": 12698, "matches_usable": 204, "mean_pm_before_c": 3.039, "mean_pm_after_c": 0.863, "mean_net_c": -2.176, "mean_net_per_match_c": -1.7, "placebo_mean_net_c": 0.022, "share_net_gt_placebo_pct": 35.88, "median_best_ask": 0.56, "median_ask_shares_at_best": 224.995, "median_ask_shares_within_2c": 2319.0, "median_ask_usd_within_2c": 1155.815, "share_events_ask_shares_within_2c_ge_100_pct": 91.062}
- WORDING: open-market moves only; a tennis 'no pass' is NOT 'Goalserve has no tennis lead'

VOL2 free after the scans measured 9,994,346,496 bytes at 20:39:24Z, below the 10 GB floor. The scans had exited; no process was stopped. This is below the stop floor, not a claim that the scans caused the total concurrent disk use.
