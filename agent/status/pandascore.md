# status: PandaScore low-latency feed (v2) - RUNNING, first capture landed 13 Nov 15:11Z

Updated: 2026-11-13 15:17Z UTC. Approval: inbox `2026-11-13-pandascore-capture-APPROVED.md`
(Nick yes 14:44:29Z; task `TASK-pandascore-trial-2026-11-12.md` v2).

- **Token:** present — `/root/API_KEYS/pandascore/.env`, mode 600, `PANDASCORE_ACCESS_TOKEN`
  (51 bytes, supplied 13 Nov). **`/etc/pkarbs/pandascore.env` could not be written**: the
  terminal refuses `/etc` writes in unattended runs (consent gate, no user present), so the
  client falls back to the API_KEYS store — code checks `/etc/pkarbs/pandascore.env` first,
  then the API_KEYS file (reorder the moment an interactive run can write `/etc`).
  Token verified absent from every log/status/data file (grep, 0 hits) and never in a URL log.
- **Client:** `live/pandascore/ll_capture.py` (214 lines, `py_compile` OK), tmux session
  `pandascore`, pid 212720, started **15:12:29Z** (first process 15:11:11Z, restarted to add
  a per-row gzip flush). Discovery every 60 s with Bearer header on the low-latency feed list;
  CS2 (`cs-go`) + Dota 2 only, LoL skipped; one socket per match at/after `opens_at`;
  close codes handled per task (1000 stop, 4004 re-check, 4001/4003/4029 log-and-stop,
  1xxx/no-code backoff 1..30 s); 5-min silence logged, socket never killed on a timer.
- **Sockets:** 10 matches connected at 15:12:29Z (6 CS2, 4 Dota 2), one per match, within
  the 3-per-match limit.
- **Output:** `/vol2/pandascore/raw/pandascore_<YYYYMMDDHH>.jsonl.gz` (gzip, flush per row,
  closed at UTC hour rollover) + `/vol2/pandascore/events.jsonl.gz`.
  **45 rows by 15:13Z; first row `kind=hello`** for match 1791798 — first capture of the day
  (task deadline: first capture today) and every message logged with recv_ns, sha1,
  updated_at, available_fields, raw payload.
- **Disk:** free at start `/` 17,564,192,768 B (55%) — above the 15 GB floor; auto-stop
  guard in code writes `events` `kind=stopped` and exits at <=15 GB.
  **Same CRITICAL as goalserve: `/vol2` resolves to the root volume** (`findmnt -T /vol2` ->
  `/dev/sda1` on `/`), not a mounted disk; the 98 GB data disk sits at
  `/mnt/HC_Volume_107257520`. Path is what the task names; nothing moved; IT to rule.
- **MB/day:** first-hour measure due ~16:12Z (file size + row count of hour 2026111315).
- **Next status:** 15:47Z, 16:17Z while anything is open; capture verified by 16 Nov 12:00Z
  (BLAST Slam Dota 17 Nov); trial ends 1 Dec.
