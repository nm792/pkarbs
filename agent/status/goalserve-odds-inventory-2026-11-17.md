# Goalserve stored in-play payload inventory — 17 November 2026 10:30Z

- Files read: 3 (the note requires at least 5); stored payload rows: 4,723 (>0); distinct events: 4. Coverage is partial: only 17 Nov hourly files 08–10 were present; no 13–16 Nov files were present in the requested payload directory.
- The 10Z gzip was still actively written at the check (mtime 10:29:50Z; the Goalserve capture process was running), so the 4,723-row inventory is a live snapshot, not a final closed-file count. The note's completion gate is therefore unmet; no absence claim for Pinnacle over the requested multi-day period is valid.
- The snapshot found top-level bookmaker id empty on all 4,723 rows and no raw-body “pinnacle” matches. This is limited to the partial files above.
- Inventory snapshot output follows.

# Goalserve stored in-play payload inventory, read-only, 17 November 2026 10:30Z

- files read: 3; stored payload rows: 4723; distinct events: 4
- first/last recv_ns: 1794902402408549391 / 1794911336750649311

## Bookmaker identifiers
- top-level `bm` values (count of rows): '' (4723)
- rows whose raw body contains the string 'pinnacle' (any case): 0

## Titles (info.sport) by event-appearances
- Esports (8165)

## Markets by title (name: appearances)
- Esports: Odd/Even (1st map) (14079), Home/Away (map 1) (8692), Home/Away (map 2) (8165), Home/Away (8165), Home Win/Over (7500), Total Kills (map 2) (7119), Round Winner (map 2) (7058), Overtime (2nd map) (7058), Handicap (map 2) (7058), Total (map 2) (7058), Rounds Handicap  (map 2, 1st  half) (6990), 1st half - winner (map 2) (6864), Asian Handicap By Maps (6600), Total Maps (6337), Most Kills (map 2) (6012), Round Winner (map 1) (5405), Total Kills (map 1) (5185), Total (map 1) (4807), Handicap (map 1) (4807), Overtime (1st map) (4601), Most Kills (map 1) (4359), Rounds Handicap  (map 1, 1st  half) (3680), 1st half - winner (map 1) (3316), To Win at Least One Map (2153), Home Winning Margin (1st Half) (2092), Away Winning Margin (1st Half) (2092), Map-match (2092), Aegis Immortal Snatched (1th map) (1517), Kill Handicap (map 2) (1107), Total Tower (map 2) (1107), Home Total Kills (2nd map) (1107), Result/Total Points (2nd map) (1107), Total Duration (map 2) (1107), First Roshans(map 2) (1107), Race To 5 Kills (map 2) (1107), First Tower (map 2) (1107), First Barracks(map 2) (1107), Total Roshans (map 2) (1107), Away Total Kills(2nd map) (1107), Correct Round Score (Map 1) (1046)

## Participant names by title (name: appearances)
- Esports: Home (89221), Away (89221), Under (72798), Over (65213), 1 (55188), 2 (55188), Yes (20676), No (20676), Odd (14079), Even (14079), X (10180), Over or Exactly (7585), Elimination (5977), Bomb Detonated (5977), Bomb Defused (5977), Time (5977), 2-4 (4184), 5-7 (4184), 8-10 (4184), 11+ (4184), 1/Yes (2153), 2/Yes (2153), 1/No (2153), 2/No (2153), 13-0 (2092), 0-13 (2092), 13-1 (2092), 1-13 (2092), 13-2 (2092), 2-13 (2092)

## Update rate of the odds block per event (seconds between consecutive changes)
- n changes: 659; median 5.69 s; p90 29.56 s; p99 558.89 s

## Field names present
- event keys: core (8165), info (8165), team_info (8165), bonus (8165), stream (8165), sts (8165), stats (8165), extra (8165), history (8165), odds (8165)
- info keys: id (8165), name (8165), sport (8165), league (8165), start_time (8165), start_date (8165), start_ts (8165), start_ts_utc (8165), period (8165), minute (8165), seconds (8165)
- stats keys: 0 (8165), 1 (8165), 2 (8165), 3 (7418), 4 (2672), 5 (1107), 6 (1107), 7 (162)

PINNACLE in stored in-play bodies: no (0 rows)


## Test output

```text
PASS exit 0
PASS 6 rows read, bad line skipped
PASS 2 distinct events
PASS bm empty string reported as ''
PASS pinnacle string found in 1 row, verdict yes
PASS markets listed with title
PASS update gaps: changes at +2.0 s (gap 2.0 from +0) and +2.5 s (gap 0.5) -> n=2, median 1.25
PASS field names listed
ALL PASS
```

## Required directory listing (first 50 lines)

```text
total 231404
drwxr-xr-x  6 root root      4096 Nov 17 09:00 .
drwxr-xr-x 20 root root      4096 Nov 17 08:59 ..
drwxr-xr-x  2 root root      4096 Nov 17 10:00 basketball_payloads
drwxr-xr-x  2 root root      4096 Nov 17 10:00 esports_payloads
-rw-r--r--  1 root root 233129110 Nov 17 09:00 goalserve_20261113.jsonl
-rw-r--r--  1 root root   3790601 Nov 17 10:28 goalserve_20261117.jsonl
drwxr-xr-x  2 root root      4096 Nov 17 10:00 hockey_nhl_payloads
drwxr-xr-x  2 root root      4096 Nov 17 10:00 tennis_payloads
```

## Required payload listing (last 20 lines)

```text
/mnt/<data-volume>/pkarbs/goalserve/basketball_payloads:
basketball_2026111709.jsonl.gz
basketball_2026111710.jsonl.gz

/mnt/<data-volume>/pkarbs/goalserve/esports_payloads:
esports_2026111708.jsonl.gz
esports_2026111709.jsonl.gz
esports_2026111710.jsonl.gz

/mnt/<data-volume>/pkarbs/goalserve/hockey_nhl_payloads:
hockey_nhl_2026111709.jsonl.gz
hockey_nhl_2026111710.jsonl.gz

/mnt/<data-volume>/pkarbs/goalserve/tennis_payloads:
tennis_2026111709.jsonl.gz
tennis_2026111710.jsonl.gz
```

## Required WebSocket grep (first 10 lines)

```text
live/pandascore/NOTE-pandascore-live-2026-11-04.md
live/pandascore/__pycache__/ll_capture.cpython-314.pyc
live/pandascore/ll_capture.py
live/pandascore/ll_capture.py.pre-p7-20261113T173734Z
live/pandascore/ll_capture.py.pre-339-20261114T135600Z
live/goalserve/KEY-INSTALL-GOALSERVE.md
live/thesports/KEY-INSTALL-THESPORTS.md
live/thesports/__pycache__/capture.cpython-314.pyc
live/thesports/SPEC-thesports-trial-2026-11-05.md
live/thesports/capture.py.pre-lead8h-20261114T0335Z
```

PINNACLE in stored in-play bodies: no (partial snapshot only: 3 files, 17 Nov 08–10Z).
